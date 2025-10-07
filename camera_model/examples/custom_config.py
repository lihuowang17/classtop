"""Example with custom configuration."""
from camera_monitor import CameraMonitor, MonitorConfig
import time


def main():
    """Example with custom configuration."""

    # Create custom configuration
    config = MonitorConfig()

    # Camera settings
    config.camera.width = 1920
    config.camera.height = 1080
    config.camera.fps = 30
    config.camera.encoder_preference = 'hardware'  # Prefer hardware encoding

    # Encoder settings
    config.encoder.nvenc_preset = 'slow'  # Better quality, slower encoding
    config.encoder.nvenc_bitrate = '10M'  # Higher bitrate for better quality

    # Recording settings
    config.recording.output_dir = 'my_recordings'
    config.recording.filename_pattern = 'video_%Y%m%d_%H%M%S'
    config.recording.format = 'mp4'

    # Streaming settings
    config.streaming.jpeg_quality = 95  # High quality streaming

    # API settings
    config.api.enabled = False  # Disable API server

    # Debug settings
    config.verbose_logging = True

    # Create monitor with custom config
    print("Initializing with custom configuration...")
    monitor = CameraMonitor(config).initialize()

    # Get encoder info
    encoders = monitor.get_encoders()
    print(f"\nPreferred H.264 encoder: {encoders['h264']['preferred']}")

    # Start recording with custom settings
    camera_index = 0
    print(f"\nStarting high-quality recording from camera {camera_index}...")

    if monitor.start_recording(camera_index):
        print("✓ Recording started with custom settings")
        print(f"  Resolution: {config.camera.width}x{config.camera.height}@{config.camera.fps}fps")
        print(f"  Encoder: {encoders['h264']['preferred']}")
        print(f"  Preset: {config.encoder.nvenc_preset}")
        print(f"  Bitrate: {config.encoder.nvenc_bitrate}")

        # Record for 5 seconds
        time.sleep(5)

        monitor.stop_recording(camera_index)
        print("✓ Recording stopped")

    monitor.cleanup()


if __name__ == "__main__":
    main()
