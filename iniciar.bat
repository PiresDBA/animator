@echo off
setlocal
cd /d "%~dp0"
title Estudio de Animacao Local - M2
echo ============================================================
echo  ESTUDIO DE ANIMACAO LOCAL - M2 (Bonecos de Palito)
echo ============================================================
echo.
echo  Iniciando o servidor FastAPI e a interface gráfica...
echo  Acesse: http://127.0.0.1:8765
echo.
start "" http://127.0.0.1:8765
.\.venv\Scripts\python.exe -m uvicorn app:app --app-dir backend --host 127.0.0.1 --port 8765
pause
