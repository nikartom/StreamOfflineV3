# Restream Server with SRS and Flask

This project implements a restream server that receives RTMP streams from OBS and forwards them to multiple platforms like Twitch, YouTube, etc. It also provides a fallback mechanism that plays a predefined video when the stream is disconnected.

## Features

- Receives RTMP streams from OBS
- Automatically forwards streams to multiple platforms
- Plays fallback video when stream is disconnected
- Web interface for managing platforms and uploading fallback video
- Automatic start/stop of streams based on OBS connection status

## Prerequisites

- Python 3.7+
- SRS (Simple Realtime Server)
- FFmpeg
- Flask

## Installation

1. Install SRS by following the official documentation: https://github.com/ossrs/srs

2. Install FFmpeg:
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install ffmpeg
   
   # CentOS/RHEL
   sudo yum install ffmpeg
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create the required directories:
   ```bash
   sudo mkdir -p /srv/streams
   sudo chown $USER:$USER /srv/streams
   ```

## Configuration

1. Configure SRS by editing `srs.conf`:
   - Set up the HTTP hooks to point to your Flask server
   - Configure the RTMP listening port (default: 1935)

2. Update the Flask application settings in `app.py` if needed:
   - PLATFORMS_FILE: Path to store platform configurations
   - FALLBACK_VIDEO: Path to the fallback video file

## Usage

1. Start SRS:
   ```bash
   ./objs/srs -c srs.conf
   ```

2. Start the Flask application:
   ```bash
   python app.py
   ```

3. Access the web interface at `http://localhost:5000`

4. Configure your streaming platforms and upload a fallback video

5. Configure OBS with the following settings:
   - Server: `rtmp://your-server-ip/live`
   - Stream Key: anything-you-want

## How It Works

1. When OBS starts streaming to `rtmp://server/live/STREAM_KEY`, SRS receives the stream
2. SRS calls the `/api/on_publish` endpoint on the Flask server
3. Flask starts forwarding the stream to all enabled platforms using FFmpeg
4. When OBS stops streaming, SRS calls the `/api/on_unpublish` endpoint
5. Flask stops all forwarding processes and starts streaming the fallback video
6. When OBS reconnects, the fallback stream stops and normal forwarding resumes

## API Endpoints

- `GET /` - Web interface
- `GET /api/platforms` - Get all configured platforms
- `POST /api/platforms` - Add a new platform
- `PUT /api/platforms/<id>` - Update a platform
- `DELETE /api/platforms/<id>` - Delete a platform
- `POST /api/upload_fallback` - Upload fallback video
- `POST /api/on_publish` - SRS hook when stream starts
- `POST /api/on_unpublish` - SRS hook when stream stops

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License.