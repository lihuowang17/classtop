"""Example with HTTP API server."""
import sys
sys.path.insert(0, '..')

from camera_monitor import CameraMonitor, MonitorConfig
from camera_monitor import api_server
import uvicorn
import threading


def main():
    """Example with HTTP API server."""

    print("Camera Monitor - HTTP API Server Example")
    print("="*60)

    # Create configuration with API enabled
    config = MonitorConfig()
    config.api.enabled = True
    config.api.host = '0.0.0.0'
    config.api.port = 8888
    config.verbose_logging = True

    # Create and initialize monitor
    monitor = CameraMonitor(config).initialize()

    # Initialize API server with monitor components
    api_server.initialize(monitor.camera_detector, monitor.encoder_detector)

    # Store active streamers reference in API server
    api_server.active_streamers = monitor.streamers

    print("\n" + "="*60)
    print("✅ Camera Monitor initialized!")
    print("\n🌐 Starting HTTP API server...")
    print(f"   API URL: http://localhost:{config.api.port}")
    print(f"   Web View: http://localhost:{config.api.port}/view")
    print(f"   API Docs: http://localhost:{config.api.port}/docs")
    print("\nPress Ctrl+C to stop")
    print("="*60 + "\n")

    try:
        # Start API server
        uvicorn.run(
            api_server.app,
            host=config.api.host,
            port=config.api.port,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
        monitor.cleanup()
        print("✅ Cleanup complete. Goodbye!")


if __name__ == "__main__":
    main()
