# Restream Server Architecture

```mermaid
graph TD
    A[OBS Studio] -->|RTMP Stream| B(SRS Server)
    B -->|on_publish Hook| C[Flask App]
    B -->|on_unpublish Hook| C
    C -->|Manage FFmpeg| D[FFmpeg Processes]
    C -->|Store Config| E[(JSON Files)]
    C -->|Serve Web UI| F[Web Browser]
    D -->|Forward Streams| G[Twitch]
    D -->|Forward Streams| H[YouTube]
    D -->|Forward Streams| I[Other Platforms]
    D -->|Fallback Stream| B
    J[Fallback Video] --> D

    style A fill:#ffe4b5,stroke:#333
    style B fill:#87ceeb,stroke:#333
    style C fill:#98fb98,stroke:#333
    style D fill:#ffa07a,stroke:#333
    style E fill:#d8bfd8,stroke:#333
    style F fill:#ffe4e1,stroke:#333
    style G fill:#9370db,stroke:#333
    style H fill:#9370db,stroke:#333
    style I fill:#9370db,stroke:#333
    style J fill:#ffffe0,stroke:#333

    classDef component fill:#fff,stroke:#333,stroke-width:2px;
    class A,B,C,D,E,F,G,H,I,J component;
```

## Component Descriptions

### OBS Studio
- Publishes RTMP stream to SRS server
- Uses URL: `rtmp://server/live/STREAM_KEY`

### SRS Server
- Receives RTMP streams
- Calls HTTP hooks on stream events:
  - `on_publish`: When stream starts
  - `on_unpublish`: When stream stops
- Forwards streams to FFmpeg processes for distribution
- Receives fallback streams from FFmpeg

### Flask Application
- Handles HTTP hooks from SRS
- Manages streaming platform configurations
- Controls FFmpeg processes
- Provides web interface for management
- Stores platform configurations in JSON files

### FFmpeg Processes
- Forward incoming streams to platforms (Twitch, YouTube, etc.)
- Stream without re-encoding (copy codec)
- Play fallback video when main stream stops
- Managed by Flask application

### JSON Files
- Store platform configurations
- Store stream status information

### Web Browser
- Accesses Flask web interface
- Manages platforms and uploads fallback video

### Streaming Platforms
- Receive forwarded streams from FFmpeg processes
- Include Twitch, YouTube, Trovo, etc.

### Fallback Video
- MP4 video played when main stream is disconnected
- Configured through web interface