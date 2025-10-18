# Visual Studio 调试与配置指南 (Windows)

本指南介绍如何在 Windows 上使用 Visual Studio 进行 ClassTop（Tauri + Rust）应用的开发、调试和性能分析。

> **注意**: 这是 Windows 专用指南。对于 macOS/Linux 开发，请参考 [VSCode 配置指南](./VSCODE_SETUP.md) 或 [Xcode 配置指南](./XCODE_SETUP.md)。

## Visual Studio vs VSCode

- **Visual Studio Code (VSCode)**: 轻量级代码编辑器，推荐用于日常开发
- **Visual Studio**: 完整的 IDE，提供高级调试和性能分析工具

本指南关注 Visual Studio，用于：
- Rust 代码的高级调试
- 性能分析和优化
- 内存泄漏检测
- 混合 C++/Rust 调试

## 前置要求

### 1. 安装 Visual Studio

下载并安装 [Visual Studio 2022 Community](https://visualstudio.microsoft.com/zh-hans/downloads/) (免费)。

**安装时选择的工作负载**:
- ✅ **"使用 C++ 的桌面开发"**
- ✅ **"Python 开发"** (可选，用于 Python 脚本调试)

**个别组件**（在"单个组件"标签中）:
- ✅ `MSVC v143` 或更新版本
- ✅ `Windows 10/11 SDK`
- ✅ `C++ CMake 工具`
- ✅ `C++ Clang 工具`
- ✅ `Just-In-Time 调试器`

安装大小约 10-20GB。

### 2. 安装 Rust 和 Node.js

参考 [Windows 开发环境搭建](./WINDOWS_SETUP.md)（如果有）或按以下步骤：

```powershell
# 安装 Rust
# 从 https://rustup.rs/ 下载并运行 rustup-init.exe

# 安装 Node.js
# 从 https://nodejs.org/ 下载并安装

# 验证
rustc --version
node --version
npm --version
```

### 3. 配置 Rust 工具链使用 MSVC

```powershell
# 设置 MSVC 为默认工具链
rustup default stable-msvc

# 或为 x86_64 Windows 添加 MSVC 目标
rustup target add x86_64-pc-windows-msvc

# 验证
rustc --version --verbose
# 应显示 "host: x86_64-pc-windows-msvc"
```

## 在 Visual Studio 中打开项目

Visual Studio 不直接支持 Cargo 项目，但可以通过多种方式集成。

### 方法 1: 打开文件夹 (推荐)

Visual Studio 2019+ 支持"打开文件夹"功能。

1. 启动 Visual Studio
2. 选择 `文件` -> `打开` -> `文件夹...`
3. 导航到 ClassTop 项目根目录并选择
4. Visual Studio 会自动检测项目结构

### 方法 2: 创建解决方案

创建一个 Visual Studio 解决方案来组织项目。

1. 创建 `ClassTop.sln` 文件：
   ```powershell
   cd /path/to/classtop
   # 创建空的解决方案文件
   New-Item -Path "ClassTop.sln" -ItemType File
   ```

2. 在 Visual Studio 中打开 `ClassTop.sln`
3. 添加现有项目：
   - 右键解决方案 -> `添加` -> `现有项目...`
   - 选择 `src-tauri/Cargo.toml`（需要 Rust 扩展）

### 方法 3: 使用 CMake (高级)

为 Rust 项目生成 CMake 配置以集成 Visual Studio。

创建 `src-tauri/CMakeLists.txt`：

```cmake
cmake_minimum_required(VERSION 3.15)
project(ClassTop)

# 添加自定义构建命令
add_custom_target(
    cargo_build ALL
    COMMAND cargo build
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Building Rust project with Cargo"
)

add_custom_target(
    cargo_clean
    COMMAND cargo clean
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Cleaning Rust project"
)
```

然后在 Visual Studio 中打开 `CMakeLists.txt`。

## 安装 Visual Studio 扩展

### 必备扩展

#### 1. Rust Language Server (rust-analyzer)

虽然 Visual Studio 没有官方 Rust 扩展，但可以使用第三方方案：

**VisualRust** (社区维护):
1. 打开 `工具` -> `扩展和更新`
2. 搜索 "Rust"
3. 安装 "Visual Rust" 或 "Rust Language Service"

**或使用 rust-analyzer 外部工具**:
```powershell
# 安装 rust-analyzer
rustup component add rust-analyzer

# 配置为外部工具（见下文）
```

#### 2. Python 开发工具

如果未在安装时选择 Python 工作负载：
1. `工具` -> `获取工具和功能...`
2. 选择 "Python 开发"
3. 安装

### 推荐扩展

- **Visual Studio Color Theme Editor**: 自定义颜色主题
- **Productivity Power Tools**: 增强的编辑功能
- **Code Maid**: 代码清理和组织
- **File Icons**: 文件类型图标

## 配置外部工具

将常用命令添加为外部工具以快速访问。

### 添加 Cargo 命令

1. 打开 `工具` -> `外部工具...`
2. 点击 `添加`

**Cargo Build**:
- **标题**: Cargo Build
- **命令**: `C:\Users\YourName\.cargo\bin\cargo.exe`
- **参数**: `build --manifest-path=$(ProjectDir)\src-tauri\Cargo.toml`
- **初始目录**: `$(ProjectDir)`
- ✅ 使用输出窗口

**Cargo Run**:
- **标题**: Cargo Run
- **命令**: `C:\Users\YourName\.cargo\bin\cargo.exe`
- **参数**: `run --manifest-path=$(ProjectDir)\src-tauri\Cargo.toml`
- **初始目录**: `$(ProjectDir)`

**Tauri Dev**:
- **标题**: Tauri Dev
- **命令**: `npm.cmd`
- **参数**: `run tauri dev`
- **初始目录**: `$(ProjectDir)`

**Tauri Build**:
- **标题**: Tauri Build
- **命令**: `npm.cmd`
- **参数**: `run tauri build -- --config src-tauri/tauri.bundle.json --profile bundle-release`
- **初始目录**: `$(ProjectDir)`

### 使用外部工具

在 `工具` 菜单中选择添加的命令即可运行。

## 调试配置

### 1. 配置 Rust 调试

创建 Visual Studio 调试配置。

#### 启动调试器

1. 构建调试版本：
   ```powershell
   cd src-tauri
   cargo build
   ```

2. 在 Visual Studio 中：
   - `调试` -> `附加到进程...`
   - 选择 `classtop.exe`
   - 或使用 `调试` -> `启动而不调试` (Ctrl+F5)

#### 配置 launch.vs.json

在项目根目录创建 `.vs/launch.vs.json`：

```json
{
  "version": "0.2.1",
  "configurations": [
    {
      "type": "default",
      "project": "src-tauri/Cargo.toml",
      "name": "Cargo Build & Debug",
      "preLaunchTask": "cargo build",
      "program": "${workspaceRoot}/src-tauri/target/debug/classtop.exe",
      "args": [],
      "stopAtEntry": false,
      "cwd": "${workspaceRoot}",
      "environment": [
        {
          "name": "RUST_BACKTRACE",
          "value": "1"
        }
      ],
      "console": "integratedTerminal"
    },
    {
      "type": "python",
      "name": "Python: Current File",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal"
    }
  ]
}
```

### 2. 设置断点

- **Rust 代码**: 在 `.rs` 文件中点击左侧边栏添加断点（红点）
- **Python 代码**: 同样方式在 `.py` 文件中添加

### 3. 调试控制

| 操作 | 快捷键 |
|------|--------|
| 启动调试 | F5 |
| 逐语句 (Step Into) | F11 |
| 逐过程 (Step Over) | F10 |
| 跳出 (Step Out) | Shift+F11 |
| 继续 | F5 |
| 停止调试 | Shift+F5 |

### 4. 查看变量

- **局部变量**: `调试` -> `窗口` -> `局部变量`
- **监视**: `调试` -> `窗口` -> `监视` -> `监视 1`
- **调用堆栈**: `调试` -> `窗口` -> `调用堆栈`

## 性能分析

Visual Studio 提供强大的性能分析工具。

### 1. 性能探查器

#### 启动探查器

1. `调试` -> `性能探查器...` (Alt+F2)
2. 选择探查工具：
   - **CPU 使用率**: CPU 性能分析
   - **.NET/C++ 内存**: 内存分配追踪
   - **检测**: 函数计时
   - **并发可视化工具**: 线程活动
3. 点击 `启动`

#### CPU 使用率分析

**用途**: 找出 CPU 热点

**步骤**:
1. 启动 CPU 探查器
2. 在应用中执行操作
3. 停止探查
4. 查看 "热路径" 和 "调用树"

**优化建议**:
- 按 "总 CPU %" 排序函数
- 展开调用树找到具体代码
- 使用 "调用方/被调用方" 视图分析函数关系

#### 内存使用情况分析

**用途**: 检测内存泄漏和过度分配

**步骤**:
1. 启动内存探查器
2. 创建快照 1
3. 执行操作（如加载课程表）
4. 创建快照 2
5. 比较两个快照的差异

**查找泄漏**:
- 重复操作多次
- 如果对象数量持续增长，可能存在泄漏
- 点击对象类型查看分配堆栈

### 2. 诊断工具窗口

在调试时自动显示，提供实时性能数据。

**启用**:
- `调试` -> `窗口` -> `显示诊断工具` (Ctrl+Alt+F2)

**功能**:
- 实时 CPU 使用率图表
- 实时内存使用情况
- 事件时间线
- 快照对比

### 3. 并发可视化工具

**用途**: 分析多线程性能

**步骤**:
1. `分析` -> `并发可视化工具` -> `启动新分析`
2. 选择应用程序
3. 查看线程活动、同步事件、CPU 利用率

**优化建议**:
- 识别线程阻塞
- 查找不必要的线程切换
- 优化锁竞争

## 性能优化工作流

### 1. 识别瓶颈

使用 CPU 探查器：

```powershell
# 构建 Release 版本
cd src-tauri
cargo build --release
```

在 Visual Studio 中：
1. `调试` -> `性能探查器...`
2. 选择 "CPU 使用率"
3. 浏览到 `target/release/classtop.exe`
4. 启动分析

### 2. 内存泄漏检测

使用内存探查器和 Valgrind for Windows：

```powershell
# 安装 Dr. Memory (类似 Valgrind)
choco install drmemory -y

# 运行内存检测
drmemory.exe -- target/debug/classtop.exe
```

### 3. 代码覆盖率

使用 `cargo-tarpaulin` 或 Visual Studio 企业版的代码覆盖率工具。

```powershell
# 安装 tarpaulin (需要 WSL)
cargo install cargo-tarpaulin

# 运行覆盖率测试
cargo tarpaulin --out Html
```

## 常见性能问题

### 问题 1: 启动时间过长

**诊断**:
- 使用 CPU 探查器分析启动过程
- 查看 "函数详细信息"

**常见原因**:
- 同步的数据库初始化
- 大量的启动时配置加载
- 阻塞的网络请求

**解决方案**:
- 异步初始化
- 懒加载非关键组件
- 使用启动画面

### 问题 2: UI 无响应

**诊断**:
- 使用 CPU 探查器查看主线程
- 检查诊断工具的 UI 线程时间线

**常见原因**:
- 主线程执行耗时操作
- 频繁的 DOM 操作
- 阻塞的 Python 调用

**解决方案**:
- 将工作移到后台线程
- 批处理 UI 更新
- 使用 `pyInvoke` 异步调用

### 问题 3: 内存持续增长

**诊断**:
- 使用内存探查器跟踪分配
- 对比多个快照

**常见原因**:
- 事件监听器未清理
- Rust 中的 `Rc<T>` 循环引用
- Python 对象未释放

**解决方案**:
- 使用 `Weak<T>` 打破循环引用
- 手动清理事件监听器
- 实现对象池或缓存策略

## 静态代码分析

### 1. Visual Studio 代码分析

**启用**:
1. 右键项目 -> `属性`
2. `代码分析` -> 启用 "在生成时启用代码分析"

### 2. Rust Clippy

在 Visual Studio 终端中运行：

```powershell
cd src-tauri
cargo clippy -- -W clippy::all
```

**集成到外部工具**:
- **标题**: Cargo Clippy
- **命令**: `cargo.exe`
- **参数**: `clippy --manifest-path=$(ProjectDir)\src-tauri\Cargo.toml -- -W clippy::all`

### 3. Python 代码检查

```powershell
# 安装 pylint
pip install pylint

# 运行检查
pylint src-tauri/python/tauri_app
```

## 项目模板和代码片段

### 创建 Rust 代码片段

1. `工具` -> `代码片段管理器...`
2. `导入...` -> 选择 `.snippet` 文件

**PyTauri Command 片段** (`pytauri-command.snippet`):

```xml
<?xml version="1.0" encoding="utf-8"?>
<CodeSnippets xmlns="http://schemas.microsoft.com/VisualStudio/2005/CodeSnippet">
  <CodeSnippet Format="1.0.0">
    <Header>
      <Title>PyTauri Command</Title>
      <Shortcut>pytcmd</Shortcut>
      <Description>Creates a PyTauri command function</Description>
      <SnippetTypes>
        <SnippetType>Expansion</SnippetType>
      </SnippetTypes>
    </Header>
    <Snippet>
      <Code Language="Python">
        <![CDATA[@commands.command()
async def $CommandName$($params$) -> $ResponseType$:
    """$description$"""
    $end$
    pass]]>
      </Code>
      <Declarations>
        <Literal>
          <ID>CommandName</ID>
          <Default>command_name</Default>
        </Literal>
        <Literal>
          <ID>params</ID>
          <Default>params</Default>
        </Literal>
        <Literal>
          <ID>ResponseType</ID>
          <Default>Response</Default>
        </Literal>
        <Literal>
          <ID>description</ID>
          <Default>Command description</Default>
        </Literal>
      </Declarations>
    </Snippet>
  </CodeSnippet>
</CodeSnippets>
```

## 常见问题

### 1. 无法附加调试器

**问题**: "无法附加到进程"

**解决方案**:
```powershell
# 以管理员身份运行 Visual Studio
# 或禁用防病毒软件的实时保护
```

### 2. Rust 符号加载失败

**问题**: 断点显示 "未加载符号"

**解决方案**:
```powershell
# 确保使用 debug 构建
cargo build

# 添加 PDB 路径到 Visual Studio
# 工具 -> 选项 -> 调试 -> 符号 -> 添加 target/debug
```

### 3. Python 调试不工作

**问题**: Python 断点未命中

**解决方案**:
1. 确保安装了 Python 开发工作负载
2. 检查 Python 解释器设置
3. 使用 `debugpy` 进行远程调试：

```python
import debugpy
debugpy.listen(5678)
debugpy.wait_for_client()
```

### 4. 性能探查器崩溃

**问题**: 探查器启动时应用崩溃

**解决方案**:
- 使用 Release 构建而非 Debug
- 禁用 "收集分配数据"
- 增加采样间隔

## 命令行工具集成

### Windows Performance Analyzer

```powershell
# 安装 Windows Performance Toolkit
# 从 Windows ADK 下载: https://learn.microsoft.com/en-us/windows-hardware/get-started/adk-install

# 记录性能跟踪
wpr -start GeneralProfile -filemode

# 运行应用
target/release/classtop.exe

# 停止记录
wpr -stop performance.etl

# 分析
wpa.exe performance.etl
```

### PerfView (Microsoft)

```powershell
# 下载 PerfView
# https://github.com/microsoft/perfview/releases

# 记录 CPU 跟踪
PerfView.exe collect /MaxCollectSec:30

# 运行应用并停止后分析
PerfView.exe performance.etl.zip
```

## 持续集成 (CI)

在 GitHub Actions 或 Azure Pipelines 中集成 Visual Studio 构建。

**GitHub Actions 示例** (`.github/workflows/windows-build.yml`):

```yaml
name: Windows Build

on: [push, pull_request]

jobs:
  build:
    runs-on: windows-latest

    steps:
    - uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: 18

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install Rust
      uses: actions-rs/toolchain@v1
      with:
        toolchain: stable-msvc
        override: true

    - name: Install dependencies
      run: npm install

    - name: Build
      run: npm run tauri build

    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: windows-build
        path: src-tauri/target/release/bundle/
```

## 参考资源

- [Visual Studio 文档](https://docs.microsoft.com/zh-cn/visualstudio/)
- [Rust 编程语言](https://doc.rust-lang.org/book/)
- [Tauri 指南](https://tauri.app/v1/guides/)
- [Windows 性能分析](https://learn.microsoft.com/zh-cn/windows-hardware/test/wpt/)

## 下一步

- 阅读 [CLAUDE.md](../CLAUDE.md) 了解项目架构
- 查看 [VSCode 配置指南](./VSCODE_SETUP.md) 用于日常开发
- 尝试使用性能探查器优化应用性能
