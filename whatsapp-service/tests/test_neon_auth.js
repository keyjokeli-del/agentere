const assert = require('assert');
const { initAuthCreds, BufferJSON } = require('@whiskeysockets/baileys');

console.log('[Test] Probando serialización y credenciales de Baileys...');

// 1. Test BufferJSON serialization of Noise / Signal keys
const originalData = {
  noiseKey: {
    private: Buffer.from('private_noise_key_12345'),
    public: Buffer.from('public_noise_key_67890')
  },
  registrationId: 12345,
  account: {
    details: 'detalles_cuenta'
  }
};

const serialized = JSON.stringify(originalData, BufferJSON.replacer);
assert(typeof serialized === 'string', 'La serialización debe retornar un string JSON');
assert(serialized.includes('"type":"Buffer"'), 'Debe incluir el tag type Buffer');

const deserialized = JSON.parse(serialized, BufferJSON.reviver);
assert(Buffer.isBuffer(deserialized.noiseKey.private), 'noiseKey.private debe ser deserializado como Buffer');
assert.strictEqual(
  deserialized.noiseKey.private.toString(),
  'private_noise_key_12345',
  'El contenido del Buffer debe ser idéntico'
);

// 2. Test initial auth creds generation
const creds = initAuthCreds();
assert(creds.noiseKey, 'initAuthCreds debe generar noiseKey');
assert(creds.pairingEphemeralKeyPair, 'initAuthCreds debe generar pairingEphemeralKeyPair');

console.log('✅ [Test] Todas las pruebas de serialización y credenciales de Baileys pasaron con éxito.');
