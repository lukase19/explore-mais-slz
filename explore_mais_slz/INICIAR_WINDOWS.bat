@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
 echo Criando ambiente virtual...
 py -m venv .venv
)
call .venv\Scripts\activate.bat
python -m pip install -r requirements.txt
if errorlevel 1 (
 echo Falha ao instalar dependencias. Verifique sua internet.
 pause
 exit /b 1
)
echo Abra http://127.0.0.1:5000
python -m backend.app
pause
