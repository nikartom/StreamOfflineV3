@echo off
REM Setup script for the Restream Server on Windows

echo Setting up Restream Server...

REM Create required directories
echo Creating directories...
mkdir data
if not exist "C:\srv\streams" (
    echo Creating C:\srv\streams directory...
    mkdir "C:\srv\streams"
)

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Check if FFmpeg is installed
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo FFmpeg not found. Please install FFmpeg:
    echo Download from https://ffmpeg.org/download.html
    echo Add FFmpeg to your PATH environment variable
) else (
    echo FFmpeg is already installed.
)

REM Check if SRS is installed
if not exist "srs\objs\srs.exe" (
    echo SRS not found. To install SRS:
    echo 1. Download from https://github.com/ossrs/srs
    echo 2. Compile following the instructions in the repository
) else (
    echo SRS is already installed.
)

echo Setup complete! Run 'start_server.bat' to start the server.