"""Configuration classes for Camera Monitor."""
from dataclasses import dataclass, field
from typing import Optional, Tuple


@dataclass
class CameraConfig:
    """Configuration for camera capture."""

    # Video settings
    width: int = 1280
    height: int = 1080
    fps: int = 30

    # Preferred encoder (None = auto-detect best)
    encoder: Optional[str] = None

    # Encoder type preference: 'hardware' or 'software'
    encoder_preference: str = 'hardware'

    def __post_init__(self):
        """Validate configuration."""
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Width and height must be positive")
        if self.fps <= 0:
            raise ValueError("FPS must be positive")
        if self.encoder_preference not in ('hardware', 'software'):
            raise ValueError("encoder_preference must be 'hardware' or 'software'")


@dataclass
class EncoderConfig:
    """Configuration for video encoding."""

    # NVENC settings
    nvenc_preset: str = 'fast'  # ultrafast, superfast, fast, medium, slow
    nvenc_bitrate: str = '5M'

    # QSV settings
    qsv_preset: str = 'medium'  # veryfast, faster, fast, medium, slow, slower, veryslow
    qsv_bitrate: str = '5M'

    # AMF settings
    amf_quality: str = 'balanced'  # speed, balanced, quality
    amf_bitrate: str = '5M'

    # Software encoder settings (libx264/libx265)
    software_preset: str = 'medium'  # ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow
    software_crf: int = 23  # 0-51, lower = better quality

    # General settings
    pixel_format: str = 'yuv420p'

    def __post_init__(self):
        """Validate configuration."""
        valid_nvenc_presets = ['ultrafast', 'superfast', 'fast', 'medium', 'slow']
        if self.nvenc_preset not in valid_nvenc_presets:
            raise ValueError(f"nvenc_preset must be one of {valid_nvenc_presets}")

        if self.software_crf < 0 or self.software_crf > 51:
            raise ValueError("software_crf must be between 0 and 51")


@dataclass
class RecordingConfig:
    """Configuration for video recording."""

    # Output directory
    output_dir: str = 'recordings'

    # Output format
    format: str = 'mp4'

    # Filename pattern (strftime compatible)
    filename_pattern: str = 'recording_%Y%m%d_%H%M%S'

    # Auto-create output directory
    create_dir: bool = True


@dataclass
class RecordingOptions:
    """Runtime options for individual recordings."""

    # Codec selection
    codec_type: Optional[str] = None  # 'H.264', 'H.265', or None (use default)

    # Specific encoder override
    encoder: Optional[str] = None  # e.g., 'h264_nvenc', 'libx264'

    # Resolution override
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[int] = None

    # Encoding parameters override
    preset: Optional[str] = None  # Encoder preset
    bitrate: Optional[str] = None  # e.g., '5M', '10M'
    crf: Optional[int] = None  # For software encoders (0-51)

    # Pixel format override
    pixel_format: Optional[str] = None

    # Output filename
    filename: Optional[str] = None

    # Custom FFmpeg arguments (advanced)
    custom_args: Optional[list] = None

    def __post_init__(self):
        """Validate options."""
        if self.codec_type and self.codec_type not in ['H.264', 'H.265']:
            raise ValueError("codec_type must be 'H.264' or 'H.265'")

        if self.crf is not None and (self.crf < 0 or self.crf > 51):
            raise ValueError("crf must be between 0 and 51")

        if self.width is not None and self.width <= 0:
            raise ValueError("width must be positive")

        if self.height is not None and self.height <= 0:
            raise ValueError("height must be positive")

        if self.fps is not None and self.fps <= 0:
            raise ValueError("fps must be positive")


@dataclass
class StreamingConfig:
    """Configuration for video streaming."""

    # JPEG quality for MJPEG streaming (1-100)
    jpeg_quality: int = 80

    # Frame rate for streaming (can be different from capture fps)
    stream_fps: Optional[int] = None  # None = same as camera fps

    def __post_init__(self):
        """Validate configuration."""
        if self.jpeg_quality < 1 or self.jpeg_quality > 100:
            raise ValueError("jpeg_quality must be between 1 and 100")


@dataclass
class APIConfig:
    """Configuration for HTTP API server."""

    # Server settings
    host: str = '0.0.0.0'
    port: int = 8888

    # Enable/disable API
    enabled: bool = True

    # CORS settings
    cors_enabled: bool = True
    cors_origins: list = field(default_factory=lambda: ['*'])

    # Auto-start server
    auto_start: bool = True

    def __post_init__(self):
        """Validate configuration."""
        if self.port < 1 or self.port > 65535:
            raise ValueError("port must be between 1 and 65535")


@dataclass
class MonitorConfig:
    """Main configuration for Camera Monitor."""

    camera: CameraConfig = field(default_factory=CameraConfig)
    encoder: EncoderConfig = field(default_factory=EncoderConfig)
    recording: RecordingConfig = field(default_factory=RecordingConfig)
    streaming: StreamingConfig = field(default_factory=StreamingConfig)
    api: APIConfig = field(default_factory=APIConfig)

    # Debug settings
    debug: bool = False
    verbose_logging: bool = True

    @classmethod
    def create_default(cls) -> 'MonitorConfig':
        """Create default configuration."""
        return cls()

    @classmethod
    def create_high_quality(cls) -> 'MonitorConfig':
        """Create high quality configuration."""
        config = cls()
        config.camera.width = 1920
        config.camera.height = 1080
        config.camera.fps = 30
        config.encoder.software_crf = 18
        config.streaming.jpeg_quality = 95
        return config

    @classmethod
    def create_low_latency(cls) -> 'MonitorConfig':
        """Create low latency configuration."""
        config = cls()
        config.camera.width = 1280
        config.camera.height = 720
        config.camera.fps = 60
        config.encoder.nvenc_preset = 'ultrafast'
        config.streaming.jpeg_quality = 70
        return config

    @classmethod
    def create_low_resource(cls) -> 'MonitorConfig':
        """Create low resource configuration."""
        config = cls()
        config.camera.width = 640
        config.camera.height = 480
        config.camera.fps = 15
        config.encoder.encoder_preference = 'software'
        config.streaming.jpeg_quality = 60
        return config
