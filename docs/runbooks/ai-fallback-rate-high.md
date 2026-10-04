# Runbook: Alta Tasa de Fallback de IA (`ai_fallback_rate > 20%`)

**Severidad:** `TICKET` (Degradado — El sistema sigue respondiendo con reglas deterministas sin tirar 503)  
**Objetivo de Nivel de Servicio (SLO):** Tasa de fallback < 20% en ventana móvil de 15 minutos; respuestas personalizadas con RAG clínico activo.

---

## 1. Síntomas
- El endpoint `GET /health/slo` devuelve HTTP 200 pero con el flag `"degraded": true`:
```json
{
  "status": "healthy",
  "degraded": true,
  "ai_fallback_rate_15m_pct": 33.3,
  "p95_latency_ms": 42.0
}
```
- Los pacientes reciben respuestas enlatadas o estándar en lugar de respuestas conversacionales detalladas.

---

## 2. Diagnóstico Rápido

### Paso 1: Revisar Eventos `ai_fallback_used` en Logs de Render
En los logs de `lumina-backend`, buscar la traza JSON:
```json
{"event": "ai_fallback_used", "reason": "rate_limit_429", "request_id": "req-..."}
```
**Causas Posibles:**
1. **`reason: "rate_limit_429"`:**
   - La capa gratuita de Groq Cloud (`llama-3.3-70b-versatile`) alcanzó el límite de solicitudes por minuto (RPM) o tokens por minuto (TPM).
   - *Comportamiento del sistema:* Lumina Dental Studio conmuta instantáneamente al motor de respuestas deterministas basadas en reglas para que ningún paciente quede sin contestación.
2. **`reason: "no_client"` o `"groq_init_failed"`:**
   - La variable `GROQ_API_KEY` en Render Environment se invalidó, expiró o no está configurada.
3. **`reason: "empty_response"`:**
   - Filtro de seguridad de contenido devolvió string vacío.

### Paso 2: Verificar Estado de Dependencias
```bash
curl -s https://lumina-backend-rti9.onrender.com/api/admin/metrics -H "X-Admin-Key: lumina_admin_2026"
```
Examinar la sección `"ai_inference_15m"` y `"dependencies" -> "groq"`.

---

## 3. Acciones de Mitigación

1. **Rotar o Revalidar `GROQ_API_KEY`:**
   - Ingresar a [Groq Cloud Console](https://console.groq.com/keys).
   - Crear una nueva clave API gratuita.
   - En Render Dashboard -> `lumina-backend` -> Environment, actualizar `GROQ_API_KEY`.
   - Render redesplegará automáticamente en ~30 segundos.

2. **Ajuste de Conmutación a Modelo Alternativo:**
   - Si `llama-3.3-70b-versatile` tiene alta congestión en Groq, cambiar la variable `GROQ_MODEL` a `llama-3.1-8b-instant` (mucho mayor cuota RPM gratuita y latencia sub-segundo).
