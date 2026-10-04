# Runbook: Pacientes no reciben respuestas (WhatsApp / Redes)

**Severidad:** `PAGE` (Crítica — `/health/slo` devuelve HTTP 503 durante 2 chequeos consecutivos)  
**Objetivo de Nivel de Servicio (SLO):** Tasa de errores 5xx < 5% en ventana móvil de 5 minutos; 100% de mensajes entrantes procesados.

---

## 1. Síntomas Comunes
- La alerta de **cron-job.org** envía un email notificando fallo en `GET /health/slo`.
- Los pacientes reportan que enviaron un mensaje por WhatsApp o comentario en Instagram/YouTube y no reciben respuesta.
- La consola del Dashboard muestra el banner de backend desconectado.

---

## 2. Diagnóstico Rápido en 3 Pasos

### Paso 1: Verificar el Estado del Microservicio Baileys (`lumina-whatsapp`)
Ejecutar desde terminal o consultar la URL:
```bash
curl -s https://lumina-whatsapp.onrender.com/api/status
```
**Valores esperados:**
```json
{
  "status": "connected",
  "hasQR": false,
  "storage": "neon_postgres",
  "neonConfigured": true
}
```
- **Si `status === "disconnected"`:** El socket de WhatsApp se desvinculó o Render durmió la instancia gratuita por falta de tráfico entrante.
  - *Acción:* Entrar al Dashboard (`/dashboard`) para disparar tráfico o abrir `POST https://lumina-whatsapp.onrender.com/api/connect`.
  - Si `hasQR === true`, ingresar a la pestaña WhatsApp del Dashboard y escanear el código QR con el teléfono clínico.

### Paso 2: Rastrear el Correlation ID (`X-Request-ID`)
Cada mensaje entrante genera un `X-Request-ID` con prefijo `wa-...` en Baileys y lo propaga a FastAPI.
1. Ir a los logs de Render (`lumina-backend` o `lumina-whatsapp`).
2. Filtrar por `request_id` del paciente o buscar el evento structured:
```json
{"event": "whatsapp_message_received", "request_id": "wa-...", "sender": "5491****6781@s.whatsapp.net"}
```
3. Si el mensaje llegó a Baileys pero no a FastAPI, verificar:
   - Variable `INTERNAL_WEBHOOK_SECRET`: ¿Es idéntica en ambos servicios de Render?
   - Si FastAPI devolvió 403 Forbidden, la sincronización del secreto se perdió.

### Paso 3: Consultar Métricas RED de Emergencia
```bash
curl -s https://lumina-backend-rti9.onrender.com/api/admin/metrics -H "X-Admin-Key: lumina_admin_2026"
```
Revisar el bloque `"dependencies"`:
- `"whatsapp_bridge"`: ¿`"error" > 0`? (Fallo en reenvío a Baileys).
- `"groq"`: ¿Inferencia bloqueada o conmutando a fallback?
- `"neon_postgres"`: ¿Conexión pool agotada?

---

## 3. Acciones de Mitigación

1. **Reinicio Rápido de Contenedor en Render:**
   - Si el socket WebSocket de Baileys quedó en estado zombie (código 1006 / 428):
   - En Render Dashboard -> `lumina-whatsapp` -> "Manual Deploy" -> "Restart Service".
   - La sesión está salvaguardada en Neon PostgreSQL (`whatsapp_sessions`), por lo que NO se perderá el emparejamiento.

2. **Intervención Humana (Human Handoff):**
   - Desde la Central de Bandejas (`/dashboard`), seleccionar el paciente y redactar un mensaje manual.
   - Esto pausa automáticamente la IA por 30 minutos para ese paciente y despacha la respuesta directa vía `POST /api/dashboard/reply`.
