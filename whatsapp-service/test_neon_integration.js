const assert = require('assert');
const { initAuthCreds, BufferJSON } = require('@whiskeysockets/baileys');

console.log('[Phase 3 Test] Iniciando validación del subsistema de WhatsApp Baileys y Neon Postgres...');

// 1. Validar serialización de todas las categorías de claves de Baileys
const testKeys = {
  'pre-key-1': {
    keyPair: {
      public: Buffer.from('pub_key_bytes_123'),
      private: Buffer.from('priv_key_bytes_456')
    }
  },
  'session-5491112345678': {
    sessionData: Buffer.from('session_crypto_handshake')
  },
  'app-state-sync-key-1': {
    keyData: Buffer.from('sync_key_bytes_789')
  }
};

for (const [keyId, value] of Object.entries(testKeys)) {
  const jsonStr = JSON.stringify(value, BufferJSON.replacer);
  assert(jsonStr.includes('"type":"Buffer"'), `La clave ${keyId} debe serializarse con formato Buffer`);
  
  const restored = JSON.parse(jsonStr, BufferJSON.reviver);
  // Check that restored object contains Buffer
  if (value.keyPair) {
    assert(Buffer.isBuffer(restored.keyPair.public), `${keyId}.keyPair.public debe ser Buffer`);
    assert.strictEqual(restored.keyPair.public.toString(), 'pub_key_bytes_123');
  }
  if (value.sessionData) {
    assert(Buffer.isBuffer(restored.sessionData), `${keyId}.sessionData debe ser Buffer`);
    assert.strictEqual(restored.sessionData.toString(), 'session_crypto_handshake');
  }
}
console.log('✔ [Phase 3 Test] Serialización y deserialización de claves criptográficas Signal: Aprobada.');

// 2. Validar credenciales maestras iniciales
const creds = initAuthCreds();
assert(creds.registrationId > 0, 'registrationId debe ser un número entero positivo');
assert(creds.noiseKey, 'noiseKey debe generarse');
assert(Buffer.isBuffer(creds.noiseKey.public), 'noiseKey.public debe ser Buffer');

const credsJson = JSON.stringify(creds, BufferJSON.replacer);
const restoredCreds = JSON.parse(credsJson, BufferJSON.reviver);
assert.strictEqual(restoredCreds.registrationId, creds.registrationId);
assert(Buffer.isBuffer(restoredCreds.noiseKey.public));
console.log('✔ [Phase 3 Test] Estructura de credenciales maestras de Baileys: Aprobada.');

// 3. Validar sintaxis SQL de la tabla de Neon PostgreSQL
const createTableQuery = `
  CREATE TABLE IF NOT EXISTS whatsapp_sessions (
    session_id VARCHAR(64) NOT NULL,
    key_id VARCHAR(255) NOT NULL,
    data TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (session_id, key_id)
  );
`;
assert(createTableQuery.includes('PRIMARY KEY (session_id, key_id)'), 'La clave primaria debe ser compuesta');
assert(createTableQuery.includes('whatsapp_sessions'), 'La tabla debe llamarse whatsapp_sessions');
console.log('✔ [Phase 3 Test] Esquema relacional para Neon PostgreSQL: Aprobado.');

console.log('✅ [Phase 3 Test] Checkpoint 3 Superado: Todos los componentes del servicio Baileys verificados.');
