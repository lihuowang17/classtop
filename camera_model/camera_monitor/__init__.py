"""Camera Monitor - A flexible video monitoring library for Windows.

This library provides easy-to-use camera monitoring with hardware-accelerated encoding,
video streaming, and recording capabilities.

Example:
    Basic usage:
    ```python
    from camera_monitor import CameraMonitor, MonitorConfig

    # Create monitor with default config
    monitor = CameraMonitor().initialize()

    # Start streaming from first camera
    monitor.start_streaming(0)

    # Start recording
    monitor.start_recording(0)

    # Stop recording
    monitor.stop_recording(0)

    # Cleanup
    monitor.cleanup()
    ```

    Using context manager:
    ```python
    with CameraMonitor() as monitor:
        monitor.start_streaming(0)
        monitor.start_recording(0)
        # ... do work ...
        monitor.stop_recording(0)
    ```

    Custom configuration:
    ```python
    config = MonitorConfig.create_high_quality()
    config.camera.fps = 60
    config.encoder.nvenc_preset = 'slow'

    monitor = CameraMonitor(config).initialize()
    ```
"""

__version__ = '1.0.0'
__author__ = 'Camera Monitor Team'

from .config import (
    MonitorConfig,
    CameraConfig,
    EncoderConfig,
    RecordingConfig,
    RecordingOptions,
    StreamingConfig,
    APIConfig
)

from .monitor import CameraMonitor
from .camera_detector import CameraDetector
from .encoder_detector import EncoderDetector
from .video_streamer import VideoStreamer

__all__ = [
    # Main class
    'CameraMonitor',

    # Configuration classes
    'MonitorConfig',
    'CameraConfig',
    'EncoderConfig',
    'RecordingConfig',
    'RecordingOptions',
    'StreamingConfig',
    'APIConfig',

    # Component classes (for advanced usage)
    'CameraDetector',
    'EncoderDetector',
    'VideoStreamer',

    # Metadata
    '__version__',
]
