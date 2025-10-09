# Camera Monitor Integration

摄像头监控模块已成功集成到 ClassTop 项目中。

## 📦 集成内容

### 1. 模块文件
已将 `camera_monitor` 模块复制到 `src-tauri/python/tauri_app/camera_monitor/`：

```
src-tauri/python/tauri_app/camera_monitor/
├── __init__.py              # 模块导出
├── config.py                # 配置类
├── monitor.py               # 主监控类
├── camera_detector.py       # 摄像头检测
├── encoder_detector.py      # 编码器检测
└── video_streamer.py        # 视频流和录制
```

**注意**：已移除 `api_server.py`，因为 ClassTop 已有自己的 API 系统。

### 2. 管理器 (camera_manager.py)
创建了 `CameraManager` 类，负责：
- 从 SettingsManager 加载配置
- 初始化摄像头系统
- 管理录制操作
- 发送事件通知

### 3. 设置项
在 `SettingsManager.DEFAULT_SETTINGS` 中添加了以下设置：

```python
# 摄像头设置
'camera_enabled': 'false',              # 是否启用摄像头功能
'camera_width': '1280',                 # 默认视频宽度
'camera_height': '720',                 # 默认视频高度
'camera_fps': '30',                     # 默认帧率
'camera_encoder_preference': 'hardware', # 编码器偏好

# 编码器设置
'encoder_nvenc_preset': 'fast',         # NVENC 预设
'encoder_nvenc_bitrate': '5M',          # NVENC 比特率

# 录制设置
'recording_output_dir': 'recordings',   # 录制文件输出目录
'recording_filename_pattern': 'recording_%Y%m%d_%H%M%S',  # 文件名模式
```

### 4. Python 命令
在 `commands.py` 中添加了 6 个新命令：

| 命令 | 功能 | 参数 |
|------|------|------|
| `initialize_camera` | 初始化摄像头系统 | 无 |
| `get_cameras` | 获取摄像头列表 | 无 |
| `get_camera_encoders` | 获取编码器信息 | 无 |
| `start_camera_recording` | 开始录制 | camera_index, filename, codec_type, width, height, fps, preset, bitrate |
| `stop_camera_recording` | 停止录制 | camera_index |
| `get_camera_status` | 获取状态 | camera_index (可选) |

### 5. 事件
在 `events.py` 中添加了 3 个事件：

- `camera-initialized` - 摄像头系统初始化完成
- `camera-recording-started` - 录制开始
- `camera-recording-stopped` - 录制停止

### 6. 依赖
在 `pyproject.toml` 中添加了依赖：

```toml
"pygrabber",      # DirectShow 摄像头检测
"opencv-python",  # 视频处理
```

## 🚀 使用方法

### 1. 启用摄像头功能

通过设置启用摄像头：

```python
# 前端调用
await pyInvoke('set_setting', {
    key: 'camera_enabled',
    value: 'true'
})
```

然后重启应用以加载 CameraManager。

### 2. 初始化摄像头系统

```python
# 前端调用
const result = await pyInvoke('initialize_camera', {})
// result: { success: true, camera_count: 1, message: "..." }
```

### 3. 获取摄像头列表

```python
const cameras = await pyInvoke('get_cameras', {})
// cameras: { cameras: [{ index: 0, name: "USB2.0 HD UVC WebCam", resolutions: [...] }] }
```

### 4. 开始录制

#### 简单录制（使用默认设置）
```python
const result = await pyInvoke('start_camera_recording', {
    camera_index: 0
})
```

#### 自定义录制（H.265 编码）
```python
const result = await pyInvoke('start_camera_recording', {
    camera_index: 0,
    codec_type: 'H.265',
    width: 1920,
    height: 1080,
    preset: 'slow',
    bitrate: '15M'
})
```

### 5. 停止录制

```python
const result = await pyInvoke('stop_camera_recording', {
    camera_index: 0
})
```

### 6. 获取状态

```python
const status = await pyInvoke('get_camera_status', {
    camera_index: 0  // 可选，不传则获取所有摄像头状态
})
```

## 📝 配置示例

### 修改摄像头默认设置

```python
# 设置默认分辨率
await pyInvoke('set_setting', { key: 'camera_width', value: '1920' })
await pyInvoke('set_setting', { key: 'camera_height', value: '1080' })

# 设置编码器参数
await pyInvoke('set_setting', { key: 'encoder_nvenc_preset', value: 'slow' })
await pyInvoke('set_setting', { key: 'encoder_nvenc_bitrate', value: '10M' })

// 重启应用生效
```

## 🎯 核心功能

### 1. 自动硬件编码器检测
系统会自动检测并测试可用的硬件编码器：
- NVIDIA NVENC (h264_nvenc, hevc_nvenc)
- Intel QSV (h264_qsv, hevc_qsv)
- AMD AMF (h264_amf, hevc_amf)
- 软件编码 (libx264, libx265)

### 2. 灵活的编码选项
每次录制都可以指定不同的参数：
- **codec_type**: 'H.264' 或 'H.265'
- **encoder**: 具体编码器名称
- **width/height/fps**: 分辨率和帧率
- **preset**: 编码速度预设
- **bitrate**: 比特率
- **filename**: 自定义文件名

### 3. 事件通知
录制操作会发送事件到前端，可用于：
- 显示录制状态
- 更新 UI
- 记录日志

## 🔧 技术细节

### 初始化流程

```
1. 应用启动
   ↓
2. SettingsManager 初始化
   ↓
3. 检查 camera_enabled 设置
   ↓
4. 如果启用，创建 CameraManager
   ↓
5. 前端调用 initialize_camera 命令
   ↓
6. CameraManager 初始化摄像头系统
   ↓
7. 检测摄像头和编码器
   ↓
8. 发送 camera-initialized 事件
```

### 录制流程

```
1. 前端调用 start_camera_recording
   ↓
2. CameraManager.start_recording()
   ↓
3. 创建 RecordingOptions (如果有自定义参数)
   ↓
4. CameraMonitor.start_recording()
   ↓
5. VideoStreamer 启动 FFmpeg 进程
   ↓
6. 发送 camera-recording-started 事件
   ↓
7. FFmpeg 持续录制到文件
   ↓
8. 前端调用 stop_camera_recording
   ↓
9. VideoStreamer 停止 FFmpeg 进程
   ↓
10. 发送 camera-recording-stopped 事件
```

### 配置加载

CameraManager 从 SettingsManager 读取配置并创建 MonitorConfig：

```python
config = MonitorConfig()
config.camera.width = int(settings_manager.get_setting('camera_width'))
config.camera.height = int(settings_manager.get_setting('camera_height'))
config.camera.fps = int(settings_manager.get_setting('camera_fps'))
config.encoder.nvenc_preset = settings_manager.get_setting('encoder_nvenc_preset')
# ... etc
```

## 🎨 前端集成建议

### 1. 设置页面
添加摄像头设置选项：
- 启用/禁用摄像头
- 选择默认分辨率
- 选择编码器偏好
- 设置录制输出目录

### 2. 录制控制界面
创建录制控制组件：
- 摄像头选择下拉框
- 开始/停止录制按钮
- 录制状态指示器
- 实时录制时长显示

### 3. 高级选项对话框
提供高级录制选项：
- 编码类型选择 (H.264/H.265)
- 分辨率和帧率选择
- 编码质量预设
- 比特率设置

### 4. 录制历史
显示录制文件列表：
- 文件名、大小、时长
- 打开文件位置
- 播放录制文件

## 📋 待办事项

- [ ] 前端 UI 实现
- [ ] 录制文件管理界面
- [ ] 实时预览功能（可选）
- [ ] 录制质量统计
- [ ] 自动录制功能

## 🐛 故障排除

### 摄像头未检测到
1. 确认摄像头已连接
2. 检查其他程序是否占用摄像头
3. 查看日志：`await pyInvoke('get_logs', { max_lines: 200 })`

### 录制失败
1. 检查 FFmpeg 是否安装
2. 验证硬件编码器是否可用
3. 尝试使用软件编码器
4. 查看详细日志

### 编码器不可用
1. 更新 GPU 驱动
2. 确认 GPU 支持硬件编码
3. 使用软件编码器作为后备

## 📚 参考文档

- 原始 camera_monitor 文档：`camera/README.md`
- 录制选项指南：`camera/RECORDING_OPTIONS.md`
- 自定义配置指南：`camera/CUSTOMIZATION_GUIDE.md`
- 项目概览：`camera/PROJECT_OVERVIEW.md`

## ✅ 集成清单

- [x] 复制 camera_monitor 模块
- [x] 移除 api_server.py
- [x] 创建 CameraManager
- [x] 添加摄像头设置
- [x] 添加 Python 命令
- [x] 添加事件通知
- [x] 更新依赖
- [x] 在 __init__.py 中初始化
- [x] 创建集成文档

## 🎉 集成完成！

摄像头监控功能已完全集成到 ClassTop 中，可以开始使用了！
