// ClassTop Admin Interface JavaScript

const API_BASE = '';
let currentClient = null;
let currentSettingKey = null;
let refreshInterval = null;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    refreshClients();
    // Auto-refresh every 5 seconds
    refreshInterval = setInterval(refreshClients, 5000);
});

// Toast notification
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast show ${type}`;

    setTimeout(() => {
        toast.className = 'toast';
    }, 3000);
}

// Refresh client list
async function refreshClients() {
    try {
        const response = await fetch(`${API_BASE}/api/clients/`);
        const clients = await response.json();

        const clientList = document.getElementById('clientList');
        const clientCount = document.getElementById('clientCount');

        const onlineCount = Object.values(clients).filter(c => c.status === 'online').length;
        clientCount.innerHTML = `在线客户端: <strong>${onlineCount}</strong> / ${Object.keys(clients).length}`;

        if (Object.keys(clients).length === 0) {
            clientList.innerHTML = '<div class="empty-state">暂无客户端连接</div>';
            return;
        }

        clientList.innerHTML = '';
        for (const [uuid, client] of Object.entries(clients)) {
            const clientItem = document.createElement('div');
            clientItem.className = `client-item ${currentClient === uuid ? 'active' : ''}`;
            clientItem.onclick = () => selectClient(uuid);

            const statusClass = client.status === 'online' ? 'online' : 'offline';
            const statusText = client.status === 'online' ? '在线' : '离线';

            clientItem.innerHTML = `
                <div class="client-item-header">
                    <div class="client-item-name">客户端</div>
                    <div class="client-item-status">${statusText}</div>
                </div>
                <div class="client-item-info">
                    <div style="font-size: 0.75rem; opacity: 0.7; margin-bottom: 0.25rem;">UUID: ${uuid.substring(0, 8)}...</div>
                    <div style="font-size: 0.75rem; opacity: 0.7;">IP: ${client.ip_address || '未知'}</div>
                </div>
            `;

            clientList.appendChild(clientItem);
        }
    } catch (error) {
        console.error('Error refreshing clients:', error);
    }
}

// Select a client
async function selectClient(uuid) {
    currentClient = uuid;

    // Update UI
    document.getElementById('welcomeMessage').style.display = 'none';
    document.getElementById('clientDetails').style.display = 'block';

    // Update active state in list
    document.querySelectorAll('.client-item').forEach(item => {
        item.classList.remove('active');
    });
    event.currentTarget?.classList.add('active');

    // Load client details
    await loadClientInfo(uuid);
    await loadSettings();
}

// Load client info
async function loadClientInfo(uuid) {
    try {
        const response = await fetch(`${API_BASE}/api/clients/${uuid}`);
        const client = await response.json();

        document.getElementById('clientUuid').textContent = client.uuid;
        document.getElementById('clientIp').textContent = client.ip_address || '未知';
        document.getElementById('clientStatus').textContent = client.status;

        const lastSeen = new Date(client.last_seen);
        document.getElementById('clientLastSeen').textContent = lastSeen.toLocaleString('zh-CN');
    } catch (error) {
        console.error('Error loading client info:', error);
        showToast('加载客户端信息失败', 'error');
    }
}

// Switch tabs
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

// ========== Settings Management ==========

async function loadSettings() {
    if (!currentClient) return;

    const settingsList = document.getElementById('settingsList');
    settingsList.innerHTML = '<div class="loading">加载中</div>';

    try {
        const response = await fetch(`${API_BASE}/api/settings/${currentClient}`);
        const settings = await response.json();

        if (Object.keys(settings).length === 0) {
            settingsList.innerHTML = '<div class="empty-state">暂无设置</div>';
            return;
        }

        settingsList.innerHTML = '';
        for (const [key, value] of Object.entries(settings)) {
            const settingItem = document.createElement('div');
            settingItem.className = 'setting-item';
            settingItem.innerHTML = `
                <div class="setting-key">${key}</div>
                <div class="setting-value">${value || '(空)'}</div>
                <button class="btn btn-sm btn-primary" onclick="showEditSettingDialog('${key}', '${value}')">
                    编辑
                </button>
            `;
            settingsList.appendChild(settingItem);
        }
    } catch (error) {
        console.error('Error loading settings:', error);
        showToast('加载设置失败', 'error');
        settingsList.innerHTML = '<div class="empty-state">加载失败</div>';
    }
}

function showEditSettingDialog(key, value) {
    currentSettingKey = key;
    document.getElementById('settingKeyLabel').textContent = `设置项: ${key}`;
    document.getElementById('settingValue').value = value;
    document.getElementById('editSettingModal').classList.add('show');
}

function closeEditSettingDialog() {
    document.getElementById('editSettingModal').classList.remove('show');
    currentSettingKey = null;
}

async function saveSetting() {
    if (!currentClient || !currentSettingKey) return;

    const value = document.getElementById('settingValue').value;

    try {
        const response = await fetch(`${API_BASE}/api/settings/${currentClient}/${currentSettingKey}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ key: currentSettingKey, value })
        });

        if (response.ok) {
            showToast('设置已更新', 'success');
            closeEditSettingDialog();
            await loadSettings();
        } else {
            const error = await response.json();
            showToast(error.detail || '更新失败', 'error');
        }
    } catch (error) {
        console.error('Error updating setting:', error);
        showToast('更新设置失败', 'error');
    }
}

// ========== Camera Management ==========

let cameraInitialized = false;
let statusRefreshInterval = null;
let previewWebSocket = null;
let previewActive = false;

async function initializeCamera() {
    if (!currentClient) {
        showToast('请先选择客户端', 'error');
        return;
    }

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
    cameraList.innerHTML = '<div class="loading">加载中</div>';

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

            // Get up to 3 resolutions to display
            const displayResolutions = cam.resolutions
                .slice(0, 3)
                .map(r => `${r.width}x${r.height}`)
                .join(', ');
            const moreResolutions = cam.resolutions.length > 3
                ? ` (+${cam.resolutions.length - 3} 更多)`
                : '';

            camItem.innerHTML = `
                <div class="camera-item-header">
                    <div class="camera-item-name">📷 ${cam.name}</div>
                    <span class="badge">索引: ${cam.index}</span>
                </div>
                <div class="camera-item-info">
                    <strong>支持分辨率:</strong> ${displayResolutions}${moreResolutions}
                </div>
            `;
            cameraList.appendChild(camItem);
        });
    } catch (error) {
        console.error('Error loading cameras:', error);
        cameraList.innerHTML = '<div class="empty-state">加载失败</div>';
        showToast('加载摄像头列表失败', 'error');
    }
}

async function loadEncoders() {
    if (!currentClient) return;

    const encoderInfo = document.getElementById('encoderInfo');
    encoderInfo.innerHTML = '<div class="loading">加载中</div>';

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
            <h4>🎬 H.264 编码器 (${data.h264.available} 个可用)</h4>
            <div class="encoder-list" id="h264List"></div>
        `;
        grid.appendChild(h264Section);

        const h264List = h264Section.querySelector('#h264List');
        if (data.h264.encoders.length === 0) {
            h264List.innerHTML = '<div class="empty-state" style="padding: 1rem;">无可用编码器</div>';
        } else {
            data.h264.encoders.forEach(enc => {
                const badge = enc.is_hardware ? 'hardware' : 'software';
                const encItem = document.createElement('div');
                encItem.className = 'encoder-item';
                encItem.innerHTML = `
                    <span class="encoder-item-name">${enc.name} - ${enc.description}</span>
                    <span class="encoder-badge ${badge}">${enc.is_hardware ? '🚀 硬件' : '💻 软件'}</span>
                `;
                h264List.appendChild(encItem);
            });

            // Add preferred encoder info
            if (data.h264.preferred) {
                const preferredInfo = document.createElement('div');
                preferredInfo.className = 'encoder-preferred';
                preferredInfo.innerHTML = `<strong>首选:</strong> ${data.h264.preferred}`;
                h264Section.appendChild(preferredInfo);
            }
        }

        // H.265 encoders
        const h265Section = document.createElement('div');
        h265Section.className = 'encoder-category';
        h265Section.innerHTML = `
            <h4>🎥 H.265 编码器 (${data.h265.available} 个可用)</h4>
            <div class="encoder-list" id="h265List"></div>
        `;
        grid.appendChild(h265Section);

        const h265List = h265Section.querySelector('#h265List');
        if (data.h265.encoders.length === 0) {
            h265List.innerHTML = '<div class="empty-state" style="padding: 1rem;">无可用编码器</div>';
        } else {
            data.h265.encoders.forEach(enc => {
                const badge = enc.is_hardware ? 'hardware' : 'software';
                const encItem = document.createElement('div');
                encItem.className = 'encoder-item';
                encItem.innerHTML = `
                    <span class="encoder-item-name">${enc.name} - ${enc.description}</span>
                    <span class="encoder-badge ${badge}">${enc.is_hardware ? '🚀 硬件' : '💻 软件'}</span>
                `;
                h265List.appendChild(encItem);
            });

            // Add preferred encoder info
            if (data.h265.preferred) {
                const preferredInfo = document.createElement('div');
                preferredInfo.className = 'encoder-preferred';
                preferredInfo.innerHTML = `<strong>首选:</strong> ${data.h265.preferred}`;
                h265Section.appendChild(preferredInfo);
            }
        }
    } catch (error) {
        console.error('Error loading encoders:', error);
        encoderInfo.innerHTML = '<div class="empty-state">加载失败</div>';
        showToast('加载编码器信息失败', 'error');
    }
}

async function startRecording() {
    if (!currentClient) {
        showToast('请先选择客户端', 'error');
        return;
    }

    const cameraIndex = parseInt(document.getElementById('selectedCamera').value);
    const codecType = document.getElementById('codecType').value || undefined;
    const resolution = document.getElementById('resolution').value;
    const bitrate = document.getElementById('bitrate').value || undefined;

    let width, height;
    if (resolution) {
        [width, height] = resolution.split('x').map(Number);
    }

    try {
        showToast('正在开始录制...', 'info');

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
            const data = await response.json();
            showToast('录制已开始', 'success');

            // Update UI
            document.getElementById('startRecBtn').disabled = true;
            document.getElementById('stopRecBtn').disabled = false;
            document.getElementById('recordingStatus').style.display = 'block';

            // Update recording info
            const codecText = codecType || 'H.264';
            const resolutionText = resolution || '默认';
            document.getElementById('recordingInfo').textContent =
                `正在录制... (${codecText}, ${resolutionText})`;

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
        showToast('正在停止录制...', 'info');

        const response = await fetch(`${API_BASE}/api/camera/${currentClient}/recording/stop`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ camera_index: cameraIndex })
        });

        if (response.ok) {
            showToast('录制已停止', 'success');

            // Update UI
            document.getElementById('startRecBtn').disabled = false;
            document.getElementById('stopRecBtn').disabled = true;
            document.getElementById('recordingStatus').style.display = 'none';

            // Stop refreshing status
            stopStatusRefresh();

            // Refresh status one last time
            await refreshCameraStatus();
        } else {
            const error = await response.json();
            showToast(error.detail || '停止录制失败', 'error');
        }
    } catch (error) {
        console.error('Error stopping recording:', error);
        showToast('停止录制失败', 'error');
    }
}

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
        // Silent fail for status refresh
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

            const streamingIcon = status.is_streaming ? '✅' : '❌';
            const recordingIcon = status.is_recording ? '✅' : '❌';

            statusItem.innerHTML = `
                <h4>📷 摄像头 ${index}</h4>
                <p><strong>名称:</strong> <span>${status.camera_name}</span></p>
                <p><strong>编码器:</strong> <span>${status.encoder}</span></p>
                <p><strong>分辨率:</strong> <span>${status.resolution}</span></p>
                <p><strong>流传输:</strong> <span>${streamingIcon} ${status.is_streaming ? '是' : '否'}</span></p>
                <p><strong>录制中:</strong> <span>${recordingIcon} ${status.is_recording ? '是' : '否'}</span></p>
                ${status.current_recording ? `<p><strong>文件:</strong> <span style="word-break: break-all; font-size: 0.75rem;">${status.current_recording}</span></p>` : ''}
            `;
            grid.appendChild(statusItem);
        }
    } else {
        statusDiv.innerHTML = '<div class="empty-state">暂无状态信息</div>';
    }
}

// ========== Camera Preview ==========

async function startPreview() {
    if (!currentClient) {
        showToast('请先选择客户端', 'error');
        return;
    }

    if (previewActive) {
        showToast('预览已在运行', 'info');
        return;
    }

    try {
        showToast('正在启动预览...', 'info');

        const cameraIndex = parseInt(document.getElementById('selectedCamera')?.value || 0);

        // Start preview on server
        const response = await fetch(`${API_BASE}/api/camera/${currentClient}/preview/start?camera_index=${cameraIndex}&fps=10`, {
            method: 'POST'
        });

        if (!response.ok) {
            const error = await response.json();
            showToast(error.detail || '启动预览失败', 'error');
            return;
        }

        // Connect to viewer WebSocket
        const viewerId = 'viewer_' + Date.now();
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${wsProtocol}//${window.location.host}/ws/viewer/${currentClient}/${viewerId}`;

        previewWebSocket = new WebSocket(wsUrl);

        previewWebSocket.onopen = () => {
            console.log('Preview WebSocket connected');
            previewActive = true;

            // Update UI
            document.getElementById('startPreviewBtn').disabled = true;
            document.getElementById('stopPreviewBtn').disabled = false;
            document.getElementById('previewPlaceholder').style.display = 'none';
            document.getElementById('previewImage').style.display = 'block';

            showToast('预览已启动', 'success');
        };

        previewWebSocket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.type === 'camera_frame' && data.frame) {
                    // Update image source with base64 frame
                    const img = document.getElementById('previewImage');
                    img.src = 'data:image/jpeg;base64,' + data.frame;
                }
            } catch (error) {
                console.error('Error processing frame:', error);
            }
        };

        previewWebSocket.onerror = (error) => {
            console.error('WebSocket error:', error);
            showToast('预览连接错误', 'error');
            stopPreview();
        };

        previewWebSocket.onclose = () => {
            console.log('Preview WebSocket closed');
            if (previewActive) {
                stopPreview();
            }
        };

    } catch (error) {
        console.error('Error starting preview:', error);
        showToast('启动预览失败', 'error');
    }
}

async function stopPreview() {
    if (!currentClient) return;

    try {
        // Stop preview on server
        const cameraIndex = parseInt(document.getElementById('selectedCamera')?.value || 0);
        const response = await fetch(`${API_BASE}/api/camera/${currentClient}/preview/stop?camera_index=${cameraIndex}`, {
            method: 'POST'
        });

        if (response.ok) {
            showToast('预览已停止', 'success');
        }
    } catch (error) {
        console.error('Error stopping preview:', error);
    }

    // Close WebSocket
    if (previewWebSocket) {
        previewWebSocket.close();
        previewWebSocket = null;
    }

    previewActive = false;

    // Update UI
    document.getElementById('startPreviewBtn').disabled = false;
    document.getElementById('stopPreviewBtn').disabled = true;
    document.getElementById('previewPlaceholder').style.display = 'block';
    document.getElementById('previewImage').style.display = 'none';
    document.getElementById('previewImage').src = '';
}