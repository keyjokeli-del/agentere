@echo off
title Lanzador de Servicios - Clinica Dental
echo ==========================================================
echo Iniciando Sistema Multi-Agente Odontologico Omnicanal
echo ==========================================================

echo [1/3] Iniciando Backend Python (FastAPI en http://localhost:8000)...
start "Backend Python FastAPI" cmd /k "cd /d %~dp0backend && ..\venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo [2/3] Iniciando Servicio WhatsApp Baileys (en http://localhost:3001)...
start "WhatsApp Baileys Service" cmd /k "cd /d %~dp0whatsapp-service && node index.js"

echo [3/3] Iniciando Panel de Control Next.js (en http://localhost:3000)...
start "Panel Web Next.js" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo Todos los servicios estan corriendo en sus terminales.
echo Abre tu navegador en: http://localhost:3000
pause
