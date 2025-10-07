# API 服务器功能添加说明

本文档说明了为 ClassTop 添加的集中管理服务器 API 功能。

## 📦 添加的文件

### 核心实现

1. **`src-tauri/python/tauri_app/api_server.py`**
   - FastAPI 实现的 HTTP API 服务器
   - 提供完整的 RESTful 接口
   - 自动生成 OpenAPI 文档
   - 后台守护线程运行

### 配置更新

2. **`src-tauri/python/tauri_app/settings_manager.py`** (已更新)
   - 添加了 API 服务器配置选项：
     - `api_server_enabled`: 是否启用 API 服务器
     - `api_server_host`: 监听地址
     - `api_server_port`: 监听端口

3. **`src-tauri/python/tauri_app/__init__.py`** (已更新)
   - 在应用初始化流程中集成 API 服务器
   - 根据配置条件启动 API 服务器

### 文档

4. **`docs/API.md`**
   - 完整的 API 参考文档
   - 包含所有端点的详细说明
   - 数据模型定义
   - 错误处理说明
   - 丰富的使用示例（Python, JavaScript, cURL）

5. **`docs/API_QUICKSTART.md`**
   - 快速上手指南
   - 启用配置步骤
   - 基础使用示例
   - 集中管理服务器开发指南
   - 包含完整的代码示例和架构建议

6. **`CLAUDE.md`** (已更新)
   - 添加了 API 服务器的架构说明
   - 更新了初始化顺序
   - 添加了使用场景说明

7. **`requirements-api.txt`**
   - API 服务器所需的 Python 依赖
   - FastAPI + Uvicorn

8. **本文档: `docs/API_IMPLEMENTATION.md`**
   - 功能添加说明

---

## 🎯 功能特性

### API 端点

API 服务器提供以下功能模块：

#### 1. 课程管理
- `GET /api/courses` - 获取所有课程
- `POST /api/courses` - 创建课程
- `GET /api/courses/{id}` - 获取单个课程
- `PUT /api/courses/{id}` - 更新课程
- `DELETE /api/courses/{id}` - 删除课程

#### 2. 课程表管理
- `GET /api/schedule` - 获取课程表
- `POST /api/schedule` - 添加课程表条目
- `GET /api/schedule/day/{day}` - 获取某天的课程表
- `GET /api/schedule/week` - 获取整周课程表
- `DELETE /api/schedule/{id}` - 删除课程表条目

#### 3. 设置管理
- `GET /api/settings` - 获取所有设置
- `GET /api/settings/{key}` - 获取单个设置
- `PUT /api/settings` - 批量更新设置
- `PUT /api/settings/{key}` - 更新单个设置
- `POST /api/settings/reset` - 重置设置为默认值

#### 4. 周次管理
- `GET /api/week/current` - 获取当前周次
- `POST /api/week/semester-start` - 设置学期开始日期

#### 5. 统计信息
- `GET /api/statistics` - 获取课程表统计信息

#### 6. 日志管理
- `GET /api/logs` - 获取应用日志

#### 7. 系统管理
- `GET /api/health` - 健康检查
- `GET /` - API 基本信息

### 技术特性

- ✅ **RESTful 设计**: 遵循 REST 架构规范
- ✅ **自动文档**: Swagger UI 和 ReDoc
- ✅ **CORS 支持**: 允许跨域访问
- ✅ **异步处理**: 基于 FastAPI 的异步实现
- ✅ **线程安全**: 使用守护线程，不阻塞主应用
- ✅ **可配置**: 通过数据库设置灵活配置
- ✅ **优雅降级**: 依赖缺失时自动禁用，不影响主应用

---

## 🚀 如何使用

### 1. 安装依赖

```bash
pip install -r requirements-api.txt
```

或手动安装：

```bash
pip install fastapi uvicorn
```

### 2. 启用 API 服务器

使用 SQLite 工具修改数据库：

```sql
UPDATE settings SET value='true' WHERE key='api_server_enabled';
```

### 3. 重启应用

重启 ClassTop 应用后，API 服务器将自动启动。

### 4. 访问 API 文档

浏览器打开：http://localhost:8765/api/docs

### 5. 测试 API

```bash
curl http://localhost:8765/api/health
```

---

## 📚 文档索引

- **快速上手**: 查看 `docs/API_QUICKSTART.md`
- **完整 API 参考**: 查看 `docs/API.md`
- **在线交互文档**: http://localhost:8765/api/docs (启动后)

---

## 🔧 配置选项

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `api_server_enabled` | `false` | 是否启用 API 服务器 |
| `api_server_host` | `0.0.0.0` | 监听地址（0.0.0.0 表示所有接口） |
| `api_server_port` | `8765` | 监听端口 |

### 修改配置

```sql
-- 更改端口
UPDATE settings SET value='9000' WHERE key='api_server_port';

-- 仅本地访问
UPDATE settings SET value='127.0.0.1' WHERE key='api_server_host';

-- 禁用 API 服务器
UPDATE settings SET value='false' WHERE key='api_server_enabled';
```

---

## 🎨 使用场景

### 场景 1: 批量数据导入

适用于学校统一导入课程表到多个客户端。

参考 `docs/API_QUICKSTART.md` 中的 Python 批量导入示例。

### 场景 2: 集中管理面板

开发 Web 管理界面，统一管理多个 ClassTop 客户端。

参考 `docs/API_QUICKSTART.md` 中的集中管理服务器开发指南。

### 场景 3: 数据同步

在多台设备之间同步课程数据。

参考 `docs/API_QUICKSTART.md` 中的数据同步示例。

### 场景 4: 自定义集成

与现有教务系统集成，自动获取课程表数据。

---

## 🔒 安全建议

⚠️ **当前版本未实现身份验证机制**

**生产环境建议**：

1. **仅在受信任网络中启用**
   - 学校内网
   - VPN 环境

2. **使用防火墙限制访问**
   ```bash
   # 示例：仅允许特定 IP 访问
   iptables -A INPUT -p tcp --dport 8765 -s 192.168.1.0/24 -j ACCEPT
   iptables -A INPUT -p tcp --dport 8765 -j DROP
   ```

3. **配合反向代理使用 HTTPS**
   - Nginx + SSL 证书
   - Caddy (自动 HTTPS)

4. **限制本地访问**
   ```sql
   UPDATE settings SET value='127.0.0.1' WHERE key='api_server_host';
   ```

**未来版本计划**：
- API Key 认证
- JWT Token 支持
- IP 白名单
- 请求速率限制

---

## 🐛 故障排查

### API 服务器无法启动

1. **检查依赖是否安装**
   ```bash
   pip list | grep -E "fastapi|uvicorn"
   ```

2. **检查端口是否被占用**
   ```bash
   # macOS/Linux
   lsof -i :8765

   # Windows
   netstat -ano | findstr :8765
   ```

3. **查看应用日志**
   ```bash
   curl http://localhost:8765/api/logs
   ```

### 无法远程访问

1. **检查监听地址**
   ```sql
   SELECT value FROM settings WHERE key='api_server_host';
   ```
   应该是 `0.0.0.0` 而不是 `127.0.0.1`

2. **检查防火墙规则**
   ```bash
   # macOS
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --listapps

   # Linux
   sudo iptables -L -n
   ```

### CORS 错误

API 服务器默认允许所有来源的跨域请求。如需限制，修改 `api_server.py` 中的 CORS 配置。

---

## 📈 性能考虑

- API 服务器运行在独立的守护线程中
- 不会阻塞主应用的 UI 响应
- SQLite 使用连接池管理
- 建议在高并发场景使用 Nginx 反向代理

---

## 🔄 与现有功能的兼容性

API 服务器功能完全可选：

- ✅ **不影响现有功能**: 默认禁用，不会改变应用行为
- ✅ **优雅降级**: 依赖缺失时自动禁用，不会导致应用崩溃
- ✅ **独立运行**: 在后台线程运行，不阻塞主应用
- ✅ **事件集成**: 所有操作会触发相应的事件，前端会自动更新

---

## 📝 开发说明

### 添加新的 API 端点

1. 在 `api_server.py` 的 `_register_routes()` 方法中添加路由
2. 使用 `@self.app.get/post/put/delete` 装饰器
3. 调用对应的 manager 方法
4. 返回统一格式的响应

示例：

```python
@self.app.get("/api/my-endpoint", tags=["MyTag"])
async def my_endpoint():
    """端点说明"""
    try:
        data = self.schedule_manager.some_method()
        return {"success": True, "data": data}
    except Exception as e:
        self.logger.log_message("error", f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

### 测试 API

使用 Swagger UI 进行交互式测试：

1. 启动应用
2. 访问 http://localhost:8765/api/docs
3. 展开端点
4. 点击 "Try it out"
5. 输入参数
6. 点击 "Execute"

---

## 📜 许可证

本功能遵循 ClassTop 主项目的许可证。

---

## 🙏 致谢

API 服务器基于以下优秀的开源项目：

- [FastAPI](https://fastapi.tiangolo.com/) - 现代高性能 Web 框架
- [Uvicorn](https://www.uvicorn.org/) - ASGI 服务器
- [Pydantic](https://pydantic-docs.helpmanual.io/) - 数据验证

---

**添加日期**: 2025-10-07

**版本**: 1.0.0
