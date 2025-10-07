"""Example using preset configurations."""
from camera_monitor import CameraMonitor, MonitorConfig
import time


def demo_preset(preset_name: str, config: MonitorConfig):
    """Demo a specific preset configuration."""
    print(f"\n{'='*60}")
    print(f"Testing {preset_name} preset")
    print(f"{'='*60}")

    monitor = CameraMonitor(config).initialize()

    camera_index = 0
    print(f"\nConfiguration:")
    print(f"  Resolution: {config.camera.width}x{config.camera.height}")
    print(f"  FPS: {config.camera.fps}")
    print(f"  JPEG Quality: {config.streaming.jpeg_quality}")

    print(f"\nStarting recording for 3 seconds...")
    monitor.start_recording(camera_index)
    time.sleep(3)
    monitor.stop_recording(camera_index)

    print("✓ Recording complete")
    monitor.cleanup()


def main():
    """Demonstrate different preset configurations."""

    print("Camera Monitor - Preset Configurations Demo")
    print("This will test three different quality presets")

    # 1. High Quality Preset
    demo_preset("HIGH QUALITY", MonitorConfig.create_high_quality())

    # 2. Low Latency Preset
    demo_preset("LOW LATENCY", MonitorConfig.create_low_latency())

    # 3. Low Resource Preset
    demo_preset("LOW RESOURCE", MonitorConfig.create_low_resource())

    print(f"\n{'='*60}")
    print("All presets tested successfully!")
    print("Check the 'recordings' directory for output files")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
