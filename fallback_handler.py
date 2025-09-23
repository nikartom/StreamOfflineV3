#!/usr/bin/env python3
"""
Fallback Video Handler for Restream Server

This script handles the fallback video streaming when the main stream is disconnected.
It's designed to work with the Flask application and SRS server.
"""

import subprocess
import os
import signal
import sys
import time
from datetime import datetime

class FallbackHandler:
    def __init__(self, fallback_video_path="/srv/streams/fallback.mp4"):
        self.fallback_video_path = fallback_video_path
        self.process = None
        self.stream_key = None
        
    def start_fallback(self, stream_key):
        """Start streaming the fallback video"""
        if not os.path.exists(self.fallback_video_path):
            print(f"Error: Fallback video not found at {self.fallback_video_path}")
            return False
            
        if self.process and self.process.poll() is None:
            print("Fallback stream is already running")
            return False
            
        self.stream_key = stream_key
        
        # FFmpeg command to stream fallback video in loop
        cmd = [
            'ffmpeg',
            '-re',  # Read input at native frame rate
            '-stream_loop', '-1',  # Loop indefinitely
            '-i', self.fallback_video_path,
            '-c', 'copy',  # Copy streams without re-encoding
            '-f', 'flv',
            f'rtmp://127.0.0.1/live/{stream_key}_fallback'
        ]
        
        try:
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"Started fallback stream for {stream_key} with PID {self.process.pid}")
            return True
        except Exception as e:
            print(f"Error starting fallback stream: {e}")
            return False
    
    def stop_fallback(self):
        """Stop the fallback video streaming"""
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
                print("Stopped fallback stream")
            except subprocess.TimeoutExpired:
                self.process.kill()
                print("Force killed fallback stream")
            except Exception as e:
                print(f"Error stopping fallback stream: {e}")
        else:
            print("No fallback stream is running")
            
        self.process = None
        self.stream_key = None
    
    def is_running(self):
        """Check if fallback stream is currently running"""
        return self.process and self.process.poll() is None

def signal_handler(sig, frame):
    """Handle SIGINT (Ctrl+C) gracefully"""
    print("\nReceived interrupt signal. Stopping fallback stream...")
    fallback_handler.stop_fallback()
    sys.exit(0)

if __name__ == "__main__":
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialize fallback handler
    fallback_handler = FallbackHandler()
    
    # Example usage
    if len(sys.argv) > 1:
        stream_key = sys.argv[1]
        print(f"Starting fallback stream for {stream_key}")
        fallback_handler.start_fallback(stream_key)
        
        # Keep the script running
        try:
            while True:
                if fallback_handler.is_running():
                    print(f"Fallback stream for {fallback_handler.stream_key} is running...")
                else:
                    print("Fallback stream is not running")
                time.sleep(10)
        except KeyboardInterrupt:
            pass
        finally:
            fallback_handler.stop_fallback()
    else:
        print("Usage: python fallback_handler.py <stream_key>")
        print("This will start streaming the fallback video to rtmp://127.0.0.1/live/<stream_key>_fallback")