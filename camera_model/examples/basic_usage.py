"""Basic usage example for Camera Monitor."""
from camera_monitor import CameraMonitor
import time


def main():
    """Basic example of camera monitoring."""
    # Create and initialize monitor
    monitor = CameraMonitor().initialize()

    # Get list of cameras
    cameras = monitor.get_cameras()
    print(f"\nFound {len(cameras)} camera(s)")

    if len(cameras) == 0:
        print("No cameras found!")
        return

    # Use first camera
    camera_index = 0

    # Start streaming
    print(f"\nStarting stream from camera {camera_index}...")
    if monitor.start_streaming(camera_index):
        print("✓ Streaming started")

    # Start recording
    print(f"\nStarting recording...")
    if monitor.start_recording(camera_index):
        print("✓ Recording started")

    # Record for 10 seconds
    print("\nRecording for 10 seconds...")
    time.sleep(10)

    # Stop recording
    print("\nStopping recording...")
    if monitor.stop_recording(camera_index):
        print("✓ Recording stopped")

    # Get status
    status = monitor.get_status(camera_index)
    print(f"\nCamera status: {status}")

    # Cleanup
    print("\nCleaning up...")
    monitor.cleanup()
    print("✓ Done!")


if __name__ == "__main__":
    main()
