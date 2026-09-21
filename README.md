# 🦷 Sistema Multi-Agente Omnicanal para Clínica Dental (Costo $0)

Sistema integral de atención automatizada a pacientes y agendamiento de citas 24/7 en tiempo real para **WhatsApp (Baileys), Facebook Messenger, Instagram Direct y YouTube**, con registro directo en **Google Calendar**, motor de IA gratuito con **Groq (Llama 3.3)**, backend en **Python (FastAPI)** y panel de administración en **Next.js**.

---

## 🚀 Arquitectura y Tecnologías ($0 Cost)

- **Backend / Agentes (Python 3.14 + FastAPI):**
  - **Triage & Reception Agent:** Detecta intenciones (`BOOK_APPOINTMENT`, `INQUIRE_PRICE`, `EMERGENCY_PAIN`, etc.) y extrae entidades del paciente.
  - **Dental FAQ & Clinical Agent:** Explica tratamientos y precios orientativos con base en el catálogo clínico, con políticas éticas de derivación a consulta física.
  - **Appointment & Calendar Agent:** Consulta huecos libres en tiempo real y reserva citas en Google Calendar.
- **Canal WhatsApp (Node.js + Baileys):**
  - Conexión directa mediante sockets WebSocket de WhatsApp Web.
  - Generación de código QR para escanear directamente desde el dashboard de Next.js sin necesidad de API de pago de Meta/Twilio.
- **Canales Sociales (Meta Webhooks & YouTube API):**
  - **Facebook Messenger e Instagram:** Endpoints de webhooks listos para modo desarrollo gratuito de Meta for Developers.
  - **YouTube:** Procesador de comentarios para responder preguntas odontológicas en videos de la clínica mediante la cuota gratuita de Google Cloud.
- **Panel de Control (Next.js 15 + Tailwind CSS):**
  - Monitor de estado de los 4 canales en tiempo real.
  - Modal de escaneo de código QR para vincular WhatsApp.
  - Simulador interactivo omnicanal para probar la atención de pacientes en vivo.
  - Visualizador de citas agendadas en Google Calendar.

---

## 📁 Estructura del Proyecto

```text
agentere/
├── backend/                       # Núcleo de agentes y API en Python
│   ├── app/
│   │   ├── agents/
│   │   │   └── dental_agents.py   # Agentes Triage, FAQ y Citas
│   │   ├── services/
│   │   │   ├── groq_service.py    # Cliente Groq Cloud (Llama 3)
│   │   │   └── calendar_service.py# Integración con Google Calendar API
│   │   ├── data/
│   │   │   └── clinic_info.json   # Catálogo de tratamientos y precios
│   │   ├── config.py              # Configuración y variables de entorno
│   │   └── main.py                # Servidor FastAPI y webhooks
│   └── tests/
│       └── test_dental_agents.py  # Pruebas automatizadas con pytest
├── whatsapp-service/              # Microservicio de WhatsApp con Baileys
│   ├── index.js                   # Conector WebSocket y generador de QR
│   └── package.json
├── frontend/                      # Dashboard web interactivo en Next.js
│   ├── src/app/
│   │   ├── page.tsx               # Panel principal con simulador y QR
│   │   └── globals.css
│   └── package.json
├── docs/intent/
│   └── dental_clinic_agents.md    # Documento de intención confirmado
├── start-all.ps1                  # Lanzador automático en PowerShell
├── start-all.bat                  # Lanzador automático en CMD
└── .env.example                   # Plantilla de variables de entorno
```

---

## ⚡ Inicio Rápido (1 Clic)

### Opción A: Desde PowerShell (Recomendada)
```powershell
.\start-all.ps1
```

### Opción B: Desde CMD (Windows)
```cmd
start-all.bat
```

Esto levantará automáticamente en tres ventanas de terminal:
1. **Backend FastAPI:** [http://localhost:8000](http://localhost:8000) (Documentación OpenAPI en `/docs`)
2. **Servicio WhatsApp:** [http://localhost:3001](http://localhost:3001)
3. **Dashboard Next.js:** [http://localhost:3000](http://localhost:3000)

---

## 🔑 Configuración de Servicios Gratuitos ($0)

Copia `.env.example` a `.env` en la raíz o en `backend/.env`:

### 1. Groq Cloud (IA Gratuita)
1. Regístrate en [console.groq.com](https://console.groq.com).
2. Ve a **API Keys** y genera una clave gratuita.
3. Colócala en tu archivo `.env`:
   ```env
   GROQ_API_KEY=gsk_tu_clave_aqui
   ```
*(Nota: Si no colocas la clave de Groq, el sistema funciona en modo demostración con respuestas simuladas inteligentes).*

### 2. Google Calendar API (Citas Reales)
1. Accede a [Google Cloud Console](https://console.cloud.google.com).
2. Crea un proyecto gratuito y habilita la **Google Calendar API**.
3. En **Credenciales**, crea una *Cuenta de Servicio (Service Account)* y descarga la clave en formato JSON con el nombre `credentials.json` en la carpeta `backend/`.
4. En tu Google Calendar personal o de la clínica, ve a *Configuración > Compartir con personas específicas* y agrega el email de la cuenta de servicio con permisos de edición.
*(Nota: Si no configuras `credentials.json`, el sistema utiliza un calendario en memoria totalmente funcional para pruebas).*

### 3. Vincular WhatsApp con Baileys
1. Abre [http://localhost:3000](http://localhost:3000).
2. Haz clic en **"Escanear Código QR"** en la tarjeta de WhatsApp.
3. Abre WhatsApp en tu celular > **Dispositivos vinculados > Vincular dispositivo**.
4. Escanea el código QR que aparece en pantalla. ¡Listo! El agente comenzará a responder automáticamente los mensajes entrantes.

### 4. Persistencia en Neon Serverless Postgres (Para Evitar Desconexiones)
Por defecto, Baileys almacena la sesión en disco local (`auth_info_baileys/`). Para garantizar que la sesión **nunca se desconecte** ante reinicios o despliegues en la nube:
1. Crea una cuenta gratuita en [neon.tech](https://neon.tech) (Capa gratuita con PostgreSQL administrado).
2. Copia la cadena de conexión (*Connection String*).
3. Pégala en tu archivo `.env`:
   ```env
   NEON_DATABASE_URL=postgresql://usuario:password@ep-ejemplo.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
4. El servicio creará automáticamente la tabla `whatsapp_sessions` y mantendrá las llaves criptográficas y tokens respaldados en la nube.

---

## 🧪 Ejecutar Pruebas Automatizadas

Para validar el funcionamiento del equipo de agentes, cálculo de turnos y webhooks:

```powershell
$env:PYTHONPATH="backend"; .\venv\Scripts\pytest.exe backend/tests/test_dental_agents.py -v
```
