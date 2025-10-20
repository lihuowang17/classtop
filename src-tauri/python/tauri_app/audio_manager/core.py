"""
核心数据类和基类
"""

import numpy as np
from typing import Callable, Optional, List
from threading import Thread, Event
from dataclasses import dataclass
from datetime import datetime
import time


@dataclass
class AudioLevel:
    """音频响度数据类"""
    timestamp: datetime
    rms: float  # 均方根值 (0-1)
    db: float   # 分贝值
    peak: float # 峰值 (0-1)
    
    def __str__(self):
        db_str = f"{self.db:.1f}" if self.db > -100 else "-∞"
        return f"AudioLevel(rms={self.rms:.4f}, db={db_str}, peak={self.peak:.4f})"


class AudioMonitor:
    """音频监控基类"""
    
    def __init__(self, device_id: Optional[int] = None, 
                 sample_rate: int = 44100,
                 block_size: int = 1024,
                 channels: int = 1):
        """
        初始化音频监控器
        
        Args:
            device_id: 设备ID，None表示使用默认设备
            sample_rate: 采样率 (Hz)
            block_size: 每次处理的采样块大小
            channels: 声道数
        """
        self.device_id = device_id
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.channels = channels
        
        self.is_running = False
        self._stop_event = Event()
        self._monitor_thread: Optional[Thread] = None
        self._callbacks: List[Callable[[AudioLevel], None]] = []
        
        # 当前音频数据
        self.current_level: Optional[AudioLevel] = None
    
    def add_callback(self, callback: Callable[[AudioLevel], None]):
        """添加响度更新回调函数"""
        if callback not in self._callbacks:
            self._callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[AudioLevel], None]):
        """移除回调函数"""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def clear_callbacks(self):
        """清除所有回调函数"""
        self._callbacks.clear()
    
    def _calculate_level(self, audio_data: np.ndarray) -> AudioLevel:
        """
        计算音频响度

        Args:
            audio_data: 音频数据数组

        Returns:
            AudioLevel对象
        """
        # 计算RMS (均方根)
        rms = np.sqrt(np.mean(audio_data**2))

        # 计算分贝值 (参考值: 1.0)
        # 使用 -100 dB 作为静音值（数字音频的实际下限）
        # 避免使用 -np.inf 因为它在 JSON 序列化时会变成 null
        if rms > 0:
            db = 20 * np.log10(rms)
            # 限制最小值为 -100 dB
            db = max(db, -100.0)
        else:
            db = -100.0

        # 计算峰值
        peak = np.max(np.abs(audio_data))

        return AudioLevel(
            timestamp=datetime.now(),
            rms=float(rms),
            db=float(db),
            peak=float(peak)
        )
    
    def _notify_callbacks(self, level: AudioLevel):
        """通知所有回调函数"""
        for callback in self._callbacks:
            try:
                callback(level)
            except Exception as e:
                print(f"回调函数执行错误: {e}")
    
    def get_current_level(self) -> Optional[AudioLevel]:
        """获取当前音频响度"""
        return self.current_level
    
    def start(self):
        """启动监控"""
        raise NotImplementedError("子类必须实现start方法")
    
    def stop(self):
        """停止监控"""
        if self.is_running:
            self.is_running = False
            self._stop_event.set()
            if self._monitor_thread:
                self._monitor_thread.join(timeout=2.0)
    
    def __enter__(self):
        """上下文管理器入口"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.stop()