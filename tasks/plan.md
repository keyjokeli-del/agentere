# Plan de Implementación Secuencial: Sistema Multi-Agente Odontológico

**Basado en:** [PRD_ARCHITECTURE.md](file:///c:/Users/herct/Desktop/agentere/docs/PRD_ARCHITECTURE.md) y [CONSTRAINTS.md](file:///c:/Users/herct/Desktop/agentere/CONSTRAINTS.md)  
**Fecha:** 2026-09-20  
**Estado:** Planificado y Desglosado

---

## 1. Visión y Dependencias Arquitectónicas

El desarrollo se organiza verticalmente de la base hacia la interfaz de usuario, garantizando que cada fase resulte en software funcional y verificable:

```
[Fase 1: Motor de Agentes Python (Triage + FAQ)]
                       │
                       ▼
[Fase 2: Motor de Citas y Google Calendar API]
                       │
                       ▼
[Fase 3: Microservicio WhatsApp Baileys + Neon Postgres]
                       │
                       ▼
[Fase 4: Panel Web y Simulador en Next.js]
```

---

## 2. Fases de Desarrollo

### Fase 1: Motor de Agentes en Python (TriageAgent & DentalFAQAgent)
- **Objetivo:** Lograr comprensión de intenciones, empatía clínica, contención médica y respuestas ultrarrápidas con Groq Llama 3.3.
- **Entregables:** Modelos Pydantic, prompts del sistema de alta precisión, clasificador de intenciones (`TriageAgent`), generador de respuestas clínicas y precios (`DentalFAQAgent`), con control de errores 429 y fallback determinista.

### Fase 2: Motor de Citas y Google Calendar API
- **Objetivo:** Cálculo autónomo de disponibilidad y registro de eventos sin solapamientos.
- **Entregables:** `CalendarService`, integración con API de Google Calendar v3 mediante Service Account / OAuth, buffers de citas (45 min) y `AppointmentAgent`.

### Fase 3: Conector WhatsApp Baileys con Persistencia en Neon Postgres
- **Objetivo:** Comunicación en tiempo real con pacientes por WhatsApp sin costo de API oficial.
- **Entregables:** Servidor Express + Baileys WebSocket, persistencia permanente de llaves criptográficas Signal en tabla `whatsapp_sessions` de Neon PostgreSQL, auto-reconexión con backoff exponencial y endpoint `/api/qr`.

### Fase 4: Panel de Control y Simulador Omnicanal en Next.js
- **Objetivo:** Centro de mando visual para recepción y odontólogos.
- **Entregables:** Dashboard Next.js 15, monitor de estado de los 4 canales, modal de código QR en vivo, simulador de chat interactivo multicanal y lista de citas sincronizadas.

---

## 3. Matriz de Riesgos y Mitigaciones

| Riesgo Técnico | Impacto | Estrategia de Mitigación |
|---|---|---|
| Rate-Limits (HTTP 429) en capa gratuita de Groq | Alto | Fallback determinista en `groq_service.py` con catálogo estático y extracción heurística. |
| Desconexión de sesión de Baileys al reiniciar | Alto | Almacenamiento de credenciales y Signal keys en Neon Serverless Postgres (`neonAuthState.js`). |
| Solapamiento de turnos en Google Calendar | Crítico | Validación estricta de intervalos de inicio y fin en `get_available_slots()`. |
| Tipado inconsistente entre backend y frontend | Medio | Pydantic v2 en Python verificado con `mypy` e interfaces TypeScript estrictas en Next.js. |
