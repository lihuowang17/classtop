# Audio Manager 集成文档

本文档说明如何在 ClassTop 中集成和使用 AudioManager 进行实时音频监控。

## 架构概览

### 后端 (Python)

1. **AudioManager** (`audio_manager/manager.py`)
   - 管理麦克风和系统音频监控
   - 提供回调机制实时获取音频数据

2. **Command Handlers** (`commands.py`)
   - `start_audio_monitoring`: 启动监控并创建 Channel
   - `stop_audio_monitoring`: 停止监控
   - `get_audio_devices`: 获取可用音频设备列表

3. **Channel 通信**
   - 使用 PyTauri 的 `Channel` 实现实时数据传输
   - `AudioLevelData` Pydantic 模型定义数据结构

### 前端 (Vue 3)

1. **AudioMonitor.vue** (`src/pages/AudioMonitor.vue`)
   - 音频监控 UI 界面
   - 实时显示音量数据和可视化进度条
   - 控制启动/停止监控

2. **Router 配置** (`src/router/index.js`)
   - 路由路径: `/audio`
   - 导航菜单: "音量监控"

## 数据流

```
Vue 前端
  ↓ pyInvoke('start_audio_monitoring', { monitor_type, channel_id })
Python Command Handler
  ↓ 创建 Channel(channel_id)
  ↓ AudioManager.start_xxx_monitoring(callback)
Audio Monitor (后台线程)
  ↓ 采集音频数据
  ↓ callback(AudioLevel)
  ↓ channel.send_model(AudioLevelData)
Vue 前端 Channel.onmessage
  ↓ 更新 UI 显示
```

## 使用方法

### 1. 启动应用

```bash
npm run tauri dev
```

### 2. 访问音量监控页面

在主窗口导航栏点击 "音量监控" 或访问 `/#/audio`

### 3. 启动监控

点击 "Start Microphone" 或 "Start System Audio" 按钮

### 4. 查看实时数据

- **RMS**: 均方根值 (0-1)
- **dB**: 分贝值 (通常 -60 到 0)
- **Peak**: 峰值 (0-1)
- **进度条**: 实时可视化 Peak 值

### 5. 停止监控

点击 "Stop All" 按钮或关闭页面时自动停止

## API 参考

### Python Commands

#### `start_audio_monitoring`

启动音频监控并通过 Channel 实时传输数据。

**请求:**
```python
{
    "monitor_type": "microphone" | "system" | "both",
    "channel_id": JavaScriptChannelId[AudioLevelData]
}
```

**响应:**
```python
{
    "success": bool,
    "message": str
}
```

#### `stop_audio_monitoring`

停止音频监控。

**请求:**
```python
{
    "monitor_type": "microphone" | "system" | "all"
}
```

**响应:**
```python
{
    "success": bool,
    "message": str
}
```

#### `get_audio_devices`

获取所有可用的音频设备。

**响应:**
```python
{
    "input_devices": List[Dict],
    "output_devices": List[Dict]
}
```

### JavaScript (Vue)

#### 创建 Channel 并监听数据

```javascript
import { Channel } from '@tauri-apps/api/core';
import { pyInvoke } from 'tauri-plugin-pytauri-api';

// 创建 Channel
const channel = new Channel();

// 监听数据
const unlisten = await channel.onmessage((data) => {
  console.log('Audio level:', data);
  // data: { timestamp, rms, db, peak }
});

// 启动监控
await pyInvoke('start_audio_monitoring', {
  monitor_type: 'microphone',
  channel_id: channel.id
});

// 停止监控
await pyInvoke('stop_audio_monitoring', {
  monitor_type: 'all'
});

// 清理
unlisten();
```

## 数据模型

### AudioLevelData (Pydantic)

```python
class AudioLevelData(BaseModel):
    timestamp: str  # ISO format datetime string
    rms: float      # 均方根值 (0-1)
    db: float       # 分贝值
    peak: float     # 峰值 (0-1)
```

### AudioLevel (Python 内部)

```python
@dataclass
class AudioLevel:
    timestamp: datetime
    rms: float  # 均方根值 (0-1)
    db: float   # 分贝值
    peak: float # 峰值 (0-1)
```

## 注意事项

1. **依赖项**: 需要安装 `sounddevice`, `numpy`, `pycaw`, `comtypes`
2. **系统音频监控**: 仅支持 Windows (使用 Core Audio API)
3. **麦克风监控**: 跨平台支持
4. **权限**: 首次使用可能需要授予麦克风权限
5. **性能**: Channel 默认实时传输，高频数据可能影响性能
6. **清理**: 页面关闭时自动停止监控并清理资源

## 故障排除

### 问题: AudioManager 初始化失败

**解决方案:**
1. 检查依赖项是否安装: `pip list | grep -E "sounddevice|numpy|pycaw"`
2. 查看日志: 使用 `get_logs` 命令查看错误信息
3. 非 Windows 系统系统音频监控不可用

### 问题: Channel 没有接收到数据

**解决方案:**
1. 确认监控已启动: 检查返回的 `success` 字段
2. 检查麦克风/系统音频是否有声音输入
3. 查看浏览器控制台错误信息
4. 检查 Channel ID 是否正确传递

### 问题: 系统音频监控不工作

**解决方案:**
1. 确认运行在 Windows 系统
2. 确认系统正在播放音频
3. 检查 Windows 音频服务是否正常
4. 尝试重启应用

## 扩展开发

### 添加音频设备选择

修改 `AudioManager.__init__()` 添加设备参数:

```python
audio_manager = AudioManager(mic_device_id=1)  # 使用设备 ID 1
```

### 调整采样参数

```python
audio_manager = AudioManager(
    sample_rate=48000,  # 提高采样率
    block_size=512      # 减小块大小以降低延迟
)
```

### 添加音频处理

在 callback 中添加自定义处理:

```python
def custom_callback(level):
    if level.peak > 0.8:
        # 触发警告
        print("Volume too high!")
    # 发送到 Channel
    channel.send_model(AudioLevelData(...))
```

## 参考资源

- [PyTauri Channel 文档](https://pytauri.github.io/pytauri/dev/reference/py/pytauri/ipc/)
- [Audio Manager README](README.md)
- [sounddevice 文档](https://python-sounddevice.readthedocs.io/)
- [pycaw 文档](https://github.com/AndreMiras/pycaw)
