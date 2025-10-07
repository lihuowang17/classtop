"""Hardware encoder detection using FFmpeg."""
import subprocess
from typing import List, Dict


class EncoderDetector:
    """Detects available hardware encoders."""

    def __init__(self):
        self.encoders = []

    def detect_encoders(self) -> List[Dict]:
        """Detect available hardware encoders (H.264 and H.265)."""
        encoders = []

        # Check for various hardware encoder types
        encoder_types = [
            # NVIDIA NVENC
            ("h264_nvenc", "H.264", "NVIDIA NVENC"),
            ("hevc_nvenc", "H.265", "NVIDIA NVENC"),
            # Intel QSV
            ("h264_qsv", "H.264", "Intel Quick Sync"),
            ("hevc_qsv", "H.265", "Intel Quick Sync"),
            # AMD AMF
            ("h264_amf", "H.264", "AMD AMF"),
            ("hevc_amf", "H.265", "AMD AMF"),
            # Software fallback
            ("libx264", "H.264", "Software (libx264)"),
            ("libx265", "H.265", "Software (libx265)"),
        ]

        for codec_name, codec_type, description in encoder_types:
            if self._check_encoder(codec_name):
                encoders.append({
                    "name": codec_name,
                    "type": codec_type,
                    "description": description,
                    "is_hardware": "nvenc" in codec_name or "qsv" in codec_name or "amf" in codec_name
                })

        self.encoders = encoders
        return encoders

    def _check_encoder(self, encoder_name: str) -> bool:
        """Check if a specific encoder is actually usable (not just listed)."""
        # First check if encoder is listed
        list_cmd = ["ffmpeg", "-hide_banner", "-encoders"]

        try:
            result = subprocess.run(
                list_cmd,
                capture_output=True,
                text=True,
                timeout=5
            )

            if encoder_name not in result.stdout:
                return False

        except Exception as e:
            print(f"Error listing encoders: {e}")
            return False

        # For software encoders, listing is enough
        if "lib" in encoder_name:
            return True

        # For hardware encoders, test if they actually work
        test_cmd = [
            "ffmpeg",
            "-f", "lavfi",
            "-i", "nullsrc=s=256x256:d=0.1",
            "-c:v", encoder_name,
            "-f", "null",
            "-"
        ]

        try:
            result = subprocess.run(
                test_cmd,
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )

            # Check if encoding succeeded (return code 0)
            # Also check stderr doesn't contain critical errors
            if result.returncode == 0:
                return True

            # Sometimes ffmpeg returns non-zero but still works
            # Check for specific error messages that indicate hardware not available
            error_indicators = [
                "Cannot load",
                "not available",
                "No capable devices",
                "Failed to",
                "does not support",
                "not supported"
            ]

            stderr_lower = result.stderr.lower()
            for indicator in error_indicators:
                if indicator.lower() in stderr_lower:
                    return False

            return False

        except subprocess.TimeoutExpired:
            return False
        except Exception as e:
            print(f"Error testing encoder {encoder_name}: {e}")
            return False

    def get_preferred_encoder(self, codec_type: str = "H.264") -> str:
        """Get the preferred encoder for a codec type (H.264 or H.265)."""
        # Priority: NVENC > QSV > AMF > Software
        priority = ["nvenc", "qsv", "amf", "lib"]

        matching_encoders = [
            e for e in self.encoders if e["type"] == codec_type
        ]

        for pref in priority:
            for encoder in matching_encoders:
                if pref in encoder["name"]:
                    return encoder["name"]

        # Fallback
        if matching_encoders:
            return matching_encoders[0]["name"]

        return "libx264" if codec_type == "H.264" else "libx265"

    def get_hardware_encoders(self) -> List[Dict]:
        """Get only hardware encoders."""
        return [e for e in self.encoders if e["is_hardware"]]

    def get_encoder_info(self) -> Dict:
        """Get summary of available encoders."""
        h264_encoders = [e for e in self.encoders if e["type"] == "H.264"]
        h265_encoders = [e for e in self.encoders if e["type"] == "H.265"]

        return {
            "h264": {
                "available": len(h264_encoders),
                "encoders": h264_encoders,
                "preferred": self.get_preferred_encoder("H.264")
            },
            "h265": {
                "available": len(h265_encoders),
                "encoders": h265_encoders,
                "preferred": self.get_preferred_encoder("H.265")
            }
        }
