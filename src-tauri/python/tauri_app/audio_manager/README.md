# Audio Manager

实时音频监控库，支持麦克风和系统音频的响度监控。

## 特性

- 🎤 麦克风音量监控
- 🔊 系统音频输出监控（使用Windows Core Audio API）
- 📊 实时响度计算（RMS, dB, Peak）
- 🔧 灵活的回调机制
- 🎯 简洁的API设计
- 📦 模块化结构

## 安装

```bash
pip install sounddevice numpy pycaw comtypes
```

## 快速开始

```python
from audio_manager import AudioManager

# 创建管理器
manager = AudioManager()

# 启动监控
manager.start_microphone_monitoring()
manager.start_system_monitoring()

# 获取当前响度
mic_level = manager.get_microphone_level()
sys_level = manager.get_system_level()

print(f"Microphone: {mic_level}")
print(f"System: {sys_level}")

# 停止监控
manager.stop_all()
```

## 使用回调

```python
def on_audio_update(level):
    print(f"dB: {level.db:.1f}, Peak: {level.peak:.3f}")

manager.start_microphone_monitoring(callback=on_audio_update)
```

## API文档

### AudioManager

主管理器类，提供统一接口。

#### 方法

- `start_microphone_monitoring(callback=None)` - 启动麦克风监控
- `start_system_monitoring(callback=None)` - 启动系统音频监控
- `start_all(mic_callback=None, sys_callback=None)` - 启动所有监控
- `stop_microphone_monitoring()` - 停止麦克风监控
- `stop_system_monitoring()` - 停止系统音频监控
- `stop_all()` - 停止所有监控
- `get_microphone_level()` - 获取当前麦克风响度
- `get_system_level()` - 获取当前系统响度
- `list_devices()` - 列出所有音频设备

### AudioLevel

音频响度数据类。

#### 属性

- `timestamp` - 时间戳
- `rms` - 均方根值 (0-1)
- `db` - 分贝值
- `peak` - 峰值 (0-1)

## 许可证

MIT License
"""
