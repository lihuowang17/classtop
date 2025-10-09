# Camera Monitor 📹

A powerful and flexible Python library for video monitoring on Windows with hardware-accelerated encoding support.

## Features ✨

- 🎥 **Automatic Camera Detection** - DirectShow-based camera detection with capability enumeration
- 🚀 **Hardware Acceleration** - Automatic detection and testing of NVIDIA NVENC, Intel QSV, and AMD AMF encoders
- 📹 **Video Streaming** - Real-time MJPEG streaming with configurable quality
- 💾 **Video Recording** - Hardware-accelerated H.264/H.265 recording to MP4
- ⚙️ **Flexible Configuration** - Comprehensive configuration system with presets
- 🌐 **HTTP API** - Optional REST API for remote control
- 🐍 **Pythonic API** - Clean, intuitive interface with context manager support
- 📊 **Detailed Logging** - Comprehensive debugging and monitoring output

## Requirements

- **OS**: Windows 10/11
- **Python**: 3.10+
- **FFmpeg**: Must be installed and available in system PATH

## Installation

### 1. Install FFmpeg

Download FFmpeg from [https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/)

Extract and add the `bin` directory to your system PATH.

Verify installation:
```bash
ffmpeg -version
```

### 2. Install Camera Monitor

```bash
pip install -e .
```

Or install dependencies directly:
```bash
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```python
from camera_monitor import CameraMonitor
import time

# Create and initialize monitor
monitor = CameraMonitor().initialize()

# Start recording from first camera
monitor.start_recording(0)

# Record for 10 seconds
time.sleep(10)

# Stop recording
monitor.stop_recording(0)

# Cleanup
monitor.cleanup()
```

### Using Context Manager

```python
from camera_monitor import CameraMonitor

with CameraMonitor() as monitor:
    # Automatic initialization and cleanup
    monitor.start_recording(0)
    time.sleep(10)
    monitor.stop_recording(0)
```

### Custom Configuration

```python
from camera_monitor import CameraMonitor, MonitorConfig

# Create custom configuration
config = MonitorConfig()
config.camera.width = 1920
config.camera.height = 1080
config.camera.fps = 30
config.encoder.nvenc_preset = 'slow'  # Better quality
config.encoder.nvenc_bitrate = '10M'  # Higher bitrate
config.recording.output_dir = 'my_videos'

# Use custom configuration
monitor = CameraMonitor(config).initialize()
monitor.start_recording(0)
```

### Using Presets

```python
from camera_monitor import CameraMonitor, MonitorConfig

# High quality preset (1920x1080, high quality encoding)
config = MonitorConfig.create_high_quality()

# Low latency preset (1280x720@60fps, fast encoding)
config = MonitorConfig.create_low_latency()

# Low resource preset (640x480@15fps, software encoding)
config = MonitorConfig.create_low_resource()

monitor = CameraMonitor(config).initialize()
```

### Per-Recording Customization

Use `RecordingOptions` to customize individual recordings:

```python
from camera_monitor import CameraMonitor, RecordingOptions

monitor = CameraMonitor().initialize()

# Record with H.265 codec
opts = RecordingOptions(codec_type='H.265')
monitor.start_recording(0, options=opts)

# Record with custom resolution and bitrate
opts = RecordingOptions(
    width=1920,
    height=1080,
    bitrate='15M'
)
monitor.start_recording(0, options=opts)

# Record with specific encoder
opts = RecordingOptions(
    encoder='hevc_nvenc',  # Use NVIDIA H.265
    preset='slow',
    bitrate='20M'
)
monitor.start_recording(0, options=opts)
```

**📖 See [RECORDING_OPTIONS.md](RECORDING_OPTIONS.md) for complete guide**

## Configuration Options

### Camera Configuration

```python
config.camera.width = 1280
config.camera.height = 720
config.camera.fps = 30
config.camera.encoder = None  # None = auto-detect
config.camera.encoder_preference = 'hardware'  # or 'software'
```

### Encoder Configuration

```python
config.encoder.nvenc_preset = 'fast'  # ultrafast, superfast, fast, medium, slow
config.encoder.nvenc_bitrate = '5M'
config.encoder.qsv_preset = 'medium'
config.encoder.qsv_bitrate = '5M'
config.encoder.amf_quality = 'balanced'  # speed, balanced, quality
config.encoder.amf_bitrate = '5M'
config.encoder.software_preset = 'medium'
config.encoder.software_crf = 23  # 0-51, lower = better quality
```

### Recording Configuration

```python
config.recording.output_dir = 'recordings'
config.recording.format = 'mp4'
config.recording.filename_pattern = 'recording_%Y%m%d_%H%M%S'
config.recording.create_dir = True
```

### Streaming Configuration

```python
config.streaming.jpeg_quality = 80  # 1-100
config.streaming.stream_fps = None  # None = same as camera
```

## API Reference

### CameraMonitor

```python
monitor = CameraMonitor(config: Optional[MonitorConfig] = None)
```

**Methods:**

- `initialize() -> CameraMonitor` - Initialize monitor
- `get_cameras() -> List[Dict]` - Get detected cameras
- `get_encoders() -> Dict` - Get encoder information
- `start_streaming(camera_index: int) -> bool` - Start streaming
- `stop_streaming(camera_index: int) -> bool` - Stop streaming
- `start_recording(camera_index: int, filename: Optional[str] = None) -> bool` - Start recording
- `stop_recording(camera_index: int) -> bool` - Stop recording
- `get_status(camera_index: Optional[int] = None) -> Dict` - Get status
- `cleanup()` - Clean up resources

## Examples

See the `examples/` directory:

- `basic_usage.py` - Basic recording
- `custom_config.py` - Custom configuration
- `preset_configs.py` - Using presets
- `context_manager.py` - Context manager usage
- `with_api_server.py` - HTTP API server

Run an example:
```bash
python examples/basic_usage.py
```

## HTTP API

Optional REST API for remote control.

### API Endpoints

- `GET /api/cameras` - List cameras
- `GET /api/encoders` - List encoders
- `POST /api/stream/{camera_index}/start` - Start streaming
- `GET /api/stream/{camera_index}/video` - Get MJPEG stream
- `POST /api/recording/{camera_index}/start` - Start recording
- `POST /api/recording/{camera_index}/stop` - Stop recording
- `GET /api/status` - Get status
- `GET /view` - Web viewer
- `GET /docs` - API documentation

Access: `http://localhost:8888/view`

## Hardware Encoder Support

Automatically detects and tests:

- **NVIDIA NVENC** (h264_nvenc, hevc_nvenc)
- **Intel QSV** (h264_qsv, hevc_qsv)
- **AMD AMF** (h264_amf, hevc_amf)
- **Software** (libx264, libx265)

Priority: NVENC > QSV > AMF > Software

## Architecture

```
camera_monitor/
├── __init__.py           # Package exports
├── config.py             # Configuration classes
├── monitor.py            # Main CameraMonitor class
├── camera_detector.py    # Camera detection
├── encoder_detector.py   # Encoder detection
├── video_streamer.py     # Streaming/recording
└── api_server.py         # HTTP API (optional)
```

## Troubleshooting

### Camera Not Detected
- Ensure camera is not in use
- Check Device Manager
- Run as administrator

### Encoder Errors
- Verify FFmpeg installation
- Update GPU drivers
- Enable `verbose_logging`

### Recording Fails
- Check output directory permissions
- Verify disk space
- Check camera resolution support

## License

MIT License

## Built With

- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [FFmpeg](https://ffmpeg.org/) - Video processing
- [pygrabber](https://github.com/bunkahle/pygrabber) - DirectShow
- [OpenCV](https://opencv.org/) - Computer vision

---

**Made with ❤️ for the computer vision community**
