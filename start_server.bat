@echo off
REM Startup script for the Restream Server on Windows

REM Check if SRS is installed
if not exist "srs\objs\srs.exe" (
    echo Error: SRS not found. Please install SRS first.
    exit /b 1
)

REM Check if required directories exist
if not exist "C:\srv\streams" (
    echo Creating C:\srv\streams directory...
    mkdir "C:\srv\streams"
)

REM Start SRS in the background
echo Starting SRS...
start /b srs\objs\srs.exe -c srs.conf

REM Wait a moment for SRS to start
timeout /t 2 /nobreak >nul

REM Start Flask application
echo Starting Flask application...
python app.py

echo Shutdown complete.