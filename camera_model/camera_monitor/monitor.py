"""Main CameraMonitor class."""
from typing import Optional, List, Dict
import threading
from .config import MonitorConfig, RecordingOptions
from .camera_detector import CameraDetector
from .encoder_detector import EncoderDetector
from .video_streamer import VideoStreamer


class CameraMonitor:
    """Main camera monitoring class with flexible configuration."""

    def __init__(self, config: Optional[MonitorConfig] = None):
        """Initialize Camera Monitor.

        Args:
            config: Configuration object. If None, uses default configuration.
        """
        self.config = config or MonitorConfig.create_default()
        self.camera_detector = CameraDetector()
        self.encoder_detector = EncoderDetector()
        self.streamers: Dict[int, VideoStreamer] = {}
        self._initialized = False

    def initialize(self) -> 'CameraMonitor':
        """Initialize the monitor by detecting cameras and encoders.

        Returns:
            Self for method chaining.
        """
        if self.config.verbose_logging:
            print("🔍 Initializing Camera Monitor...")

        # Detect cameras
        if self.config.verbose_logging:
            print("📹 Detecting cameras...")
        self.cameras = self.camera_detector.detect_cameras()

        if self.config.verbose_logging:
            self._print_cameras()

        # Detect encoders
        if self.config.verbose_logging:
            print("🎬 Detecting hardware encoders...")
        self.encoders = self.encoder_detector.detect_encoders()
        self.encoder_info = self.encoder_detector.get_encoder_info()

        if self.config.verbose_logging:
            self._print_encoders()

        self._initialized = True
        return self

    def get_cameras(self) -> List[Dict]:
        """Get list of detected cameras.

        Returns:
            List of camera information dictionaries.
        """
        self._ensure_initialized()
        return self.cameras

    def get_encoders(self) -> Dict:
        """Get information about available encoders.

        Returns:
            Dictionary with encoder information.
        """
        self._ensure_initialized()
        return self.encoder_info

    def get_streamer(self, camera_index: int) -> VideoStreamer:
        """Get or create a video streamer for a camera.

        Args:
            camera_index: Index of the camera.

        Returns:
            VideoStreamer instance for the camera.

        Raises:
            IndexError: If camera index is invalid.
        """
        self._ensure_initialized()

        if camera_index >= len(self.cameras):
            raise IndexError(f"Camera index {camera_index} out of range. Available: 0-{len(self.cameras)-1}")

        if camera_index not in self.streamers:
            camera = self.cameras[camera_index]

            # Determine encoder to use
            encoder = self.config.camera.encoder
            if not encoder:
                # Auto-select based on preference
                if self.config.camera.encoder_preference == 'hardware':
                    encoder = self.encoder_detector.get_preferred_encoder("H.264")
                else:
                    encoder = "libx264"

            streamer = VideoStreamer(
                camera_name=camera["name"],
                camera_index=camera_index,
                encoder=encoder,
                config=self.config
            )

            self.streamers[camera_index] = streamer

        return self.streamers[camera_index]

    def start_streaming(self, camera_index: int) -> bool:
        """Start streaming from a camera.

        Args:
            camera_index: Index of the camera.

        Returns:
            True if successful, False otherwise.
        """
        streamer = self.get_streamer(camera_index)
        return streamer.start_streaming()

    def stop_streaming(self, camera_index: int) -> bool:
        """Stop streaming from a camera.

        Args:
            camera_index: Index of the camera.

        Returns:
            True if successful, False otherwise.
        """
        if camera_index not in self.streamers:
            return True

        streamer = self.streamers[camera_index]
        return streamer.stop_streaming()

    def start_recording(
        self,
        camera_index: int,
        filename: Optional[str] = None,
        options: Optional[RecordingOptions] = None
    ) -> bool:
        """Start recording from a camera.

        Args:
            camera_index: Index of the camera.
            filename: Optional custom filename for the recording.
            options: Optional recording options for customizing this recording.

        Returns:
            True if successful, False otherwise.

        Example:
            # Record with H.265 codec
            opts = RecordingOptions(codec_type='H.265')
            monitor.start_recording(0, options=opts)

            # Record with custom resolution and bitrate
            opts = RecordingOptions(width=1920, height=1080, bitrate='10M')
            monitor.start_recording(0, options=opts)
        """
        streamer = self.get_streamer(camera_index)
        return streamer.start_recording(filename, options)

    def stop_recording(self, camera_index: int) -> bool:
        """Stop recording from a camera.

        Args:
            camera_index: Index of the camera.

        Returns:
            True if successful, False otherwise.
        """
        if camera_index not in self.streamers:
            return True

        streamer = self.streamers[camera_index]
        return streamer.stop_recording()

    def get_status(self, camera_index: Optional[int] = None) -> Dict:
        """Get status of camera(s).

        Args:
            camera_index: Index of specific camera, or None for all cameras.

        Returns:
            Status dictionary.
        """
        if camera_index is not None:
            if camera_index not in self.streamers:
                return {
                    "camera_index": camera_index,
                    "status": "inactive"
                }
            return self.streamers[camera_index].get_status()
        else:
            # Return status of all active streamers
            return {
                "active_cameras": len(self.streamers),
                "streamers": {idx: streamer.get_status() for idx, streamer in self.streamers.items()}
            }

    def cleanup(self):
        """Clean up all resources."""
        for streamer in self.streamers.values():
            streamer.cleanup()
        self.streamers.clear()

    def _ensure_initialized(self):
        """Ensure monitor is initialized."""
        if not self._initialized:
            raise RuntimeError("CameraMonitor not initialized. Call initialize() first.")

    def _print_cameras(self):
        """Print detected cameras."""
        print(f"\n📹 Detected {len(self.cameras)} camera(s):")
        print("-" * 60)
        for cam in self.cameras:
            print(f"  [{cam['index']}] {cam['name']}")
            print(f"      Available resolutions:")
            for res in cam['resolutions'][:5]:  # Show first 5
                fps_str = ", ".join([f"{fps:.0f}" for fps in res['fps']])
                print(f"        - {res['width']}x{res['height']} @ {fps_str} fps")
        print()

    def _print_encoders(self):
        """Print detected encoders."""
        print("\n🎬 Hardware Encoder Detection:")
        print("-" * 60)

        # H.264
        print(f"  H.264 Encoders ({self.encoder_info['h264']['available']} available):")
        for enc in self.encoder_info['h264']['encoders']:
            hw_mark = "✓ HW" if enc['is_hardware'] else "  SW"
            print(f"    {hw_mark} {enc['name']:<15} - {enc['description']}")
        print(f"    Preferred: {self.encoder_info['h264']['preferred']}")

        print()

        # H.265
        print(f"  H.265 Encoders ({self.encoder_info['h265']['available']} available):")
        for enc in self.encoder_info['h265']['encoders']:
            hw_mark = "✓ HW" if enc['is_hardware'] else "  SW"
            print(f"    {hw_mark} {enc['name']:<15} - {enc['description']}")
        print(f"    Preferred: {self.encoder_info['h265']['preferred']}")

        print()

    def __enter__(self):
        """Context manager entry."""
        return self.initialize()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()
