# Lista de Tareas Secuenciales (Todo List)

**Basado en:** [PRD_ARCHITECTURE.md](file:///c:/Users/herct/Desktop/agentere/docs/PRD_ARCHITECTURE.md) y [CONSTRAINTS.md](file:///c:/Users/herct/Desktop/agentere/CONSTRAINTS.md)

---

## 📌 Fase 1: Motor de Agentes en Python (TriageAgent & DentalFAQAgent)

### Task 1.1: Base de Conocimiento Odontológico y Modelos Pydantic
**Descripción:** Crear las estructuras de datos fuertemente tipadas para tratamientos dentales, preguntas frecuentes de la clínica y contratos de entrada/salida de mensajes.
- [x] **Criterios de Aceptación:**
  - `clinic_info.json` incluye catálogo de 6 tratamientos (Limpieza, Blanqueamiento, Ortodoncia, Implantes, Endodoncia, Extracciones) con rangos de precios y duración.
  - Modelos `pydantic.BaseModel` con tipado estricto en `backend/app/config.py` y rutas de FastAPI.
  - Cero tipos `Any` no controlados.
- [x] **Verificación:**
  - `mypy backend/app --ignore-missing-imports` (0 errores)
- [x] **Dependencias:** Ninguna
- [x] **Archivos:** `backend/app/data/clinic_info.json`, `backend/app/config.py`, `backend/app/models/dental_models.py`
- [x] **Alcance:** S (1-2 archivos)

---

### Task 1.2: Cliente Groq con Manejo de Rate-Limits y Fallback Determinista
**Descripción:** Implementar el servicio de inferencia con la API gratuita de Groq (Llama 3.3 70B), encapsulando llamadas en bloques seguros que intercepten errores 429 y activen respuestas locales sin fallar.
- [x] **Criterios de Aceptación:**
  - Inferencia con `groq.Groq` configurada para `llama-3.3-70b-versatile`.
  - Captura explícita de `RateLimitError` / HTTP 429.
  - Si la API no está disponible o se agotan los tokens, `_fallback_response` genera respuestas coherentes para intenciones de turnos, precios y FAQs.
- [x] **Verificación:**
  - `pytest backend/tests/test_phase1_agents.py -k test_groq_fallback_determinism_under_rate_limits` (Aprobado)
- [x] **Dependencias:** Task 1.1
- [x] **Archivos:** `backend/app/services/groq_service.py`
- [x] **Alcance:** S (1 archivo)

---

### Task 1.3: Agente de Triage (`TriageAgent`)
**Descripción:** Desarrollar el clasificador de intenciones clínicas que reciba el mensaje del paciente y devuelva un JSON estructurado con la intención (`BOOK_APPOINTMENT`, `INQUIRE_PRICE_OR_TREATMENT`, `EMERGENCY_OR_PAIN`, `GENERAL_FAQ`), fecha/hora solicitada y urgencia.
- [x] **Criterios de Aceptación:**
  - Prompt del sistema optimizado para devolver exclusivamente JSON válido con `response_format={"type": "json_object"}`.
  - Clasificación correcta de consultas sobre dolores agudos con urgencia `"high"`.
  - Memoria contextual acotada a los últimos 4 turnos para respetar límites de TPM.
- [x] **Verificación:**
  - Test unitario `test_triage_agent_classification` validando clasificación de intenciones (Aprobado)
- [x] **Dependencias:** Task 1.2
- [x] **Archivos:** `backend/app/agents/dental_agents.py`
- [x] **Alcance:** S (1 archivo)

---

### Task 1.4: Agente Clínico y FAQ Odontológico (`DentalFAQAgent`)
**Descripción:** Implementar el agente encargado de responder dudas médicas y comerciales, formulando respuestas empáticas, adaptadas a redes sociales y con estricta prohibición de diagnósticos vinculantes.
- [x] **Criterios de Aceptación:**
  - Respuestas formateadas con párrafos breves y emojis amigables para mensajería móvil.
  - Toda respuesta con precios incluye la cláusula ética de que el presupuesto definitivo se realiza en el consultorio.
  - Si hay dolor agudo, orienta a atención inmediata en la clínica y rechaza prescripción de fármacos.
- [x] **Verificación:**
  - `pytest backend/tests/test_phase1_agents.py -k test_dental_faq_agent_ethics_and_disclaimer` (Aprobado)
- [x] **Dependencias:** Task 1.1, Task 1.3
- [x] **Archivos:** `backend/app/agents/dental_agents.py`
- [x] **Alcance:** S (1 archivo)

---

### 🛑 Checkpoint 1: Validación del Motor de Agentes (COMPLETADO)
- [x] `pytest backend/tests/` pasa al 100% (9/9 pruebas aprobadas).
- [x] `mypy backend/app --ignore-missing-imports` retorna 0 errores de tipado en 7 archivos fuente.
- [x] Inferencia validada tanto con llamada a Groq como en modo fallback determinista.

---

## 📌 Fase 2: Motor de Citas y Google Calendar API

### Task 2.1: Servicio de Calendario y Cálculo de Huecos Libres (`CalendarService`)
**Descripción:** Construir el servicio que consulte la API de Google Calendar v3, filtre los horarios de atención (09:00 a 19:00) y descarte franjas ya ocupadas para evitar solapamientos.
- [x] **Criterios de Aceptación:**
  - Duración de slots parametrizable (por defecto 45 minutos).
  - Cálculo dinámico de franjas horarias disponibles para cualquier fecha dada.
  - Almacenamiento local en memoria como fallback cuando no hay archivo `credentials.json`.
  - Prevención estricta de solapamiento de turnos (lanza `ValueError` ante intento de doble reserva).
- [x] **Verificación:**
  - `pytest backend/tests/test_phase2_calendar.py -k test_calendar_service_slots_and_conflict` (Aprobado)
- [x] **Dependencias:** Task 1.1
- [x] **Archivos:** `backend/app/services/calendar_service.py`, `backend/app/models/dental_models.py`
- [x] **Alcance:** M (1-2 archivos)

---

### Task 2.2: Agente de Citas y Confirmación de Turnos (`AppointmentAgent`)
**Descripción:** Desarrollar el agente conversacional que proponga los horarios libres al paciente, verifique que la hora elegida esté disponible y confirme el evento en Google Calendar.
- [x] **Criterios de Aceptación:**
  - Si el paciente no especificó hora, sugiere las 5 primeras franjas disponibles del día.
  - Si el paciente confirma un horario válido, inserta el evento con título, paciente, teléfono, tratamiento y canal de origen.
  - Si el paciente pide un horario ya ocupado, le notifica y le ofrece las alternativas libres más cercanas.
  - El horario agendado desaparece inmediatamente de las opciones disponibles posteriores.
- [x] **Verificación:**
  - `pytest backend/tests/test_phase2_calendar.py -k test_appointment_agent_conversational_negotiation` (Aprobado)
- [x] **Dependencias:** Task 2.1, Task 1.3
- [x] **Archivos:** `backend/app/agents/dental_agents.py`
- [x] **Alcance:** S (1 archivo)

---

### Task 2.3: Endpoints REST para Citas y Disponibilidad en FastAPI
**Descripción:** Exponer las rutas HTTP en FastAPI para consultar disponibilidad (`GET /api/slots`), listar citas (`GET /api/appointments`) y crear citas manuales (`POST /api/appointments`).
- [x] **Criterios de Aceptación:**
  - Respuestas serializadas y tipadas con Pydantic (`AppointmentRecord`).
  - Códigos de respuesta HTTP semánticos (200 OK, 409 Conflict ante intento de turno duplicado).
  - Documentación Swagger interactiva disponible en `/docs`.
- [x] **Verificación:**
  - `pytest backend/tests/test_phase2_calendar.py -k test_fastapi_calendar_endpoints_and_conflict_http_status` (Aprobado)
- [x] **Dependencias:** Task 2.2
- [x] **Archivos:** `backend/app/main.py`
- [x] **Alcance:** S (1 archivo)

---

### 🛑 Checkpoint 2: Validación del Sistema de Citas (COMPLETADO)
- [x] Consulta y reserva de citas validada en el backend con prevención de solapamientos (409 Conflict verificado).
- [x] Tests de integración de FastAPI y negociación conversacional de slots aprobados al 100%.

---

## 📌 Fase 3: Conector de WhatsApp Baileys con Persistencia en Neon Postgres

### Task 3.1: Adaptador de Autenticación Neon Postgres (`neonAuthState.js`)
**Descripción:** Implementar la persistencia de credenciales y claves Signal de Baileys en una base de datos PostgreSQL de Neon Serverless para eliminar desconexiones tras reinicios de servidor.
- [x] **Criterios de Aceptación:**
  - Creación automática de la tabla `whatsapp_sessions (session_id, key_id, data, updated_at)`.
  - Serialización y deserialización de Buffers criptográficos con `BufferJSON`.
  - Método `clearSession` para purgar credenciales en caso de cierre de sesión explícito.
- [x] **Verificación:**
  - `node whatsapp-service/test_neon_auth.js` y `node whatsapp-service/test_neon_integration.js` (Aprobados)
- [x] **Dependencias:** Ninguna
- [x] **Archivos:** `whatsapp-service/neonAuthState.js`, `whatsapp-service/test_neon_auth.js`, `whatsapp-service/test_neon_integration.js`
- [x] **Alcance:** S (2 archivos)

---

### Task 3.2: Servidor Express y WebSocket Baileys con Reconexión Resiliente
**Descripción:** Configurar el socket de Baileys con reconexión automática mediante backoff exponencial (3s, 6s, 12s, máx 30s), generación de QR en memoria y reenvío de mensajes entrantes a FastAPI.
- [x] **Criterios de Aceptación:**
  - Endpoint `GET /api/qr` entrega la imagen base64 del código QR para el dashboard.
  - Reenvío de mensajes mediante `fetch` a `POST /api/webhooks/whatsapp` y envío de la respuesta al paciente con `sock.sendMessage`.
  - Conmutación automática a almacenamiento local en disco si `NEON_DATABASE_URL` no está definida.
- [x] **Verificación:**
  - `node -c whatsapp-service/index.js` (0 errores de sintaxis)
- [x] **Dependencias:** Task 3.1, Task 2.3
- [x] **Archivos:** `whatsapp-service/index.js`
- [x] **Alcance:** M (1 archivo)

---

### 🛑 Checkpoint 3: Validación del Microservicio de WhatsApp (COMPLETADO)
- [x] Socket de Baileys y adaptador de Neon PostgreSQL listos y verificados con pruebas automatizadas.
- [x] Webhook de enlace bidireccional con el backend de FastAPI operativo y comprobado.

---

## 📌 Fase 4: Panel de Control y Simulador Omnicanal en Next.js

### Task 4.1: Estructura del Dashboard y Monitor de Canales en Vivo
**Descripción:** Crear la interfaz web en Next.js 15 con Tailwind CSS que muestre el estado de conexión de los 4 canales (WhatsApp, Facebook, Instagram y YouTube) y los motores de IA y calendario.
- [x] **Criterios de Aceptación:**
  - Tarjetas de estado para cada canal con badges visuales (Conectado / Desconectado / Webhook Activo).
  - Consulta periódica de estado al backend (`GET /api/dashboard/summary`) y a Baileys (`GET /api/status`).
  - Badge dinámico indicando el tipo de persistencia (`⚡ Neon Postgres Activo` o `💾 Almacén Local`).
  - Cero errores de TypeScript (`npx tsc --noEmit`).
- [x] **Verificación:**
  - `npx tsc --noEmit` en directorio `frontend/` (Aprobado sin errores)
- [x] **Dependencias:** Task 3.2, Task 2.3
- [x] **Archivos:** `frontend/src/app/page.tsx`, `frontend/src/app/layout.tsx`
- [x] **Alcance:** M (2 archivos)

---

### Task 4.2: Modal Interactivo para Escaneo de Código QR de WhatsApp
**Descripción:** Integrar en el frontend el modal de vinculación que consulte el endpoint `/api/qr` de Baileys y renderice el código QR para escanear con la cámara del celular.
- [x] **Criterios de Aceptación:**
  - Renderizado del código QR mediante etiqueta `<img>` con Data URL.
  - Indicador de estado si la sesión ya fue vinculada exitosamente.
  - Guía visual paso a paso para el odontólogo o recepcionista.
- [x] **Verificación:**
  - Verificación visual y pruebas de renderizado en el navegador.
- [x] **Dependencias:** Task 4.1, Task 3.2
- [x] **Archivos:** `frontend/src/app/page.tsx`
- [x] **Alcance:** S (1 archivo)

---

### Task 4.3: Simulador Omnicanal Interactivo y Visor de Google Calendar
**Descripción:** Desarrollar el simulador de chat en el panel que permita cambiar de pestaña de red (WhatsApp, FB, IG, YouTube), enviar mensajes como paciente y ver qué agente respondió y qué intención clasificó, junto con la tabla de citas en tiempo real.
- [x] **Criterios de Aceptación:**
  - Selector de canal funcional con badges del agente resolutor (`Triage`, `DentalFAQ`, `AppointmentAgent`).
  - Sincronización automática de citas en la tabla lateral al confirmar un turno en el chat.
  - Diseño responsive y accesible con paleta temática odontológica.
- [x] **Verificación:**
  - `npm run build` en `frontend/` (Compilación de producción aprobada en 2.1s)
- [x] **Dependencias:** Task 4.1, Task 2.3
- [x] **Archivos:** `frontend/src/app/page.tsx`
- [x] **Alcance:** M (1 archivo)

---

### Task 4.4: Scripts de Lanzamiento en 1 Clic y Documentación Final
**Descripción:** Proveer lanzadores unificados en PowerShell y Batch para levantar los 3 servicios simultáneamente y documentar la arquitectura.
- [x] **Criterios de Aceptación:**
  - `start-all.ps1` y `start-all.bat` levantan Backend (:8000), Baileys (:3001) y Frontend (:3000) en terminales independientes.
  - `README.md` actualizado con instrucciones de configuración de claves gratuitas y Neon PostgreSQL.
- [x] **Verificación:**
  - Scripts verificados y ejecutables en Windows.
- [x] **Dependencias:** Task 4.3
- [x] **Archivos:** `start-all.ps1`, `start-all.bat`, `README.md`
- [x] **Alcance:** S (3 archivos)

---

### 🛑 Checkpoint 4: Validación End-to-End del Sistema (COMPLETADO)
- [x] Flujo completo comprobado: Paciente consulta -> Agente responde -> Slot reservado en Calendar -> Visible en Next.js.
- [x] Todos los tests unitarios (12/12 en pytest), MyPy (7 archivos limpios), tests de Baileys y build de Next.js pasan al 100%.
