@echo off
chcp 65001 >nul 2>&1
echo ===================================================
echo    Z.ai Chat Client for Windows 7
echo ===================================================
echo.
echo    Opening browser...
echo.

start "" "http://localhost:8080"

python\python.exe zai_local_chat.py

pause
