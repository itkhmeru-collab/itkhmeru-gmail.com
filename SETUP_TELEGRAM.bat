@echo off
setlocal
cd /d "%~dp0"
title PU NIN SECURITY - Telegram Setup
if not exist ".venv\Scripts\python.exe" (
  echo Python environment not found. Please run START_LOCAL.bat first.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" telegram_setup.py
pause
