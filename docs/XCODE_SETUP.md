# Xcode 调试与性能分析指南

本指南介绍如何使用 Xcode 对 ClassTop（Tauri + Rust）应用进行高级调试、性能分析和优化。

> **注意**: 这是 macOS 专用指南。Xcode 仅在 macOS 上可用。对于 Linux/Windows 开发，请参考 [VSCode 配置指南](./VSCODE_SETUP.md)。

## 为什么使用 Xcode？

虽然 VSCode 是主要开发环境，但 Xcode 提供了强大的 macOS 原生工具：

- **Instruments**: 专业的性能分析工具（CPU、内存、网络、磁盘 I/O）
- **LLDB 调试器**: 原生的 macOS 调试体验
- **Memory Graph**: 可视化内存泄漏检测
- **Time Profiler**: 精确的 CPU 性能分析
- **Allocations**: 内存分配追踪

## 前置要求

### 1. 安装 Xcode

从 App Store 安装 Xcode (免费)：

```bash
# 或使用命令行安装
xcode-select --install
```

完整 Xcode 大小约 10-15GB，需要耐心等待下载。

### 2. 安装 Command Line Tools

```bash
# 安装（如果尚未安装）
xcode-select --install

# 验证
xcode-select -p
# 应输出: /Applications/Xcode.app/Contents/Developer
```

### 3. 接受许可协议

```bash
sudo xcodebuild -license accept
```

## 在 Xcode 中打开项目

Xcode 不直接支持 Tauri/Cargo 项目，但可以通过以下方法使用其调试工具。

### 方法 1: 使用 Xcode 打开可执行文件

1. **构建项目**：
```bash
cd ~/path/to/classtop
npm run tauri build
```

2. **在 Finder 中定位 .app**：
```bash
open src-tauri/target/release/bundle/macos/
```

3. **右键 ClassTop.app** -> "显示包内容" -> 导航到 `Contents/MacOS/ClassTop`

4. **用 Xcode 打开**：
   - 启动 Xcode
   - 菜单: `File` -> `Open...`
   - 选择可执行文件 `Contents/MacOS/ClassTop`
   - 或直接拖放到 Xcode 图标

### 方法 2: 从命令行启动 Xcode 调试

```bash
# 构建调试版本
cd src-tauri
cargo build

# 使用 lldb 启动调试
lldb target/debug/classtop

# 在 lldb 中
(lldb) run
```

### 方法 3: 创建 Xcode 项目（高级）

为 Rust 项目生成 Xcode 项目文件：

```bash
# 安装 cargo-xcode
cargo install cargo-xcode

# 在 src-tauri 目录生成 Xcode 项目
cd src-tauri
cargo xcode

# 打开生成的 .xcodeproj
open classtop.xcodeproj
```

## 使用 Instruments 进行性能分析

Instruments 是 Xcode 的性能分析工具集。

### 启动 Instruments

#### 方法 1: 从 Xcode

1. 打开 Xcode
2. 菜单: `Xcode` -> `Open Developer Tool` -> `Instruments`
3. 选择模板（见下文）
4. 点击"Choose Target"，选择 ClassTop 应用或可执行文件

#### 方法 2: 从命令行

```bash
# 直接启动 Instruments
open -a Instruments

# 或使用特定模板
instruments -t "Time Profiler" -D ~/Desktop/trace.trace /path/to/ClassTop.app
```

### 常用 Instruments 模板

#### 1. Time Profiler (CPU 性能分析)

**用途**: 找出 CPU 密集型代码段

**使用步骤**:
1. 选择 "Time Profiler" 模板
2. 点击红色录制按钮启动应用
3. 执行应用中的操作（如加载课程表、更新进度条）
4. 点击停止按钮
5. 查看 "Call Tree"，按 "Self Time" 排序

**优化建议**:
- 查找 Self Time 高的函数
- 展开调用栈找到具体代码位置
- 使用 "Invert Call Tree" 选项反转视图

#### 2. Allocations (内存分配追踪)

**用途**: 追踪内存分配和泄漏

**使用步骤**:
1. 选择 "Allocations" 模板
2. 启动并使用应用
3. 点击 "Mark Generation" 创建内存快照
4. 执行操作后再次点击 "Mark Generation"
5. 查看两个快照之间的内存增长

**查找泄漏**:
- 重复执行相同操作多次
- 如果内存持续增长而不释放，可能存在泄漏
- 使用 "Statistics" 视图查看增长最快的对象类型

#### 3. Leaks (内存泄漏检测)

**用途**: 自动检测内存泄漏

**使用步骤**:
1. 选择 "Leaks" 模板
2. 启动应用并正常使用
3. Instruments 会自动每 10 秒检测一次泄漏
4. 泄漏检测到时会在时间线上显示红色标记

**修复泄漏**:
- 点击泄漏条目查看调用栈
- 识别泄漏发生的代码位置
- 在 Rust 中，通常检查 `Rc<T>` 循环引用或未正确释放的资源

#### 4. System Trace (系统级性能分析)

**用途**: 综合分析 CPU、线程、系统调用

**使用步骤**:
1. 选择 "System Trace" 模板
2. 录制短时间的会话（1-2 分钟）
3. 查看线程活动、系统调用、CPU 使用率

**优化建议**:
- 检查是否有过多的系统调用
- 识别阻塞主线程的操作
- 查找异常的线程创建/销毁模式

#### 5. Network (网络活动监控)

**用途**: 监控网络请求（如 API 调用）

**使用步骤**:
1. 选择 "Network" 模板
2. 启动应用并触发网络请求
3. 查看请求详情、响应时间、数据量

#### 6. File Activity (磁盘 I/O 分析)

**用途**: 监控文件读写操作

**使用步骤**:
1. 选择 "File Activity" 模板
2. 执行数据库操作（课程增删改查）
3. 查看 SQLite 文件的读写模式

## LLDB 调试器

Xcode 内置的 LLDB 是强大的原生调试器。

### 从 Xcode 调试

1. 打开 Xcode
2. `File` -> `Open...` -> 选择可执行文件
3. 设置断点：
   - 打开源文件（如果可用）
   - 点击行号左侧添加断点
4. `Product` -> `Run` (或 `Cmd+R`)

### 从命令行使用 LLDB

```bash
# 启动 LLDB
cd src-tauri
cargo build
lldb target/debug/classtop

# LLDB 命令
(lldb) breakpoint set --name main  # 在 main 函数设置断点
(lldb) run                          # 运行程序
(lldb) step                         # 单步进入
(lldb) next                         # 单步跳过
(lldb) continue                     # 继续运行
(lldb) print variable_name          # 打印变量
(lldb) bt                           # 查看调用栈
(lldb) frame variable               # 查看当前帧的所有变量
(lldb) quit                         # 退出
```

### Rust 专用 LLDB 命令

```bash
# 加载 Rust LLDB 辅助工具
(lldb) command script import /path/to/rust/etc/lldb_rust_formatters.py

# 或在 ~/.lldbinit 中自动加载
echo 'command script import ~/.rustup/toolchains/stable-aarch64-apple-darwin/lib/rustlib/etc/lldb_rust_formatters.py' >> ~/.lldbinit
```

**美化 Rust 类型显示**:
- 默认情况下，Rust 的 `String`、`Vec` 等类型在 LLDB 中显示复杂
- 加载格式化工具后会以更易读的方式显示

## Memory Graph (内存图调试)

Xcode 的 Memory Graph 可以可视化对象引用关系。

### 使用 Memory Graph

1. 在 Xcode 中运行应用
2. 点击底部工具栏的"Debug Memory Graph"按钮（类似三个方块的图标）
3. 查看对象树和引用关系

### 查找循环引用

1. 在左侧边栏按内存大小排序
2. 查找异常大的对象或不应存在的对象
3. 点击对象查看引用图
4. 寻找循环引用（A -> B -> C -> A）

## 性能优化工作流

### 1. 识别瓶颈

使用 Time Profiler：
```bash
# 构建 release 版本以获得准确的性能数据
npm run tauri build -- --profile release

# 用 Instruments 分析
instruments -t "Time Profiler" /path/to/ClassTop.app
```

### 2. 分析内存使用

使用 Allocations：
```bash
instruments -t "Allocations" /path/to/ClassTop.app
```

**关注点**:
- 启动时的内存分配
- 反复操作后的内存增长
- 空闲时的内存占用

### 3. 检测泄漏

使用 Leaks 模板自动扫描。

**常见 Rust 泄漏原因**:
- `Rc<RefCell<T>>` 循环引用
- 未正确关闭的文件/数据库连接
- 长生命周期的闭包捕获大对象
- FFI 边界的内存未释放

### 4. 优化 I/O

使用 File Activity 模板：
- 检查是否有不必要的文件读写
- SQLite 查询是否可以优化（使用索引、批量操作）
- 日志写入是否过于频繁

## 常见性能问题和解决方案

### 问题 1: 启动时间过长

**诊断**:
```bash
# 使用 Time Profiler 分析启动过程
instruments -t "Time Profiler" -l 10000 /path/to/ClassTop.app
```

**常见原因**:
- 初始化时执行大量数据库查询
- 加载过多的初始数据
- 同步的网络请求

**解决方案**:
- 延迟非关键初始化
- 使用异步加载
- 实现启动画面掩盖加载时间

### 问题 2: UI 卡顿

**诊断**: 使用 Time Profiler 查看主线程占用

**常见原因**:
- 在主线程执行耗时操作
- 频繁的 UI 更新
- 未优化的渲染

**解决方案**:
- 将耗时操作移至后台线程
- 节流/防抖频繁更新
- 使用虚拟滚动（如果适用）

### 问题 3: 内存持续增长

**诊断**: 使用 Allocations 和 Leaks

**常见原因**:
- 事件监听器未清理
- 缓存无限增长
- Vue 组件未正确销毁

**解决方案**:
- 在组件销毁时清理监听器
- 实现 LRU 缓存
- 检查 `onUnmounted` 钩子

## Xcode 项目配置优化

如果使用 `cargo-xcode` 生成了项目，可以进行以下配置：

### 1. 构建配置

在 Xcode 中:
1. 选择项目根节点
2. "Build Settings" 标签
3. 搜索并调整：
   - `Optimization Level`: Release 使用 `-O3`
   - `Debug Information Format`: `DWARF with dSYM`

### 2. Scheme 配置

1. `Product` -> `Scheme` -> `Edit Scheme...`
2. **Run**:
   - Build Configuration: `Debug` (开发) 或 `Release` (性能分析)
   - 启用 "Debug executable"
3. **Profile**:
   - Build Configuration: `Release`

### 3. 环境变量

在 Scheme 的 "Arguments" 标签中添加：
```
RUST_BACKTRACE=1
RUST_LOG=debug
```

## 命令行工具

### 1. `sample` - CPU 采样

```bash
# 采样 10 秒
sample ClassTop 10 -file ~/Desktop/classtop_sample.txt

# 查看采样结果
open ~/Desktop/classtop_sample.txt
```

### 2. `leaks` - 内存泄漏检测

```bash
# 检测运行中的应用
leaks ClassTop

# 持续监控
leaks ClassTop -atExit
```

### 3. `heap` - 堆分析

```bash
# 查看堆对象
heap ClassTop

# 按大小排序
heap ClassTop | head -50
```

### 4. `vmmap` - 虚拟内存映射

```bash
# 查看内存布局
vmmap ClassTop

# 摘要信息
vmmap -summary ClassTop
```

## 集成到开发流程

### 定期性能检查清单

每次重大更改后：

1. **启动时间**: 使用 Time Profiler 确保 < 3 秒
2. **内存占用**: 使用 Allocations 确保 < 200MB（空闲时）
3. **泄漏检测**: 使用 Leaks 确保无泄漏
4. **CPU 使用**: 空闲时 < 5%

### 自动化性能测试

创建脚本 `scripts/profile.sh`：

```bash
#!/bin/bash

APP_PATH="./src-tauri/target/release/bundle/macos/ClassTop.app"
OUTPUT_DIR="./performance_reports"

mkdir -p "$OUTPUT_DIR"

echo "Running Time Profiler..."
instruments -t "Time Profiler" -D "$OUTPUT_DIR/time_profile.trace" "$APP_PATH" &
PID=$!
sleep 30
kill $PID

echo "Running Allocations..."
instruments -t "Allocations" -D "$OUTPUT_DIR/allocations.trace" "$APP_PATH" &
PID=$!
sleep 30
kill $PID

echo "Running Leaks..."
instruments -t "Leaks" -D "$OUTPUT_DIR/leaks.trace" "$APP_PATH" &
PID=$!
sleep 30
kill $PID

echo "Performance profiling complete. Results in $OUTPUT_DIR"
```

## 常见问题

### 1. Instruments 无法附加到进程

**问题**: "Failed to attach to process"

**解决方案**:
```bash
# 确保应用未被代码签名限制
codesign --remove-signature /path/to/ClassTop.app/Contents/MacOS/ClassTop

# 或在开发者设置中允许调试
sudo DevToolsSecurity -enable
```

### 2. 符号信息缺失

**问题**: Instruments 显示地址而非函数名

**解决方案**:
```bash
# 确保构建时包含调试符号
cargo build --profile release-with-debug

# 在 Cargo.toml 中添加
[profile.release-with-debug]
inherits = "release"
debug = true
```

### 3. LLDB 断点未命中

**问题**: 断点显示灰色或未触发

**解决方案**:
- 确保使用 `debug` 构建配置
- 检查代码是否被编译优化掉
- 使用函数名断点而非行号断点

## 参考资源

- [Instruments 官方文档](https://help.apple.com/instruments/mac/)
- [LLDB 调试指南](https://lldb.llvm.org/use/tutorial.html)
- [Rust LLDB 扩展](https://github.com/rust-lang/rust/tree/master/src/etc)
- [Xcode 性能优化指南](https://developer.apple.com/library/archive/documentation/Performance/Conceptual/PerformanceOverview/)

## 下一步

- 阅读 [CLAUDE.md](../CLAUDE.md) 了解项目架构
- 查看 [macOS 开发环境搭建](./MACOS_SETUP.md)
- 尝试使用 Instruments 分析当前应用的性能瓶颈
