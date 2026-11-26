@echo off
REM Gera o executavel do backend (Windows) em frontend\backend-bin\vortex-backend.exe
cd /d "%~dp0..\backend"
if not exist venv python -m venv venv
venv\Scripts\pip install -r requirements.txt
venv\Scripts\pyinstaller --noconfirm --onefile --name vortex-backend --distpath "%~dp0..\frontend\backend-bin" app.py
echo OK: frontend\backend-bin\vortex-backend.exe
