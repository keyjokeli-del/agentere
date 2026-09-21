# 🦷 Lumina Dental Studio — Ecosistema Multi-Agente Omnicanal ($0 USD)

[![Next.js](https://img.shields.io/badge/Next.js-15.5-black?style=flat&logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Baileys](https://img.shields.io/badge/Baileys-WhatsApp_Web-25D366?style=flat&logo=whatsapp)](https://github.com/WhiskeySockets/Baileys)
[![Groq](https://img.shields.io/badge/Groq-Llama_3.3_70B-f55036?style=flat)](https://groq.com/)
[![Neon](https://img.shields.io/badge/Neon-Serverless_Postgres-00E5FF?style=flat&logo=postgresql)](https://neon.tech/)
[![Render](https://img.shields.io/badge/Render-Free_Tier-46E3B7?style=flat&logo=render)](https://render.com/)
[![Vercel](https://img.shields.io/badge/Vercel-Production-black?style=flat&logo=vercel)](https://vercel.com/)
[![License](https://img.shields.io/badge/Costo-0_USD_Mensual-emerald)](https://github.com/keyjokeli-del/agentere)

> 🚀 **Despliegue en Vivo en Producción ($0 USD):**
> - **Sitio Web & Landing Page (Vercel):** [https://lumina-dental-nairoby-dominguez.vercel.app](https://lumina-dental-nairoby-dominguez.vercel.app)
> - **Portal Clínico & Dashboard (Vercel):** [https://lumina-dental-nairoby-dominguez.vercel.app/dashboard](https://lumina-dental-nairoby-dominguez.vercel.app/dashboard)
> - **API Backend & Swagger (Render):** [https://lumina-backend-rti9.onrender.com/docs](https://lumina-backend-rti9.onrender.com/docs)
> - **Servicio de WhatsApp Baileys (Render):** [https://lumina-whatsapp.onrender.com](https://lumina-whatsapp.onrender.com)

Sistema integral de atención automatizada a pacientes y reserva inteligente de citas odontológicas 24/7 en tiempo real. Soporta **WhatsApp (Baileys sin costo de API)**, **Facebook Messenger**, **Instagram Direct** y **YouTube**, integrado directamente con **Google Calendar** para prevención estricta de solapamientos (turnos dedicados de 45 minutos), con persistencia criptográfica en **Neon Serverless Postgres** y un panel de administración y Landing Page clínica de alta conversión construidos en **Next.js 15**.

---

## 🏛️ Arquitectura de Producción a Costo $0

```mermaid
flowchart TD
    subgraph Canales ["📱 Canales de Entrada"]
        WA["WhatsApp (Paciente)"]
        IG["Instagram Direct"]
        FB["Facebook Messenger"]
        YT["YouTube Comments"]
        LP["Landing Page Web (Next.js)"]
    end

    subgraph Vercel ["⚡ Vercel Edge Network (Free)"]
        Front["Lumina Frontend (Next.js 15)\n- Landing Page con Glassmorphism\n- Monitor Omnicanal & Modal QR\n- Agendador de Citas Interactivo"]
    end

    subgraph Render ["☁️ Render Cloud Platform (Free Tier 512MB RAM)"]
        subgraph S1 ["Microservicio WhatsApp (Docker / Node.js 20)"]
            Bai["Baileys Socket Engine\n- Multi-File Auth Adapter\n- Backoff Exponencial\n- Max Heap: 256MB"]
        end
        subgraph S2 ["Backend Core (Docker / Python 3.11)"]
            Fast["FastAPI Engine (Uvicorn)\n- TriageAgent (Priorización)\n- DentalFAQAgent (Catálogo)\n- AppointmentAgent (Citas)\n- Single Worker / Low RAM"]
        end
    end

    subgraph CloudServices ["🌐 Servicios en la Nube ($0 USD Tier)"]
        Groq["Groq Cloud API\nLlama 3.3 70B Versatile\n< 1s latencia de inferencia"]
        GCal["Google Calendar API v3\nService Account\nBloqueo Anti-Colisión"]
        Neon["Neon Serverless Postgres\nTabla whatsapp_sessions\nPersistencia Signal keys"]
        Uptime["UptimeRobot (Free Ping)\nKeep-Alive cada 14 min\nCero Sleep"]
    end

    WA <-->|WebSockets| Bai
    Bai <-->|Persistencia Tokens| Neon
    Bai <-->|Webhook HTTP| Fast
    LP <--> Front
    IG & FB & YT -->|REST Webhooks| Fast
    Front -->|REST API| Fast
    Front -->|Status & QR| Bai
    Fast <-->|Inferencia IA| Groq
    Fast <-->|Reserva & Disponibilidad| GCal
    Uptime -.->|HTTP GET Ping| Fast
    Uptime -.->|HTTP GET Ping| Bai
```

---

## 📁 Estructura del Repositorio

```text
agentere/
├── .github/workflows/
│   └── ci.yml                     # Pipeline de CI/CD (Pytest, MyPy, Tests Node.js, Build Next.js)
├── backend/                       # Núcleo de agentes y API REST en Python
│   ├── app/
│   │   ├── agents/
│   │   │   └── dental_agents.py   # Coordinador, TriageAgent, FAQAgent y AppointmentAgent
│   │   ├── services/
│   │   │   ├── groq_service.py    # Cliente Groq Cloud con fallback por rate-limit
│   │   │   └── calendar_service.py# Google Calendar API con soporte GOOGLE_CREDENTIALS_JSON
│   │   ├── data/
│   │   │   └── clinic_info.json   # Catálogo clínico de tratamientos y precios
│   │   ├── config.py              # Validación de configuración y entornos
│   │   └── main.py                # Servidor FastAPI, endpoints REST y webhooks
│   ├── tests/                     # Suite de pruebas unitarias y colisiones (12 tests)
│   ├── Dockerfile                 # Multi-stage ultra-liviano (Python 3.11-slim, < 150MB RAM)
│   ├── .dockerignore
│   └── requirements.txt           # Dependencias de producción fijadas
├── whatsapp-service/              # Microservicio de WhatsApp con Baileys
│   ├── index.js                   # WebSocket de WhatsApp, generador de QR y reenvío
│   ├── neonAuthState.js           # Adaptador de persistencia Signal en Neon Postgres
│   ├── test_neon_auth.js          # Pruebas de serialización criptográfica (Node.js test runner)
│   ├── Dockerfile                 # Multi-stage Alpine (Node.js 20, límite de heap 256MB)
│   ├── .dockerignore
│   └── package.json
├── frontend/                      # Landing Page y Panel de Control en Next.js 15
│   ├── src/app/
│   │   ├── page.tsx               # Landing Page de Lumina Dental Studio
│   │   ├── dashboard/             # Panel del consultorio (Monitor, QR, Simulador, Turnos)
│   │   └── globals.css            # Utilidades Glassmorphism y aceleración por GPU
│   ├── src/components/landing/    # Componentes de Landing (Hero, Features, BookingCTA, etc.)
│   ├── vercel.json                # Configuración de cabeceras de seguridad y caché
│   └── package.json
├── render.yaml                    # Infraestructura como Código (Blueprint) para Render
├── vercel.json                    # Configuración de despliegue raíz en Vercel
├── docker-compose.yml             # Orquestador multi-contenedor para entorno local
├── pytest.ini                     # Configuración de Pytest con PYTHONPATH automático
├── start-all.ps1                  # Lanzador local 1-clic para PowerShell
├── start-all.bat                  # Lanzador local 1-clic para CMD
└── .env.example                   # Plantilla de variables de entorno
```

---

## 🚀 Despliegue a Producción Paso a Paso ($0 USD)

### Paso 1: Base de Datos Neon Postgres (Persistencia de WhatsApp)
1. Crea una cuenta gratuita en [Neon.tech](https://neon.tech).
2. Crea un proyecto (ej. `lumina-dental`).
3. En el **Dashboard de Neon**, copia la cadena de conexión (`Connection String`):
   ```text
   postgresql://neondb_owner:password@ep-cool-fog-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
4. Guarda esta URL; la usarás como `DATABASE_URL` en Render. *(El microservicio crea la tabla `whatsapp_sessions` de manera automática en el primer inicio).*

### Paso 2: IA en Groq Cloud (Capa Gratuita)
1. Regístrate en [console.groq.com](https://console.groq.com).
2. Ve a **API Keys** y crea una nueva clave gratuita.
3. Guarda tu `GROQ_API_KEY` (comienza con `gsk_...`).

### Paso 3: Google Calendar API (Agenda Médica en Tiempo Real)
1. Ingresa en [Google Cloud Console](https://console.cloud.google.com).
2. Crea un proyecto y habilita la **Google Calendar API**.
3. Ve a **IAM y administración > Cuentas de servicio**, crea una cuenta (ej. `lumina-bot@...`) y genera una clave privada en formato **JSON**.
4. Abre tu Google Calendar personal o de la clínica, ve a **Configuración > Compartir con personas específicas** y añade el correo de la cuenta de servicio con permisos para *"Realizar cambios en eventos"*.
5. Copia el contenido del archivo JSON descargado en una sola línea (o en bloque) para usarlo como variable de entorno `GOOGLE_CREDENTIALS_JSON`.

### Paso 4: Despliegue de Backend y WhatsApp en Render con `render.yaml`
1. Sube tu código a tu repositorio de GitHub: `https://github.com/keyjokeli-del/agentere`.
2. Ingresa a [dashboard.render.com](https://dashboard.render.com) y haz clic en **New + > Blueprint**.
3. Selecciona tu repositorio `agentere`. Render detectará automáticamente el archivo [`render.yaml`](file:///c:/Users/herct/Desktop/agentere/render.yaml).
4. El Blueprint creará dos servicios web Docker gratuitos:
   - `lumina-backend`: Servidor FastAPI en el puerto 8000.
   - `lumina-whatsapp`: Microservicio Baileys en el puerto 3001.
5. Completa las variables de entorno marcadas con `sync: false`:
   - `GROQ_API_KEY`: Tu clave de Groq.
   - `GOOGLE_CREDENTIALS_JSON`: El JSON completo de tu Service Account de Google.
   - `DATABASE_URL`: Tu connection string de Neon Postgres.
6. Haz clic en **Apply**. En 3-5 minutos ambos servicios estarán compilados y activos con SSL gratuito:
   - Backend: `https://lumina-backend.onrender.com`
   - WhatsApp: `https://lumina-whatsapp.onrender.com`

### Paso 5: Despliegue del Frontend en Vercel
1. Ingresa a [Vercel.com](https://vercel.com) y haz clic en **Add New > Project**.
2. Conecta tu repositorio de GitHub `agentere`.
3. Vercel detectará la configuración de [`vercel.json`](file:///c:/Users/herct/Desktop/agentere/vercel.json).
4. En **Environment Variables**, añade las URLs públicas obtenidas en Render:
   - `NEXT_PUBLIC_BACKEND_URL`: `https://lumina-backend.onrender.com`
   - `NEXT_PUBLIC_WHATSAPP_URL`: `https://lumina-whatsapp.onrender.com`
5. Haz clic en **Deploy**. Tu Landing Page y Panel estarán publicados en `https://lumina-dental.vercel.app`.

### Paso 6: Mantener los Contenedores Activos 24/7 (Cero Sleep)
Los servicios web en el plan gratuito de Render se suspenden tras 15 minutos sin tráfico entrante. Para mantenerlos despiertos 24/7 sin pagar un solo centavo:
1. Crea una cuenta gratuita en [UptimeRobot.com](https://uptimerobot.com).
2. Añade 2 monitores tipo **HTTP(s)** con intervalo de **14 minutos**:
   - Monitor 1: `https://lumina-backend.onrender.com/`
   - Monitor 2: `https://lumina-whatsapp.onrender.com/api/status`
3. Esto garantizará que ambos servicios permanezcan calientes y respondan a los mensajes de WhatsApp en menos de 2 segundos.

---

## 🔐 Matriz de Variables de Entorno en Producción

| Variable | Servicio | Descripción | Ejemplo / Valor |
|---|:---:|---|---|
| `GROQ_API_KEY` | Backend | Clave de autenticación para Groq Cloud | `gsk_AbCdEf123456...` |
| `GROQ_MODEL` | Backend | Modelo de lenguaje Llama 3 optimizado | `llama-3.3-70b-versatile` |
| `GOOGLE_CALENDAR_ID` | Backend | ID del calendario de Google | `primary` o `clinica@gmail.com` |
| `GOOGLE_CREDENTIALS_JSON` | Backend | Contenido JSON de la cuenta de servicio de Google | `{"type":"service_account",...}` |
| `DATABASE_URL` | WhatsApp | Conexión SSL a Neon Postgres para llaves Signal | `postgresql://user:pass@ep-cool.neon.tech/neondb?sslmode=require` |
| `WA_SESSION_ID` | WhatsApp | Identificador único de la sesión en base de datos | `lumina_dental_session` |
| `PYTHON_BACKEND_URL` | WhatsApp | Webhook de FastAPI para procesar mensajes | `https://lumina-backend.onrender.com/api/webhooks/whatsapp` |
| `NODE_OPTIONS` | WhatsApp | Límite estricto de memoria heap para evitar OOM | `--max-old-space-size=256` |
| `NEXT_PUBLIC_BACKEND_URL` | Frontend | URL pública del backend para el navegador | `https://lumina-backend.onrender.com` |
| `NEXT_PUBLIC_WHATSAPP_URL` | Frontend | URL pública del servicio de WhatsApp | `https://lumina-whatsapp.onrender.com` |

---

## 💻 Inicio en Entorno Local

### Opción 1: Con Scripts de Inicio 1-Clic
```powershell
# En PowerShell:
.\start-all.ps1

# O en CMD (Windows):
start-all.bat
```

### Opción 2: Con Docker Compose
```bash
docker compose up --build
```

Servicios locales activos:
- **Landing Page & Panel Next.js:** [http://localhost:3000](http://localhost:3000)
- **FastAPI Backend:** [http://localhost:8000](http://localhost:8000) (Swagger en `/docs`)
- **Microservicio WhatsApp Baileys:** [http://localhost:3001](http://localhost:3001)

---

## 🧪 Validación y Pruebas Automatizadas

El proyecto incluye suites completas de pruebas automatizadas:

```bash
# 1. Pruebas de Triage, FAQ y Prevención de Colisiones de Agenda (Pytest):
pytest

# 2. Análisis Estático de Tipos en Python (MyPy):
mypy --ignore-missing-imports backend/app

# 3. Pruebas del Adaptador Criptográfico de Neon Postgres:
node --test whatsapp-service/test_neon_auth.js

# 4. Verificación Estricta de Tipos en Frontend (TypeScript):
npm --prefix frontend run typecheck

# 5. Compilación de Producción de Next.js:
npm --prefix frontend run build
```

---

## 📱 Vinculación de WhatsApp del Consultorio

1. Ingresa a la sección `/dashboard` de la aplicación web.
2. Abre el modal **"Escanear Código QR"** en la tarjeta de estado de WhatsApp.
3. En el teléfono móvil del consultorio, abre WhatsApp > **Dispositivos vinculados > Vincular un dispositivo**.
4. Escanea el código QR que se actualiza dinámicamente en pantalla.
5. El sistema confirmará la conexión y guardará los tokens criptográficos en **Neon Postgres**, permitiendo que los agentes respondan y agenden turnos automáticamente las 24 horas del día.
