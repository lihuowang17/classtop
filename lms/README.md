# ClassTop LMS (Light Management Service)

ClassTop LMS 是一个基于 FastAPI 的轻量级现场管理服务，用于本地网络环境下的实时控制和监控多个 ClassTop 客户端。

## 功能特性

- ⚙️ **设置管理**: 远程查看和修改客户端设置
- 📹 **监控管理**: 实时查看监控状态，远程控制录制和推流
- 🔄 **实时通信**: 基于 WebSocket 的双向通信
- 🖥️ **精美界面**: 现代化的 Material Design 管理界面
- 🔌 **自动重连**: 客户端自动重连机制

## 快速开始

### 1. 安装依赖

```bash
cd lms
pip install -r requirements.txt
```

### 2. 启动服务器

```bash
python main.py
```

服务器将在 `http://localhost:8000` 启动。

### 3. 配置客户端

在 ClassTop 客户端的设置中配置：

- `server_url`: `http://localhost:8000` (或服务器的实际地址)
- `client_uuid`: 自动生成的客户端唯一标识

客户端将自动连接到管理后台。

### 4. 访问管理界面

在浏览器中打开: `http://localhost:8000`

## 架构说明

### LMS 服务端 (`lms/`)

```
lms/
├── main.py                    # FastAPI 应用入口
├── websocket_manager.py       # WebSocket 连接管理
├── models.py                  # 数据模型
├── db.py                      # SQLite 数据库层 (NEW)
├── management_client.py       # Management-Server 连接客户端 (NEW)
├── api/
│   ├── clients.py            # 客户端管理 API
│   ├── settings.py           # 设置管理 API
│   └── cctv.py               # CCTV 管理 API
├── static/
│   ├── index.html            # 管理界面
│   ├── style.css             # 样式
│   └── app.js                # 前端逻辑
└── requirements.txt
```

### 客户端端 (`src-tauri/python/tauri_app/`)

- `websocket_client.py`: WebSocket 客户端实现
- `__init__.py`: 集成 WebSocket 客户端初始化

## API 文档

服务器启动后访问: `http://localhost:8000/docs`

### 客户端管理

- `GET /api/clients/`: 获取所有客户端
- `GET /api/clients/online`: 获取在线客户端
- `GET /api/clients/{uuid}`: 获取客户端信息
- `POST /api/clients/{uuid}/command`: 发送命令到客户端

### 设置管理

- `GET /api/settings/{uuid}`: 获取客户端所有设置
- `GET /api/settings/{uuid}/{key}`: 获取单个设置
- `PUT /api/settings/{uuid}/{key}`: 更新单个设置
- `POST /api/settings/{uuid}/batch`: 批量更新设置

### CCTV 管理

- `GET /api/cctv/{uuid}/state`: 获取监控状态
- `GET /api/cctv/{uuid}/cameras`: 检测可用摄像头
- `POST /api/cctv/{uuid}/cameras`: 添加摄像头
- `DELETE /api/cctv/{uuid}/cameras/{camera_id}`: 删除摄像头
- `POST /api/cctv/{uuid}/control`: 控制摄像头（录制/推流）
- `GET /api/cctv/{uuid}/storage`: 获取存储信息
- `POST /api/cctv/{uuid}/storage/cleanup`: 清理旧录像

## WebSocket 通信协议

### 客户端 → 服务器

**心跳包**:
```json
{
  "type": "heartbeat",
  "timestamp": 1234567890.123
}
```

**状态更新**:
```json
{
  "type": "state_update",
  "data": {
    "settings": {...},
    "cctv_state": {...}
  }
}
```

**命令响应**:
```json
{
  "type": "response",
  "request_id": "req_123",
  "success": true,
  "data": {...}
}
```

### 服务器 → 客户端

**命令**:
```json
{
  "type": "command",
  "request_id": "req_123",
  "command": "get_all_settings",
  "params": {}
}
```

## 支持的命令

客户端支持以下命令：

### 设置命令
- `get_all_settings`: 获取所有设置
- `get_setting`: 获取单个设置
- `set_setting`: 设置单个值
- `update_settings_batch`: 批量更新设置
- `refresh_state`: 刷新客户端状态

### CCTV 命令
- `cctv_detect_cameras`: 检测摄像头
- `cctv_add_camera`: 添加摄像头
- `cctv_remove_camera`: 删除摄像头
- `cctv_get_camera_resolutions`: 获取支持的分辨率
- `cctv_start_recording`: 开始录制
- `cctv_stop_recording`: 停止录制
- `cctv_start_streaming`: 开始推流
- `cctv_stop_streaming`: 停止推流
- `cctv_get_camera_state`: 获取摄像头状态
- `cctv_get_all_states`: 获取所有状态
- `cctv_get_storage_info`: 获取存储信息
- `cctv_cleanup_storage`: 清理存储
- `cctv_get_recordings`: 获取录像列表
- `cctv_delete_recording`: 删除录像
- `cctv_get_config`: 获取配置

## 生产环境部署

### 使用 Gunicorn + Uvicorn

```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### 使用 Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 安全建议

1. **使用 HTTPS**: 生产环境务必使用 SSL/TLS
2. **身份验证**: 添加 JWT 或 OAuth2 认证
3. **访问控制**: 限制管理界面的访问
4. **防火墙**: 配置防火墙规则
5. **监控日志**: 启用访问日志和错误日志

## 客户端依赖

客户端需要安装 `websockets` 库：

```bash
pip install websockets
```

## 故障排查

### 客户端无法连接

1. 检查 `server_url` 设置是否正确
2. 确认服务器正在运行
3. 检查网络防火墙设置
4. 查看客户端日志中的错误信息

### 命令执行失败

1. 检查 API 文档 `/docs` 查看参数格式
2. 查看服务器日志获取详细错误
3. 确认客户端 CCTV 系统已启用（如果是 CCTV 命令）

### 连接频繁断开

1. 检查网络稳定性
2. 调整心跳间隔（默认 30 秒）
3. 检查服务器资源使用情况

## 技术栈

- **后端**: FastAPI + Uvicorn
- **WebSocket**: websockets 库
- **前端**: 原生 JavaScript + CSS
- **数据验证**: Pydantic

## License

Copyright © 2025 ClassTop Project
