# Quick Start Guide

Get started with Camera Monitor in 5 minutes!

## Installation

### 1. Install FFmpeg

**Windows:**
- Download: https://www.gyan.dev/ffmpeg/builds/
- Extract and add `bin` folder to PATH
- Verify: `ffmpeg -version`

### 2. Install Camera Monitor

```bash
cd camera
pip install -r requirements.txt
```

Or install as package:
```bash
pip install -e .
```

## First Recording

Create a file `test.py`:

```python
from camera_monitor import CameraMonitor
import time

# Initialize and record
monitor = CameraMonitor().initialize()
monitor.start_recording(0)
time.sleep(10)  # Record for 10 seconds
monitor.stop_recording(0)
monitor.cleanup()

print("✓ Recording saved to recordings/ directory!")
```

Run it:
```bash
python test.py
```

## Use H.265 Codec

```python
from camera_monitor import CameraMonitor, RecordingOptions

monitor = CameraMonitor().initialize()

# Record with H.265
opts = RecordingOptions(codec_type='H.265')
monitor.start_recording(0, options=opts)
time.sleep(10)
monitor.stop_recording(0)
monitor.cleanup()
```

## Custom Quality

```python
from camera_monitor import RecordingOptions

# High quality
opts = RecordingOptions(
    codec_type='H.265',
    width=1920,
    height=1080,
    preset='slow',
    bitrate='15M'
)

monitor.start_recording(0, options=opts)
```

## Run Examples

```bash
# Basic usage
python examples/basic_usage.py

# Advanced recording with H.264/H.265
python examples/advanced_recording.py

# Custom configuration
python examples/custom_config.py
```

## Common Use Cases

### 1. Simple Recording
```python
monitor = CameraMonitor().initialize()
monitor.start_recording(0)
time.sleep(60)  # 60 seconds
monitor.stop_recording(0)
```

### 2. Multiple Recordings
```python
monitor = CameraMonitor().initialize()

# Recording 1
monitor.start_recording(0, filename='video1.mp4')
time.sleep(5)
monitor.stop_recording(0)

# Recording 2 with different settings
opts = RecordingOptions(codec_type='H.265')
monitor.start_recording(0, options=opts)
time.sleep(5)
monitor.stop_recording(0)
```

### 3. Context Manager (Auto Cleanup)
```python
with CameraMonitor() as monitor:
    monitor.start_recording(0)
    time.sleep(10)
    monitor.stop_recording(0)
```

### 4. List Available Cameras
```python
monitor = CameraMonitor().initialize()
cameras = monitor.get_cameras()

for cam in cameras:
    print(f"Camera {cam['index']}: {cam['name']}")
```

### 5. Check Encoders
```python
monitor = CameraMonitor().initialize()
encoders = monitor.get_encoders()

print("H.264 encoders:", [e['name'] for e in encoders['h264']['encoders']])
print("H.265 encoders:", [e['name'] for e in encoders['h265']['encoders']])
print("Preferred H.264:", encoders['h264']['preferred'])
```

## Configuration Presets

```python
from camera_monitor import MonitorConfig

# High quality
config = MonitorConfig.create_high_quality()

# Low latency
config = MonitorConfig.create_low_latency()

# Low resource
config = MonitorConfig.create_low_resource()

monitor = CameraMonitor(config).initialize()
```

## Troubleshooting

### Camera not detected
```bash
# List DirectShow devices
ffmpeg -list_devices true -f dshow -i dummy
```

### FFmpeg not found
```bash
# Check FFmpeg installation
ffmpeg -version

# Add to PATH (Windows)
# System Properties > Environment Variables > Path > Add FFmpeg bin folder
```

### Poor recording quality
```python
# Increase bitrate
opts = RecordingOptions(bitrate='20M')

# Or use slower preset
opts = RecordingOptions(preset='slow')

# Or lower CRF (software encoding)
opts = RecordingOptions(encoder='libx264', crf=18)
```

### Large file size
```python
# Use H.265
opts = RecordingOptions(codec_type='H.265')

# Or lower bitrate
opts = RecordingOptions(bitrate='3M')

# Or lower resolution
opts = RecordingOptions(width=1280, height=720)
```

## Next Steps

- Read [README.md](README.md) for full documentation
- Check [RECORDING_OPTIONS.md](RECORDING_OPTIONS.md) for all options
- See [CUSTOMIZATION_GUIDE.md](CUSTOMIZATION_GUIDE.md) for advanced usage
- Try [examples/](examples/) for code samples

## Getting Help

- Check the documentation
- Look at example code
- Enable verbose logging: `config.verbose_logging = True`
- Check the console output for errors

Happy recording! 📹
