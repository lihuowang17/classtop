"""HTTP API server for remote control."""
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import time
import config


app = FastAPI(title="Camera Monitor API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
camera_detector = None
encoder_detector = None
active_streamers = {}


def initialize(cam_detector, enc_detector):
    """Initialize API with detectors."""
    global camera_detector, encoder_detector
    camera_detector = cam_detector
    encoder_detector = enc_detector


class RecordingRequest(BaseModel):
    """Request to start recording."""
    filename: Optional[str] = None


class StreamerConfig(BaseModel):
    """Streamer configuration."""
    camera_index: int
    width: Optional[int] = config.DEFAULT_WIDTH
    height: Optional[int] = config.DEFAULT_HEIGHT
    fps: Optional[int] = config.DEFAULT_FPS
    encoder: Optional[str] = None


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Camera Monitor API",
        "version": "1.0.0",
        "endpoints": {
            "cameras": "/api/cameras",
            "encoders": "/api/encoders",
            "stream": "/api/stream/{camera_index}",
            "recording": "/api/recording/{camera_index}",
            "status": "/api/status"
        }
    }


@app.get("/api/cameras")
async def get_cameras():
    """Get list of available cameras and their configurations."""
    if not camera_detector:
        raise HTTPException(status_code=500, detail="Camera detector not initialized")

    return {
        "cameras": camera_detector.cameras,
        "count": len(camera_detector.cameras)
    }


@app.get("/api/encoders")
async def get_encoders():
    """Get list of available encoders."""
    if not encoder_detector:
        raise HTTPException(status_code=500, detail="Encoder detector not initialized")

    return encoder_detector.get_encoder_info()


@app.post("/api/stream/{camera_index}/start")
async def start_stream(camera_index: int, stream_config: Optional[StreamerConfig] = None):
    """Start streaming from a camera."""
    if camera_index >= len(camera_detector.cameras):
        raise HTTPException(status_code=404, detail="Camera not found")

    # Get or create streamer
    if camera_index not in active_streamers:
        from video_streamer import VideoStreamer
        camera = camera_detector.cameras[camera_index]

        # Get preferred encoder
        encoder = encoder_detector.get_preferred_encoder("H.264")
        if stream_config and stream_config.encoder:
            encoder = stream_config.encoder

        streamer = VideoStreamer(
            camera_name=camera["name"],
            camera_index=camera_index,
            encoder=encoder
        )

        # Set resolution if provided
        if stream_config:
            streamer.set_resolution(
                stream_config.width or config.DEFAULT_WIDTH,
                stream_config.height or config.DEFAULT_HEIGHT,
                stream_config.fps or config.DEFAULT_FPS
            )

        active_streamers[camera_index] = streamer

    streamer = active_streamers[camera_index]
    success = streamer.start_streaming()

    if success:
        return {
            "status": "streaming",
            "camera_index": camera_index,
            "stream_url": f"http://localhost:{config.API_PORT}/api/stream/{camera_index}/video"
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to start streaming")


@app.get("/api/stream/{camera_index}/video")
async def stream_video(camera_index: int):
    """Get MJPEG video stream from camera."""
    if camera_index not in active_streamers:
        raise HTTPException(status_code=404, detail="Streamer not found. Start streaming first.")

    streamer = active_streamers[camera_index]

    if not streamer.is_streaming:
        raise HTTPException(status_code=400, detail="Stream not active. Start streaming first.")

    def generate():
        """Generate MJPEG frames."""
        while streamer.is_streaming:
            frame = streamer.get_frame()
            if frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.033)  # ~30 fps

    return StreamingResponse(
        generate(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@app.post("/api/stream/{camera_index}/stop")
async def stop_stream(camera_index: int):
    """Stop streaming from a camera."""
    if camera_index not in active_streamers:
        raise HTTPException(status_code=404, detail="Streamer not found")

    streamer = active_streamers[camera_index]
    success = streamer.stop_streaming()

    if success:
        return {"status": "stopped", "camera_index": camera_index}
    else:
        raise HTTPException(status_code=500, detail="Failed to stop streaming")


@app.post("/api/recording/{camera_index}/start")
async def start_recording(camera_index: int, request: RecordingRequest):
    """Start recording from a camera."""
    if camera_index >= len(camera_detector.cameras):
        raise HTTPException(status_code=404, detail="Camera not found")

    # Get or create streamer
    if camera_index not in active_streamers:
        from video_streamer import VideoStreamer
        camera = camera_detector.cameras[camera_index]

        # Get preferred encoder
        encoder = encoder_detector.get_preferred_encoder("H.264")

        streamer = VideoStreamer(
            camera_name=camera["name"],
            camera_index=camera_index,
            encoder=encoder
        )

        active_streamers[camera_index] = streamer

    streamer = active_streamers[camera_index]
    success = streamer.start_recording(request.filename)

    if success:
        return {
            "status": "recording",
            "camera_index": camera_index,
            "filename": streamer.current_recording
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to start recording")


@app.post("/api/recording/{camera_index}/stop")
async def stop_recording(camera_index: int):
    """Stop recording from a camera."""
    if camera_index not in active_streamers:
        raise HTTPException(status_code=404, detail="Streamer not found")

    streamer = active_streamers[camera_index]
    success = streamer.stop_recording()

    if success:
        return {"status": "stopped", "camera_index": camera_index}
    else:
        raise HTTPException(status_code=500, detail="Failed to stop recording")


@app.get("/api/status")
async def get_status():
    """Get status of all active streamers."""
    statuses = {}
    for camera_index, streamer in active_streamers.items():
        statuses[camera_index] = streamer.get_status()

    return {
        "active_cameras": len(active_streamers),
        "streamers": statuses
    }


@app.get("/api/status/{camera_index}")
async def get_camera_status(camera_index: int):
    """Get status of a specific camera."""
    if camera_index not in active_streamers:
        return {
            "camera_index": camera_index,
            "status": "inactive"
        }

    streamer = active_streamers[camera_index]
    return streamer.get_status()


@app.get("/view")
async def view_page():
    """Simple HTML page to view the stream."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Camera Monitor</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f0f0f0;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background-color: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
            }
            .controls {
                margin: 20px 0;
            }
            button {
                padding: 10px 20px;
                margin: 5px;
                font-size: 14px;
                cursor: pointer;
                border: none;
                border-radius: 4px;
                background-color: #007bff;
                color: white;
            }
            button:hover {
                background-color: #0056b3;
            }
            button.danger {
                background-color: #dc3545;
            }
            button.danger:hover {
                background-color: #c82333;
            }
            #stream {
                width: 100%;
                max-width: 800px;
                border: 2px solid #ddd;
                border-radius: 4px;
            }
            .status {
                margin: 10px 0;
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 4px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Camera Monitor</h1>
            <div class="controls">
                <button onclick="startStream(0)">Start Stream (Camera 0)</button>
                <button onclick="stopStream(0)" class="danger">Stop Stream</button>
                <button onclick="startRecording(0)">Start Recording</button>
                <button onclick="stopRecording(0)" class="danger">Stop Recording</button>
                <button onclick="checkStatus()">Check Status</button>
            </div>
            <div class="status" id="status">Status: Ready</div>
            <img id="stream" src="" alt="Video stream will appear here">
        </div>
        <script>
            async function startStream(cameraIndex) {
                try {
                    const response = await fetch(`/api/stream/${cameraIndex}/start`, {
                        method: 'POST'
                    });
                    const data = await response.json();
                    document.getElementById('status').textContent = 'Status: Streaming';
                    document.getElementById('stream').src = data.stream_url;
                } catch (error) {
                    document.getElementById('status').textContent = 'Error: ' + error;
                }
            }

            async function stopStream(cameraIndex) {
                try {
                    await fetch(`/api/stream/${cameraIndex}/stop`, {
                        method: 'POST'
                    });
                    document.getElementById('status').textContent = 'Status: Stopped';
                    document.getElementById('stream').src = '';
                } catch (error) {
                    document.getElementById('status').textContent = 'Error: ' + error;
                }
            }

            async function startRecording(cameraIndex) {
                try {
                    const response = await fetch(`/api/recording/${cameraIndex}/start`, {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({})
                    });
                    const data = await response.json();
                    document.getElementById('status').textContent = 'Status: Recording to ' + data.filename;
                } catch (error) {
                    document.getElementById('status').textContent = 'Error: ' + error;
                }
            }

            async function stopRecording(cameraIndex) {
                try {
                    await fetch(`/api/recording/${cameraIndex}/stop`, {
                        method: 'POST'
                    });
                    const response = await fetch(`/api/status/${cameraIndex}`);
                    const data = await response.json();
                    document.getElementById('status').textContent = 'Status: Recording stopped';
                } catch (error) {
                    document.getElementById('status').textContent = 'Error: ' + error;
                }
            }

            async function checkStatus() {
                try {
                    const response = await fetch('/api/status');
                    const data = await response.json();
                    document.getElementById('status').textContent = 'Status: ' + JSON.stringify(data, null, 2);
                } catch (error) {
                    document.getElementById('status').textContent = 'Error: ' + error;
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
