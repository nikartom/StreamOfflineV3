#!/bin/bash
# Setup script for the Restream Server

echo "Setting up Restream Server..."

# Create required directories
echo "Creating directories..."
mkdir -p data
sudo mkdir -p /srv/streams
sudo chown $USER:$USER /srv/streams

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "FFmpeg not found. Please install FFmpeg:"
    echo "Ubuntu/Debian: sudo apt install ffmpeg"
    echo "CentOS/RHEL: sudo yum install ffmpeg"
    echo "macOS: brew install ffmpeg"
else
    echo "FFmpeg is already installed."
fi

# Check if SRS is installed
if [ ! -f "./srs/objs/srs" ]; then
    echo "SRS not found. To install SRS, run:"
    echo "git clone https://github.com/ossrs/srs.git"
    echo "cd srs/trunk"
    echo "./configure && make"
else
    echo "SRS is already installed."
fi

echo "Setup complete! Run './start_server.sh' to start the server."