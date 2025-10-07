# ClassTop API 快速上手指南

本指南帮助您快速启用和使用 ClassTop 的集中管理 API。

## 📋 目录

- [什么是 ClassTop API？](#什么是-classtop-api)
- [快速启用](#快速启用)
- [访问 API 文档](#访问-api-文档)
- [基础使用示例](#基础使用示例)
- [集中管理服务器开发指南](#集中管理服务器开发指南)

---

## 什么是 ClassTop API？

ClassTop API 是一个 RESTful HTTP 接口，允许外部系统：

- **远程管理课程和课程表数据**
- **批量导入/导出数据**
- **集中管理多个 ClassTop 客户端**
- **构建自定义管理面板**
- **自动化数据同步**

## 快速启用

### 方法 1: 直接修改数据库（推荐）

1. 找到 ClassTop 的数据库文件 `classtop.db`（通常在应用数据目录）

2. 使用 SQLite 工具执行：

```sql
UPDATE settings SET value='true' WHERE key='api_server_enabled';
```

3. 重启 ClassTop 应用

4. 验证 API 是否启动：

```bash
curl http://localhost:8765/api/health
```

如果看到如下响应，说明 API 已成功启动：

```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2025-10-07T10:30:00",
    "version": "1.0.0"
  }
}
```

### 方法 2: 使用 Python 命令

创建一个临时 Python 脚本：

```python
import sqlite3

# 修改为您的数据库路径
db_path = "path/to/classtop.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 启用 API 服务器
cursor.execute("UPDATE settings SET value='true' WHERE key='api_server_enabled'")
cursor.execute("UPDATE settings SET value='0.0.0.0' WHERE key='api_server_host'")
cursor.execute("UPDATE settings SET value='8765' WHERE key='api_server_port'")

conn.commit()
conn.close()

print("API 服务器配置已启用，请重启 ClassTop 应用。")
```

### 配置说明

| 设置项 | 默认值 | 说明 |
|--------|--------|------|
| `api_server_enabled` | false | 是否启用 API 服务器 |
| `api_server_host` | 0.0.0.0 | 监听地址（0.0.0.0 = 所有网络接口） |
| `api_server_port` | 8765 | 监听端口 |

**安全建议**：
- 如果只需本地访问，将 `api_server_host` 改为 `127.0.0.1`
- 使用防火墙限制外部访问
- 生产环境建议配合 Nginx 使用 HTTPS

---

## 访问 API 文档

启动 API 后，访问以下 URL 查看交互式文档：

- **Swagger UI**（推荐）: http://localhost:8765/api/docs
- **ReDoc**: http://localhost:8765/api/redoc

在 Swagger UI 中，您可以：
- 查看所有 API 端点
- 在线测试 API 调用
- 查看请求/响应示例
- 下载 OpenAPI 规范文件

---

## 基础使用示例

### 示例 1: 获取所有课程

```bash
curl http://localhost:8765/api/courses
```

**响应**：
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "高等数学",
      "teacher": "张三",
      "location": "教学楼A101",
      "color": "#FF5722"
    }
  ]
}
```

### 示例 2: 创建新课程

```bash
curl -X POST http://localhost:8765/api/courses \
  -H "Content-Type: application/json" \
  -d '{
    "name": "计算机网络",
    "teacher": "王教授",
    "location": "实验楼301",
    "color": "#2196F3"
  }'
```

### 示例 3: 获取本周课程表

```bash
# 1. 获取当前周次
WEEK=$(curl -s http://localhost:8765/api/week/current | jq -r '.data.week')

# 2. 获取课程表
curl "http://localhost:8765/api/schedule/week?week=$WEEK"
```

### 示例 4: Python 批量导入

```python
import requests

BASE_URL = "http://localhost:8765"

# 批量导入课程
courses = [
    {"name": "高等数学", "teacher": "张三", "location": "A101", "color": "#FF5722"},
    {"name": "大学英语", "teacher": "李四", "location": "B203", "color": "#4CAF50"},
    {"name": "计算机原理", "teacher": "王五", "location": "C301", "color": "#2196F3"},
]

course_ids = {}
for course in courses:
    response = requests.post(f"{BASE_URL}/api/courses", json=course)
    if response.ok:
        course_id = response.json()["data"]["id"]
        course_ids[course["name"]] = course_id
        print(f"✓ 导入课程: {course['name']} (ID: {course_id})")

# 批量导入课程表
schedules = [
    {"course": "高等数学", "day": 1, "start": "08:00", "end": "09:40", "weeks": [1,2,3,4,5]},
    {"course": "大学英语", "day": 2, "start": "10:00", "end": "11:40", "weeks": [1,2,3,4,5]},
    {"course": "计算机原理", "day": 3, "start": "14:00", "end": "15:40", "weeks": [1,2,3,4,5]},
]

for schedule in schedules:
    entry = {
        "course_id": course_ids[schedule["course"]],
        "day_of_week": schedule["day"],
        "start_time": schedule["start"],
        "end_time": schedule["end"],
        "weeks": schedule["weeks"]
    }
    response = requests.post(f"{BASE_URL}/api/schedule", json=entry)
    if response.ok:
        print(f"✓ 导入课程表: {schedule['course']} - 周{schedule['day']}")

print("\n导入完成！")
```

---

## 集中管理服务器开发指南

### 架构建议

如果您要开发集中管理服务器，推荐以下架构：

```
┌─────────────────────┐
│  管理服务器 (Node.js/Python)  │
│  - 管理界面           │
│  - 数据聚合           │
│  - 权限控制           │
└─────────┬───────────┘
          │
          ├──────────┬──────────┬──────────┐
          │          │          │          │
    ┌─────▼────┐ ┌──▼──────┐ ┌─▼───────┐ │
    │ClassTop 1│ │ClassTop 2│ │ClassTop 3│...
    │(API:8765)│ │(API:8766)│ │(API:8767)│
    └──────────┘ └──────────┘ └──────────┘
```

### 核心功能实现

#### 1. 客户端发现和注册

利用 `client_uuid` 识别不同的 ClassTop 实例：

```javascript
// Node.js 示例
const axios = require('axios');

class ClassTopManager {
  constructor() {
    this.clients = new Map();
  }

  async registerClient(host, port) {
    const baseURL = `http://${host}:${port}`;

    // 健康检查
    const health = await axios.get(`${baseURL}/api/health`);
    if (health.data.success) {
      // 获取客户端 UUID
      const settings = await axios.get(`${baseURL}/api/settings`);
      const uuid = settings.data.data.client_uuid;

      this.clients.set(uuid, {
        uuid,
        host,
        port,
        baseURL,
        lastSeen: new Date()
      });

      console.log(`✓ 注册客户端: ${uuid} (${host}:${port})`);
      return uuid;
    }
  }

  async getAllClients() {
    return Array.from(this.clients.values());
  }
}

// 使用
const manager = new ClassTopManager();
await manager.registerClient('192.168.1.100', 8765);
await manager.registerClient('192.168.1.101', 8765);
```

#### 2. 数据聚合

汇总所有客户端的课程数据：

```python
import requests
from typing import List, Dict

class ClassTopAggregator:
    def __init__(self, clients: List[Dict[str, str]]):
        """
        clients: [{"uuid": "...", "host": "...", "port": 8765}, ...]
        """
        self.clients = clients

    def get_all_courses(self) -> Dict[str, List]:
        """获取所有客户端的课程"""
        result = {}
        for client in self.clients:
            url = f"http://{client['host']}:{client['port']}/api/courses"
            try:
                response = requests.get(url)
                if response.ok:
                    courses = response.json()["data"]
                    result[client['uuid']] = courses
            except Exception as e:
                print(f"✗ 获取 {client['uuid']} 的课程失败: {e}")

        return result

    def get_statistics_summary(self) -> Dict:
        """获取所有客户端的统计信息"""
        total_stats = {
            "total_clients": len(self.clients),
            "total_courses": 0,
            "total_schedule_entries": 0,
            "clients": []
        }

        for client in self.clients:
            url = f"http://{client['host']}:{client['port']}/api/statistics"
            try:
                response = requests.get(url)
                if response.ok:
                    stats = response.json()["data"]
                    total_stats["total_courses"] += stats["total_courses"]
                    total_stats["total_schedule_entries"] += stats["total_schedule_entries"]
                    total_stats["clients"].append({
                        "uuid": client['uuid'],
                        "stats": stats
                    })
            except Exception as e:
                print(f"✗ 获取 {client['uuid']} 的统计失败: {e}")

        return total_stats

# 使用
clients = [
    {"uuid": "client-1", "host": "192.168.1.100", "port": 8765},
    {"uuid": "client-2", "host": "192.168.1.101", "port": 8765},
]

aggregator = ClassTopAggregator(clients)

# 获取所有课程
all_courses = aggregator.get_all_courses()
for uuid, courses in all_courses.items():
    print(f"{uuid}: {len(courses)} 门课程")

# 获取统计摘要
summary = aggregator.get_statistics_summary()
print(f"总计: {summary['total_courses']} 门课程, {summary['total_schedule_entries']} 个课程表条目")
```

#### 3. 批量操作

向多个客户端推送相同的课程数据：

```python
def batch_create_course(clients: List[Dict], course_data: Dict) -> Dict:
    """批量创建课程"""
    results = {"success": [], "failed": []}

    for client in clients:
        url = f"http://{client['host']}:{client['port']}/api/courses"
        try:
            response = requests.post(url, json=course_data)
            if response.ok:
                course_id = response.json()["data"]["id"]
                results["success"].append({
                    "uuid": client['uuid'],
                    "course_id": course_id
                })
            else:
                results["failed"].append({
                    "uuid": client['uuid'],
                    "error": response.text
                })
        except Exception as e:
            results["failed"].append({
                "uuid": client['uuid'],
                "error": str(e)
            })

    return results

# 使用
course = {
    "name": "统一培训课程",
    "teacher": "培训讲师",
    "location": "线上",
    "color": "#FF5722"
}

results = batch_create_course(clients, course)
print(f"成功: {len(results['success'])}, 失败: {len(results['failed'])}")
```

#### 4. 数据同步

实现主从同步，将主节点的数据同步到从节点：

```python
class ClassTopSyncManager:
    def __init__(self, master_client: Dict, slave_clients: List[Dict]):
        self.master = master_client
        self.slaves = slave_clients

    def sync_courses(self):
        """同步课程数据"""
        # 1. 获取主节点的课程
        master_url = f"http://{self.master['host']}:{self.master['port']}"
        response = requests.get(f"{master_url}/api/courses")
        master_courses = response.json()["data"]

        print(f"主节点有 {len(master_courses)} 门课程")

        # 2. 同步到从节点
        for slave in self.slaves:
            slave_url = f"http://{slave['host']}:{slave['port']}"

            # 获取从节点现有课程
            response = requests.get(f"{slave_url}/api/courses")
            slave_courses = response.json()["data"]
            slave_course_names = {c["name"] for c in slave_courses}

            # 添加缺失的课程
            added = 0
            for course in master_courses:
                if course["name"] not in slave_course_names:
                    course_data = {
                        "name": course["name"],
                        "teacher": course.get("teacher"),
                        "location": course.get("location"),
                        "color": course.get("color")
                    }
                    response = requests.post(f"{slave_url}/api/courses", json=course_data)
                    if response.ok:
                        added += 1

            print(f"✓ 同步到 {slave['uuid']}: 添加 {added} 门课程")

# 使用
master = {"uuid": "master", "host": "192.168.1.100", "port": 8765}
slaves = [
    {"uuid": "slave-1", "host": "192.168.1.101", "port": 8765},
    {"uuid": "slave-2", "host": "192.168.1.102", "port": 8765},
]

sync_manager = ClassTopSyncManager(master, slaves)
sync_manager.sync_courses()
```

### Web 管理界面示例

使用 Vue.js 构建简单的管理界面：

```vue
<template>
  <div class="classtop-manager">
    <h1>ClassTop 集中管理面板</h1>

    <!-- 客户端列表 -->
    <div class="clients">
      <h2>客户端列表 ({{ clients.length }})</h2>
      <div v-for="client in clients" :key="client.uuid" class="client-card">
        <h3>{{ client.uuid }}</h3>
        <p>地址: {{ client.host }}:{{ client.port }}</p>
        <button @click="viewClient(client)">查看详情</button>
      </div>
    </div>

    <!-- 统计信息 -->
    <div class="statistics">
      <h2>统计信息</h2>
      <p>总课程数: {{ totalCourses }}</p>
      <p>总课程表条目: {{ totalScheduleEntries }}</p>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      clients: [],
      totalCourses: 0,
      totalScheduleEntries: 0
    }
  },

  async mounted() {
    await this.loadClients();
  },

  methods: {
    async loadClients() {
      // 假设有一个管理服务器 API
      const response = await fetch('/api/classtop-clients');
      const data = await response.json();
      this.clients = data.clients;
      this.totalCourses = data.totalCourses;
      this.totalScheduleEntries = data.totalScheduleEntries;
    },

    viewClient(client) {
      // 打开 ClassTop 的 Swagger UI
      window.open(`http://${client.host}:${client.port}/api/docs`, '_blank');
    }
  }
}
</script>
```

---

## 完整 API 文档

详细的 API 文档请查看：[docs/API.md](./API.md)

包括：
- 所有 API 端点详细说明
- 请求/响应示例
- 数据模型定义
- 错误处理
- 更多使用示例

---

## 常见问题

### API 服务器无法启动？

1. 检查是否安装了依赖：
   ```bash
   pip install fastapi uvicorn
   ```

2. 检查端口是否被占用：
   ```bash
   lsof -i :8765  # macOS/Linux
   netstat -ano | findstr :8765  # Windows
   ```

3. 查看应用日志：
   ```bash
   curl http://localhost:8765/api/logs
   ```

### 如何更改端口？

```sql
UPDATE settings SET value='9000' WHERE key='api_server_port';
```

然后重启应用。

### 如何限制仅本地访问？

```sql
UPDATE settings SET value='127.0.0.1' WHERE key='api_server_host';
```

### 如何添加 HTTPS？

使用 Nginx 反向代理：

```nginx
server {
    listen 443 ssl;
    server_name classtop.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location /api/ {
        proxy_pass http://localhost:8765/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 支持

如有问题，请提交 Issue 到项目仓库。
