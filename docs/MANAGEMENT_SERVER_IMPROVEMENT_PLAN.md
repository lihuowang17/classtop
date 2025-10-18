# ClassTop 管理服务器改进方案

## 📊 当前状态分析

### 项目概况

目前存在两个管理服务器项目：

| 项目 | 技术栈 | 主要功能 | 状态 |
|------|--------|---------|------|
| **admin-server** | FastAPI + Python | WebSocket 实时控制、CCTV 管理、设置管理 | ✅ 已实现 |
| **Classtop-Management-Server** | Rust + Actix-Web + PostgreSQL | 数据同步、多客户端管理、统计分析 | ✅ 已实现 |

### 功能对比

#### admin-server (项目内)
**位置**: `classtop/admin-server/`

**优势**:
- ✅ WebSocket 双向实时通信
- ✅ 远程控制客户端设置
- ✅ CCTV 监控管理（录制/推流）
- ✅ 简单易部署（单个 Python 脚本）
- ✅ 已与客户端集成

**局限**:
- ❌ 无持久化数据库（仅内存管理）
- ❌ 不支持多客户端数据对比
- ❌ 缺少统计分析功能
- ❌ 无 Web 管理界面（仅静态页面）
- ❌ 扩展性有限

**核心功能**:
1. WebSocket 连接管理
2. 实时命令发送（设置修改、CCTV 控制）
3. 客户端状态监控
4. 心跳保持

#### Classtop-Management-Server (独立项目)
**位置**: `/Users/logos/RustroverProjects/Classtop-Management-Server/`

**优势**:
- ✅ PostgreSQL 数据持久化
- ✅ RESTful API 设计
- ✅ Vue 3 + MDUI 2 管理界面
- ✅ Swagger/ReDoc API 文档
- ✅ 多客户端数据集中管理
- ✅ 统计分析和对比
- ✅ 高性能 Rust 实现

**局限**:
- ❌ 未与客户端集成（待实现）
- ❌ 无实时控制功能
- ❌ 不支持 WebSocket
- ❌ 缺少 CCTV 管理

**核心功能**:
1. 客户端注册管理
2. 课程/课程表数据同步
3. 统计分析和可视化
4. 多客户端数据对比

## 🎯 改进目标

### 短期目标（1-2 周）
1. **实现客户端数据同步** - 完成 Classtop-Management-Server 与客户端的集成
2. **改进 admin-server** - 添加数据持久化和更好的管理界面
3. **统一文档** - 整合两个项目的文档，明确使用场景

### 中期目标（1-2 月）
4. **功能整合** - 评估是否需要合并两个项目
5. **添加认证系统** - 实现 JWT 或 API Key 认证
6. **性能优化** - 优化数据同步和 WebSocket 性能

### 长期目标（3-6 月）
7. **微服务架构** - 拆分为独立的服务模块
8. **高可用部署** - 支持集群部署和负载均衡
9. **高级功能** - 数据分析、报表生成、告警系统

## 📋 具体改进方案

### 方案 A: 双轨并行（推荐）

**思路**: 保留两个项目，各司其职，相互补充

**架构**:
```
┌─────────────────────────────────────────────┐
│         ClassTop Client (Tauri)             │
│  - 本地课程管理和进度显示                      │
│  - SQLite 本地数据库                          │
└──────────┬──────────────────┬────────────────┘
           │                  │
           │ WebSocket        │ HTTP API
           │ (实时控制)        │ (数据同步)
           │                  │
┌──────────▼──────────┐  ┌───▼────────────────────┐
│   admin-server      │  │ Management-Server      │
│   (FastAPI)         │  │ (Rust + PostgreSQL)    │
├─────────────────────┤  ├────────────────────────┤
│ - 实时控制          │  │ - 数据收集和存储        │
│ - 设置管理          │  │ - 统计分析              │
│ - CCTV 管理         │  │ - Web 管理界面          │
│ - 命令执行          │  │ - 多客户端对比          │
└─────────────────────┘  └────────────────────────┘
```

**优势**:
- ✅ 各项目专注核心功能
- ✅ 不需要大规模重构
- ✅ 用户可按需部署
- ✅ 降低单点故障风险

**实施步骤**:

#### 第一阶段: 客户端数据同步（参考 CLIENT_INTEGRATION_TODO.md）

1. **客户端修改** (`classtop/`):
   - [ ] 添加 `location` 字段到 `courses` 表
   - [ ] 创建 `sync_client.py` 模块
   - [ ] 扩展 `schedule_manager.py` 添加数据获取方法
   - [ ] 在 `__init__.py` 中集成同步客户端
   - [ ] 更新 `Settings.vue` 添加服务器配置 UI
   - [ ] 安装 `requests` 依赖

2. **测试验证**:
   - [ ] 本地测试客户端注册
   - [ ] 测试数据同步功能
   - [ ] 测试自动同步
   - [ ] 多客户端同步测试

#### 第二阶段: admin-server 改进

1. **添加数据持久化**:
   - [ ] 集成 SQLite 存储客户端状态
   - [ ] 记录连接历史和命令日志
   - [ ] 添加配置持久化

2. **改进 Web 界面**:
   - [ ] 使用 Vue 3 重写前端（或使用 MDUI 2）
   - [ ] 添加客户端列表和状态监控
   - [ ] 实时日志查看
   - [ ] CCTV 监控面板优化

3. **增强安全性**:
   - [ ] 添加 API Key 认证
   - [ ] WebSocket 连接验证
   - [ ] IP 白名单支持

#### 第三阶段: 项目互联

1. **数据共享**:
   - admin-server 可查询 Management-Server 的历史数据
   - Management-Server 显示客户端在线状态（来自 admin-server）

2. **统一入口**:
   - 创建统一的管理门户
   - 集成两个服务的功能

### 方案 B: 完全整合

**思路**: 将 admin-server 的功能整合到 Classtop-Management-Server

**架构**:
```
┌──────────────────────────────────────┐
│   ClassTop Management Server        │
│   (Rust + Actix-Web + PostgreSQL)   │
├──────────────────────────────────────┤
│ REST API          │  WebSocket API   │
│ - 数据同步        │  - 实时控制      │
│ - 客户端管理      │  - 命令执行      │
│ - 统计分析        │  - 状态监控      │
│                   │  - CCTV 管理     │
├──────────────────────────────────────┤
│      Vue 3 + MDUI 2 管理界面          │
└──────────────────────────────────────┘
```

**优势**:
- ✅ 统一架构，易于维护
- ✅ 共享数据库和认证
- ✅ 性能更好（Rust）
- ✅ 部署简单

**劣势**:
- ❌ 需要用 Rust 重写 WebSocket 和 CCTV 逻辑
- ❌ 开发周期长
- ❌ 风险较高

**实施步骤**（如果选择此方案）:

1. **在 Management-Server 中添加 WebSocket 支持**:
   - [ ] 添加 `actix-web-actors` 依赖
   - [ ] 实现 WebSocket 处理器
   - [ ] 移植 `websocket_manager.py` 逻辑

2. **移植 CCTV 管理功能**:
   - [ ] 分析 Python CCTV 逻辑
   - [ ] 用 Rust 重新实现（可能需要调用 FFmpeg）
   - [ ] 或保留 Python 部分作为微服务

3. **整合前端**:
   - [ ] 将 admin-server 的前端功能迁移到 Vue 3 项目
   - [ ] 添加实时状态监控页面
   - [ ] 集成 WebSocket 客户端

## 🔧 技术改进建议

### admin-server 改进

#### 1. 添加数据库支持

**文件**: `classtop/admin-server/db.py` (新建)

```python
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

class AdminDatabase:
    def __init__(self, db_path: str = "admin.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.init_db()

    def init_db(self):
        """初始化数据库表"""
        cursor = self.conn.cursor()

        # 客户端连接历史
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS connection_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_uuid TEXT NOT NULL,
                client_name TEXT,
                connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                disconnected_at TIMESTAMP,
                ip_address TEXT
            )
        """)

        # 命令执行日志
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS command_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_uuid TEXT NOT NULL,
                command TEXT NOT NULL,
                params TEXT,
                response TEXT,
                success BOOLEAN,
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # CCTV 事件日志
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cctv_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_uuid TEXT NOT NULL,
                event_type TEXT NOT NULL,
                camera_id TEXT,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()

    def log_connection(self, uuid: str, name: str, ip: str):
        """记录客户端连接"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO connection_logs (client_uuid, client_name, ip_address)
            VALUES (?, ?, ?)
        """, (uuid, name, ip))
        self.conn.commit()
        return cursor.lastrowid

    def log_disconnection(self, log_id: int):
        """记录客户端断开"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE connection_logs
            SET disconnected_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (log_id,))
        self.conn.commit()

    def log_command(self, uuid: str, command: str, params: dict,
                    response: dict, success: bool):
        """记录命令执行"""
        import json
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO command_logs
            (client_uuid, command, params, response, success)
            VALUES (?, ?, ?, ?, ?)
        """, (uuid, command, json.dumps(params), json.dumps(response), success))
        self.conn.commit()

    def get_client_history(self, uuid: str, limit: int = 50) -> List[Dict]:
        """获取客户端连接历史"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM connection_logs
            WHERE client_uuid = ?
            ORDER BY connected_at DESC
            LIMIT ?
        """, (uuid, limit))

        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
```

**集成到 main.py**:

```python
from db import AdminDatabase

# 初始化数据库
admin_db = AdminDatabase()

# 在 WebSocket 连接建立时
@app.websocket("/ws/{client_uuid}")
async def websocket_endpoint(websocket: WebSocket, client_uuid: str):
    await websocket.accept()

    # 记录连接
    client_info = await websocket.receive_json()
    log_id = admin_db.log_connection(
        client_uuid,
        client_info.get("name", "Unknown"),
        websocket.client.host
    )

    try:
        # ... 现有逻辑 ...
    finally:
        # 记录断开
        admin_db.log_disconnection(log_id)
```

#### 2. 改进前端界面

使用 MDUI 2 重写静态页面：

**文件**: `classtop/admin-server/static/index.html`

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ClassTop 管理后台</title>
    <link rel="stylesheet" href="https://unpkg.com/mdui@2/mdui.css">
    <script src="https://unpkg.com/mdui@2/mdui.global.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/vue@3"></script>
</head>
<body>
    <div id="app" class="mdui-theme-auto">
        <mdui-top-app-bar>
            <mdui-top-app-bar-title>ClassTop 管理后台</mdui-top-app-bar-title>
            <div style="flex-grow: 1"></div>
            <mdui-button-icon icon="refresh" @click="refreshClients"></mdui-button-icon>
        </mdui-top-app-bar>

        <div class="mdui-container" style="margin-top: 80px;">
            <mdui-card variant="outlined">
                <div style="padding: 16px;">
                    <h2>在线客户端</h2>
                    <mdui-list>
                        <mdui-list-item v-for="client in clients" :key="client.uuid">
                            <div>
                                <div>{{ client.name }}</div>
                                <div class="mdui-text-secondary">{{ client.uuid }}</div>
                            </div>
                            <mdui-button-icon slot="end-icon" icon="settings"
                                              @click="openSettings(client)">
                            </mdui-button-icon>
                        </mdui-list-item>
                    </mdui-list>
                </div>
            </mdui-card>
        </div>
    </div>

    <script>
        const { createApp } = Vue;

        createApp({
            data() {
                return {
                    clients: []
                };
            },
            methods: {
                async refreshClients() {
                    const res = await fetch('/api/clients/online');
                    this.clients = await res.json();
                },
                openSettings(client) {
                    // TODO: 打开设置对话框
                }
            },
            mounted() {
                this.refreshClients();
                setInterval(this.refreshClients, 5000);
            }
        }).mount('#app');
    </script>
</body>
</html>
```

### Classtop-Management-Server 改进

#### 1. 添加 WebSocket 支持（可选）

如果选择方案 B，需要添加 WebSocket：

**文件**: `/Users/logos/RustroverProjects/Classtop-Management-Server/src/websocket.rs` (新建)

```rust
use actix::{Actor, StreamHandler};
use actix_web::{web, HttpRequest, HttpResponse};
use actix_web_actors::ws;
use serde::{Deserialize, Serialize};
use std::time::{Duration, Instant};

const HEARTBEAT_INTERVAL: Duration = Duration::from_secs(30);
const CLIENT_TIMEOUT: Duration = Duration::from_secs(60);

#[derive(Serialize, Deserialize)]
struct WsMessage {
    #[serde(rename = "type")]
    msg_type: String,
    data: Option<serde_json::Value>,
}

pub struct ClientWebSocket {
    client_uuid: String,
    last_heartbeat: Instant,
}

impl ClientWebSocket {
    pub fn new(client_uuid: String) -> Self {
        Self {
            client_uuid,
            last_heartbeat: Instant::now(),
        }
    }
}

impl Actor for ClientWebSocket {
    type Context = ws::WebsocketContext<Self>;

    fn started(&mut self, ctx: &mut Self::Context) {
        log::info!("WebSocket connected: {}", self.client_uuid);
        // 启动心跳检测
        self.start_heartbeat(ctx);
    }
}

impl StreamHandler<Result<ws::Message, ws::ProtocolError>> for ClientWebSocket {
    fn handle(&mut self, msg: Result<ws::Message, ws::ProtocolError>, ctx: &mut Self::Context) {
        match msg {
            Ok(ws::Message::Ping(msg)) => {
                self.last_heartbeat = Instant::now();
                ctx.pong(&msg);
            }
            Ok(ws::Message::Pong(_)) => {
                self.last_heartbeat = Instant::now();
            }
            Ok(ws::Message::Text(text)) => {
                // 处理文本消息
                if let Ok(ws_msg) = serde_json::from_str::<WsMessage>(&text) {
                    self.handle_message(ws_msg, ctx);
                }
            }
            Ok(ws::Message::Close(reason)) => {
                ctx.close(reason);
                ctx.stop();
            }
            _ => {}
        }
    }
}

impl ClientWebSocket {
    fn start_heartbeat(&self, ctx: &mut ws::WebsocketContext<Self>) {
        ctx.run_interval(HEARTBEAT_INTERVAL, |act, ctx| {
            if Instant::now().duration_since(act.last_heartbeat) > CLIENT_TIMEOUT {
                log::warn!("Client {} heartbeat timeout, disconnecting", act.client_uuid);
                ctx.stop();
            } else {
                ctx.ping(b"");
            }
        });
    }

    fn handle_message(&self, msg: WsMessage, ctx: &mut ws::WebsocketContext<Self>) {
        match msg.msg_type.as_str() {
            "heartbeat" => {
                // 心跳响应
            }
            "command" => {
                // 处理命令
            }
            _ => {
                log::warn!("Unknown message type: {}", msg.msg_type);
            }
        }
    }
}

pub async fn websocket_route(
    req: HttpRequest,
    stream: web::Payload,
    path: web::Path<String>,
) -> Result<HttpResponse, actix_web::Error> {
    let client_uuid = path.into_inner();
    let ws = ClientWebSocket::new(client_uuid);
    ws::start(ws, &req, stream)
}
```

**在 main.rs 中注册路由**:

```rust
mod websocket;

// 在 HttpServer::new 中添加
.route("/ws/{client_uuid}", web::get().to(websocket::websocket_route))
```

## 📝 文档改进

### 1. 创建统一架构文档

**文件**: `classtop/docs/MANAGEMENT_ARCHITECTURE.md` (新建)

内容应包括：
- 两个管理服务器的定位和使用场景
- 推荐的部署架构
- 数据流向图
- 集成指南

### 2. 更新 README

在 `classtop/README.md` 和 `Classtop-Management-Server/README.md` 中：
- 说明两个管理服务器的关系
- 链接到对方的项目
- 明确使用场景

## 🚀 实施路线图

### 优先级排序

| 优先级 | 任务 | 预计时间 | 依赖 |
|-------|------|---------|------|
| P0 | 实现客户端与 Management-Server 数据同步 | 3-5 天 | 无 |
| P1 | admin-server 添加数据库支持 | 2-3 天 | 无 |
| P2 | 改进 admin-server Web 界面 | 2-3 天 | P1 |
| P2 | 完善文档和部署指南 | 1-2 天 | P0 |
| P3 | 添加认证系统 | 3-5 天 | P0, P1 |
| P3 | 性能优化和测试 | 2-3 天 | P0, P1 |

### 第一周计划

**目标**: 完成数据同步基础功能

- [ ] Day 1-2: 客户端数据库 Schema 更新和 sync_client.py 开发
- [ ] Day 3: 前端设置页面开发
- [ ] Day 4: 本地测试和调试
- [ ] Day 5: 文档编写和 Code Review

### 第二周计划

**目标**: admin-server 改进

- [ ] Day 1-2: 添加数据库支持
- [ ] Day 3-4: 改进 Web 界面
- [ ] Day 5: 测试和优化

## 🎯 推荐方案

**建议采用方案 A（双轨并行）**，原因：

1. **低风险**: 不需要大规模重构
2. **快速交付**: 可以分阶段实施
3. **灵活部署**: 用户可按需选择
4. **职责清晰**:
   - admin-server → 实时控制和监控
   - Management-Server → 数据收集和分析

**下一步行动**:
1. 开始实施客户端数据同步（参考 CLIENT_INTEGRATION_TODO.md）
2. 并行改进 admin-server 的数据持久化
3. 完善文档，说明两个系统的使用场景

是否需要我开始实施某个具体部分？
