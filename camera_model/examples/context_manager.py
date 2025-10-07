"""Example using context manager for automatic cleanup."""
from camera_monitor import CameraMonitor, MonitorConfig
import time


def main():
    """Example using context manager."""

    print("Camera Monitor - Context Manager Example")
    print("Using 'with' statement for automatic cleanup\n")

    # Using context manager - automatic cleanup on exit
    with CameraMonitor() as monitor:
        # Monitor is automatically initialized
        cameras = monitor.get_cameras()

        if len(cameras) == 0:
            print("No cameras found!")
            return

        camera_index = 0

        print(f"Using camera: {cameras[camera_index]['name']}\n")

        # Start streaming
        print("Starting stream...")
        monitor.start_streaming(camera_index)

        # Start recording
        print("Starting recording...")
        monitor.start_recording(camera_index)

        # Do work
        print("Recording for 5 seconds...")
        for i in range(5, 0, -1):
            print(f"  {i}...")
            time.sleep(1)

        # Stop recording
        print("\nStopping recording...")
        monitor.stop_recording(camera_index)

        # Get final status
        status = monitor.get_status(camera_index)
        print(f"\nFinal status:")
        print(f"  Streaming: {status['is_streaming']}")
        print(f"  Recording: {status['is_recording']}")

        # Cleanup happens automatically when exiting 'with' block
        print("\nExiting context - automatic cleanup will occur")

    print("✓ Cleanup complete!")


if __name__ == "__main__":
    main()
