# 摄像头监控功能集成指南

摄像头监控功能已成功集成到 ClassTop WebSocket 管理系统中。

## ✅ 已完成的后端集成

### 1. WebSocket 客户端扩展
**文件**: `src-tauri/python/tauri_app/websocket_client.py`

添加了以下摄像头命令：
- `camera_initialize` - 初始化摄像头系统
- `camera_get_cameras` - 获取摄像头列表
- `camera_get_encoders` - 获取编码器信息
- `camera_start_recording` - 开始录制
- `camera_stop_recording` - 停止录制
- `camera_get_status` - 获取状态
- `camera_start_streaming` - 开始视频流
- `camera_stop_streaming` - 停止视频流

### 2. 数据模型
**文件**: `admin-server/models.py`

添加的模型：
```python
class CameraInfo(BaseModel):
    """摄像头信息"""
    index: int
    name: str
    resolutions: List[Dict[str, Any]]

class CameraStatus(BaseModel):
    """摄像头状态"""
    camera_name: str
    camera_index: int
    encoder: str
    resolution: str
    is_streaming: bool
    is_recording: bool
    current_recording: Optional[str] = None

class RecordingRequest(BaseModel):
    """录制请求"""
    camera_index: int = 0
    filename: Optional[str] = None
    codec_type: Optional[str] = None  # 'H.264' or 'H.265'
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[int] = None
    preset: Optional[str] = None
    bitrate: Optional[str] = None
```

### 3. API 路由
**文件**: `admin-server/api/camera.py`

提供的端点：
- `POST /api/camera/{client_uuid}/initialize` - 初始化摄像头
- `GET /api/camera/{client_uuid}/cameras` - 获取摄像头列表
- `GET /api/camera/{client_uuid}/encoders` - 获取编码器
- `POST /api/camera/{client_uuid}/recording/start` - 开始录制
- `POST /api/camera/{client_uuid}/recording/stop` - 停止录制
- `GET /api/camera/{client_uuid}/status` - 获取状态
- `POST /api/camera/{client_uuid}/streaming/start` - 开始流传输
- `POST /api/camera/{client_uuid}/streaming/stop` - 停止流传输

已在 `main.py` 中注册路由。

## 📋 前端集成指南

### 步骤 1: 更新 HTML (index.html)

在 `<div class="tabs">` 中添加摄像头标签页：

```html
<div class="tabs">
    <button class="tab-btn active" onclick="switchTab('settings')">⚙️ 设置管理</button>
    <button class="tab-btn" onclick="switchTab('camera')">📹 摄像头监控</button>
</div>
```

在 `<div class="tab-content" id="settingsTab">` 后添加摄像头标签页内容：

```html
<!-- Camera Tab -->
<div class="tab-content" id="cameraTab" style="display: none;">
    <!-- Camera Status -->
    <section class="section">
        <div class="section-header">
            <h3>摄像头状态</h3>
            <button class="btn btn-sm btn-primary" onclick="initializeCamera()">🚀 初始化摄像头</button>
        </div>
        <div id="cameraStatus">
            <div class="empty-state">请先初始化摄像头系统</div>
        </div>
    </section>

    <!-- Camera List -->
    <section class="section">
        <div class="section-header">
            <h3>可用摄像头</h3>
            <button class="btn btn-sm btn-primary" onclick="loadCameras()">🔄 刷新</button>
        </div>
        <div class="camera-list" id="cameraList">
            <div class="loading">未加载</div>
        </div>
    </section>

    <!-- Recording Controls -->
    <section class="section">
        <h3>录制控制</h3>
        <div class="recording-controls">
            <div class="form-group">
                <label>摄像头:</label>
                <select id="selectedCamera">
                    <option value="0">摄像头 0</option>
                </select>
            </div>

            <div class="form-group">
                <label>编码格式:</label>
                <select id="codecType">
                    <option value="">默认 (H.264)</option>
                    <option value="H.264">H.264</option>
                    <option value="H.265">H.265 (HEVC)</option>
                </select>
            </div>

            <div class="form-group">
                <label>分辨率:</label>
                <select id="resolution">
                    <option value="">默认 (1280x720)</option>
                    <option value="1920x1080">1920x1080 (1080p)</option>
                    <option value="1280x720">1280x720 (720p)</option>
                    <option value="640x480">640x480 (480p)</option>
                </select>
            </div>

            <div class="form-group">
                <label>比特率:</label>
                <select id="bitrate">
                    <option value="">默认 (5M)</option>
                    <option value="10M">10M (高质量)</option>
                    <option value="5M">5M (标准)</option>
                    <option value="3M">3M (较低)</option>
                </select>
            </div>

            <div class="button-group">
                <button class="btn btn-success" onclick="startRecording()" id="startRecBtn">
                    ⏺️ 开始录制
                </button>
                <button class="btn btn-danger" onclick="stopRecording()" id="stopRecBtn" disabled>
                    ⏹️ 停止录制
                </button>
            </div>
        </div>

        <div class="recording-status" id="recordingStatus" style="display: none;">
            <div class="status-indicator recording">
                <span class="status-dot"></span>
                正在录制...
            </div>
        </div>
    </section>

    <!-- Encoder Info -->
    <section class="section">
        <div class="section-header">
            <h3>可用编码器</h3>
        </div>
        <div id="encoderInfo">
            <div class="loading">未加载</div>
        </div>
    </section>
</div>
```

### 步骤 2: 更新 CSS (style.css)

添加摄像头相关样式：

```css
/* Camera Tab Styles */
.camera-list {
    display: grid;
    gap: 1rem;
}

.camera-item {
    padding: 1rem;
    background: #f5f5f5;
    border-radius: 8px;
    border: 1px solid #ddd;
}

.camera-item-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
}

.camera-item-name {
    font-weight: 600;
    font-size: 1rem;
}

.camera-item-info {
    font-size: 0.875rem;
    color: #666;
}

.recording-controls {
    display: grid;
    gap: 1rem;
}

.form-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.form-group label {
    font-weight: 500;
    font-size: 0.875rem;
}

.form-group select,
.form-group input {
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 0.875rem;
}

.button-group {
    display: flex;
    gap: 0.5rem;
    margin-top: 1rem;
}

.btn-success {
    background-color: #28a745;
    color: white;
}

.btn-success:hover {
    background-color: #218838;
}

.btn-danger {
    background-color: #dc3545;
    color: white;
}

.btn-danger:hover {
    background-color: #c82333;
}

.btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.recording-status {
    margin-top: 1rem;
    padding: 1rem;
    background: #fff3cd;
    border: 1px solid #ffc107;
    border-radius: 8px;
}

.status-indicator.recording {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 600;
    color: #d32f2f;
}

.status-indicator.recording .status-dot {
    width: 12px;
    height: 12px;
    background-color: #d32f2f;
    border-radius: 50%;
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    0%, 100% {
        opacity: 1;
    }
    50% {
        opacity: 0.5;
    }
}

.encoder-grid {
    display: grid;
    gap: 1rem;
}

.encoder-category {
    background: #f5f5f5;
    padding: 1rem;
    border-radius: 8px;
}

.encoder-category h4 {
    margin: 0 0 0.5rem 0;
    font-size: 1rem;
}

.encoder-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.encoder-item {
    display: flex;
    justify-content: space-between;
    padding: 0.5rem;
    background: white;
    border-radius: 4px;
    font-size: 0.875rem;
}

.encoder-badge {
    display: inline-block;
    padding: 0.25rem 0.5rem;
    background: #007bff;
    color: white;
    border-radius: 4px;
    font-size: 0.75rem;
}

.encoder-badge.hardware {
    background: #28a745;
}

.encoder-badge.software {
    background: #6c757d;
}
```

### 步骤 3: 更新 JavaScript (app.js)

在文件末尾添加摄像头功能：

```javascript
// ========== Camera Management ==========

let cameraInitialized = false;

// Switch tabs (update existing function)
function switchTab(tab) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    event.currentTarget.classList.add('active');

    // Update tab content
    document.getElementById('settingsTab').style.display = tab === 'settings' ? 'block' : 'none';
    document.getElementById('cameraTab').style.display = tab === 'camera' ? 'block' : 'none';

    // Load camera data when switching to camera tab
    if (tab === 'camera' && cameraInitialized) {
        loadCameras();
        loadEncoders();
        refreshCameraStatus();
    }
}

async function initializeCamera() {
    if (!currentClient) return;

    try {
        showToast('正在初始化摄像头系统...', 'info');

        const response = await fetch(`${API_BASE}/api/camera/${currentClient}/initialize`, {
            method: 'POST'
        });

        if (response.ok) {
            const data = await response.json();
            showToast(`摄像头初始化成功！发现 ${data.camera_count} 个摄像头`, 'success');
            cameraInitialized = true;

            // Load camera info
            await loadCameras();
            await loadEncoders();
            updateCameraStatus(data);
        } else {
            const error = await response.json();
            showToast(error.detail || '初始化失败', 'error');
        }
    } catch (error) {
        console.error('Error initializing camera:', error);
        showToast('初始化摄像头系统失败', 'error');
    }
}

async function loadCameras() {
    if (!currentClient) return;

    const cameraList = document.getElementById('cameraList');
    cameraList.innerHTML = '<div class="loading">加载中...</div>';

    try {
        const response = await fetch(`${API_BASE}/api/camera/${currentClient}/cameras`);
        if (!response.ok) throw new Error('Failed to load cameras');

        const data = await response.json();
        const cameras = data.cameras || [];

        if (cameras.length === 0) {
            cameraList.innerHTML = '<div class="empty-state">未发现摄像头</div>';
            return;
        }

        // Update camera selector
        const selector = document.getElementById('selectedCamera');
        selector.innerHTML = '';
        cameras.forEach(cam => {
            const option = document.createElement('option');
            option.value = cam.index;
            option.textContent = `[${cam.index}] ${cam.name}`;
            selector.appendChild(option);
        });

        // Display camera list
        cameraList.innerHTML = '';
        cameras.forEach(cam => {
            const camItem = document.createElement('div');
            camItem.className = 'camera-item';
            camItem.innerHTML = `
                <div class="camera-item-header">
                    <div class="camera-item-name">${cam.name}</div>
                    <span class="badge">索引: ${cam.index}</span>
                </div>
                <div class="camera-item-info">
                    <strong>支持分辨率:</strong> ${cam.resolutions.slice(0, 3).map(r => `${r.width}x${r.height}`).join(', ')}
                </div>
            `;
            cameraList.appendChild(camItem);
        });
    } catch (error) {
        console.error('Error loading cameras:', error);
        cameraList.innerHTML = '<div class="empty-state">加载失败</div>';
    }
}

async function loadEncoders() {
    if (!currentClient) return;

    const encoderInfo = document.getElementById('encoderInfo');
    encoderInfo.innerHTML = '<div class="loading">加载中...</div>';

    try {
        const response = await fetch(`${API_BASE}/api/camera/${currentClient}/encoders`);
        if (!response.ok) throw new Error('Failed to load encoders');

        const data = await response.json();

        encoderInfo.innerHTML = '<div class="encoder-grid"></div>';
        const grid = encoderInfo.querySelector('.encoder-grid');

        // H.264 encoders
        const h264Section = document.createElement('div');
        h264Section.className = 'encoder-category';
        h264Section.innerHTML = `
            <h4>H.264 编码器 (${data.h264.available} 个)</h4>
            <div class="encoder-list" id="h264List"></div>
            <p style="margin-top: 0.5rem; font-size: 0.875rem;">
                <strong>首选:</strong> ${data.h264.preferred}
            </p>
        `;
        grid.appendChild(h264Section);

        const h264List = h264Section.querySelector('#h264List');
        data.h264.encoders.forEach(enc => {
            const badge = enc.is_hardware ? 'hardware' : 'software';
            h264List.innerHTML += `
                <div class="encoder-item">
                    <span>${enc.name} - ${enc.description}</span>
                    <span class="encoder-badge ${badge}">${enc.is_hardware ? '硬件' : '软件'}</span>
                </div>
            `;
        });

        // H.265 encoders
        const h265Section = document.createElement('div');
        h265Section.className = 'encoder-category';
        h265Section.innerHTML = `
            <h4>H.265 编码器 (${data.h265.available} 个)</h4>
            <div class="encoder-list" id="h265List"></div>
            <p style="margin-top: 0.5rem; font-size: 0.875rem;">
                <strong>首选:</strong> ${data.h265.preferred}
            </p>
        `;
        grid.appendChild(h265Section);

        const h265List = h265Section.querySelector('#h265List');
        data.h265.encoders.forEach(enc => {
            const badge = enc.is_hardware ? 'hardware' : 'software';
            h265List.innerHTML += `
                <div class="encoder-item">
                    <span>${enc.name} - ${enc.description}</span>
                    <span class="encoder-badge ${badge}">${enc.is_hardware ? '硬件' : '软件'}</span>
                </div>
            `;
        });
    } catch (error) {
        console.error('Error loading encoders:', error);
        encoderInfo.innerHTML = '<div class="empty-state">加载失败</div>';
    }
}

async function startRecording() {
    if (!currentClient) return;

    const cameraIndex = parseInt(document.getElementById('selectedCamera').value);
    const codecType = document.getElementById('codecType').value || undefined;
    const resolution = document.getElementById('resolution').value;
    const bitrate = document.getElementById('bitrate').value || undefined;

    let width, height;
    if (resolution) {
        [width, height] = resolution.split('x').map(Number);
    }

    try {
        const response = await fetch(`${API_BASE}/api/camera/${currentClient}/recording/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                camera_index: cameraIndex,
                codec_type: codecType,
                width,
                height,
                bitrate
            })
        });

        if (response.ok) {
            showToast('录制已开始', 'success');
            document.getElementById('startRecBtn').disabled = true;
            document.getElementById('stopRecBtn').disabled = false;
            document.getElementById('recordingStatus').style.display = 'block';

            // Start refreshing status
            startStatusRefresh();
        } else {
            const error = await response.json();
            showToast(error.detail || '开始录制失败', 'error');
        }
    } catch (error) {
        console.error('Error starting recording:', error);
        showToast('开始录制失败', 'error');
    }
}

async function stopRecording() {
    if (!currentClient) return;

    const cameraIndex = parseInt(document.getElementById('selectedCamera').value);

    try {
        const response = await fetch(`${API_BASE}/api/camera/${currentClient}/recording/stop`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ camera_index: cameraIndex })
        });

        if (response.ok) {
            showToast('录制已停止', 'success');
            document.getElementById('startRecBtn').disabled = false;
            document.getElementById('stopRecBtn').disabled = true;
            document.getElementById('recordingStatus').style.display = 'none';

            // Stop refreshing status
            stopStatusRefresh();
        } else {
            const error = await response.json();
            showToast(error.detail || '停止录制失败', 'error');
        }
    } catch (error) {
        console.error('Error stopping recording:', error);
        showToast('停止录制失败', 'error');
    }
}

let statusRefreshInterval = null;

function startStatusRefresh() {
    if (statusRefreshInterval) return;
    statusRefreshInterval = setInterval(refreshCameraStatus, 2000);
}

function stopStatusRefresh() {
    if (statusRefreshInterval) {
        clearInterval(statusRefreshInterval);
        statusRefreshInterval = null;
    }
}

async function refreshCameraStatus() {
    if (!currentClient) return;

    try {
        const response = await fetch(`${API_BASE}/api/camera/${currentClient}/status`);
        if (response.ok) {
            const data = await response.json();
            updateCameraStatus(data);
        }
    } catch (error) {
        console.error('Error refreshing status:', error);
    }
}

function updateCameraStatus(data) {
    const statusDiv = document.getElementById('cameraStatus');

    if (data.status && data.status.streamers) {
        const streamers = data.status.streamers;
        const count = Object.keys(streamers).length;

        if (count === 0) {
            statusDiv.innerHTML = '<div class="empty-state">无活动的摄像头</div>';
            return;
        }

        statusDiv.innerHTML = '<div class="status-grid"></div>';
        const grid = statusDiv.querySelector('.status-grid');

        for (const [index, status] of Object.entries(streamers)) {
            const statusItem = document.createElement('div');
            statusItem.className = 'status-item';
            statusItem.innerHTML = `
                <h4>摄像头 ${index}</h4>
                <p><strong>名称:</strong> ${status.camera_name}</p>
                <p><strong>编码器:</strong> ${status.encoder}</p>
                <p><strong>分辨率:</strong> ${status.resolution}</p>
                <p><strong>流传输:</strong> ${status.is_streaming ? '✅ 是' : '❌ 否'}</p>
                <p><strong>录制中:</strong> ${status.is_recording ? '✅ 是' : '❌ 否'}</p>
                ${status.current_recording ? `<p><strong>文件:</strong> ${status.current_recording}</p>` : ''}
            `;
            grid.appendChild(statusItem);
        }
    }
}
```

## 🎯 使用流程

### 1. 启用摄像头功能

在客户端启用摄像头：
```
设置 camera_enabled = true
重启 ClassTop 客户端
```

### 2. 管理端操作

1. 打开管理界面 `http://localhost:8000`
2. 选择一个在线客户端
3. 切换到"📹 摄像头监控"标签页
4. 点击"🚀 初始化摄像头"按钮
5. 选择摄像头和录制参数
6. 点击"⏺️ 开始录制"

### 3. API 调用示例

```python
import requests

CLIENT_UUID = "your-client-uuid"
BASE_URL = "http://localhost:8000"

# 初始化摄像头
response = requests.post(f"{BASE_URL}/api/camera/{CLIENT_UUID}/initialize")
print(response.json())

# 获取摄像头列表
response = requests.get(f"{BASE_URL}/api/camera/{CLIENT_UUID}/cameras")
cameras = response.json()

# 开始录制 (H.265, 1080p)
response = requests.post(
    f"{BASE_URL}/api/camera/{CLIENT_UUID}/recording/start",
    json={
        "camera_index": 0,
        "codec_type": "H.265",
        "width": 1920,
        "height": 1080,
        "bitrate": "10M"
    }
)

# 停止录制
response = requests.post(
    f"{BASE_URL}/api/camera/{CLIENT_UUID}/recording/stop",
    json={"camera_index": 0}
)
```

## 🎨 UI 优化建议

### 实时预览（可选）
如果需要实时预览功能，可以：
1. 在客户端启动 HTTP 流服务器（已在 `video_streamer.py` 中实现）
2. 在管理端添加 `<img>` 标签显示 MJPEG 流
3. 使用客户端 IP 和端口访问流

示例：
```html
<div class="video-preview">
    <img id="videoStream" src="" alt="视频预览" style="max-width: 100%;">
</div>

<script>
// 开始流传输后
document.getElementById('videoStream').src =
    `http://${clientIP}:8889/api/stream/0/video`;
</script>
```

### 录制历史
可以添加一个录制历史列表，显示：
- 录制时间
- 文件名
- 文件大小
- 时长
- 下载/播放按钮

## ✅ 集成清单

- [x] WebSocket 客户端支持摄像头命令
- [x] 添加摄像头数据模型
- [x] 创建摄像头 API 路由
- [x] 注册 API 路由到主应用
- [ ] 前端 HTML 更新（参考上方代码）
- [ ] 前端 CSS 样式（参考上方代码）
- [ ] 前端 JavaScript 实现（参考上方代码）
- [ ] 测试完整流程

## 🚀 部署说明

### 服务器端
```bash
cd admin-server
pip install -r requirements.txt
python main.py
```

### 客户端
确保在 ClassTop 设置中：
- `camera_enabled`: true
- `camera_width`: 1280
- `camera_height`: 720
- `camera_fps`: 30

## 📝 注意事项

1. **性能**: 硬件编码器优先级 NVENC > QSV > AMF > Software
2. **网络**: 实时预览需要客户端网络可访问
3. **权限**: 确保摄像头未被其他程序占用
4. **存储**: 录制文件存储在客户端 `recordings/` 目录

## 🎉 完成！

摄像头监控功能已完全集成到 WebSocket 管理系统。参考上述代码完成前端实现即可使用全部功能。
