# ClassTop 双轨并行架构方案

## 📐 架构概述

### 系统组成

```
┌─────────────────────────────────────────────────────────┐
│                  Management Server                      │
│              (企业级中央管理服务器)                       │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Core Modules                                     │  │
│  │  - Data Sync (HTTP API)                          │  │
│  │  - Statistics & Analytics                        │  │
│  │  - Multi-client Management                       │  │
│  │  - PostgreSQL Persistence                        │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Extended Modules (New)                          │  │
│  │  - WebSocket Real-time Control                   │  │
│  │  - CCTV Management                               │  │
│  │  - LMS Instance Management                       │  │
│  │  - Remote Command Execution                      │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Web UI (Vue 3 + MDUI 2)                        │  │
│  │  - Dashboard                                      │  │
│  │  - Client Management                             │  │
│  │  - Real-time Control Panel                      │  │
│  │  - LMS Instance Monitor                         │  │
│  └──────────────────────────────────────────────────┘  │
└────────────┬──────────────────────────┬─────────────────┘
             │                          │
             │ HTTP/WS                  │ HTTP (管理)
             │                          │
┌────────────▼──────────┐   ┌───────────▼──────────┐
│   ClassTop Client     │   │   LMS Instances      │
│   (Tauri + PyTauri)   │   │   (轻量管理服务)      │
├───────────────────────┤   ├──────────────────────┤
│ - Local UI            │   │ - WebSocket Server   │
│ - SQLite DB           │   │ - Command Router     │
│ - Course Display      │   │ - Client Registry    │
│ - Data Sync Client    │   │ - SQLite Cache       │
│ - WebSocket Client    │   │ - FastAPI            │
└───────────┬───────────┘   └──────────────────────┘
            │                         ▲
            │ WebSocket (实时控制)     │
            └─────────────────────────┘
```

### 角色定位

#### 1. ClassTop Client (客户端)
**定位**: 终端用户应用
- 本地课程管理和显示
- 同时连接 LMS 和 Management-Server
- 响应实时控制命令
- 定期同步数据

#### 2. LMS (轻量管理服务，原 admin-server)
**定位**: 轻量级现场管理服务
- 部署在本地网络
- 管理 10-50 个客户端
- 提供实时控制和监控
- 低延迟 WebSocket 连接
- 可选离线运行

**使用场景**:
- 学校机房管理
- 教室设备控制
- 实时监控需求
- 网络隔离环境

#### 3. Management-Server (中央管理服务器)
**定位**: 企业级中央管理平台
- 部署在云端或数据中心
- 管理数百至数千个客户端
- 集中数据存储和分析
- 管理多个 LMS 实例
- 提供统一管理界面

**使用场景**:
- 多校区统一管理
- 数据分析和报表
- 长期数据存储
- 跨地域管理

## 🔄 通信模式

### 客户端 ↔ LMS (实时控制)

**协议**: WebSocket
**用途**: 低延迟实时控制

```
Client                    LMS
  │                        │
  ├──── Connect (WS) ─────>│
  │<──── Accept ───────────┤
  │                        │
  ├──── Heartbeat ────────>│
  │<──── ACK ───────────────┤
  │                        │
  │<──── Command ───────────┤ (设置修改/CCTV控制)
  ├──── Response ─────────>│
  │                        │
```

**支持的操作**:
- 实时设置修改
- CCTV 录制/推流控制
- 状态查询
- 日志获取

### 客户端 ↔ Management-Server (数据同步)

**协议**: HTTP REST API
**用途**: 批量数据同步

```
Client                Management-Server
  │                        │
  ├──── Register (POST) ──>│
  │<──── UUID ─────────────┤
  │                        │
  ├──── Sync Data (POST) ─>│ (定期，如每5分钟)
  │<──── Result ───────────┤
  │                        │
```

**同步的数据**:
- 课程和课程表
- 客户端状态
- 设置快照
- CCTV 配置

### Management-Server ↔ LMS (实例管理)

**协议**: HTTP + WebSocket
**用途**: 管理和监控 LMS 实例

```
LMS                   Management-Server
  │                        │
  ├──── Register (POST) ──>│ (启动时)
  │<──── API Key ──────────┤
  │                        │
  ├──── Heartbeat (WS) ───>│ (每30秒)
  │<──── ACK ──────────────┤
  │                        │
  │<──── Query Clients ─────┤ (查询LMS管理的客户端)
  ├──── Client List ──────>│
  │                        │
```

**管理功能**:
- LMS 实例注册
- 健康检查
- 客户端列表同步
- 配置分发
- 日志收集

## 📝 详细设计

### 1. LMS (轻量管理服务) 重命名和改进

#### 目录结构调整

```bash
# 当前
classtop/admin-server/

# 改为
classtop/lms/  (Light Management Service)
```

#### 改进内容

**A. 添加数据持久化**

```python
# lms/db.py (新建)
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

class LMSDatabase:
    """LMS 本地数据库"""

    def __init__(self, db_path: str = "lms.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.init_db()

    def init_db(self):
        """初始化数据库"""
        cursor = self.conn.cursor()

        # LMS 配置
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lms_config (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 客户端注册信息
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                uuid TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                ip_address TEXT,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'online',
                metadata TEXT
            )
        """)

        # 连接历史
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS connection_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_uuid TEXT NOT NULL,
                event_type TEXT NOT NULL,
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

    def register_client(self, uuid: str, name: str, ip: str, metadata: dict = None):
        """注册客户端"""
        import json
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO clients (uuid, name, ip_address, last_seen, status, metadata)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP, 'online', ?)
        """, (uuid, name, ip, json.dumps(metadata) if metadata else None))
        self.conn.commit()

    def update_client_status(self, uuid: str, status: str):
        """更新客户端状态"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE clients SET status = ?, last_seen = CURRENT_TIMESTAMP
            WHERE uuid = ?
        """, (status, uuid))
        self.conn.commit()

    def log_command(self, uuid: str, command: str, params: dict, response: dict, success: bool):
        """记录命令执行"""
        import json
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO command_logs (client_uuid, command, params, response, success)
            VALUES (?, ?, ?, ?, ?)
        """, (uuid, command, json.dumps(params), json.dumps(response), success))
        self.conn.commit()

    def get_online_clients(self) -> List[Dict]:
        """获取在线客户端"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT uuid, name, ip_address, last_seen, status
            FROM clients
            WHERE status = 'online'
            ORDER BY last_seen DESC
        """)
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_client_stats(self, uuid: str) -> Dict:
        """获取客户端统计"""
        cursor = self.conn.cursor()

        # 命令执行统计
        cursor.execute("""
            SELECT
                COUNT(*) as total_commands,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_commands,
                MAX(executed_at) as last_command_time
            FROM command_logs
            WHERE client_uuid = ?
        """, (uuid,))
        result = cursor.fetchone()

        return {
            "total_commands": result[0] or 0,
            "successful_commands": result[1] or 0,
            "last_command_time": result[2]
        }
```

**B. 注册到 Management-Server**

```python
# lms/management_client.py (新建)
import requests
import uuid
import socket
import time
import threading
from typing import Optional

class ManagementClient:
    """连接到 Management-Server 的客户端"""

    def __init__(self, management_url: str, lms_db):
        self.management_url = management_url
        self.lms_db = lms_db
        self.lms_uuid = self._get_or_create_uuid()
        self.api_key = None
        self.heartbeat_thread = None
        self.is_running = False

    def _get_or_create_uuid(self) -> str:
        """获取或创建 LMS UUID"""
        cursor = self.lms_db.conn.cursor()
        cursor.execute("SELECT value FROM lms_config WHERE key = 'lms_uuid'")
        result = cursor.fetchone()

        if result:
            return result[0]
        else:
            lms_uuid = str(uuid.uuid4())
            cursor.execute(
                "INSERT INTO lms_config (key, value) VALUES ('lms_uuid', ?)",
                (lms_uuid,)
            )
            self.lms_db.conn.commit()
            return lms_uuid

    def register(self) -> bool:
        """注册 LMS 到 Management-Server"""
        try:
            data = {
                "lms_uuid": self.lms_uuid,
                "name": f"LMS-{socket.gethostname()}",
                "host": socket.gethostbyname(socket.gethostname()),
                "port": 8000,  # LMS 端口
                "version": "1.0.0"
            }

            url = f"{self.management_url}/api/lms/register"
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()

            result = response.json()
            if result.get("success"):
                self.api_key = result["data"].get("api_key")
                # 保存 API Key
                cursor = self.lms_db.conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO lms_config (key, value) VALUES ('api_key', ?)",
                    (self.api_key,)
                )
                self.lms_db.conn.commit()
                print(f"✓ LMS 注册成功: {self.lms_uuid}")
                return True

        except Exception as e:
            print(f"✗ LMS 注册失败: {e}")
            return False

    def start_heartbeat(self):
        """启动心跳线程"""
        if self.is_running:
            return

        self.is_running = True
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self.heartbeat_thread.start()

    def _heartbeat_loop(self):
        """心跳循环"""
        while self.is_running:
            try:
                # 获取在线客户端列表
                clients = self.lms_db.get_online_clients()

                data = {
                    "lms_uuid": self.lms_uuid,
                    "client_count": len(clients),
                    "clients": [
                        {
                            "uuid": c["uuid"],
                            "name": c["name"],
                            "status": c["status"]
                        }
                        for c in clients
                    ]
                }

                headers = {"Authorization": f"Bearer {self.api_key}"}
                url = f"{self.management_url}/api/lms/heartbeat"
                response = requests.post(url, json=data, headers=headers, timeout=5)

                if response.status_code == 200:
                    print(f"✓ 心跳成功: {len(clients)} 个在线客户端")
                else:
                    print(f"✗ 心跳失败: {response.status_code}")

            except Exception as e:
                print(f"✗ 心跳异常: {e}")

            time.sleep(30)  # 每30秒一次

    def stop_heartbeat(self):
        """停止心跳"""
        self.is_running = False
        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=5)
```

**C. 更新 main.py 集成**

```python
# lms/main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from websocket_manager import manager
from db import LMSDatabase
from management_client import ManagementClient
import os

app = FastAPI(title="LMS - Light Management Service")

# 初始化数据库
lms_db = LMSDatabase()

# 初始化 Management-Server 客户端
management_url = os.getenv("MANAGEMENT_SERVER_URL", "http://localhost:8765")
management_client = ManagementClient(management_url, lms_db) if management_url else None

@app.on_event("startup")
async def startup():
    """启动时注册到 Management-Server"""
    if management_client:
        if management_client.register():
            management_client.start_heartbeat()

@app.on_event("shutdown")
async def shutdown():
    """关闭时停止心跳"""
    if management_client:
        management_client.stop_heartbeat()

@app.websocket("/ws/{client_uuid}")
async def websocket_endpoint(websocket: WebSocket, client_uuid: str):
    await manager.connect(client_uuid, websocket)

    # 记录连接
    client_info = await websocket.receive_json()
    lms_db.register_client(
        client_uuid,
        client_info.get("name", "Unknown"),
        websocket.client.host
    )

    try:
        while True:
            data = await websocket.receive_json()

            # 处理消息
            if data.get("type") == "heartbeat":
                await websocket.send_json({"type": "heartbeat_ack"})
                lms_db.update_client_status(client_uuid, "online")

            elif data.get("type") == "response":
                # 记录命令响应
                request_id = data.get("request_id")
                lms_db.log_command(
                    client_uuid,
                    data.get("command", ""),
                    {},
                    data.get("data", {}),
                    data.get("success", False)
                )

    except WebSocketDisconnect:
        manager.disconnect(client_uuid)
        lms_db.update_client_status(client_uuid, "offline")

# ... 其他路由保持不变 ...
```

### 2. Management-Server 功能扩展

#### A. 添加 LMS 实例管理

**数据库 Schema 更新**

```sql
-- migrations/003_add_lms_support.sql

-- LMS 实例表
CREATE TABLE IF NOT EXISTS lms_instances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lms_uuid UUID NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    host VARCHAR(255),
    port INTEGER DEFAULT 8000,
    api_key VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'offline',  -- online, offline, error
    last_heartbeat TIMESTAMPTZ,
    client_count INTEGER DEFAULT 0,
    version VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- LMS 管理的客户端关系表
CREATE TABLE IF NOT EXISTS lms_client_mapping (
    id SERIAL PRIMARY KEY,
    lms_id UUID NOT NULL REFERENCES lms_instances(id) ON DELETE CASCADE,
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    connected_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(lms_id, client_id)
);

-- LMS 心跳日志
CREATE TABLE IF NOT EXISTS lms_heartbeats (
    id SERIAL PRIMARY KEY,
    lms_id UUID NOT NULL REFERENCES lms_instances(id) ON DELETE CASCADE,
    client_count INTEGER,
    received_at TIMESTAMPTZ DEFAULT NOW()
);

-- 为 clients 表添加 lms_id 字段
ALTER TABLE clients ADD COLUMN IF NOT EXISTS lms_id UUID REFERENCES lms_instances(id);

-- 索引
CREATE INDEX IF NOT EXISTS idx_lms_status ON lms_instances(status);
CREATE INDEX IF NOT EXISTS idx_lms_last_heartbeat ON lms_instances(last_heartbeat);
CREATE INDEX IF NOT EXISTS idx_lms_client_mapping_lms ON lms_client_mapping(lms_id);
CREATE INDEX IF NOT EXISTS idx_clients_lms_id ON clients(lms_id);
```

**Rust 数据模型**

```rust
// src/models.rs

use serde::{Deserialize, Serialize};
use utoipa::ToSchema;
use uuid::Uuid;
use chrono::{DateTime, Utc};

#[derive(Debug, Serialize, Deserialize, ToSchema)]
pub struct LMSInstance {
    pub id: Uuid,
    pub lms_uuid: Uuid,
    pub name: String,
    pub host: Option<String>,
    pub port: i32,
    pub status: String,
    pub last_heartbeat: Option<DateTime<Utc>>,
    pub client_count: i32,
    pub version: Option<String>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Deserialize, ToSchema)]
pub struct RegisterLMSRequest {
    pub lms_uuid: Uuid,
    pub name: String,
    pub host: String,
    pub port: i32,
    pub version: String,
}

#[derive(Debug, Serialize, ToSchema)]
pub struct RegisterLMSResponse {
    pub lms_id: Uuid,
    pub api_key: String,
}

#[derive(Debug, Deserialize, ToSchema)]
pub struct LMSHeartbeatRequest {
    pub lms_uuid: Uuid,
    pub client_count: i32,
    pub clients: Vec<LMSClientInfo>,
}

#[derive(Debug, Deserialize, Serialize, ToSchema)]
pub struct LMSClientInfo {
    pub uuid: Uuid,
    pub name: String,
    pub status: String,
}
```

**API Handler**

```rust
// src/handlers/lms.rs (新建)

use actix_web::{web, HttpResponse};
use sqlx::PgPool;
use uuid::Uuid;
use crate::models::*;
use crate::db::repository::Repository;
use crate::error::{AppError, AppResult};

/// 注册 LMS 实例
#[utoipa::path(
    post,
    path = "/api/lms/register",
    request_body = RegisterLMSRequest,
    responses(
        (status = 200, description = "LMS registered successfully", body = ApiResponse<RegisterLMSResponse>),
        (status = 400, description = "Bad request"),
        (status = 500, description = "Internal server error")
    ),
    tag = "LMS Management"
)]
pub async fn register_lms(
    pool: web::Data<PgPool>,
    req: web::Json<RegisterLMSRequest>,
) -> AppResult<HttpResponse> {
    let repo = Repository::new(pool.get_ref().clone());

    // 生成 API Key
    let api_key = generate_api_key();

    // 注册 LMS
    let lms_id = repo.register_lms(
        req.lms_uuid,
        &req.name,
        &req.host,
        req.port,
        &api_key,
        &req.version,
    ).await?;

    let response = RegisterLMSResponse {
        lms_id,
        api_key,
    };

    Ok(HttpResponse::Ok().json(ApiResponse::success(response)))
}

/// LMS 心跳
#[utoipa::path(
    post,
    path = "/api/lms/heartbeat",
    request_body = LMSHeartbeatRequest,
    responses(
        (status = 200, description = "Heartbeat received"),
        (status = 401, description = "Unauthorized"),
        (status = 404, description = "LMS not found")
    ),
    tag = "LMS Management",
    security(("api_key" = []))
)]
pub async fn lms_heartbeat(
    pool: web::Data<PgPool>,
    req: web::Json<LMSHeartbeatRequest>,
    // TODO: 添加 API Key 验证中间件
) -> AppResult<HttpResponse> {
    let repo = Repository::new(pool.get_ref().clone());

    // 更新 LMS 状态
    repo.update_lms_heartbeat(
        req.lms_uuid,
        req.client_count,
        &req.clients,
    ).await?;

    Ok(HttpResponse::Ok().json(ApiResponse::success("Heartbeat received")))
}

/// 获取所有 LMS 实例
#[utoipa::path(
    get,
    path = "/api/lms",
    responses(
        (status = 200, description = "List of LMS instances", body = ApiResponse<Vec<LMSInstance>>)
    ),
    tag = "LMS Management"
)]
pub async fn list_lms(
    pool: web::Data<PgPool>,
) -> AppResult<HttpResponse> {
    let repo = Repository::new(pool.get_ref().clone());
    let instances = repo.get_all_lms_instances().await?;
    Ok(HttpResponse::Ok().json(ApiResponse::success(instances)))
}

/// 获取单个 LMS 实例详情
#[utoipa::path(
    get,
    path = "/api/lms/{lms_id}",
    params(
        ("lms_id" = Uuid, Path, description = "LMS instance ID")
    ),
    responses(
        (status = 200, description = "LMS instance details", body = ApiResponse<LMSInstance>),
        (status = 404, description = "LMS not found")
    ),
    tag = "LMS Management"
)]
pub async fn get_lms(
    pool: web::Data<PgPool>,
    lms_id: web::Path<Uuid>,
) -> AppResult<HttpResponse> {
    let repo = Repository::new(pool.get_ref().clone());
    let instance = repo.get_lms_by_id(*lms_id).await?;
    Ok(HttpResponse::Ok().json(ApiResponse::success(instance)))
}

/// 获取 LMS 管理的客户端列表
#[utoipa::path(
    get,
    path = "/api/lms/{lms_id}/clients",
    params(
        ("lms_id" = Uuid, Path, description = "LMS instance ID")
    ),
    responses(
        (status = 200, description = "List of clients managed by this LMS", body = ApiResponse<Vec<Client>>)
    ),
    tag = "LMS Management"
)]
pub async fn get_lms_clients(
    pool: web::Data<PgPool>,
    lms_id: web::Path<Uuid>,
) -> AppResult<HttpResponse> {
    let repo = Repository::new(pool.get_ref().clone());
    let clients = repo.get_clients_by_lms(*lms_id).await?;
    Ok(HttpResponse::Ok().json(ApiResponse::success(clients)))
}

/// 删除 LMS 实例
#[utoipa::path(
    delete,
    path = "/api/lms/{lms_id}",
    params(
        ("lms_id" = Uuid, Path, description = "LMS instance ID")
    ),
    responses(
        (status = 200, description = "LMS deleted successfully"),
        (status = 404, description = "LMS not found")
    ),
    tag = "LMS Management"
)]
pub async fn delete_lms(
    pool: web::Data<PgPool>,
    lms_id: web::Path<Uuid>,
) -> AppResult<HttpResponse> {
    let repo = Repository::new(pool.get_ref().clone());
    repo.delete_lms(*lms_id).await?;
    Ok(HttpResponse::Ok().json(ApiResponse::success("LMS deleted")))
}

// 辅助函数
fn generate_api_key() -> String {
    use rand::Rng;
    const CHARSET: &[u8] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    let mut rng = rand::thread_rng();
    (0..32)
        .map(|_| {
            let idx = rng.gen_range(0..CHARSET.len());
            CHARSET[idx] as char
        })
        .collect()
}
```

**数据库操作 (Repository)**

```rust
// src/db.rs - 添加到 Repository impl

impl Repository {
    pub async fn register_lms(
        &self,
        lms_uuid: Uuid,
        name: &str,
        host: &str,
        port: i32,
        api_key: &str,
        version: &str,
    ) -> AppResult<Uuid> {
        let row = sqlx::query!(
            r#"
            INSERT INTO lms_instances (lms_uuid, name, host, port, api_key, version, status)
            VALUES ($1, $2, $3, $4, $5, $6, 'online')
            RETURNING id
            "#,
            lms_uuid,
            name,
            host,
            port,
            api_key,
            version
        )
        .fetch_one(&self.pool)
        .await
        .map_err(|e| AppError::Database(e.to_string()))?;

        Ok(row.id)
    }

    pub async fn update_lms_heartbeat(
        &self,
        lms_uuid: Uuid,
        client_count: i32,
        clients: &[LMSClientInfo],
    ) -> AppResult<()> {
        // 更新 LMS 状态
        sqlx::query!(
            r#"
            UPDATE lms_instances
            SET last_heartbeat = NOW(),
                client_count = $2,
                status = 'online',
                updated_at = NOW()
            WHERE lms_uuid = $1
            "#,
            lms_uuid,
            client_count
        )
        .execute(&self.pool)
        .await
        .map_err(|e| AppError::Database(e.to_string()))?;

        // 记录心跳日志
        let lms_id = self.get_lms_id_by_uuid(lms_uuid).await?;
        sqlx::query!(
            r#"
            INSERT INTO lms_heartbeats (lms_id, client_count)
            VALUES ($1, $2)
            "#,
            lms_id,
            client_count
        )
        .execute(&self.pool)
        .await
        .map_err(|e| AppError::Database(e.to_string()))?;

        // 更新客户端与 LMS 的映射关系
        for client in clients {
            sqlx::query!(
                r#"
                INSERT INTO lms_client_mapping (lms_id, client_id)
                VALUES ($1, $2)
                ON CONFLICT (lms_id, client_id) DO NOTHING
                "#,
                lms_id,
                client.uuid
            )
            .execute(&self.pool)
            .await
            .ok(); // 忽略错误，客户端可能未注册到 Management-Server
        }

        Ok(())
    }

    pub async fn get_all_lms_instances(&self) -> AppResult<Vec<LMSInstance>> {
        let instances = sqlx::query_as!(
            LMSInstance,
            r#"
            SELECT id, lms_uuid, name, host, port, status,
                   last_heartbeat, client_count, version,
                   created_at, updated_at
            FROM lms_instances
            ORDER BY created_at DESC
            "#
        )
        .fetch_all(&self.pool)
        .await
        .map_err(|e| AppError::Database(e.to_string()))?;

        Ok(instances)
    }

    pub async fn get_lms_by_id(&self, lms_id: Uuid) -> AppResult<LMSInstance> {
        let instance = sqlx::query_as!(
            LMSInstance,
            r#"
            SELECT id, lms_uuid, name, host, port, status,
                   last_heartbeat, client_count, version,
                   created_at, updated_at
            FROM lms_instances
            WHERE id = $1
            "#,
            lms_id
        )
        .fetch_optional(&self.pool)
        .await
        .map_err(|e| AppError::Database(e.to_string()))?
        .ok_or(AppError::NotFound("LMS instance not found".to_string()))?;

        Ok(instance)
    }

    pub async fn get_clients_by_lms(&self, lms_id: Uuid) -> AppResult<Vec<Client>> {
        let clients = sqlx::query_as!(
            Client,
            r#"
            SELECT c.id, c.uuid, c.name, c.api_url, c.status,
                   c.last_sync, c.created_at
            FROM clients c
            INNER JOIN lms_client_mapping lcm ON c.id = lcm.client_id
            WHERE lcm.lms_id = $1
            ORDER BY c.name
            "#,
            lms_id
        )
        .fetch_all(&self.pool)
        .await
        .map_err(|e| AppError::Database(e.to_string()))?;

        Ok(clients)
    }

    pub async fn delete_lms(&self, lms_id: Uuid) -> AppResult<()> {
        sqlx::query!(
            "DELETE FROM lms_instances WHERE id = $1",
            lms_id
        )
        .execute(&self.pool)
        .await
        .map_err(|e| AppError::Database(e.to_string()))?;

        Ok(())
    }

    async fn get_lms_id_by_uuid(&self, lms_uuid: Uuid) -> AppResult<Uuid> {
        let row = sqlx::query!(
            "SELECT id FROM lms_instances WHERE lms_uuid = $1",
            lms_uuid
        )
        .fetch_optional(&self.pool)
        .await
        .map_err(|e| AppError::Database(e.to_string()))?
        .ok_or(AppError::NotFound("LMS not found".to_string()))?;

        Ok(row.id)
    }
}
```

#### B. 添加 WebSocket 实时控制功能

**WebSocket Handler**

```rust
// src/handlers/websocket.rs (新建)

use actix::{Actor, StreamHandler, Handler, Message as ActixMessage, AsyncContext};
use actix_web::{web, HttpRequest, HttpResponse, Error};
use actix_web_actors::ws;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use uuid::Uuid;

/// WebSocket 消息类型
#[derive(Debug, Serialize, Deserialize)]
#[serde(tag = "type")]
pub enum WSMessage {
    #[serde(rename = "command")]
    Command {
        target_client: Uuid,
        request_id: String,
        command: String,
        params: serde_json::Value,
    },
    #[serde(rename = "response")]
    Response {
        request_id: String,
        success: bool,
        data: serde_json::Value,
    },
    #[serde(rename = "heartbeat")]
    Heartbeat,
    #[serde(rename = "register")]
    Register {
        client_uuid: Uuid,
        client_type: String, // "client" 或 "lms"
    },
}

/// WebSocket 连接管理器
pub struct WSConnectionManager {
    // client_uuid -> WebSocket Actor Address
    connections: Arc<Mutex<HashMap<Uuid, actix::Addr<WSConnection>>>>,
}

impl WSConnectionManager {
    pub fn new() -> Self {
        Self {
            connections: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    pub fn register(&self, uuid: Uuid, addr: actix::Addr<WSConnection>) {
        self.connections.lock().unwrap().insert(uuid, addr);
    }

    pub fn unregister(&self, uuid: &Uuid) {
        self.connections.lock().unwrap().remove(uuid);
    }

    pub fn send_to_client(&self, uuid: Uuid, msg: WSMessage) -> Result<(), String> {
        if let Some(addr) = self.connections.lock().unwrap().get(&uuid) {
            addr.do_send(SendWSMessage(msg));
            Ok(())
        } else {
            Err(format!("Client {} not connected", uuid))
        }
    }

    pub fn get_online_count(&self) -> usize {
        self.connections.lock().unwrap().len()
    }
}

/// WebSocket Actor
pub struct WSConnection {
    uuid: Option<Uuid>,
    client_type: Option<String>,
    manager: web::Data<WSConnectionManager>,
}

impl Actor for WSConnection {
    type Context = ws::WebsocketContext<Self>;

    fn started(&mut self, ctx: &mut Self::Context) {
        println!("WebSocket connection started");
    }

    fn stopped(&mut self, _: &mut Self::Context) {
        if let Some(uuid) = self.uuid {
            self.manager.unregister(&uuid);
            println!("WebSocket disconnected: {}", uuid);
        }
    }
}

/// 处理 WebSocket 消息
impl StreamHandler<Result<ws::Message, ws::ProtocolError>> for WSConnection {
    fn handle(&mut self, msg: Result<ws::Message, ws::ProtocolError>, ctx: &mut Self::Context) {
        match msg {
            Ok(ws::Message::Ping(msg)) => ctx.pong(&msg),
            Ok(ws::Message::Pong(_)) => {}
            Ok(ws::Message::Text(text)) => {
                // 解析消息
                match serde_json::from_str::<WSMessage>(&text) {
                    Ok(ws_msg) => self.handle_ws_message(ws_msg, ctx),
                    Err(e) => eprintln!("Failed to parse WebSocket message: {}", e),
                }
            }
            Ok(ws::Message::Binary(_)) => {
                eprintln!("Binary messages not supported");
            }
            Ok(ws::Message::Close(reason)) => {
                ctx.close(reason);
                ctx.stop();
            }
            _ => (),
        }
    }
}

impl WSConnection {
    fn handle_ws_message(&mut self, msg: WSMessage, ctx: &mut ws::WebsocketContext<Self>) {
        match msg {
            WSMessage::Register { client_uuid, client_type } => {
                self.uuid = Some(client_uuid);
                self.client_type = Some(client_type.clone());
                self.manager.register(client_uuid, ctx.address());

                println!("Client registered: {} (type: {})", client_uuid, client_type);

                // 发送确认
                let response = WSMessage::Response {
                    request_id: "register".to_string(),
                    success: true,
                    data: serde_json::json!({"message": "Registered successfully"}),
                };
                ctx.text(serde_json::to_string(&response).unwrap());
            }
            WSMessage::Heartbeat => {
                let response = WSMessage::Response {
                    request_id: "heartbeat".to_string(),
                    success: true,
                    data: serde_json::json!({"timestamp": chrono::Utc::now()}),
                };
                ctx.text(serde_json::to_string(&response).unwrap());
            }
            WSMessage::Response { .. } => {
                // 响应消息会被路由到等待的请求
                // 这里可以实现请求-响应映射逻辑
                if let Ok(json) = serde_json::to_string(&msg) {
                    ctx.text(json);
                }
            }
            _ => {}
        }
    }
}

/// 内部消息：发送 WebSocket 消息
#[derive(ActixMessage)]
#[rtype(result = "()")]
struct SendWSMessage(WSMessage);

impl Handler<SendWSMessage> for WSConnection {
    type Result = ();

    fn handle(&mut self, msg: SendWSMessage, ctx: &mut Self::Context) {
        if let Ok(json) = serde_json::to_string(&msg.0) {
            ctx.text(json);
        }
    }
}

/// WebSocket 端点
pub async fn ws_endpoint(
    req: HttpRequest,
    stream: web::Payload,
    manager: web::Data<WSConnectionManager>,
) -> Result<HttpResponse, Error> {
    ws::start(
        WSConnection {
            uuid: None,
            client_type: None,
            manager,
        },
        &req,
        stream,
    )
}

/// HTTP API：向客户端发送命令
#[utoipa::path(
    post,
    path = "/api/control/command",
    request_body = SendCommandRequest,
    responses(
        (status = 200, description = "Command sent successfully"),
        (status = 404, description = "Client not connected")
    ),
    tag = "Real-time Control"
)]
pub async fn send_command(
    manager: web::Data<WSConnectionManager>,
    req: web::Json<SendCommandRequest>,
) -> Result<HttpResponse, Error> {
    let msg = WSMessage::Command {
        target_client: req.target_client,
        request_id: req.request_id.clone(),
        command: req.command.clone(),
        params: req.params.clone(),
    };

    match manager.send_to_client(req.target_client, msg) {
        Ok(_) => Ok(HttpResponse::Ok().json(serde_json::json!({
            "success": true,
            "message": "Command sent"
        }))),
        Err(e) => Ok(HttpResponse::NotFound().json(serde_json::json!({
            "success": false,
            "error": e
        }))),
    }
}

#[derive(Debug, Deserialize)]
pub struct SendCommandRequest {
    pub target_client: Uuid,
    pub request_id: String,
    pub command: String,
    pub params: serde_json::Value,
}
```

**路由注册**

```rust
// src/main.rs - 添加 WebSocket 路由

use actix_web::{web, App, HttpServer};
mod handlers;
use handlers::websocket::{ws_endpoint, send_command, WSConnectionManager};

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // ... 初始化数据库连接池 ...

    // 创建 WebSocket 连接管理器
    let ws_manager = web::Data::new(WSConnectionManager::new());

    HttpServer::new(move || {
        App::new()
            .app_data(pool.clone())
            .app_data(ws_manager.clone())
            // WebSocket 路由
            .route("/ws", web::get().to(ws_endpoint))
            .route("/api/control/command", web::post().to(send_command))
            // ... 其他路由 ...
    })
    .bind(("0.0.0.0", 8765))?
    .run()
    .await
}
```

#### C. 添加 CCTV 管理功能

**数据模型**

```rust
// src/models.rs - 添加 CCTV 相关模型

#[derive(Debug, Serialize, Deserialize, ToSchema)]
pub struct CCTVConfig {
    pub id: Uuid,
    pub client_id: Uuid,
    pub camera_id: String,
    pub camera_name: String,
    pub rtsp_url: Option<String>,
    pub recording_enabled: bool,
    pub streaming_enabled: bool,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Deserialize, ToSchema)]
pub struct UpdateCCTVRequest {
    pub camera_name: Option<String>,
    pub rtsp_url: Option<String>,
    pub recording_enabled: Option<bool>,
    pub streaming_enabled: Option<bool>,
}

#[derive(Debug, Serialize, ToSchema)]
pub struct CCTVStatus {
    pub camera_id: String,
    pub is_recording: bool,
    pub is_streaming: bool,
    pub last_frame_time: Option<DateTime<Utc>>,
}
```

**数据库迁移**

```sql
-- migrations/004_add_cctv_support.sql

CREATE TABLE IF NOT EXISTS cctv_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    camera_id VARCHAR(100) NOT NULL,
    camera_name VARCHAR(255) NOT NULL,
    rtsp_url TEXT,
    recording_enabled BOOLEAN DEFAULT FALSE,
    streaming_enabled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(client_id, camera_id)
);

CREATE TABLE IF NOT EXISTS cctv_events (
    id SERIAL PRIMARY KEY,
    camera_config_id UUID NOT NULL REFERENCES cctv_configs(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL, -- start_recording, stop_recording, start_stream, stop_stream, error
    details JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cctv_configs_client ON cctv_configs(client_id);
CREATE INDEX IF NOT EXISTS idx_cctv_events_camera ON cctv_events(camera_config_id);
CREATE INDEX IF NOT EXISTS idx_cctv_events_time ON cctv_events(created_at);
```

### 3. 客户端更新

#### A. 双连接支持

**配置更新**

```python
# src-tauri/python/tauri_app/settings_manager.py

class SettingsManager:
    """设置管理器"""

    DEFAULT_SETTINGS = {
        # ... 现有设置 ...

        # LMS 连接配置
        "lms_enabled": "true",
        "lms_url": "ws://localhost:8000/ws",
        "lms_auto_reconnect": "true",

        # Management-Server 连接配置
        "management_server_enabled": "true",
        "management_server_url": "http://localhost:8765",
        "management_ws_url": "ws://localhost:8765/ws",
        "sync_interval": "300",  # 5分钟

        # 双连接模式
        "dual_connection_mode": "both",  # lms_only, management_only, both
    }
```

**连接管理器**

```python
# src-tauri/python/tauri_app/connection_manager.py (新建)

import asyncio
import websockets
import json
from typing import Optional, Callable
from datetime import datetime

class LMSConnection:
    """LMS WebSocket 连接"""

    def __init__(self, url: str, client_uuid: str, on_command: Callable):
        self.url = url
        self.client_uuid = client_uuid
        self.on_command = on_command
        self.websocket = None
        self.is_connected = False
        self.reconnect_task = None

    async def connect(self):
        """连接到 LMS"""
        try:
            self.websocket = await websockets.connect(self.url)
            self.is_connected = True

            # 发送注册消息
            await self.websocket.send(json.dumps({
                "type": "register",
                "client_uuid": self.client_uuid,
                "client_type": "client"
            }))

            # 启动消息处理循环
            asyncio.create_task(self._message_loop())

            print(f"✓ Connected to LMS: {self.url}")
            return True

        except Exception as e:
            print(f"✗ Failed to connect to LMS: {e}")
            self.is_connected = False
            return False

    async def _message_loop(self):
        """消息处理循环"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                await self._handle_message(data)
        except Exception as e:
            print(f"✗ LMS message loop error: {e}")
            self.is_connected = False
            # 触发重连
            asyncio.create_task(self.reconnect())

    async def _handle_message(self, data: dict):
        """处理收到的消息"""
        msg_type = data.get("type")

        if msg_type == "command":
            # 执行命令
            request_id = data.get("request_id")
            command = data.get("command")
            params = data.get("params", {})

            try:
                result = await self.on_command(command, params)
                response = {
                    "type": "response",
                    "request_id": request_id,
                    "success": True,
                    "data": result
                }
            except Exception as e:
                response = {
                    "type": "response",
                    "request_id": request_id,
                    "success": False,
                    "data": {"error": str(e)}
                }

            await self.websocket.send(json.dumps(response))

        elif msg_type == "response":
            # 响应消息
            print(f"Received response: {data}")

    async def send_heartbeat(self):
        """发送心跳"""
        if self.is_connected and self.websocket:
            try:
                await self.websocket.send(json.dumps({"type": "heartbeat"}))
            except Exception as e:
                print(f"✗ Heartbeat failed: {e}")
                self.is_connected = False

    async def reconnect(self):
        """重连"""
        await asyncio.sleep(5)  # 5秒后重试
        await self.connect()

    async def close(self):
        """关闭连接"""
        self.is_connected = False
        if self.websocket:
            await self.websocket.close()


class ManagementServerConnection:
    """Management-Server HTTP 连接"""

    def __init__(self, base_url: str, ws_url: str, client_uuid: str):
        self.base_url = base_url
        self.ws_url = ws_url
        self.client_uuid = client_uuid
        self.ws_connection = None
        self.sync_task = None

    async def register(self) -> bool:
        """注册客户端"""
        import aiohttp

        try:
            async with aiohttp.ClientSession() as session:
                data = {
                    "uuid": self.client_uuid,
                    "name": f"ClassTop-{self.client_uuid[:8]}",
                    "api_url": "http://localhost:1420"  # 客户端本地 API
                }

                async with session.post(
                    f"{self.base_url}/api/clients/register",
                    json=data
                ) as resp:
                    if resp.status == 200:
                        print(f"✓ Registered to Management-Server")
                        return True
                    else:
                        print(f"✗ Registration failed: {resp.status}")
                        return False

        except Exception as e:
            print(f"✗ Failed to register: {e}")
            return False

    async def sync_data(self, courses: list, schedules: list, settings: dict):
        """同步数据到 Management-Server"""
        import aiohttp

        try:
            async with aiohttp.ClientSession() as session:
                data = {
                    "client_uuid": self.client_uuid,
                    "courses": courses,
                    "schedules": schedules,
                    "settings": settings,
                    "timestamp": datetime.utcnow().isoformat()
                }

                async with session.post(
                    f"{self.base_url}/api/sync",
                    json=data
                ) as resp:
                    if resp.status == 200:
                        print(f"✓ Data synced successfully")
                        return True
                    else:
                        print(f"✗ Sync failed: {resp.status}")
                        return False

        except Exception as e:
            print(f"✗ Sync error: {e}")
            return False

    async def start_periodic_sync(self, interval: int, get_data_func: Callable):
        """启动定期同步"""
        while True:
            await asyncio.sleep(interval)

            # 获取当前数据
            data = await get_data_func()
            await self.sync_data(
                data.get("courses", []),
                data.get("schedules", []),
                data.get("settings", {})
            )

    async def connect_websocket(self, on_command: Callable):
        """连接 WebSocket 以接收实时控制"""
        self.ws_connection = LMSConnection(
            self.ws_url,
            self.client_uuid,
            on_command
        )
        await self.ws_connection.connect()


class ConnectionManager:
    """统一连接管理器"""

    def __init__(self, settings_manager):
        self.settings = settings_manager
        self.lms_conn: Optional[LMSConnection] = None
        self.mgmt_conn: Optional[ManagementServerConnection] = None
        self.client_uuid = self._get_client_uuid()

    def _get_client_uuid(self) -> str:
        """获取客户端 UUID"""
        import uuid
        # 从配置读取或生成新的
        client_uuid = self.settings.get_setting("client_uuid")
        if not client_uuid:
            client_uuid = str(uuid.uuid4())
            self.settings.update_setting("client_uuid", client_uuid)
        return client_uuid

    async def initialize(self, command_handler: Callable):
        """初始化所有连接"""
        mode = self.settings.get_setting("dual_connection_mode")

        if mode in ["lms_only", "both"]:
            await self._init_lms_connection(command_handler)

        if mode in ["management_only", "both"]:
            await self._init_management_connection(command_handler)

    async def _init_lms_connection(self, command_handler: Callable):
        """初始化 LMS 连接"""
        if self.settings.get_setting("lms_enabled") == "true":
            lms_url = self.settings.get_setting("lms_url")
            self.lms_conn = LMSConnection(lms_url, self.client_uuid, command_handler)
            await self.lms_conn.connect()

    async def _init_management_connection(self, command_handler: Callable):
        """初始化 Management-Server 连接"""
        if self.settings.get_setting("management_server_enabled") == "true":
            base_url = self.settings.get_setting("management_server_url")
            ws_url = self.settings.get_setting("management_ws_url")

            self.mgmt_conn = ManagementServerConnection(
                base_url,
                ws_url,
                self.client_uuid
            )

            # 注册
            await self.mgmt_conn.register()

            # 连接 WebSocket
            await self.mgmt_conn.connect_websocket(command_handler)

            # 启动定期同步
            sync_interval = int(self.settings.get_setting("sync_interval"))
            asyncio.create_task(
                self.mgmt_conn.start_periodic_sync(
                    sync_interval,
                    self._get_sync_data
                )
            )

    async def _get_sync_data(self) -> dict:
        """获取需要同步的数据"""
        # 这里调用 schedule_manager 和 settings_manager 获取数据
        # 简化示例
        return {
            "courses": [],
            "schedules": [],
            "settings": {}
        }

    async def close(self):
        """关闭所有连接"""
        if self.lms_conn:
            await self.lms_conn.close()
        # Management-Server 连接也需要清理
```

**集成到主应用**

```python
# src-tauri/python/tauri_app/__init__.py

from .connection_manager import ConnectionManager

async def command_handler(command: str, params: dict):
    """处理来自管理服务器的命令"""
    if command == "update_setting":
        key = params.get("key")
        value = params.get("value")
        settings_manager.update_setting(key, value)
        return {"message": "Setting updated"}

    elif command == "start_cctv_recording":
        camera_id = params.get("camera_id")
        # 调用 CCTV 管理器
        return {"message": f"Recording started for {camera_id}"}

    # ... 其他命令 ...

    return {"error": "Unknown command"}

async def main(app: tauri.App):
    """应用主入口"""
    global settings_manager, schedule_manager

    # ... 初始化现有组件 ...

    # 初始化连接管理器
    global connection_manager
    connection_manager = ConnectionManager(settings_manager)
    await connection_manager.initialize(command_handler)

    # ... 其余初始化 ...
```

## 📋 实施计划

### 阶段 1: LMS 重命名和基础改进 (1-2天)

1. **重命名目录**
   ```bash
   cd classtop
   git mv admin-server lms
   ```

2. **添加数据库层**
   - 创建 `lms/db.py`
   - 实现客户端注册、命令日志、CCTV 事件记录

3. **添加 Management-Server 客户端**
   - 创建 `lms/management_client.py`
   - 实现注册、心跳逻辑

4. **更新主程序**
   - 修改 `lms/main.py` 集成新功能
   - 添加启动/关闭钩子

### 阶段 2: Management-Server 功能扩展 (2-3天)

1. **数据库迁移**
   - 创建 `migrations/003_add_lms_support.sql`
   - 创建 `migrations/004_add_cctv_support.sql`
   - 运行迁移

2. **实现 LMS 管理 API**
   - 创建 `src/handlers/lms.rs`
   - 实现注册、心跳、列表、删除等接口
   - 添加到 Repository

3. **实现 WebSocket 实时控制**
   - 创建 `src/handlers/websocket.rs`
   - 实现 WebSocket Actor 和连接管理器
   - 添加命令路由

4. **实现 CCTV 管理**
   - 添加 CCTV 数据模型
   - 实现 CCTV 配置 CRUD
   - 添加事件记录

### 阶段 3: 客户端双连接支持 (2-3天)

1. **添加连接配置**
   - 更新 `settings_manager.py` 默认配置
   - 添加 LMS 和 Management-Server 配置项

2. **实现连接管理器**
   - 创建 `connection_manager.py`
   - 实现 LMS WebSocket 连接
   - 实现 Management-Server HTTP + WS 连接
   - 实现自动重连逻辑

3. **实现命令处理器**
   - 创建统一的命令处理接口
   - 支持设置修改、CCTV 控制等命令

4. **集成到主应用**
   - 修改 `__init__.py` 启动流程
   - 测试双连接模式

### 阶段 4: 前端 UI 更新 (2-3天)

1. **Management-Server 前端**
   - 添加 LMS 实例监控页面
   - 显示 LMS 列表、状态、客户端数量
   - 实现实时控制面板
   - 添加 CCTV 管理界面

2. **LMS 管理页面**
   - 显示连接的客户端列表
   - 实时状态监控
   - 命令执行历史

### 阶段 5: 测试和文档 (1-2天)

1. **集成测试**
   - 测试 LMS 到 Management-Server 注册
   - 测试客户端双连接
   - 测试实时控制功能
   - 测试数据同步

2. **性能测试**
   - 测试大量客户端连接
   - 测试 WebSocket 延迟
   - 测试数据同步性能

3. **文档更新**
   - 更新 README
   - 创建部署指南
   - 创建迁移指南

## 🚀 部署指南

### LMS 部署

```bash
# 1. 重命名并进入目录
cd classtop/lms

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
export MANAGEMENT_SERVER_URL=http://your-management-server:8765

# 4. 启动 LMS
python main.py
```

### Management-Server 部署

```bash
# 1. 进入目录
cd Classtop-Management-Server

# 2. 运行数据库迁移
psql -U postgres -d classtop_management < migrations/003_add_lms_support.sql
psql -U postgres -d classtop_management < migrations/004_add_cctv_support.sql

# 3. 构建
cargo build --release

# 4. 启动
./target/release/classtop-management-server
```

### 客户端配置

```python
# 在客户端设置界面或配置文件中设置

# 启用双连接模式
dual_connection_mode = "both"

# LMS 配置
lms_enabled = "true"
lms_url = "ws://your-lms:8000/ws"

# Management-Server 配置
management_server_enabled = "true"
management_server_url = "http://your-management-server:8765"
management_ws_url = "ws://your-management-server:8765/ws"
sync_interval = "300"  # 5分钟
```

## 📊 架构优势

### 灵活部署

1. **小规模场景**：仅使用 LMS
   - 单个机房/教室
   - 实时控制需求
   - 无需中央服务器

2. **中等规模场景**：LMS + Management-Server
   - 多个机房统一管理
   - 需要数据分析
   - 保留实时控制能力

3. **大规模场景**：多个 LMS + Management-Server
   - 多校区部署
   - 分层管理
   - 统一数据中心

### 性能优势

- **实时控制**：LMS WebSocket 提供毫秒级延迟
- **批量同步**：Management-Server HTTP 批量处理
- **负载分担**：LMS 分担实时通信负载
- **可扩展性**：可横向扩展 LMS 数量

### 可靠性优势

- **离线运行**：LMS 可独立运行
- **故障隔离**：单个 LMS 故障不影响其他
- **自动重连**：客户端自动重连机制
- **数据备份**：Management-Server 集中备份

## 🔧 未来扩展

1. **LMS 集群**：多个 LMS 实例负载均衡
2. **数据加密**：敏感数据传输加密
3. **权限管理**：细粒度权限控制
4. **监控告警**：系统监控和告警通知
5. **移动端**：移动端管理应用

---

**完成时间估算**: 8-12 个工作日
**优先级**: 高
**维护者**: Zixiao System Team