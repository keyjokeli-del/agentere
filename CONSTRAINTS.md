# Constraints: Estándares de Calidad y Resiliencia

**Proyecto:** Sistema Multi-Agente Omnicanal para Clínica Dental  
**Última revisión:** 2026-09-20 por @ingenieria-clinica  
**Objetivo:** Establecer el contrato formal de calidad, resiliencia y tipado estricto para garantizar operación $0 USD ininterrumpida y libre de fallos silenciosos.

---

## 1. Reglas Base Obligatorias (The Floor)

Estas reglas aplican a cada commit y edición. Están activas permanentemente:
- **Cero comentarios de supresión:** Prohibido el uso de `@ts-ignore`, `@ts-nocheck`, `eslint-disable`, `# noqa` y `# type: ignore` para silenciar errores del compilador o linter.
- **Cero bloques de excepción mudos:** Prohibido dejar `except:` vacíos o bloques `catch {}` sin logging estructurado del error o fallback controlado.
- **Cero stubs sin implementar:** Prohibido dejar `TODO`, `throw new Error("Not implemented")` o funciones con `pass` en flujos de producción.
- **Cero secretos en código fuente:** Credenciales de Groq, tokens de Meta o service accounts de Google Calendar NUNCA se escriben directamente en código; se consumen vía variables de entorno (`.env`).
- **Pruebas inmutables:** No se pueden eliminar ni desactivar assertions de tests existentes para forzar un pase en verde.
- **Inmutabilidad del estándar:** Este archivo `CONSTRAINTS.md` no se relaja ni debilita para justificar código defectuoso.

---

## 2. Dimensiones de Calidad con Comandos Verificables

| Dimensión | Estándar Obligatorio | Comando de Verificación | Cuándo se Ejecuta |
|---|---|---|---|
| **Tipado Frontend** | 0 errores TypeScript estricto | `npm run build` (o `npx tsc --noEmit`) | En cada cambio de UI |
| **Tipado Backend** | 0 errores de tipo en modelos y rutas | `mypy backend/app` | En cada cambio de agente/API |
| **Validación de Datos** | 100% de payloads parseados con Pydantic v2 | `pytest backend/tests/test_dental_agents.py` | Pre-commit / CI |
| **Resiliencia Baileys** | Auto-reconexión con backoff exponencial | `node -c whatsapp-service/index.js` + Test de reconexión | Deploy / Task end |
| **Groq Rate-Limits** | Control de error 429 y fallback local determinista | `pytest backend/tests/test_dental_agents.py -k test_chat_faq_flow` | En cada cambio de agentes |
| **Agenda Google Calendar** | Detección y rechazo de solapamiento de turnos | `pytest backend/tests/test_dental_agents.py -k test_calendar_slots_and_booking` | En cada cambio de citas |

---

## 3. Especificación Técnica de los 3 Pilares Críticos

### Pilar 1: Manejo Resiliente de WebSockets en Baileys (Reconexión Automática)
Para evitar que la clínica dental quede desconectada si el teléfono pierde señal temporal o reinicia:
1. **Detección de Desconexión:** El socket debe interceptar el evento `connection.update` y clasificar la causa con `lastDisconnect?.error?.output?.statusCode`.
2. **Reconexión Automática vs Logout:**
   - Si la causa es `DisconnectReason.loggedOut` (401), el sistema purga el directorio de sesión `auth_info_baileys/`, limpia el estado a `disconnected` y genera inmediatamente un nuevo código QR para escanear en pantalla.
   - Para cualquier otra causa de red (timeout, socket hang up, 428, 515 restart required, red intermitente), el servicio **DEBE reconectarse automáticamente**.
3. **Estrategia de Backoff:**
   - La reconexión se ejecuta mediante temporizador con retardo progresivo (backoff exponencial de 3s, 6s, 12s hasta un máximo de 30s) para evitar sobrecargar los servidores de WhatsApp.
4. **Preservación de Estado:** Los mensajes entrantes durante la reconexión se procesan en lote tan pronto se restablece el socket (`messages.upsert` de Baileys).

### Pilar 2: Control de Rate-Limits y Fallback para la Capa Gratuita de Groq
La capa gratuita de Groq Cloud impone límites estrictos de peticiones por minuto (RPM) y tokens por minuto (TPM):
1. **Captura Estricta de Errores:** Toda llamada a `groq_service.chat_completion()` debe estar encapsulada en bloque `try/except Exception`.
2. **Manejo de HTTP 429 (Rate Limit Exceeded):**
   - Si la API de Groq devuelve código 429 o error de cuota temporal, el agente **NUNCA debe arrojar un error 500 al paciente ni detener el webhook**.
   - Se debe activar inmediatamente el **mecanismo de fallback inteligente local**:
     - Para intención de agendamiento: se extraen datos con expresiones regulares/reglas de fecha y se consulta el calendario localmente.
     - Para consultas generales: se responde con la información predeterminada del catálogo clínico de tratamientos y teléfono de recepción.
3. **Control de Longitud de Tokens:**
   - Limitar `max_tokens` a un máximo de 350 tokens por respuesta conversacional de redes sociales.
   - Enviar únicamente los últimos 4 turnos conversacionales en el contexto para preservar el presupuesto de tokens por minuto (TPM).

### Pilar 3: Tipado Fuerte en Python (Pydantic / MyPy) y Next.js (TypeScript Estricto)
Para prevenir errores en tiempo de ejecución en producción:
1. **Python (Backend):**
   - Todos los modelos de entrada y salida de FastAPI deben heredar de `pydantic.BaseModel` con tipos explícitos (`str`, `int`, `Optional[T]`, `List[T]`, `Dict[str, Any]`).
   - Prohibido el paso de diccionarios arbitrarios (`dict` sin tipar) en funciones críticas de cálculo de fechas de citas y turnos.
   - Código validado con `mypy` sin errores de resolución de tipos.
2. **Next.js (Frontend):**
   - Configuración de `tsconfig.json` con `"strict": true`.
   - Todas las entidades de API (`Appointment`, `Activity`, `ClinicSettings`) deben poseer su respectiva `interface` o `type` exportada.
   - Prohibido el uso de `any` en componentes de React, funciones de fetch o estados del simulador.

---

## 4. Métricas Medidas (Ratchets - No Permitir Degradación)

| Métrica | Valor Base Actual | Dirección Exigida |
|---|---|---|
| Cobertura de Tests Backend | 4 pruebas aprobadas (100% de suites) | No debe disminuir |
| Errores de Tipado TypeScript | 0 errores | Debe mantenerse en 0 |
| Errores de Tipado MyPy | 0 errores | Debe mantenerse en 0 |
| Tiempo de Compilación Next.js | < 3.0s | No superar los 10.0s |

---

## 5. Tabla de Excepciones Registradas

| ID | Regla Afectada | Ruta | Justificación Técnica | Responsable | Fecha Expiración |
|---|---|---|---|---|---|
| *Ninguna* | - | - | El proyecto opera bajo cumplimiento total del estándar base. | @ingenieria | 2026-12-31 |
