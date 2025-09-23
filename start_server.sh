#!/bin/bash
# Startup script for the Restream Server

# Check if SRS is installed
if [ ! -f "./srs/objs/srs" ]; then
    echo "Error: SRS not found. Please install SRS first."
    exit 1
fi

# Check if required directories exist
if [ ! -d "/srv/streams" ]; then
    echo "Creating /srv/streams directory..."
    sudo mkdir -p /srv/streams
    sudo chown $USER:$USER /srv/streams
fi

# Start SRS in the background
echo "Starting SRS..."
./srs/objs/srs -c srs.conf &

# Wait a moment for SRS to start
sleep 2

# Start Flask application
echo "Starting Flask application..."
python app.py

# When Flask stops, kill SRS
pkill srs
echo "Shutdown complete."