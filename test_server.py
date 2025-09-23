#!/usr/bin/env python3
"""
Test script for the Restream Server
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_api_endpoints():
    """Test all API endpoints"""
    print("Testing API endpoints...")
    
    # Test getting platforms (should be empty initially)
    response = requests.get(f"{BASE_URL}/api/platforms")
    print(f"GET /api/platforms: {response.status_code}")
    
    # Test adding a platform
    platform_data = {
        "name": "Test Platform",
        "rtmp_url": "rtmp://test.example.com/app",
        "stream_key": "testkey123",
        "enabled": True
    }
    
    response = requests.post(f"{BASE_URL}/api/platforms", json=platform_data)
    print(f"POST /api/platforms: {response.status_code}")
    
    # Test getting platforms again
    response = requests.get(f"{BASE_URL}/api/platforms")
    print(f"GET /api/platforms: {response.status_code}")
    platforms = response.json()
    print(f"Platforms: {len(platforms)}")
    
    if platforms:
        platform_id = platforms[0]['id']
        
        # Test updating a platform
        update_data = {
            "enabled": False
        }
        
        response = requests.put(f"{BASE_URL}/api/platforms/{platform_id}", json=update_data)
        print(f"PUT /api/platforms/{platform_id}: {response.status_code}")
        
        # Test deleting a platform
        response = requests.delete(f"{BASE_URL}/api/platforms/{platform_id}")
        print(f"DELETE /api/platforms/{platform_id}: {response.status_code}")
    
    # Test status endpoint
    response = requests.get(f"{BASE_URL}/api/status")
    print(f"GET /api/status: {response.status_code}")

if __name__ == "__main__":
    test_api_endpoints()