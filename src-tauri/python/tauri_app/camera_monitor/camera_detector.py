"""Camera detection using DirectShow."""
import subprocess
from typing import List, Dict
from pygrabber.dshow_graph import FilterGraph


class CameraDetector:
    """Detects available cameras and their configurations."""

    def __init__(self):
        self.cameras = []

    def detect_cameras(self) -> List[Dict]:
        """Detect all available cameras using DirectShow."""
        graph = FilterGraph()
        devices = graph.get_input_devices()

        cameras = []
        for index, device_name in enumerate(devices):
            camera_info = {
                "index": index,
                "name": device_name,
                "resolutions": self._detect_resolutions(index)
            }
            cameras.append(camera_info)

        self.cameras = cameras
        return cameras

    def _detect_resolutions(self, camera_index: int) -> List[Dict]:
        """Detect available resolutions and FPS for a camera using FFmpeg."""
        resolutions = []

        # Use ffmpeg to list formats
        cmd = [
            "ffmpeg",
            "-f", "dshow",
            "-list_options", "true",
            "-i", f"video={self._get_camera_name(camera_index)}",
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )

            # Parse ffmpeg output
            output = result.stderr
            current_res = None

            for line in output.split('\n'):
                # Look for resolution lines like "1920x1080"
                if 'pixel_format=' in line or 'vcodec=' in line:
                    parts = line.strip().split()
                    for i, part in enumerate(parts):
                        if 's=' in part:
                            # Extract resolution
                            res_str = part.split('=')[1]
                            if 'x' in res_str:
                                width, height = res_str.split('x')
                                try:
                                    current_res = {
                                        "width": int(width),
                                        "height": int(height),
                                        "fps": []
                                    }
                                except ValueError:
                                    continue

                        if 'fps=' in part and current_res:
                            # Extract FPS
                            fps_str = part.split('=')[1]
                            try:
                                fps = float(fps_str)
                                if fps not in current_res["fps"]:
                                    current_res["fps"].append(fps)
                            except ValueError:
                                continue

                    # Add resolution if we have complete info
                    if current_res and current_res["fps"]:
                        # Check if this resolution already exists
                        existing = next(
                            (r for r in resolutions
                             if r["width"] == current_res["width"]
                             and r["height"] == current_res["height"]),
                            None
                        )
                        if existing:
                            # Merge FPS values
                            for fps in current_res["fps"]:
                                if fps not in existing["fps"]:
                                    existing["fps"].append(fps)
                        else:
                            resolutions.append(current_res.copy())
                        current_res = None

            # If no resolutions detected, add common defaults
            if not resolutions:
                resolutions = [
                    {"width": 1920, "height": 1080, "fps": [30.0]},
                    {"width": 1280, "height": 720, "fps": [30.0]},
                    {"width": 640, "height": 480, "fps": [30.0]},
                ]

        except subprocess.TimeoutExpired:
            # Fallback to common resolutions
            resolutions = [
                {"width": 1920, "height": 1080, "fps": [30.0]},
                {"width": 1280, "height": 720, "fps": [30.0]},
                {"width": 640, "height": 480, "fps": [30.0]},
            ]
        except Exception as e:
            print(f"Error detecting resolutions for camera {camera_index}: {e}")
            resolutions = [
                {"width": 1920, "height": 1080, "fps": [30.0]},
                {"width": 1280, "height": 720, "fps": [30.0]},
            ]

        return resolutions

    def _get_camera_name(self, camera_index: int) -> str:
        """Get camera name by index."""
        graph = FilterGraph()
        devices = graph.get_input_devices()
        if camera_index < len(devices):
            return devices[camera_index]
        return ""

    def get_camera_info(self, camera_index: int) -> Dict:
        """Get information for a specific camera."""
        if camera_index < len(self.cameras):
            return self.cameras[camera_index]
        return {}
