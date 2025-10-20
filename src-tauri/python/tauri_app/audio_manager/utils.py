"""
工具函数
"""

import sounddevice as sd
import numpy as np
from typing import Dict, List


def list_audio_devices() -> Dict[str, List[Dict]]:
    """
    列出所有可用的音频设备
    
    Returns:
        包含输入和输出设备信息的字典
    """
    devices = sd.query_devices()
    input_devices = []
    output_devices = []
    
    for i, device in enumerate(devices):
        device_info = {
            'id': i,
            'name': device['name'],
            'channels': device['max_input_channels'] if device['max_input_channels'] > 0 
                       else device['max_output_channels'],
            'sample_rate': device['default_samplerate']
        }
        
        if device['max_input_channels'] > 0:
            input_devices.append(device_info)
        if device['max_output_channels'] > 0:
            output_devices.append(device_info)
    
    return {
        'input': input_devices,
        'output': output_devices
    }


def format_db(db: float, precision: int = 1) -> str:
    """
    格式化分贝值显示
    
    Args:
        db: 分贝值
        precision: 小数精度
        
    Returns:
        格式化的字符串
    """
    if db == -np.inf:
        return "-inf"
    return f"{db:.{precision}f}"


def create_progress_bar(value: float, width: int = 20, 
                       filled_char: str = '█', 
                       empty_char: str = '░') -> str:
    """
    创建文本进度条
    
    Args:
        value: 值 (0.0-1.0)
        width: 进度条宽度
        filled_char: 填充字符
        empty_char: 空白字符
        
    Returns:
        进度条字符串
    """
    value = max(0.0, min(1.0, value))  # 限制在0-1之间
    filled = int(value * width)
    return filled_char * filled + empty_char * (width - filled)


def db_to_linear(db: float) -> float:
    """
    将分贝值转换为线性值
    
    Args:
        db: 分贝值
        
    Returns:
        线性值 (0.0-1.0)
    """
    if db == -np.inf:
        return 0.0
    return 10 ** (db / 20)


def linear_to_db(linear: float) -> float:
    """
    将线性值转换为分贝值
    
    Args:
        linear: 线性值 (0.0-1.0)
        
    Returns:
        分贝值
    """
    if linear <= 0:
        return -np.inf
    return 20 * np.log10(linear)
