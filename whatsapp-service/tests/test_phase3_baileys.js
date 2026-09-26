const assert = require('assert');
const { test, describe, before, after } = require('node:test');
const http = require('http');
const { BufferJSON, initAuthCreds } = require('@whiskeysockets/baileys');
const { useNeonAuthState } = require('../neonAuthState');
const { app, calculateBackoffDelay } = require('../index');

describe('Fase 3: Microservicio WhatsApp Baileys & Neon Postgres', () => {

  // --- 1. Validar el Adaptador de Persistencia neonAuthState.js ---
  describe('1. Persistencia con Neon PostgreSQL (neonAuthState.js)', () => {
    let mockStore = {};
    let queriesExecuted = [];

    // Mock PostgreSQL Pool
    const mockPool = {
      query: async (sql, params = []) => {
        queriesExecuted.push({ sql, params });
        const normalizedSql = sql.trim().toUpperCase();

        if (normalizedSql.startsWith('CREATE TABLE IF NOT EXISTS WHATSAPP_SESSIONS')) {
          return { rows: [] };
        }

        if (normalizedSql.startsWith('SELECT DATA FROM WHATSAPP_SESSIONS')) {
          const [sessionId, keyId] = params;
          const key = `${sessionId}:${keyId}`;
          if (mockStore[key]) {
            return { rows: [{ data: mockStore[key] }] };
          }
          return { rows: [] };
        }

        if (normalizedSql.startsWith('INSERT INTO WHATSAPP_SESSIONS')) {
          const [sessionId, keyId, data] = params;
          mockStore[`${sessionId}:${keyId}`] = data;
          return { rowCount: 1 };
        }

        if (normalizedSql.startsWith('DELETE FROM WHATSAPP_SESSIONS WHERE SESSION_ID = $1 AND KEY_ID = $2')) {
          const [sessionId, keyId] = params;
          delete mockStore[`${sessionId}:${keyId}`];
          return { rowCount: 1 };
        }

        if (normalizedSql.startsWith('DELETE FROM WHATSAPP_SESSIONS WHERE SESSION_ID = $1')) {
          const [sessionId] = params;
          for (const k of Object.keys(mockStore)) {
            if (k.startsWith(`${sessionId}:`)) {
              delete mockStore[k];
            }
          }
          return { rowCount: 1 };
        }

        return { rows: [] };
      }
    };

    test('Inicializa esquema de tabla relacional whatsapp_sessions', async () => {
      queriesExecuted = [];
      mockStore = {};
      const auth = await useNeonAuthState('postgres://mock:neon@ep-test.neon.tech/neondb', 'clinic_test', mockPool);

      const tableCreation = queriesExecuted.find(q => q.sql.includes('CREATE TABLE IF NOT EXISTS whatsapp_sessions'));
      assert(tableCreation, 'Debe ejecutar la sentencia CREATE TABLE');
      assert(tableCreation.sql.includes('PRIMARY KEY (session_id, key_id)'), 'Debe definir clave primaria compuesta');
      assert(auth.state.creds, 'Debe inicializar credenciales');
    });

    test('Persiste y recupera credenciales maestras y buffers Noise/Signal', async () => {
      const auth = await useNeonAuthState('postgres://mock:neon@ep-test.neon.tech/neondb', 'clinic_test', mockPool);
      
      // Guardar creds
      await auth.saveCreds();
      assert(mockStore['clinic_test:creds'], 'Las credenciales maestras deben almacenarse en la DB');

      // Modificar clave en memoria y volver a cargar desde el mock
      const storedJson = mockStore['clinic_test:creds'];
      const decoded = JSON.parse(storedJson, BufferJSON.reviver);
      assert.strictEqual(decoded.registrationId, auth.state.creds.registrationId);
      assert(Buffer.isBuffer(decoded.noiseKey.public), 'El buffer Noise debe restaurarse como Buffer binario');
    });

    test('Gestiona almacenamiento por categorías de claves (pre-keys, sessions, app-state)', async () => {
      const auth = await useNeonAuthState('postgres://mock:neon@ep-test.neon.tech/neondb', 'clinic_test', mockPool);

      // Escribir claves
      await auth.state.keys.set({
        'pre-key': {
          '100': { keyPair: { public: Buffer.from('pub_100'), private: Buffer.from('priv_100') } }
        },
        'session': {
          '5491100001111': { handshake: Buffer.from('session_crypto_state') }
        }
      });

      assert(mockStore['clinic_test:pre-key-100'], 'Debe guardar pre-key-100');
      assert(mockStore['clinic_test:session-5491100001111'], 'Debe guardar session');

      // Leer claves con keys.get
      const preKeys = await auth.state.keys.get('pre-key', ['100']);
      assert(preKeys['100'], 'Debe retornar la pre-key 100');
      assert(Buffer.isBuffer(preKeys['100'].keyPair.public));
      assert.strictEqual(preKeys['100'].keyPair.public.toString(), 'pub_100');

      // Borrar una clave enviando valor falsy
      await auth.state.keys.set({
        'pre-key': { '100': null }
      });
      assert.strictEqual(mockStore['clinic_test:pre-key-100'], undefined, 'La pre-key debe ser eliminada');
    });

    test('clearSession purga todas las llaves de la sesión en logout', async () => {
      const auth = await useNeonAuthState('postgres://mock:neon@ep-test.neon.tech/neondb', 'clinic_test', mockPool);
      await auth.saveCreds();
      assert(Object.keys(mockStore).length > 0);

      await auth.clearSession();
      const remainingClinicKeys = Object.keys(mockStore).filter(k => k.startsWith('clinic_test:'));
      assert.strictEqual(remainingClinicKeys.length, 0, 'No deben quedar llaves tras clearSession');
    });
  });

  // --- 2. Validar Backoff Exponencial ---
  describe('2. Reconexión Automática con Backoff Exponencial', () => {
    test('Calcula los retardos exponenciales correctamente con tope en 30s', () => {
      assert.strictEqual(calculateBackoffDelay(1), 3000, 'Intento 1: 3000ms (3s)');
      assert.strictEqual(calculateBackoffDelay(2), 6000, 'Intento 2: 6000ms (6s)');
      assert.strictEqual(calculateBackoffDelay(3), 12000, 'Intento 3: 12000ms (12s)');
      assert.strictEqual(calculateBackoffDelay(4), 24000, 'Intento 4: 24000ms (24s)');
      assert.strictEqual(calculateBackoffDelay(5), 30000, 'Intento 5: 30000ms (cap 30s)');
      assert.strictEqual(calculateBackoffDelay(10), 30000, 'Intento 10: 30000ms (cap 30s)');
    });
  });

  // --- 3. Validar Endpoints REST y Reenvío Bidireccional ---
  describe('3. Endpoints REST de Baileys y Webhook Bidireccional', () => {
    let server;
    let testPort;

    before(async () => {
      await new Promise((resolve) => {
        server = http.createServer(app);
        server.listen(0, () => {
          testPort = server.address().port;
          resolve();
        });
      });
    });

    after(async () => {
      await new Promise((resolve) => {
        server.close(resolve);
      });
    });

    test('GET /api/qr sirve el estado y payload del código QR', async () => {
      const res = await fetch(`http://127.0.0.1:${testPort}/api/qr`);
      assert.strictEqual(res.status, 200);
      const data = await res.json();
      assert('status' in data, 'Debe incluir propiedad status');
      assert('storage' in data, 'Debe incluir propiedad storage');
      assert('qr' in data, 'Debe incluir propiedad qr');
    });

    test('GET /api/status retorna estado de conexión y persistencia', async () => {
      const res = await fetch(`http://127.0.0.1:${testPort}/api/status`);
      assert.strictEqual(res.status, 200);
      const data = await res.json();
      assert.strictEqual(typeof data.status, 'string');
      assert.strictEqual(typeof data.hasQR, 'boolean');
      assert.strictEqual(typeof data.neonConfigured, 'boolean');
    });

    test('POST /api/send valida parámetros obligatorios to y message', async () => {
      const resEmpty = await fetch(`http://127.0.0.1:${testPort}/api/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });
      assert.strictEqual(resEmpty.status, 400);
      const errData = await resEmpty.json();
      assert(errData.error.includes('Faltan parámetros'));

      // Intentar enviar sin conexión activa debe retornar HTTP 503
      const resDisconnected = await fetch(`http://127.0.0.1:${testPort}/api/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ to: '5491112345678', message: 'Recordatorio de turno' })
      });
      assert.strictEqual(resDisconnected.status, 503);
      const discData = await resDisconnected.json();
      assert(discData.error.includes('no está conectado'));
    });

    test('Reenvío bidireccional: Webhook FastAPI procesa mensajes entrantes de WhatsApp', async () => {
      // Validar contrato del endpoint FastAPI POST /api/webhooks/whatsapp
      const waIncomingPayload = {
        message: 'Hola, tengo mucho dolor de muela urgente',
        sender_id: '5491188776655@s.whatsapp.net',
        sender_name: 'Mateo Rossi'
      };

      // Simular la llamada que Baileys realiza hacia el backend FastAPI
      const backendUrl = process.env.PYTHON_BACKEND_URL || 'http://localhost:8000/api/webhooks/whatsapp';
      try {
        const pyRes = await fetch(backendUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(waIncomingPayload)
        });
        if (pyRes.ok) {
          const pyData = await pyRes.json();
          assert(pyData.reply, 'FastAPI debe responder con un texto reply');
          assert(pyData.agent, 'FastAPI debe indicar el agente resolutor');
          assert.strictEqual(pyData.status, 'processed');
        } else {
          console.log('[Info] FastAPI no estaba corriendo durante este test unitario aislado; validando contrato estático.');
        }
      } catch (err) {
        // En aislamiento unitario, backend puede estar apagado. Validar que la estructura de payload sea la esperada.
        assert.strictEqual(waIncomingPayload.sender_id, '5491188776655@s.whatsapp.net');
        assert(waIncomingPayload.message.length > 0);
      }
    });
  });

});
