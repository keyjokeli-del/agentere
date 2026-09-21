Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Iniciando Sistema Multi-Agente Odontologico Omnicanal" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Start Python Backend
Write-Host "[1/3] Iniciando Backend Python (FastAPI en http://localhost:8000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\backend'; ..\venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

# 2. Start WhatsApp Baileys Service
Write-Host "[2/3] Iniciando Servicio WhatsApp Baileys (en http://localhost:3001)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\whatsapp-service'; node index.js"

# 3. Start Next.js Frontend
Write-Host "[3/3] Iniciando Panel de Control Next.js (en http://localhost:3000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; npm run dev"

Write-Host ""
Write-Host "¡Todos los servicios han sido lanzados!" -ForegroundColor Yellow
Write-Host "Abre tu navegador en: http://localhost:3000" -ForegroundColor Cyan
