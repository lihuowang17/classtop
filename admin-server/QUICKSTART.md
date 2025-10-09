# 快速入门指南

## 第一步：安装 websockets 库（客户端）

在 ClassTop 主目录执行：

```bash
pip install websockets
```

## 第二步：启动管理服务器

1. 打开命令提示符
2. 进入 admin-server 目录：
   ```bash
   cd C:\Users\Chen\Documents\classtop\admin-server
   ```
3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
4. 启动服务器：
   ```bash
   python main.py
   ```
   或双击 `start.bat`

服务器将在 `http://localhost:8000` 启动。

## 第三步：配置客户端

1. 启动 ClassTop 客户端程序
2. 打开设置页面
3. 确认以下设置项存在：
   - `server_url`: 已自动设为空，修改为 `http://localhost:8000`
   - `client_uuid`: 已自动生成

4. 重启客户端程序，客户端将自动连接到管理服务器

## 第四步：使用管理界面

1. 在浏览器打开: `http://localhost:8000`
2. 左侧将显示已连接的客户端列表
3. 点击客户端查看详情和管理

## 功能演示

### 设置管理

1. 选择一个在线客户端
2. 切换到"设置管理"标签
3. 点击任意设置项的"编辑"按钮
4. 修改值后保存

## 远程访问（可选）

如果需要从其他电脑访问管理后台：

1. 获取服务器电脑的 IP 地址（使用 `ipconfig` 命令）
2. 修改客户端的 `server_url` 为: `http://服务器IP:8000`
3. 在浏览器访问: `http://服务器IP:8000`

## 常见问题

**Q: 客户端显示离线？**
- 检查客户端日志，查看连接错误
- 确认 server_url 设置正确
- 确认服务器正在运行

**Q: 命令执行失败？**
- 查看浏览器控制台和服务器日志
- 检查命令参数是否正确

**Q: 如何查看日志？**
- 服务器日志：命令提示符窗口中显示
- 客户端日志：ClassTop 程序日志文件

## 下一步

- 阅读完整的 `README.md` 了解所有功能
- 查看 API 文档: `http://localhost:8000/docs`
- 根据需求配置生产环境部署
