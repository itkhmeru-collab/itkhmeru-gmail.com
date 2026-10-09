@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title PU NIN WEB ADMIN - Auto Setup
set "PYEXE="
set "INSTALLER=%TEMP%\python-3.12.10-amd64.exe"

rem First try an existing Python 3.12 or 3.11 through the Python Launcher.
where py >nul 2>nul
if not errorlevel 1 (
  py -3.12 -c "import sys; assert sys.maxsize > 2**32" >nul 2>nul
  if not errorlevel 1 set "PYEXE=py -3.12"
  if not defined PYEXE (
    py -3.11 -c "import sys; assert sys.maxsize > 2**32" >nul 2>nul
    if not errorlevel 1 set "PYEXE=py -3.11"
  )
)

rem If no supported Python is available, download and install official Python 3.12.10 x64.
if not defined PYEXE (
  echo [1/4] Python 3.11/3.12 x64 was not found.
  echo Downloading official Python 3.12.10 x64 installer...
  powershell -NoProfile -ExecutionPolicy Bypass -Command "$ProgressPreference='SilentlyContinue'; Invoke-WebRequest -UseBasicParsing -Uri 'https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe' -OutFile '%INSTALLER%'"
  if errorlevel 1 goto download_failed
  if not exist "%INSTALLER%" goto download_failed
  echo Installing Python for the current Windows user. Please wait...
  start /wait "Python Setup" "%INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_launcher=1 Include_test=0
  if errorlevel 1 goto install_failed
  del "%INSTALLER%" >nul 2>nul
  rem Use the installed executable directly; no reboot is needed.
  if exist "%LocalAppData%\Programs\Python\Python312\python.exe" set "PYEXE=%LocalAppData%\Programs\Python\Python312\python.exe"
  if not defined PYEXE (
    where py >nul 2>nul
    if not errorlevel 1 (
      py -3.12 --version >nul 2>nul
      if not errorlevel 1 set "PYEXE=py -3.12"
    )
  )
  if not defined PYEXE goto install_failed
)

echo Using Python:
%PYEXE% --version
if errorlevel 1 goto install_failed
if not exist ".venv\Scripts\python.exe" (
  echo [2/4] Creating virtual environment...
  %PYEXE% -m venv .venv
  if errorlevel 1 goto failed
)
echo [3/4] Installing required packages...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
if not exist ".env" (
  copy ".env.example" ".env" >nul
  echo.
  echo [ACTION REQUIRED] Created .env from .env.example.
  echo Fill in FIREBASE_API_KEY and FLASK_SECRET_KEY. Telegram values are optional.
  notepad .env
  echo Save .env, close Notepad, then run START_LOCAL.bat again.
  pause
  exit /b 0
)
echo [4/4] Starting PU NIN Web Admin...
echo Open http://127.0.0.1:5000 in your browser. Keep this window open.
start "" http://127.0.0.1:5000
".venv\Scripts\python.exe" app.py
pause
exit /b 0

:download_failed
echo.
echo [ERROR] Python download failed. Check your Internet connection or download from:
echo https://www.python.org/downloads/release/python-31210/
pause
exit /b 1

:install_failed
echo.
echo [ERROR] Python installation/check failed. Run this file again or install Python 3.11/3.12 x64 from python.org.
pause
exit /b 1

:failed
echo.
echo [ERROR] Setup failed. Check the error above and confirm Internet access.
pause
exit /b 1
