# Recording Options Guide

Complete guide to using `RecordingOptions` for flexible video recording.

## Overview

`RecordingOptions` allows you to customize individual recordings with different settings, overriding the default configuration.

## Basic Usage

```python
from camera_monitor import CameraMonitor, RecordingOptions

monitor = CameraMonitor().initialize()

# Create recording options
opts = RecordingOptions(codec_type='H.265', bitrate='10M')

# Start recording with options
monitor.start_recording(0, options=opts)
```

## RecordingOptions Parameters

### Codec Selection

```python
# Use H.264 codec (default)
opts = RecordingOptions(codec_type='H.264')

# Use H.265 codec (better compression)
opts = RecordingOptions(codec_type='H.265')
```

### Specific Encoder

```python
# Force specific encoder
opts = RecordingOptions(encoder='h264_nvenc')  # NVIDIA
opts = RecordingOptions(encoder='hevc_nvenc')  # NVIDIA H.265
opts = RecordingOptions(encoder='h264_qsv')    # Intel
opts = RecordingOptions(encoder='h264_amf')    # AMD
opts = RecordingOptions(encoder='libx264')     # Software H.264
opts = RecordingOptions(encoder='libx265')     # Software H.265
```

### Resolution and FPS

```python
# Custom resolution
opts = RecordingOptions(
    width=1920,
    height=1080,
    fps=60
)

# Low resolution for bandwidth saving
opts = RecordingOptions(
    width=640,
    height=480,
    fps=15
)
```

### Encoding Quality

```python
# Hardware encoders: Use preset and bitrate
opts = RecordingOptions(
    preset='slow',      # ultrafast, superfast, fast, medium, slow
    bitrate='15M'       # Higher = better quality, larger file
)

# Software encoders: Use CRF
opts = RecordingOptions(
    encoder='libx264',
    crf=18,             # 0-51, lower = better quality (18-28 recommended)
    preset='slower'     # Slower = better compression
)
```

### Pixel Format

```python
# Change pixel format (advanced)
opts = RecordingOptions(pixel_format='yuv444p')  # Default: yuv420p
```

### Custom Filename

```python
# Specify custom filename
opts = RecordingOptions(filename='my_video.mp4')
```

### Custom FFmpeg Arguments

```python
# Advanced: Add custom FFmpeg parameters
opts = RecordingOptions(
    custom_args=[
        '-profile:v', 'high',
        '-level', '4.2',
        '-g', '60'
    ]
)
```

## Common Use Cases

### High Quality Recording

```python
opts = RecordingOptions(
    codec_type='H.265',
    width=1920,
    height=1080,
    preset='slow',
    bitrate='20M'
)
monitor.start_recording(0, options=opts)
```

### Low Bandwidth Recording

```python
opts = RecordingOptions(
    width=640,
    height=480,
    fps=15,
    bitrate='1M'
)
monitor.start_recording(0, options=opts)
```

### Ultra High Quality (Software Encoding)

```python
opts = RecordingOptions(
    encoder='libx265',
    width=1920,
    height=1080,
    crf=16,           # Very high quality
    preset='veryslow'  # Best compression
)
monitor.start_recording(0, options=opts)
```

### Fast Recording (Low Latency)

```python
opts = RecordingOptions(
    codec_type='H.264',
    preset='ultrafast',
    bitrate='5M'
)
monitor.start_recording(0, options=opts)
```

### Multiple Recordings with Different Settings

```python
monitor = CameraMonitor().initialize()

# Recording 1: H.264 for compatibility
opts1 = RecordingOptions(
    codec_type='H.264',
    filename='video_h264.mp4'
)
monitor.start_recording(0, options=opts1)
time.sleep(5)
monitor.stop_recording(0)

# Recording 2: H.265 for better compression
opts2 = RecordingOptions(
    codec_type='H.265',
    filename='video_h265.mp4'
)
monitor.start_recording(0, options=opts2)
time.sleep(5)
monitor.stop_recording(0)
```

## Codec Comparison

### H.264 vs H.265

| Feature | H.264 | H.265 |
|---------|-------|-------|
| Compression | Good | Better (~50% smaller) |
| Encoding Speed | Faster | Slower |
| Compatibility | Excellent | Good (newer) |
| GPU Support | Widespread | Common |
| Use Case | General purpose | High quality, storage-sensitive |

### Hardware vs Software Encoding

| Feature | Hardware (NVENC/QSV/AMF) | Software (libx264/libx265) |
|---------|-------------------------|---------------------------|
| Speed | Very Fast | Slower |
| Quality | Good | Excellent |
| CPU Usage | Low | High |
| Settings | Limited | Full control |
| Use Case | Real-time, high FPS | Maximum quality |

## Preset Guide

### Hardware Encoder Presets (NVENC/QSV)

- `ultrafast` / `veryfast` - Fastest encoding, lower quality
- `fast` / `faster` - Good balance (recommended)
- `medium` - Balanced speed and quality
- `slow` / `slower` - Better quality, slower encoding

### Software Encoder Presets (libx264/libx265)

- `ultrafast` - Fastest, largest files
- `superfast`, `veryfast`, `faster` - Fast encoding
- `fast` - Good balance
- `medium` - Default, balanced (recommended)
- `slow`, `slower` - Better compression
- `veryslow` - Best compression, very slow

## Bitrate Guidelines

| Resolution | Low | Medium | High | Ultra |
|------------|-----|--------|------|-------|
| 640x480 | 1M | 2M | 3M | 5M |
| 1280x720 | 3M | 5M | 8M | 10M |
| 1920x1080 | 5M | 10M | 15M | 25M |
| 3840x2160 | 20M | 40M | 60M | 100M |

## CRF Guidelines (Software Encoders)

| CRF | Quality | Use Case |
|-----|---------|----------|
| 0-17 | Visually lossless | Archival, editing |
| 18-23 | Very high quality | Recommended |
| 24-28 | Good quality | General use |
| 29-35 | Acceptable | Low bandwidth |
| 36+ | Poor quality | Not recommended |

## Parameter Priority

When multiple parameters are specified, they are applied in this order:

1. **Encoder Selection**: `encoder` > `codec_type` > default
2. **Resolution**: `options` > config > default
3. **Encoding Quality**: `options` > config
4. **Pixel Format**: `options` > config > default

## Error Handling

```python
from camera_monitor import RecordingOptions

# Options are validated on creation
try:
    opts = RecordingOptions(
        codec_type='H.266',  # Invalid codec type
        crf=100              # Out of range
    )
except ValueError as e:
    print(f"Invalid options: {e}")

# Check if recording started successfully
if not monitor.start_recording(0, options=opts):
    print("Recording failed to start")
```

## Complete Example

```python
from camera_monitor import CameraMonitor, RecordingOptions
import time

# Initialize monitor
with CameraMonitor() as monitor:

    # High quality H.265 recording
    high_quality = RecordingOptions(
        codec_type='H.265',
        width=1920,
        height=1080,
        preset='slow',
        bitrate='15M',
        filename='high_quality.mp4'
    )

    print("Starting high quality recording...")
    monitor.start_recording(0, options=high_quality)
    time.sleep(10)
    monitor.stop_recording(0)

    # Fast H.264 recording for streaming
    fast_recording = RecordingOptions(
        codec_type='H.264',
        preset='ultrafast',
        bitrate='5M',
        filename='fast_recording.mp4'
    )

    print("Starting fast recording...")
    monitor.start_recording(0, options=fast_recording)
    time.sleep(10)
    monitor.stop_recording(0)

    print("All recordings complete!")
```

## Tips and Best Practices

1. **Codec Selection**:
   - Use H.264 for maximum compatibility
   - Use H.265 when storage space is limited
   - Use hardware encoders for real-time recording

2. **Quality vs Performance**:
   - For real-time: Use `fast` or `ultrafast` preset
   - For archival: Use `slow` preset or low CRF
   - For streaming: Balance bitrate with available bandwidth

3. **Resolution**:
   - Higher resolution = larger files and more CPU/GPU usage
   - Test camera's native resolution for best quality
   - Scale down if needed for performance

4. **Testing**:
   - Test different settings before production use
   - Monitor CPU/GPU usage during recording
   - Check file sizes and playback quality

5. **Storage**:
   - H.265 saves ~50% storage vs H.264
   - Lower CRF or higher bitrate = larger files
   - Monitor available disk space

## See Also

- [Basic Usage](examples/basic_usage.py)
- [Custom Configuration](examples/custom_config.py)
- [Advanced Recording Examples](examples/advanced_recording.py)
- [API Documentation](README.md)
