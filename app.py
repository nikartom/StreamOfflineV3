from flask import Flask, request, jsonify, render_template, redirect, url_for
import json
import os
from datetime import datetime
from ffmpeg_manager import ffmpeg_manager

app = Flask(__name__)

# Configuration
PLATFORMS_FILE = 'data/platforms.json'
FALLBACK_VIDEO = '/srv/streams/fallback.mp4'

# Ensure data directories exist
os.makedirs('data', exist_ok=True)
os.makedirs('/srv/streams', exist_ok=True)

# Initialize data files if they don't exist
if not os.path.exists(PLATFORMS_FILE):
    with open(PLATFORMS_FILE, 'w') as f:
        json.dump([], f)

def load_platforms():
    """Load platforms from JSON file"""
    try:
        with open(PLATFORMS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_platforms(platforms):
    """Save platforms to JSON file"""
    with open(PLATFORMS_FILE, 'w') as f:
        json.dump(platforms, f, indent=2)

@app.route('/')
def index():
    """Main dashboard page"""
    platforms = load_platforms()
    status = ffmpeg_manager.get_stream_status()
    fallback_exists = os.path.exists(FALLBACK_VIDEO)
    return render_template('index.html', platforms=platforms, status=status, fallback_exists=fallback_exists)

@app.route('/api/platforms', methods=['GET'])
def get_platforms():
    """Get all platforms"""
    platforms = load_platforms()
    return jsonify(platforms)

@app.route('/api/platforms', methods=['POST'])
def add_platform():
    """Add a new platform"""
    data = request.get_json()
    platforms = load_platforms()
    
    # Add new platform
    platform = {
        'id': len(platforms) + 1,
        'name': data.get('name'),
        'rtmp_url': data.get('rtmp_url'),
        'stream_key': data.get('stream_key'),
        'enabled': data.get('enabled', True)
    }
    platforms.append(platform)
    
    save_platforms(platforms)
    return jsonify(platform), 201

@app.route('/api/platforms/<int:platform_id>', methods=['PUT'])
def update_platform(platform_id):
    """Update a platform"""
    data = request.get_json()
    platforms = load_platforms()
    
    # Find and update platform
    for platform in platforms:
        if platform['id'] == platform_id:
            platform.update({
                'name': data.get('name', platform['name']),
                'rtmp_url': data.get('rtmp_url', platform['rtmp_url']),
                'stream_key': data.get('stream_key', platform['stream_key']),
                'enabled': data.get('enabled', platform['enabled'])
            })
            break
    
    save_platforms(platforms)
    return jsonify(platform)

@app.route('/api/platforms/<int:platform_id>', methods=['DELETE'])
def delete_platform(platform_id):
    """Delete a platform"""
    platforms = load_platforms()
    platforms = [p for p in platforms if p['id'] != platform_id]
    save_platforms(platforms)
    return '', 204

@app.route('/api/on_publish', methods=['POST'])
def on_publish():
    """SRS hook when stream starts"""
    data = request.get_json() or request.form.to_dict()
    stream_key = data.get('name')  # Stream key from RTMP URL
    
    print(f"Stream started: {stream_key}")
    
    # Stop any fallback streams for this key
    ffmpeg_manager.stop_fallback_stream()
    
    # Update stream status
    status = ffmpeg_manager.get_stream_status()
    status['active_stream'] = stream_key
    status['is_fallback_active'] = False
    ffmpeg_manager.update_stream_status(status)
    
    # Start forwarding to platforms
    platforms = load_platforms()
    for platform in platforms:
        if platform['enabled']:
            ffmpeg_manager.start_forward_stream(stream_key, platform)
    
    return jsonify({'status': 'ok'})

@app.route('/api/on_unpublish', methods=['POST'])
def on_unpublish():
    """SRS hook when stream stops"""
    data = request.get_json() or request.form.to_dict()
    stream_key = data.get('name')  # Stream key from RTMP URL
    
    print(f"Stream stopped: {stream_key}")
    
    # Update stream status
    status = ffmpeg_manager.get_stream_status()
    if status['active_stream'] == stream_key:
        status['active_stream'] = None
        ffmpeg_manager.update_stream_status(status)
        
        # Start fallback stream
        ffmpeg_manager.start_fallback_stream(stream_key)
    
    # Stop forwarding to platforms
    ffmpeg_manager.stop_all_forward_streams(stream_key)
    
    return jsonify({'status': 'ok'})

@app.route('/api/upload_fallback', methods=['POST'])
def upload_fallback():
    """Upload fallback video"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        file.save(FALLBACK_VIDEO)
        return jsonify({'status': 'ok', 'message': 'Fallback video uploaded successfully'})
    except Exception as e:
        return jsonify({'error': f'Failed to save file: {str(e)}'}), 500

@app.route('/api/status', methods=['GET'])
def api_status():
    """Get current status"""
    status = ffmpeg_manager.get_stream_status()
    platforms = load_platforms()
    fallback_exists = os.path.exists(FALLBACK_VIDEO)
    
    return jsonify({
        'stream_status': status,
        'platforms': platforms,
        'fallback_exists': fallback_exists
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)