require('dotenv').config({ path: require('path').resolve(__dirname, '../.env') });
require('dotenv').config(); // Also check local .env

const express = require('express');
const cors = require('cors');
const qrcode = require('qrcode');
const pino = require('pino');
const path = require('path');
const fs = require('fs');

const {
  default: makeWASocket,
  useMultiFileAuthState,
  DisconnectReason,
  fetchLatestBaileysVersion
} = require('@whiskeysockets/baileys');

const { useNeonAuthState } = require('./neonAuthState');

const app = express();
app.use(cors());
app.use(express.json());

// Global safety handlers to prevent process termination on abnormal WebSocket drops (e.g. 1006 / 428)
process.on('unhandledRejection', (reason) => {
  console.warn('[Baileys Warning] Unhandled Promise Rejection interceptado:', reason);
});
process.on('uncaughtException', (err) => {
  console.error('[Baileys Error] Uncaught Exception interceptado:', err.message);
});

const PORT = process.env.WHATSAPP_SERVICE_PORT || process.env.PORT || 3001;
const PYTHON_BACKEND_URL = process.env.PYTHON_BACKEND_URL || 'http://localhost:8000/api/webhooks/whatsapp';
const NEON_DATABASE_URL = process.env.NEON_DATABASE_URL || process.env.DATABASE_URL || '';
const WA_SESSION_ID = process.env.WA_SESSION_ID || 'dental_clinic_session';

let currentQR = null;
let connectionStatus = 'disconnected'; // 'disconnected' | 'connecting' | 'connected'
let connectedUser = null;
let sock = null;
let reconnectAttempts = 0;
let clearDBSession = null;
let activeStorageMode = 'local_disk';

const logger = pino({ level: 'warn' });
const authFolder = path.join(__dirname, 'auth_info_baileys');

function calculateBackoffDelay(attempt) {
  // Exponential backoff: 3s, 6s, 12s, 24s, capped at 30s
  return Math.min(3000 * Math.pow(2, Math.max(0, attempt - 1)), 30000);
}

async function forwardToFastAPI(messageText, sender, senderName) {
  const response = await fetch(PYTHON_BACKEND_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: messageText,
      sender_id: sender,
      sender_name: senderName
    })
  });
  if (!response.ok) {
    throw new Error(`FastAPI devolvió status ${response.status}: ${response.statusText}`);
  }
  return await response.json();
}

async function startWhatsApp() {
  connectionStatus = 'connecting';

  try {
    let state, saveCreds;

    // Decide storage engine: Neon Postgres vs Local Disk
    if (NEON_DATABASE_URL && NEON_DATABASE_URL.startsWith('postgres')) {
      try {
        console.log('[Baileys] Inicializando almacenamiento persistente en Neon PostgreSQL...');
        const neonAuth = await useNeonAuthState(NEON_DATABASE_URL, WA_SESSION_ID);
        state = neonAuth.state;
        saveCreds = neonAuth.saveCreds;
        clearDBSession = neonAuth.clearSession;
        activeStorageMode = 'neon_postgres';
      } catch (dbErr) {
        console.error('[Baileys] Error conectando a Neon PostgreSQL:', dbErr.message);
        console.log('[Baileys] Pasando a modo de contingencia: almacenamiento en disco local.');
        const localAuth = await useMultiFileAuthState(authFolder);
        state = localAuth.state;
        saveCreds = localAuth.saveCreds;
        activeStorageMode = 'local_disk';
      }
    } else {
      console.log('[Baileys] Sin NEON_DATABASE_URL. Utilizando almacenamiento en disco local (auth_info_baileys).');
      const localAuth = await useMultiFileAuthState(authFolder);
      state = localAuth.state;
      saveCreds = localAuth.saveCreds;
      activeStorageMode = 'local_disk';
    }

    const { version, isLatest } = await fetchLatestBaileysVersion();

    sock = makeWASocket({
      version,
      logger,
      printQRInTerminal: false,
      auth: state,
      generateHighQualityLinkPreview: true,
    });

    sock.ev.on('creds.update', saveCreds);

    sock.ev.on('connection.update', async (update) => {
      const { connection, lastDisconnect, qr } = update;

      if (qr) {
        try {
          currentQR = await qrcode.toDataURL(qr);
          connectionStatus = 'waiting_for_scan';
          console.log('[Baileys] Código QR generado. Listo para escanear en el dashboard.');
        } catch (err) {
          console.error('[Baileys] Error generando código QR:', err);
        }
      }

      if (connection === 'close') {
        const statusCode = lastDisconnect?.error?.output?.statusCode;
        const isLoggedOut = statusCode === DisconnectReason.loggedOut;
        
        console.log(
          `[Baileys] Conexión cerrada (código ${statusCode}): ${lastDisconnect?.error?.message || lastDisconnect?.error}`
        );
        connectionStatus = 'disconnected';
        currentQR = null;
        connectedUser = null;

        if (isLoggedOut) {
          console.log('[Baileys] Sesión cerrada o expirada. Purgando credenciales...');
          if (clearDBSession) {
            await clearDBSession().catch(() => {});
          }
          if (fs.existsSync(authFolder)) {
            fs.rmSync(authFolder, { recursive: true, force: true });
          }
          reconnectAttempts = 0;
          setTimeout(startWhatsApp, 1500);
        } else {
          // Exponential backoff: 3s, 6s, 12s, max 30s
          reconnectAttempts++;
          const delay = calculateBackoffDelay(reconnectAttempts);
          console.log(`[Baileys] Reconectando automáticamente en ${delay / 1000}s (intento #${reconnectAttempts})...`);
          setTimeout(startWhatsApp, delay);
        }
      } else if (connection === 'open') {
        console.log(`[Baileys] ¡WhatsApp conectado con éxito! Modo de almacenamiento: ${activeStorageMode}`);
        connectionStatus = 'connected';
        currentQR = null;
        connectedUser = sock.user?.id || 'Conectado';
        reconnectAttempts = 0; // Reset backoff
      }
    });

    sock.ev.on('messages.upsert', async ({ messages, type }) => {
      if (type !== 'notify') return;

      for (const msg of messages) {
        if (!msg.message || msg.key.fromMe) continue;
        const sender = msg.key.remoteJid;
        if (sender.endsWith('@broadcast')) continue;

        const messageText =
          msg.message.conversation ||
          msg.message.extendedTextMessage?.text ||
          msg.message.imageMessage?.caption ||
          '';

        if (!messageText.trim()) continue;

        const senderName = msg.pushName || 'Paciente';
        console.log(`[Baileys] Mensaje recibido de ${senderName} (${sender}): ${messageText}`);

        try {
          // Forward to Python Backend Agent
          const data = await forwardToFastAPI(messageText, sender, senderName);
          if (data && data.reply) {
            console.log(`[Baileys] Enviando respuesta del agente a ${sender}...`);
            await sock.sendMessage(sender, { text: data.reply });
          }
        } catch (err) {
          console.error('[Baileys] Error conectando con el backend de Python:', err.message);
        }
      }
    });
  } catch (initErr) {
    console.error('[Baileys] Error durante la inicialización:', initErr.message || initErr);
    connectionStatus = 'disconnected';
    reconnectAttempts++;
    const delay = calculateBackoffDelay(reconnectAttempts);
    console.log(`[Baileys] Reintentando inicialización en ${delay / 1000}s (intento #${reconnectAttempts})...`);
    setTimeout(startWhatsApp, delay);
  }
}

// REST Endpoints for Dashboard
app.get('/api/status', (req, res) => {
  res.json({
    status: connectionStatus,
    user: connectedUser,
    hasQR: Boolean(currentQR),
    storage: activeStorageMode,
    neonConfigured: Boolean(NEON_DATABASE_URL)
  });
});

app.get('/api/qr', (req, res) => {
  res.json({
    qr: currentQR,
    status: connectionStatus,
    storage: activeStorageMode
  });
});

app.post('/api/send', async (req, res) => {
  const { to, message } = req.body || {};
  if (!to || !message) {
    return res.status(400).json({ error: 'Faltan parámetros requeridos: "to" y "message"' });
  }
  if (connectionStatus !== 'connected' || !sock) {
    return res.status(503).json({ error: 'WhatsApp no está conectado actualmente' });
  }
  try {
    const jid = to.includes('@') ? to : `${to.replace(/\D/g, '')}@s.whatsapp.net`;
    const result = await sock.sendMessage(jid, { text: message });
    return res.json({ success: true, result });
  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
});

app.post('/api/connect', (req, res) => {
  if (connectionStatus === 'connected') {
    return res.json({ message: 'Ya está conectado' });
  }
  startWhatsApp();
  res.json({ message: 'Iniciando conexión de WhatsApp...' });
});

app.post('/api/disconnect', async (req, res) => {
  try {
    if (sock) {
      await sock.logout();
    }
    if (clearDBSession) {
      await clearDBSession();
    }
    if (fs.existsSync(authFolder)) {
      fs.rmSync(authFolder, { recursive: true, force: true });
    }
    connectionStatus = 'disconnected';
    currentQR = null;
    connectedUser = null;
    res.json({ message: 'Sesión cerrada y credenciales eliminadas' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`[WhatsApp Service] Escuchando en http://localhost:${PORT}`);
    console.log(`[WhatsApp Service] Modo de persistencia: ${NEON_DATABASE_URL ? 'Neon PostgreSQL' : 'Disco local (auth_info_baileys)'}`);
    // Automatically start connection on launch
    startWhatsApp();
  });
}

module.exports = {
  app,
  startWhatsApp,
  calculateBackoffDelay,
  forwardToFastAPI,
  getStatus: () => ({ connectionStatus, currentQR, connectedUser, activeStorageMode })
};
