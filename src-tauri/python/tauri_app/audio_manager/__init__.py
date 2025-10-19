"""
音频管理器包
提供麦克风和系统音频的实时监控功能
"""

from .core import AudioLevel
from .manager import AudioManager
from .microphone import MicrophoneMonitor
from .system_audio import SystemAudioMonitor
from .utils import list_audio_devices, format_db, create_progress_bar

__version__ = "1.0.0"
__author__ = "HwlloChen"

__all__ = [
    'AudioManager',
    'AudioLevel',
    'MicrophoneMonitor',
    'SystemAudioMonitor',
    'list_audio_devices',
    'format_db',
    'create_progress_bar'
]