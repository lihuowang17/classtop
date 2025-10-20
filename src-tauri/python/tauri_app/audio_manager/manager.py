"""
音频管理器主类
"""

from typing import Optional, Callable, Dict, List
from .core import AudioLevel
from .microphone import MicrophoneMonitor
from .system_audio import SystemAudioMonitor
from .utils import list_audio_devices


class AudioManager:
    """音频管理器主类"""

    def __init__(self,
                 mic_device_id: Optional[int] = None,
                 sample_rate: int = 44100,
                 block_size: int = 1024):
        """
        初始化音频管理器

        Args:
            mic_device_id: 麦克风设备ID
            sample_rate: 采样率
            block_size: 采样块大小
        """
        self.microphone_monitor = MicrophoneMonitor(
            device_id=mic_device_id,
            sample_rate=sample_rate,
            block_size=block_size
        )
        self.system_monitor = SystemAudioMonitor(
            sample_rate=sample_rate,
            block_size=block_size
        )

    def start_microphone_monitoring(self,
                                   callback: Optional[Callable[[AudioLevel], None]] = None):
        """
        启动麦克风监控

        Args:
            callback: 可选的响度更新回调函数
        """
        if callback:
            self.microphone_monitor.add_callback(callback)
        self.microphone_monitor.start()

    def start_system_monitoring(self,
                               callback: Optional[Callable[[AudioLevel], None]] = None):
        """
        启动系统音频监控

        Args:
            callback: 可选的响度更新回调函数
        """
        if callback:
            self.system_monitor.add_callback(callback)
        self.system_monitor.start()

    def start_all(self,
                  mic_callback: Optional[Callable[[AudioLevel], None]] = None,
                  sys_callback: Optional[Callable[[AudioLevel], None]] = None):
        """
        启动所有监控

        Args:
            mic_callback: 麦克风回调函数
            sys_callback: 系统音频回调函数
        """
        self.start_microphone_monitoring(mic_callback)
        self.start_system_monitoring(sys_callback)

    def stop_microphone_monitoring(self):
        """停止麦克风监控"""
        self.microphone_monitor.stop()

    def stop_system_monitoring(self):
        """停止系统音频监控"""
        self.system_monitor.stop()

    def stop_all(self):
        """停止所有监控"""
        self.stop_microphone_monitoring()
        self.stop_system_monitoring()

    def get_microphone_level(self) -> Optional[AudioLevel]:
        """获取当前麦克风响度"""
        return self.microphone_monitor.get_current_level()

    def get_system_level(self) -> Optional[AudioLevel]:
        """获取当前系统音频响度"""
        return self.system_monitor.get_current_level()

    @staticmethod
    def list_devices() -> Dict[str, List[Dict]]:
        """
        列出所有可用的音频设备

        Returns:
            包含输入和输出设备信息的字典
        """
        return list_audio_devices()

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.stop_all()
