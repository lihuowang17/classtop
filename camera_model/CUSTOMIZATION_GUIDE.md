# Customization Guide

Complete guide to customizing Camera Monitor for your needs.

## Table of Contents

1. [Global Configuration](#global-configuration)
2. [Per-Recording Options](#per-recording-options)
3. [Codec Selection](#codec-selection)
4. [Quality vs Performance](#quality-vs-performance)
5. [Examples](#examples)

## Global Configuration

Global configuration using `MonitorConfig` sets defaults for all recordings:

```python
from camera_monitor import CameraMonitor, MonitorConfig

config = MonitorConfig()

# Camera settings (applies to all recordings by default)
config.camera.width = 1920
config.camera.height = 1080
config.camera.fps = 30
config.camera.encoder_preference = 'hardware'

# Encoder settings (used when no per-recording options)
config.encoder.nvenc_preset = 'medium'
config.encoder.nvenc_bitrate = '8M'

monitor = CameraMonitor(config).initialize()
```

## Per-Recording Options

Override configuration for individual recordings using `RecordingOptions`:

```python
from camera_monitor import RecordingOptions

# This recording uses custom settings
opts = RecordingOptions(
    codec_type='H.265',
    width=1920,
    height=1080,
    preset='slow',
    bitrate='15M'
)

monitor.start_recording(0, options=opts)
```

### Key Differences

| Feature | MonitorConfig | RecordingOptions |
|---------|---------------|------------------|
| Scope | Global default | Per-recording |
| When Set | At initialization | At recording start |
| Override | No | Yes (overrides config) |
| Use Case | Default settings | Special recordings |

## Codec Selection

### Method 1: By Codec Type (Recommended)

```python
# System automatically selects best encoder for codec type
opts = RecordingOptions(codec_type='H.264')  # or 'H.265'
```

**How it works:**
- System checks available encoders
- Selects best available (NVENC > QSV > AMF > Software)
- No need to know specific encoder names

### Method 2: Specific Encoder

```python
# Force specific encoder
opts = RecordingOptions(encoder='hevc_nvenc')
```

**Available encoders:**
- H.264: `h264_nvenc`, `h264_qsv`, `h264_amf`, `libx264`
- H.265: `hevc_nvenc`, `hevc_qsv`, `hevc_amf`, `libx265`

### When to Use Each

**Use codec_type when:**
- You want best available encoder
- Don't care about specific hardware
- Want portable code

**Use specific encoder when:**
- Need specific hardware features
- Testing encoder performance
- Debugging encoder issues

## Quality vs Performance

### Three Dimensions of Quality

1. **Resolution** - Image size (pixels)
2. **Bitrate/CRF** - Data rate (quality per frame)
3. **Preset** - Encoding efficiency

### Quality Presets

#### Maximum Quality (Storage-intensive)
```python
opts = RecordingOptions(
    codec_type='H.265',
    width=1920,
    height=1080,
    preset='slow',
    bitrate='25M'
)
```
- Best quality
- Largest CPU/GPU usage
- Medium file size (H.265 compression)

#### Balanced (Recommended)
```python
opts = RecordingOptions(
    codec_type='H.264',
    width=1280,
    height=720,
    preset='medium',
    bitrate='5M'
)
```
- Good quality
- Moderate CPU/GPU usage
- Reasonable file size

#### Fast/Real-time
```python
opts = RecordingOptions(
    codec_type='H.264',
    width=1280,
    height=720,
    preset='ultrafast',
    bitrate='3M'
)
```
- Acceptable quality
- Minimal CPU/GPU usage
- Larger files (less compression)

#### Low Bandwidth
```python
opts = RecordingOptions(
    width=640,
    height=480,
    fps=15,
    bitrate='1M'
)
```
- Lower quality
- Minimal bandwidth
- Small files

## Examples

### Example 1: Surveillance Camera

```python
# 24/7 recording with balanced settings
config = MonitorConfig()
config.camera.width = 1280
config.camera.height = 720
config.camera.fps = 15  # Lower FPS saves storage
config.encoder.nvenc_bitrate = '2M'
config.recording.output_dir = 'surveillance'

monitor = CameraMonitor(config).initialize()
monitor.start_recording(0)
```

### Example 2: High-Quality Archive

```python
# Occasional high-quality recordings
monitor = CameraMonitor().initialize()

opts = RecordingOptions(
    codec_type='H.265',
    width=1920,
    height=1080,
    preset='veryslow',  # Maximum compression
    crf=18,             # High quality
    filename='archive_video.mp4'
)

monitor.start_recording(0, options=opts)
```

### Example 3: Multiple Simultaneous Recordings

```python
# Note: Not currently supported (one recording at a time per camera)
# For multiple simultaneous recordings, use multiple camera instances

monitor1 = CameraMonitor().initialize()
monitor2 = CameraMonitor().initialize()

# Different qualities from same camera would require
# multiple camera indices or external routing
```

### Example 4: Adaptive Quality

```python
def record_adaptive(monitor, camera_index, quality='medium'):
    """Record with quality level."""

    quality_settings = {
        'low': RecordingOptions(
            width=640, height=480, fps=15, bitrate='1M'
        ),
        'medium': RecordingOptions(
            width=1280, height=720, fps=30, bitrate='5M'
        ),
        'high': RecordingOptions(
            width=1920, height=1080, fps=30, bitrate='15M'
        )
    }

    opts = quality_settings.get(quality, quality_settings['medium'])
    monitor.start_recording(camera_index, options=opts)

# Usage
monitor = CameraMonitor().initialize()
record_adaptive(monitor, 0, quality='high')
```

### Example 5: Time-of-Day Settings

```python
from datetime import datetime

def get_recording_options():
    """Different settings based on time of day."""
    hour = datetime.now().hour

    if 22 <= hour or hour < 6:  # Night (10 PM - 6 AM)
        return RecordingOptions(
            fps=10,        # Lower FPS at night
            bitrate='2M'   # Lower bitrate
        )
    else:  # Day
        return RecordingOptions(
            fps=30,
            bitrate='5M'
        )

# Usage
monitor = CameraMonitor().initialize()
opts = get_recording_options()
monitor.start_recording(0, options=opts)
```

### Example 6: Different Codecs for Different Purposes

```python
monitor = CameraMonitor().initialize()

# Recording 1: H.264 for streaming/sharing
h264_opts = RecordingOptions(
    codec_type='H.264',
    filename='share_video.mp4'
)
monitor.start_recording(0, options=h264_opts)
time.sleep(10)
monitor.stop_recording(0)

# Recording 2: H.265 for archiving
h265_opts = RecordingOptions(
    codec_type='H.265',
    preset='slower',
    filename='archive_video.mp4'
)
monitor.start_recording(0, options=h265_opts)
time.sleep(10)
monitor.stop_recording(0)
```

## Decision Trees

### Codec Selection

```
Need recording?
├─ For sharing/compatibility? → Use H.264
├─ For storage efficiency? → Use H.265
└─ For editing? → Use H.264 with high bitrate
```

### Quality Selection

```
What's your priority?
├─ Real-time performance?
│   └─ Use preset='ultrafast', bitrate='3M'
├─ Storage space?
│   └─ Use H.265, preset='slow', bitrate='3M'
├─ Maximum quality?
│   └─ Use preset='slow', crf=16 or bitrate='20M'
└─ Balanced?
    └─ Use preset='medium', bitrate='5M'
```

### Hardware Selection

```
Have NVIDIA GPU?
├─ Yes → Use NVENC (fastest, good quality)
├─ No → Have Intel CPU?
    ├─ Yes → Use QSV (fast, good quality)
    ├─ No → Have AMD GPU?
        ├─ Yes → Use AMF (fast, good quality)
        └─ No → Use Software (slower, best quality)
```

## Performance Tips

1. **GPU Encoding** - Always use if available (10-100x faster)
2. **Resolution** - Lower resolution = faster encoding
3. **Preset** - Fast presets = real-time capable
4. **Multiple Cameras** - Hardware encoders can handle multiple streams
5. **Disk Speed** - Use SSD for high bitrate recordings

## Storage Tips

1. **H.265 vs H.264** - H.265 saves ~50% storage
2. **Lower FPS** - 15fps vs 30fps saves 50% storage
3. **Compression** - Slower presets save storage
4. **Bitrate** - Lower bitrate = smaller files (but lower quality)
5. **Resolution** - 720p vs 1080p saves ~50% storage

## Troubleshooting

### Recording Too Slow
- Use faster preset
- Lower resolution/FPS
- Use hardware encoder

### File Too Large
- Use H.265 instead of H.264
- Lower bitrate
- Use slower preset (better compression)

### Quality Too Low
- Increase bitrate
- Increase resolution
- Use slower preset
- Lower CRF value

### Encoder Not Available
- Check with `monitor.get_encoders()`
- Update GPU drivers
- Use software fallback

## See Also

- [RECORDING_OPTIONS.md](RECORDING_OPTIONS.md) - Complete RecordingOptions reference
- [examples/advanced_recording.py](examples/advanced_recording.py) - Code examples
- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - Architecture details
- [README.md](README.md) - Main documentation
