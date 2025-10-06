@echo off
cd /d "d:\Projects\LC management"
call venv\Scripts\activate.bat
echo.
echo ========================================
echo   LC Management API - LAN Server
echo ========================================
echo.
echo Starting server for LAN access...
echo Your friend can connect to: http://10.65.148.34:8001
echo API Documentation: http://10.65.148.34:8001/docs
echo.
python start_lan_server.py
pause
