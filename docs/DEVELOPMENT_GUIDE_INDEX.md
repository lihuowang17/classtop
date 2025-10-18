# ClassTop 开发文档索引

欢迎查看 ClassTop 的开发文档！本索引帮助你快速找到所需的开发指南。

## 🚀 快速开始

新手开发者？请按以下顺序阅读：

1. **选择你的操作系统**，按照对应的环境搭建指南：
   - [Linux 开发环境搭建](./LINUX_SETUP.md)
   - [macOS 开发环境搭建](./MACOS_SETUP.md)
   - Windows 开发环境（见 [../README.md](../README.md#windows-开发环境)）

2. **配置你的 IDE/编辑器**：
   - [VSCode 配置指南](./VSCODE_SETUP.md) - **推荐用于日常开发**
   - [Xcode 配置指南](./XCODE_SETUP.md) - macOS 高级调试
   - [Visual Studio 配置指南](./VISUAL_STUDIO_SETUP.md) - Windows 高级调试

3. **了解项目架构**：
   - [项目架构说明](../CLAUDE.md)

## 📖 文档分类

### 平台相关

#### Linux
- **[Linux 开发环境搭建](./LINUX_SETUP.md)**
  - 支持的发行版：Ubuntu、Debian、Fedora、Arch Linux
  - 系统依赖安装
  - Node.js、Python、Rust 安装
  - 构建和运行
  - 常见问题解决

#### macOS
- **[macOS 开发环境搭建](./MACOS_SETUP.md)**
  - 支持 Intel 和 Apple Silicon (M1/M2/M3)
  - Xcode Command Line Tools 安装
  - Homebrew 配置
  - 代码签名和公证
  - Universal Binary 构建

#### Windows
- **Windows 开发环境**（在 [README.md](../README.md#windows-开发环境) 中）
  - Visual Studio 依赖
  - MSVC 工具链配置
  - 基本开发流程

### IDE/编辑器配置

#### VSCode (全平台推荐)
- **[VSCode 配置指南](./VSCODE_SETUP.md)**
  - ✅ **推荐用于日常开发**
  - 必备扩展安装（Vue、Rust、Python、Tauri）
  - 项目配置文件（settings.json、tasks.json、launch.json）
  - 调试配置
  - 代码片段
  - 键盘快捷键
  - 性能优化

#### Xcode (macOS 专用)
- **[Xcode 配置指南](./XCODE_SETUP.md)**
  - ⚡ **用于高级调试和性能分析**
  - Instruments 性能分析工具
    - Time Profiler (CPU)
    - Allocations (内存)
    - Leaks (泄漏检测)
    - Network、File Activity
  - LLDB 调试器
  - Memory Graph
  - 性能优化工作流

#### Visual Studio (Windows 专用)
- **[Visual Studio 配置指南](./VISUAL_STUDIO_SETUP.md)**
  - ⚡ **用于高级调试和性能分析**
  - 项目配置
  - Rust 调试
  - 性能探查器
  - CPU 使用率分析
  - 内存泄漏检测
  - 并发可视化工具
  - 静态代码分析

### 项目架构和 API

#### 项目架构
- **[CLAUDE.md](../CLAUDE.md)** - 完整的项目架构说明
  - 技术栈详解
  - 双窗口系统
  - Python-Rust 通信流程
  - 数据库结构
  - 事件系统
  - 周数计算逻辑
  - 常见开发模式

#### API 文档
- **[API 文档](./API.md)** - HTTP API 完整参考
  - 课程管理 API
  - 课程表 API
  - 设置 API
  - 请求/响应格式

- **[API 快速开始](./API_QUICKSTART.md)** - API 使用示例
  - 基本使用
  - 常见操作示例
  - cURL 命令示例

#### API 实现
- **[API 实现说明](./API_IMPLEMENTATION.md)** - API 服务器架构
- **[客户端适配指南](./CLIENT_ADAPTATION.md)** - 如何适配 ClassTop 客户端
- **[客户端集成 TODO](./CLIENT_INTEGRATION_TODO.md)** - 集成任务清单

## 🔍 按需求查找

### 我想...

#### 搭建开发环境
- **Linux 用户** → [Linux 开发环境搭建](./LINUX_SETUP.md)
- **macOS 用户** → [macOS 开发环境搭建](./MACOS_SETUP.md)
- **Windows 用户** → [README.md](../README.md#windows-开发环境)

#### 配置编辑器
- **日常开发** → [VSCode 配置指南](./VSCODE_SETUP.md)
- **性能调优 (macOS)** → [Xcode 配置指南](./XCODE_SETUP.md)
- **性能调优 (Windows)** → [Visual Studio 配置指南](./VISUAL_STUDIO_SETUP.md)

#### 调试问题
- **前端调试** → [VSCode 配置指南 - 调试部分](./VSCODE_SETUP.md#调试配置)
- **Rust 调试 (macOS)** → [Xcode - LLDB 调试器](./XCODE_SETUP.md#lldb-调试器)
- **Rust 调试 (Windows)** → [Visual Studio - 调试配置](./VISUAL_STUDIO_SETUP.md#调试配置)
- **Python 调试** → [VSCode - launch.json](./VSCODE_SETUP.md#5-配置调试-launchjson)

#### 性能优化
- **CPU 性能分析 (macOS)** → [Xcode - Time Profiler](./XCODE_SETUP.md#1-time-profiler-cpu-性能分析)
- **CPU 性能分析 (Windows)** → [Visual Studio - CPU 使用率分析](./VISUAL_STUDIO_SETUP.md#cpu-使用率分析)
- **内存泄漏检测 (macOS)** → [Xcode - Leaks](./XCODE_SETUP.md#3-leaks-内存泄漏检测)
- **内存泄漏检测 (Windows)** → [Visual Studio - 内存使用情况分析](./VISUAL_STUDIO_SETUP.md#内存使用情况分析)

#### 了解项目结构
- **整体架构** → [CLAUDE.md](../CLAUDE.md)
- **前端结构** → [CLAUDE.md - 前端模块结构](../CLAUDE.md#frontend-module-structure)
- **后端结构** → [CLAUDE.md - Python 模块结构](../CLAUDE.md#python-module-structure)
- **数据库设计** → [CLAUDE.md - 数据库 Schema](../CLAUDE.md#database-schema)

#### 使用 API
- **API 参考** → [API 文档](./API.md)
- **API 示例** → [API 快速开始](./API_QUICKSTART.md)
- **启用 API 服务器** → [CLAUDE.md - API Server](../CLAUDE.md#api-server-optional)

#### 构建和发布
- **Linux 构建** → [Linux - 构建生产版本](./LINUX_SETUP.md#构建生产版本)
- **macOS 构建** → [macOS - 构建生产版本](./MACOS_SETUP.md#构建生产版本)
- **Windows 构建** → [README.md - 构建生产版本](../README.md#构建生产版本)
- **代码签名 (macOS)** → [macOS - 代码签名和公证](./MACOS_SETUP.md#代码签名和公证-可选)

#### 解决问题
- **Linux 常见问题** → [Linux - 常见问题](./LINUX_SETUP.md#常见问题)
- **macOS 常见问题** → [macOS - 常见问题](./MACOS_SETUP.md#常见问题)
- **VSCode 问题排查** → [VSCode - 问题排查](./VSCODE_SETUP.md#问题排查)
- **Xcode 常见问题** → [Xcode - 常见问题](./XCODE_SETUP.md#常见问题)
- **Visual Studio 常见问题** → [Visual Studio - 常见问题](./VISUAL_STUDIO_SETUP.md#常见问题)

## 🛠️ 开发工作流推荐

### 新项目开发者
1. 根据操作系统完成环境搭建
2. 安装并配置 VSCode
3. 阅读 CLAUDE.md 了解项目架构
4. 运行 `npm run tauri dev` 启动开发服务器
5. 尝试修改代码并观察效果

### 日常开发
- **编辑器**: VSCode
- **启动命令**: `npm run tauri dev`
- **前端热重载**: 自动
- **后端重启**: 修改 Python/Rust 代码后需重启

### 性能调优
- **macOS**: 使用 Xcode Instruments
- **Windows**: 使用 Visual Studio Performance Profiler
- **Linux**: 使用 perf 或 valgrind

### 调试流程
1. **前端问题**: 浏览器开发者工具 (F12)
2. **Rust 问题**: VSCode + CodeLLDB 或 Xcode/Visual Studio
3. **Python 问题**: VSCode Python 调试器

## 📚 相关资源

### 官方文档
- [Tauri 官方文档](https://tauri.app/)
- [Vue 3 官方文档](https://vuejs.org/)
- [Rust 官方书籍](https://doc.rust-lang.org/book/)
- [PyTauri 文档](https://pytauri.github.io/)

### 工具文档
- [VSCode 文档](https://code.visualstudio.com/docs)
- [Xcode 文档](https://developer.apple.com/documentation/xcode)
- [Visual Studio 文档](https://docs.microsoft.com/zh-cn/visualstudio/)

### 社区
- [Tauri Discord](https://discord.com/invite/tauri)
- [Rust 中文社区](https://rustcc.cn/)
- [Vue.js 中文社区](https://cn.vuejs.org/)

## 🤝 贡献文档

发现文档有误或需要补充？欢迎：
1. 提交 [Issue](https://github.com/Zixiao-System/classtop/issues)
2. 发起 Pull Request
3. 联系维护者

## 📝 文档更新日志

- **2025-01-XX**: 添加 Linux、macOS 开发环境搭建指南
- **2025-01-XX**: 添加 VSCode、Xcode、Visual Studio 配置指南
- **2025-01-XX**: 创建文档索引

---

**提示**: 建议将本索引页添加到浏览器书签，方便快速查找文档。
