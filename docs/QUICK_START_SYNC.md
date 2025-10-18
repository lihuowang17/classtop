# ClassTop 管理服务器快速实施指南

本指南帮助你快速实施客户端与 Classtop-Management-Server 的数据同步功能。

## 📋 前置条件

- ClassTop 客户端项目：`/Users/logos/fleet/classtop`
- Classtop-Management-Server 项目：`/Users/logos/RustroverProjects/Classtop-Management-Server`
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+

## 🚀 快速开始（5 步完成基础集成）

### 步骤 1: 启动 Management Server

```bash
cd /Users/logos/RustroverProjects/Classtop-Management-Server

# 配置数据库
cp .env.example .env
# 编辑 .env 文件，设置 DATABASE_URL

# 构建前端
cd frontend
npm install
npm run build
cd ..

# 启动服务器
cargo run --release
```

验证：访问 http://localhost:8765，应看到管理界面。

### 步骤 2: 客户端数据库迁移

在 `classtop/src-tauri/python/tauri_app/db.py` 中添加迁移方法：

```python
def migrate_database(self):
    """数据库迁移：添加新字段"""
    cursor = self.conn.cursor()

    # 检查 location 字段是否存在
    cursor.execute("PRAGMA table_info(courses)")
    columns = [column[1] for column in cursor.fetchall()]

    if 'location' not in columns:
        cursor.execute("ALTER TABLE courses ADD COLUMN location TEXT")
        self.conn.commit()
        print("✓ 添加 location 字段到 courses 表")
```

在 `Database.__init__()` 或 `main()` 中调用：

```python
# 在初始化数据库连接后
db_manager = Database()
db_manager.migrate_database()
```

### 步骤 3: 创建同步客户端模块

创建文件 `classtop/src-tauri/python/tauri_app/sync_client.py`：

```python
"""
服务器同步客户端
负责与 Classtop-Management-Server 通信
"""

import requests
import threading
import time
import json
import socket
import uuid
from typing import Optional, Dict, List


class SyncClient:
    """服务器同步客户端"""

    def __init__(self, settings_manager, schedule_manager, logger):
        self.settings_manager = settings_manager
        self.schedule_manager = schedule_manager
        self.logger = logger
        self.sync_thread = None
        self.is_running = False

    def register_client(self) -> bool:
        """向服务器注册客户端"""
        try:
            server_url = self.settings_manager.get_setting("server_url", "")
            if not server_url:
                self.logger.log_message("warning", "未配置服务器地址")
                return False

            # 获取或生成客户端 UUID
            client_uuid = self.settings_manager.get_setting("client_uuid", "")
            if not client_uuid:
                client_uuid = str(uuid.uuid4())
                self.settings_manager.set_setting("client_uuid", client_uuid)

            # 获取客户端名称
            client_name = self.settings_manager.get_setting("client_name", socket.gethostname())

            # 构造注册数据
            data = {
                "uuid": client_uuid,
                "name": client_name,
                "api_url": ""  # 如果启用了客户端 API，填写地址
            }

            # 发送注册请求
            url = f"{server_url.rstrip('/')}/api/clients/register"
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()

            result = response.json()
            if result.get("success"):
                self.logger.log_message("info", f"客户端注册成功: {client_name}")
                return True
            else:
                self.logger.log_message("error", f"客户端注册失败: {result}")
                return False

        except Exception as e:
            self.logger.log_message("error", f"注册客户端失败: {e}")
            return False

    def sync_to_server(self) -> bool:
        """同步数据到服务器"""
        try:
            server_url = self.settings_manager.get_setting("server_url", "")
            client_uuid = self.settings_manager.get_setting("client_uuid", "")

            if not server_url or not client_uuid:
                self.logger.log_message("warning", "服务器地址或客户端 UUID 未配置")
                return False

            # 获取所有课程
            courses = self.schedule_manager.get_all_courses()

            # 获取所有课程表条目
            schedule_entries = self.schedule_manager.get_all_schedule_entries()

            # 构造同步数据
            sync_data = {
                "client_uuid": client_uuid,
                "courses": [
                    {
                        "id_on_client": course["id"],
                        "name": course["name"],
                        "teacher": course.get("teacher") or "",
                        "location": course.get("location") or "",
                        "color": course.get("color") or "#6750A4"
                    }
                    for course in courses
                ],
                "schedule_entries": [
                    {
                        "id_on_client": entry["id"],
                        "course_id_on_client": entry["course_id"],
                        "day_of_week": entry["day_of_week"],
                        "start_time": entry["start_time"],
                        "end_time": entry["end_time"],
                        "weeks": json.loads(entry["weeks"]) if entry.get("weeks") else []
                    }
                    for entry in schedule_entries
                ]
            }

            # 发送同步请求
            url = f"{server_url.rstrip('/')}/api/sync"
            response = requests.post(url, json=sync_data, timeout=30)
            response.raise_for_status()

            result = response.json()
            if result.get("success"):
                sync_info = result.get("data", {})
                courses_synced = sync_info.get("courses_synced", 0)
                entries_synced = sync_info.get("schedule_entries_synced", 0)
                self.logger.log_message(
                    "info",
                    f"同步成功: {courses_synced} 门课程, {entries_synced} 个课程表条目"
                )
                return True
            else:
                self.logger.log_message("error", f"同步失败: {result}")
                return False

        except Exception as e:
            self.logger.log_message("error", f"同步到服务器失败: {e}")
            return False

    def test_connection(self) -> Dict:
        """测试服务器连接"""
        try:
            server_url = self.settings_manager.get_setting("server_url", "")
            if not server_url:
                return {"success": False, "message": "未配置服务器地址"}

            url = f"{server_url.rstrip('/')}/api/health"
            response = requests.get(url, timeout=5)
            response.raise_for_status()

            result = response.json()
            if result.get("success"):
                return {"success": True, "message": "连接成功", "data": result.get("data")}
            else:
                return {"success": False, "message": "服务器响应异常"}

        except requests.exceptions.Timeout:
            return {"success": False, "message": "连接超时"}
        except requests.exceptions.ConnectionError:
            return {"success": False, "message": "无法连接到服务器"}
        except Exception as e:
            return {"success": False, "message": f"连接失败: {str(e)}"}

    def start_auto_sync(self):
        """启动自动同步（后台线程）"""
        sync_enabled = self.settings_manager.get_setting("sync_enabled", "false")
        if sync_enabled.lower() != "true":
            self.logger.log_message("info", "同步功能未启用")
            return

        if self.is_running:
            self.logger.log_message("warning", "同步线程已在运行")
            return

        self.is_running = True
        self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self.sync_thread.start()
        self.logger.log_message("info", "启动自动同步线程")

    def stop_auto_sync(self):
        """停止自动同步"""
        self.is_running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=5)
        self.logger.log_message("info", "停止自动同步线程")

    def _sync_loop(self):
        """同步循环"""
        while self.is_running:
            try:
                interval = int(self.settings_manager.get_setting("sync_interval", "300"))

                # 执行同步
                success = self.sync_to_server()
                if success:
                    self.logger.log_message("info", f"同步成功，等待 {interval} 秒")
                else:
                    self.logger.log_message("error", "同步失败，将在下次重试")

                # 等待指定间隔
                for _ in range(interval):
                    if not self.is_running:
                        break
                    time.sleep(1)

            except Exception as e:
                self.logger.log_message("error", f"同步循环异常: {e}")
                time.sleep(60)  # 出错后等待 1 分钟
```

### 步骤 4: 扩展 schedule_manager.py

在 `classtop/src-tauri/python/tauri_app/schedule_manager.py` 中添加：

```python
def get_all_courses(self):
    """获取所有课程（用于同步）"""
    cursor = self.conn.cursor()
    cursor.execute("""
        SELECT id, name, teacher, location, color, note
        FROM courses
        ORDER BY id
    """)

    courses = []
    for row in cursor.fetchall():
        courses.append({
            "id": row[0],
            "name": row[1],
            "teacher": row[2] or "",
            "location": row[3] or "",
            "color": row[4] or "#6750A4",
            "note": row[5] or ""
        })

    return courses

def get_all_schedule_entries(self):
    """获取所有课程表条目（用于同步）"""
    cursor = self.conn.cursor()
    cursor.execute("""
        SELECT s.id, s.course_id, s.day_of_week, s.start_time, s.end_time, s.weeks,
               c.name, c.teacher, c.location, c.color
        FROM schedule s
        JOIN courses c ON s.course_id = c.id
        ORDER BY s.day_of_week, s.start_time
    """)

    entries = []
    for row in cursor.fetchall():
        entries.append({
            "id": row[0],
            "course_id": row[1],
            "day_of_week": row[2],
            "start_time": row[3],
            "end_time": row[4],
            "weeks": row[5],
            "course_name": row[6],
            "teacher": row[7] or "",
            "location": row[8] or "",
            "color": row[9] or "#6750A4"
        })

    return entries
```

### 步骤 5: 集成到应用初始化

在 `classtop/src-tauri/python/tauri_app/__init__.py` 中：

```python
from .sync_client import SyncClient

# 全局变量
sync_client = None

def main():
    """应用初始化"""
    global logger, db_manager, settings_manager, schedule_manager, sync_client

    # ... 现有初始化代码 ...

    # 初始化同步客户端
    sync_client = SyncClient(settings_manager, schedule_manager, logger)

    # 启动时尝试注册并启动自动同步
    sync_enabled = settings_manager.get_setting("sync_enabled", "false")
    if sync_enabled.lower() == "true":
        sync_client.register_client()
        sync_client.start_auto_sync()

    logger.log_message("info", "应用初始化完成")

# 添加 Tauri 命令
@commands.command()
async def test_server_connection():
    """测试服务器连接"""
    if sync_client:
        return sync_client.test_connection()
    return {"success": False, "message": "同步客户端未初始化"}

@commands.command()
async def sync_now():
    """立即同步到服务器"""
    if sync_client:
        success = sync_client.sync_to_server()
        return {"success": success}
    return {"success": False, "message": "同步客户端未初始化"}

@commands.command()
async def register_to_server():
    """注册到服务器"""
    if sync_client:
        success = sync_client.register_client()
        return {"success": success}
    return {"success": False, "message": "同步客户端未初始化"}
```

## 🧪 测试步骤

### 1. 安装 Python 依赖

```bash
cd /Users/logos/fleet/classtop
pip install requests
```

### 2. 启动 Management Server

```bash
cd /Users/logos/RustroverProjects/Classtop-Management-Server
cargo run --release
```

### 3. 启动客户端

```bash
cd /Users/logos/fleet/classtop
npm run tauri dev
```

### 4. 配置客户端

1. 打开设置页面
2. 添加以下配置到数据库（手动或通过 UI）：
   - `server_url`: `http://localhost:8765`
   - `client_name`: `测试客户端-01`
   - `sync_enabled`: `true`
   - `sync_interval`: `60`  （测试用，1 分钟）

### 5. 测试同步

在客户端 Python 控制台或日志中查看：
- "客户端注册成功" 消息
- "同步成功: X 门课程, Y 个课程表条目" 消息

访问 http://localhost:8765：
- 查看"客户端"页面，应看到注册的客户端
- 查看"数据查看"页面，应看到同步的课程和课程表

## ⚠️ 常见问题

### 问题 1: 无法导入 requests

**解决方案**:
```bash
# 确保在正确的 Python 环境中安装
which python3
pip3 install requests
```

### 问题 2: 连接超时

**解决方案**:
- 检查 Management Server 是否在运行
- 确认端口 8765 未被占用
- 测试连接：`curl http://localhost:8765/api/health`

### 问题 3: location 字段错误

**解决方案**:
```bash
# 手动添加字段
sqlite3 ~/.local/share/classtop/classtop.db
ALTER TABLE courses ADD COLUMN location TEXT;
.quit
```

### 问题 4: 同步失败

**解决方案**:
1. 查看客户端日志
2. 查看 Management Server 日志
3. 使用 curl 测试 API:
```bash
curl -X POST http://localhost:8765/api/sync \
  -H "Content-Type: application/json" \
  -d '{
    "client_uuid": "test-uuid",
    "courses": [],
    "schedule_entries": []
  }'
```

## 📚 下一步

完成基础集成后，可以：

1. **添加前端 UI**: 在设置页面添加服务器配置界面（参考 CLIENT_ADAPTATION.md）
2. **改进 admin-server**: 添加数据持久化（参考 MANAGEMENT_SERVER_IMPROVEMENT_PLAN.md）
3. **性能优化**: 实现增量同步、缓存等
4. **安全加固**: 添加 API Key 认证、HTTPS 支持

详细指南请查看：
- [客户端适配指南](./CLIENT_ADAPTATION.md)
- [集成任务清单](./CLIENT_INTEGRATION_TODO.md)
- [改进计划](./MANAGEMENT_SERVER_IMPROVEMENT_PLAN.md)
