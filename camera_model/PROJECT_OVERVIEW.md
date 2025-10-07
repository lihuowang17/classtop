# Camera Monitor - Project Overview

## 📁 Project Structure

```
camera/
├── camera_monitor/              # Main library package
│   ├── __init__.py             # Package exports and documentation
│   ├── config.py               # Configuration dataclasses
│   ├── monitor.py              # Main CameraMonitor class
│   ├── camera_detector.py      # DirectShow camera detection
│   ├── encoder_detector.py     # Hardware encoder detection
│   ├── video_streamer.py       # Video streaming and recording
│   └── api_server.py           # HTTP API server
│
├── examples/                    # Usage examples
│   ├── basic_usage.py          # Basic recording example
│   ├── context_manager.py      # Context manager usage
│   ├── custom_config.py        # Custom configuration
│   ├── preset_configs.py       # Using presets
│   └── with_api_server.py      # HTTP API server example
│
├── recordings/                  # Default output directory (created at runtime)
│
├── setup.py                     # Package installation script
├── requirements.txt             # Python dependencies
├── README.md                    # Main documentation
└── PROJECT_OVERVIEW.md          # This file
```

## 🎯 Core Components

### 1. Configuration System (`config.py`)

Flexible, type-safe configuration using Python dataclasses:

- **MonitorConfig**: Main configuration container
- **CameraConfig**: Camera capture settings (resolution, fps, encoder)
- **EncoderConfig**: Encoder-specific parameters (NVENC, QSV, AMF, software)
- **RecordingConfig**: Recording output settings
- **StreamingConfig**: Streaming quality settings
- **APIConfig**: HTTP API server settings

**Preset Configurations:**
- `MonitorConfig.create_default()` - Balanced settings
- `MonitorConfig.create_high_quality()` - High quality recording
- `MonitorConfig.create_low_latency()` - Low latency streaming
- `MonitorConfig.create_low_resource()` - Minimal resource usage

### 2. Camera Monitor (`monitor.py`)

Main entry point for the library:

```python
monitor = CameraMonitor(config).initialize()
monitor.start_recording(0)
monitor.stop_recording(0)
monitor.cleanup()
```

**Features:**
- Auto-initialization of cameras and encoders
- Per-camera streamer management
- Automatic encoder selection
- Context manager support
- Status monitoring

### 3. Camera Detector (`camera_detector.py`)

DirectShow-based camera detection:

- Lists all available cameras
- Detects supported resolutions and frame rates
- Uses pygrabber for DirectShow access
- Fallback to common resolutions if detection fails

### 4. Encoder Detector (`encoder_detector.py`)

Hardware encoder detection and testing:

- Tests actual encoder availability (not just listing)
- Detects NVIDIA NVENC, Intel QSV, AMD AMF
- Software encoder fallback
- Priority-based encoder selection

### 5. Video Streamer (`video_streamer.py`)

Core streaming and recording functionality:

- OpenCV-based camera capture for streaming
- FFmpeg-based recording with hardware acceleration
- Configurable JPEG quality for streaming
- Per-encoder parameter configuration
- Detailed logging and error handling

### 6. API Server (`api_server.py`)

Optional HTTP REST API:

- FastAPI-based server
- MJPEG video streaming endpoint
- Remote camera control
- Interactive API documentation (Swagger UI)
- Web viewer interface

## 🔧 Key Design Patterns

### 1. Builder Pattern
Configuration objects use builder pattern for flexibility:
```python
config = MonitorConfig()
config.camera.width = 1920
config.encoder.nvenc_preset = 'slow'
```

### 2. Context Manager
Automatic resource management:
```python
with CameraMonitor() as monitor:
    monitor.start_recording(0)
```

### 3. Dependency Injection
Configuration injected into components:
```python
streamer = VideoStreamer(camera_name, camera_index, encoder, config=config)
```

### 4. Factory Methods
Preset configurations via factory methods:
```python
config = MonitorConfig.create_high_quality()
```

## 🚀 Usage Patterns

### Pattern 1: Simple Recording

```python
from camera_monitor import CameraMonitor

monitor = CameraMonitor().initialize()
monitor.start_recording(0)
time.sleep(10)
monitor.stop_recording(0)
monitor.cleanup()
```

### Pattern 2: Custom Configuration

```python
from camera_monitor import CameraMonitor, MonitorConfig

config = MonitorConfig()
config.camera.width = 1920
config.camera.height = 1080
config.encoder.nvenc_bitrate = '10M'

monitor = CameraMonitor(config).initialize()
```

### Pattern 3: Preset Configuration

```python
config = MonitorConfig.create_high_quality()
monitor = CameraMonitor(config).initialize()
```

### Pattern 4: Context Manager

```python
with CameraMonitor() as monitor:
    monitor.start_recording(0)
    time.sleep(10)
    monitor.stop_recording(0)
```

### Pattern 5: HTTP API Server

```python
from camera_monitor import CameraMonitor
from camera_monitor import api_server
import uvicorn

monitor = CameraMonitor().initialize()
api_server.initialize(monitor.camera_detector, monitor.encoder_detector)
api_server.active_streamers = monitor.streamers
uvicorn.run(api_server.app, host='0.0.0.0', port=8888)
```

## 🎨 Configuration Examples

### High Performance

```python
config = MonitorConfig()
config.camera.width = 1280
config.camera.height = 720
config.camera.fps = 60
config.encoder.nvenc_preset = 'ultrafast'
config.encoder.nvenc_bitrate = '8M'
```

### High Quality

```python
config = MonitorConfig()
config.camera.width = 1920
config.camera.height = 1080
config.camera.fps = 30
config.encoder.nvenc_preset = 'slow'
config.encoder.nvenc_bitrate = '15M'
config.streaming.jpeg_quality = 95
```

### Low Bandwidth

```python
config = MonitorConfig()
config.camera.width = 640
config.camera.height = 480
config.camera.fps = 15
config.encoder.software_crf = 28
config.streaming.jpeg_quality = 60
```

## 📊 Data Flow

```
User Code
    ↓
CameraMonitor (monitor.py)
    ↓
├─→ CameraDetector (camera_detector.py) → DirectShow → Camera List
├─→ EncoderDetector (encoder_detector.py) → FFmpeg → Encoder List
└─→ VideoStreamer (video_streamer.py)
        ├─→ OpenCV → Frames → JPEG → HTTP Stream
        └─→ FFmpeg → DirectShow → Hardware Encoder → MP4 File
```

## 🔑 Key Features

1. **Type Safety**: All configuration uses type-annotated dataclasses
2. **Validation**: Configuration validation in `__post_init__` methods
3. **Flexibility**: Multiple configuration methods (default, presets, custom)
4. **Hardware Acceleration**: Automatic detection and use of GPU encoders
5. **Error Handling**: Comprehensive error handling and logging
6. **Resource Management**: Automatic cleanup via context managers
7. **Extensibility**: Easy to add new encoders or camera sources

## 📝 Adding New Features

### Adding a New Encoder

1. Add detection logic in `encoder_detector.py`
2. Add configuration in `config.py:EncoderConfig`
3. Add encoding logic in `video_streamer.py:start_recording()`

### Adding a New Configuration Preset

Add factory method in `config.py:MonitorConfig`:

```python
@classmethod
def create_my_preset(cls) -> 'MonitorConfig':
    config = cls()
    config.camera.width = 1280
    config.camera.height = 720
    # ... configure other settings
    return config
```

### Adding a New API Endpoint

Add endpoint in `api_server.py`:

```python
@app.get("/api/my_endpoint")
async def my_endpoint():
    return {"result": "data"}
```

## 🧪 Testing

Run examples to test functionality:

```bash
# Basic usage
python examples/basic_usage.py

# Custom config
python examples/custom_config.py

# Presets
python examples/preset_configs.py

# Context manager
python examples/context_manager.py

# API server
python examples/with_api_server.py
```

## 📦 Installation

As a library:
```bash
pip install -e .
```

As a standalone tool:
```bash
python examples/with_api_server.py
```

## 🛠️ Development

### Code Style
- PEP 8 compliant
- Type hints for all public APIs
- Comprehensive docstrings

### Dependencies
- Minimal dependencies (FastAPI, OpenCV, pygrabber)
- Optional dependencies (FastAPI for API server)

### Compatibility
- Python 3.10+
- Windows 10/11 only (DirectShow)
- FFmpeg required

## 🎯 Design Goals

1. **Simple for Simple Tasks**: One-liners for basic use cases
2. **Flexible for Complex Tasks**: Full configuration control when needed
3. **Type Safe**: Catch errors early with type checking
4. **Well Documented**: Clear examples and API documentation
5. **Hardware Accelerated**: Automatic use of GPU when available
6. **Production Ready**: Proper error handling and resource management

## 🚦 Status

✅ Core functionality complete
✅ Configuration system complete
✅ Examples complete
✅ Documentation complete
✅ Package structure complete

Ready for use as a library!
