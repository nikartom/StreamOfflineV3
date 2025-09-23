import subprocess
import os
import json
import time
from datetime import datetime

class FFmpegManager:
    def __init__(self):
        self.processes = {}  # Dictionary to store running processes
        self.FALLBACK_VIDEO = '/srv/streams/fallback.mp4'
        self.STREAM_STATUS_FILE = 'data/stream_status.json'
        
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        # Initialize status file if it doesn't exist
        if not os.path.exists(self.STREAM_STATUS_FILE):
            with open(self.STREAM_STATUS_FILE, 'w') as f:
                json.dump({
                    'active_stream': None,
                    'is_fallback_active': False,
                    'fallback_process': None
                }, f)
    
    def get_stream_status(self):
        """Get current stream status"""
        try:
            with open(self.STREAM_STATUS_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'active_stream': None,
                'is_fallback_active': False,
                'fallback_process': None
            }
    
    def update_stream_status(self, status):
        """Update stream status"""
        with open(self.STREAM_STATUS_FILE, 'w') as f:
            json.dump(status, f, indent=2)
    
    def start_forward_stream(self, stream_key, platform):
        """Start forwarding stream to a platform using FFmpeg"""
        # Construct output URL
        output_url = f"{platform['rtmp_url']}/{platform['stream_key']}"
        
        # Use FFmpeg to forward stream
        cmd = [
            'ffmpeg',
            '-i', f'rtmp://127.0.0.1/live/{stream_key}',
            '-c', 'copy',  # Copy streams without re-encoding
            '-f', 'flv',
            output_url
        ]
        
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process_key = f"{stream_key}_{platform['id']}"
            self.processes[process_key] = process
            print(f"Started forward stream to {platform['name']} with PID {process.pid}")
            return process.pid
        except Exception as e:
            print(f"Error starting forward stream to {platform['name']}: {e}")
            return None
    
    def stop_forward_stream(self, stream_key, platform_id):
        """Stop forwarding stream to a specific platform"""
        process_key = f"{stream_key}_{platform_id}"
        if process_key in self.processes:
            process = self.processes[process_key]
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception as e:
                print(f"Error stopping forward stream {process_key}: {e}")
            finally:
                self.processes.pop(process_key, None)
                print(f"Stopped forward stream {process_key}")
    
    def stop_all_forward_streams(self, stream_key):
        """Stop all forward streams for a given stream key"""
        for key, process in list(self.processes.items()):
            if key.startswith(f"{stream_key}_"):
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                except Exception as e:
                    print(f"Error stopping forward stream {key}: {e}")
                finally:
                    self.processes.pop(key, None)
        
        print(f"Stopped all forward streams for {stream_key}")
    
    def start_fallback_stream(self, stream_key):
        """Start fallback video streaming"""
        if not os.path.exists(self.FALLBACK_VIDEO):
            print(f"Warning: Fallback video {self.FALLBACK_VIDEO} not found")
            return False
        
        # Stop any existing fallback stream
        self.stop_fallback_stream()
        
        # Start FFmpeg to stream fallback video in loop
        cmd = [
            'ffmpeg',
            '-re',  # Read input at native frame rate
            '-stream_loop', '-1',  # Loop indefinitely
            '-i', self.FALLBACK_VIDEO,
            '-c', 'copy',  # Copy streams without re-encoding
            '-f', 'flv',
            f'rtmp://127.0.0.1/live/{stream_key}_fallback'
        ]
        
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes[f"fallback_{stream_key}"] = process
            
            # Update status
            status = self.get_stream_status()
            status['is_fallback_active'] = True
            status['fallback_process'] = {
                'pid': process.pid,
                'started_at': datetime.now().isoformat()
            }
            self.update_stream_status(status)
            
            print(f"Started fallback stream for {stream_key} with PID {process.pid}")
            return True
        except Exception as e:
            print(f"Error starting fallback stream: {e}")
            return False
    
    def stop_fallback_stream(self):
        """Stop fallback video streaming"""
        # Update status first
        status = self.get_stream_status()
        status['is_fallback_active'] = False
        status['fallback_process'] = None
        self.update_stream_status(status)
        
        # Kill all fallback processes
        for key, process in list(self.processes.items()):
            if key.startswith("fallback_"):
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                except Exception as e:
                    print(f"Error stopping fallback stream {key}: {e}")
                finally:
                    self.processes.pop(key, None)
        
        print("Stopped fallback streams")

# Create a global instance
ffmpeg_manager = FFmpegManager()