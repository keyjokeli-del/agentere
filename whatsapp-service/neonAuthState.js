const { Pool } = require('pg');
const { initAuthCreds, BufferJSON } = require('@whiskeysockets/baileys');

/**
 * Custom Baileys Auth State Adapter using Neon PostgreSQL
 * Ensures WhatsApp token and cryptographic keys persist across server restarts.
 */
async function useNeonAuthState(databaseUrl, sessionId = 'dental_clinic_session', customPool = null) {
  const pool = customPool || new Pool({
    connectionString: databaseUrl,
    ssl: {
      rejectUnauthorized: false
    }
  });

  // Ensure table exists
  await pool.query(`
    CREATE TABLE IF NOT EXISTS whatsapp_sessions (
      session_id VARCHAR(64) NOT NULL,
      key_id VARCHAR(255) NOT NULL,
      data TEXT NOT NULL,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY (session_id, key_id)
    );
  `);

  console.log(`[NeonAuthState] Conectado a Neon PostgreSQL. Tabla whatsapp_sessions lista para sesión: '${sessionId}'`);

  // Helper to read a key
  const readData = async (keyId) => {
    try {
      const res = await pool.query(
        'SELECT data FROM whatsapp_sessions WHERE session_id = $1 AND key_id = $2',
        [sessionId, keyId]
      );
      if (res.rows.length > 0) {
        return JSON.parse(res.rows[0].data, BufferJSON.reviver);
      }
      return null;
    } catch (error) {
      console.error(`[NeonAuthState] Error leyendo clave '${keyId}':`, error.message);
      return null;
    }
  };

  // Helper to write/update a key
  const writeData = async (keyId, value) => {
    try {
      const serialized = JSON.stringify(value, BufferJSON.replacer);
      await pool.query(
        `INSERT INTO whatsapp_sessions (session_id, key_id, data, updated_at)
         VALUES ($1, $2, $3, CURRENT_TIMESTAMP)
         ON CONFLICT (session_id, key_id)
         DO UPDATE SET data = EXCLUDED.data, updated_at = CURRENT_TIMESTAMP`,
        [sessionId, keyId, serialized]
      );
    } catch (error) {
      console.error(`[NeonAuthState] Error guardando clave '${keyId}':`, error.message);
    }
  };

  // Helper to delete keys
  const removeData = async (keyId) => {
    try {
      await pool.query(
        'DELETE FROM whatsapp_sessions WHERE session_id = $1 AND key_id = $2',
        [sessionId, keyId]
      );
    } catch (error) {
      console.error(`[NeonAuthState] Error eliminando clave '${keyId}':`, error.message);
    }
  };

  // Clear all session data on logout
  const clearSession = async () => {
    try {
      await pool.query('DELETE FROM whatsapp_sessions WHERE session_id = $1', [sessionId]);
      console.log(`[NeonAuthState] Sesión '${sessionId}' purgada de Neon PostgreSQL.`);
    } catch (error) {
      console.error(`[NeonAuthState] Error purgando sesión '${sessionId}':`, error.message);
    }
  };

  // Initialize creds
  const existingCreds = await readData('creds');
  const creds = existingCreds || initAuthCreds();

  return {
    state: {
      creds,
      keys: {
        get: async (type, ids) => {
          const data = {};
          await Promise.all(
            ids.map(async (id) => {
              const value = await readData(`${type}-${id}`);
              if (value) {
                data[id] = value;
              }
            })
          );
          return data;
        },
        set: async (data) => {
          const tasks = [];
          for (const category in data) {
            for (const id in data[category]) {
              const value = data[category][id];
              const key = `${category}-${id}`;
              if (value) {
                tasks.push(writeData(key, value));
              } else {
                tasks.push(removeData(key));
              }
            }
          }
          await Promise.all(tasks);
        }
      }
    },
    saveCreds: () => writeData('creds', creds),
    clearSession,
    pool
  };
}

module.exports = { useNeonAuthState };
