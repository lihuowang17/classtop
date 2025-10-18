# macOS 开发环境搭建指南

本指南将帮助你在 macOS 系统上搭建 ClassTop 的完整开发环境。

## 系统要求

- **操作系统**: macOS 11 (Big Sur) 或更高版本
- **芯片**: Intel x86_64 或 Apple Silicon (M1/M2/M3)
- **内存**: 至少 4GB RAM (推荐 8GB+)
- **磁盘空间**: 至少 10GB 可用空间 (包含 Xcode)

## 前置依赖安装

### 1. 安装 Xcode Command Line Tools

Xcode Command Line Tools 包含编译器和构建工具，是必需的。

```bash
# 安装 Command Line Tools
xcode-select --install
```

点击弹出窗口中的"安装"按钮，等待安装完成。

验证安装：

```bash
xcode-select -p
# 应输出: /Library/Developer/CommandLineTools 或 /Applications/Xcode.app/Contents/Developer
```

**可选**: 如果需要完整的 Xcode (用于 iOS 开发或深度调试)，从 App Store 安装 Xcode。

### 2. 安装 Homebrew

Homebrew 是 macOS 的包管理器，用于安装其他依赖。

```bash
# 安装 Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Apple Silicon 用户需要添加到 PATH
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"

# 验证安装
brew --version
```

### 3. 安装 Node.js

推荐使用 nvm 或 Homebrew 安装：

#### 方法 1: 使用 nvm (推荐)

```bash
# 安装 nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# 重新加载 shell 配置
source ~/.zshrc  # macOS 默认使用 zsh

# 安装 Node.js 18+
nvm install 18
nvm use 18
nvm alias default 18

# 验证安装
node --version  # 应显示 v18.x.x
npm --version
```

#### 方法 2: 使用 Homebrew

```bash
brew install node@18
echo 'export PATH="/opt/homebrew/opt/node@18/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# 验证安装
node --version
npm --version
```

### 4. 安装 Python

macOS 自带 Python，但通常版本较旧。建议安装 Python 3.10+：

```bash
# 使用 Homebrew 安装 Python 3
brew install python@3.11

# 验证安装
python3 --version  # 应显示 3.10+ 或 3.11+
pip3 --version
```

**或者使用 pyenv** (推荐，可管理多个 Python 版本):

```bash
# 安装 pyenv
brew install pyenv

# 添加到 shell 配置
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init --path)"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
source ~/.zshrc

# 安装 Python 3.11
pyenv install 3.11
pyenv global 3.11

# 验证
python --version
```

### 5. 安装 Rust

使用 rustup 安装 Rust 工具链：

```bash
# 安装 rustup
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 选择默认安装选项 (1)
# 重新加载环境变量
source $HOME/.cargo/env

# 验证安装
rustc --version
cargo --version
```

### 6. 安装其他必需工具

```bash
# 安装构建依赖
brew install cmake pkg-config

# 可选：安装更快的链接器
brew install llvm
```

## 克隆并配置项目

### 1. 克隆仓库

```bash
git clone https://github.com/Zixiao-System/classtop.git
cd classtop
```

### 2. 安装项目依赖

```bash
# 安装前端依赖
npm install

# 安装 Python 依赖（如果有 requirements.txt）
pip3 install -r requirements.txt
```

## 开发模式运行

### 启动开发服务器

```bash
# 启动 Tauri 开发模式（会同时启动前端和后端）
npm run tauri dev
```

首次运行会编译 Rust 代码，可能需要 5-10 分钟。

**预期结果**:
- 打开两个窗口：
  - **TopBar 窗口** (1400x50): 置顶课程进度条
  - **Main 窗口** (1200x800): 课程管理界面

### 仅运行前端开发服务器

```bash
npm run dev
```

前端将在 `http://localhost:1420` 上运行。

## 构建生产版本

### 标准构建

```bash
npm run tauri build -- --config src-tauri/tauri.bundle.json --profile bundle-release
```

### 构建产物位置

```bash
# macOS App Bundle
src-tauri/target/bundle-release/bundle/macos/ClassTop.app

# DMG 安装包
src-tauri/target/bundle-release/dmg/ClassTop_*.dmg
```

### 安装和运行

```bash
# 方法 1: 直接运行 .app
open src-tauri/target/bundle-release/bundle/macos/ClassTop.app

# 方法 2: 安装 DMG
open src-tauri/target/bundle-release/dmg/ClassTop_*.dmg
# 然后将 ClassTop 拖到 Applications 文件夹
```

## Apple Silicon 特别说明

### Universal Binary (通用二进制)

如果需要构建同时支持 Intel 和 Apple Silicon 的应用：

```bash
# 添加 x86_64 目标
rustup target add x86_64-apple-darwin

# 构建通用二进制
npm run tauri build -- --target universal-apple-darwin
```

### 交叉编译

在 M1/M2/M3 Mac 上为 Intel Mac 构建：

```bash
rustup target add x86_64-apple-darwin
npm run tauri build -- --target x86_64-apple-darwin
```

在 Intel Mac 上为 Apple Silicon 构建：

```bash
rustup target add aarch64-apple-darwin
npm run tauri build -- --target aarch64-apple-darwin
```

## 代码签名和公证 (可选)

如果需要分发应用，需要 Apple Developer 账号进行签名和公证。

### 1. 配置开发者证书

```bash
# 在 Keychain Access 中导入开发者证书
# 或使用 Xcode 自动管理
```

### 2. 配置 Tauri 签名

在 `src-tauri/tauri.conf.json` 中添加：

```json
{
  "bundle": {
    "macOS": {
      "signingIdentity": "Developer ID Application: Your Name (TEAM_ID)",
      "entitlements": null,
      "exceptionDomain": null,
      "providerShortName": null
    }
  }
}
```

### 3. 公证应用

```bash
# 构建并签名
npm run tauri build

# 公证 DMG (需要 Apple ID 和 app-specific password)
xcrun notarytool submit \
  src-tauri/target/release/bundle/dmg/ClassTop_*.dmg \
  --apple-id "your-email@example.com" \
  --password "app-specific-password" \
  --team-id "YOUR_TEAM_ID" \
  --wait

# 装订公证票据
xcrun stapler staple src-tauri/target/release/bundle/dmg/ClassTop_*.dmg
```

## 常见问题

### 1. 找不到 xcode-select

**错误**: `xcode-select: command not found`

**解决方案**:
```bash
# 确保已安装 Command Line Tools
xcode-select --install
```

### 2. Homebrew 未在 PATH 中

**错误**: `brew: command not found`

**解决方案** (Apple Silicon):
```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

**解决方案** (Intel):
```bash
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.zprofile
source ~/.zprofile
```

### 3. Python 版本冲突

**错误**: `Python 3.10+ required, but found 2.7`

**解决方案**:
```bash
# 使用 python3 而不是 python
which python3
python3 --version

# 或设置别名
echo 'alias python=python3' >> ~/.zshrc
echo 'alias pip=pip3' >> ~/.zshrc
source ~/.zshrc
```

### 4. 权限错误

**错误**: `Operation not permitted` 或权限被拒绝

**解决方案**:
```bash
# 不要使用 sudo 安装 npm 包
npm config set prefix ~/.npm-global
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.zshrc
source ~/.zshrc
```

### 5. Rust 编译慢

**解决方案**: 启用更快的链接器
```bash
# 创建或编辑 ~/.cargo/config.toml
mkdir -p ~/.cargo
cat >> ~/.cargo/config.toml << 'EOF'
[target.x86_64-apple-darwin]
rustflags = ["-C", "link-arg=-fuse-ld=lld"]

[target.aarch64-apple-darwin]
rustflags = ["-C", "link-arg=-fuse-ld=lld"]

[build]
jobs = 8  # 根据 CPU 核心数调整
EOF
```

### 6. 系统托盘不显示

macOS 的系统托盘默认隐藏不常用图标。

**解决方案**:
- 按住 `Command` 键拖动图标调整顺序
- 使用 [Bartender](https://www.macbartender.com/) 或 [Hidden Bar](https://github.com/dwarvesf/hidden) 管理菜单栏图标

### 7. "App is damaged" 错误

未签名的应用可能显示此错误。

**解决方案**:
```bash
# 移除隔离属性
xattr -cr /path/to/ClassTop.app

# 或在"系统偏好设置 > 安全性与隐私"中允许运行
```

## 开发工具推荐

### IDE 配置

- **VSCode**: 参见 [VSCode 配置指南](./VSCODE_SETUP.md)
- **Xcode**: 参见 [Xcode 配置指南](./XCODE_SETUP.md) (用于 Rust 调试和性能分析)

### 推荐工具

- **iTerm2**: 更强大的终端 (`brew install --cask iterm2`)
- **DB Browser for SQLite**: 数据库查看工具 (`brew install --cask db-browser-for-sqlite`)
- **Postman**: API 测试 (`brew install --cask postman`)
- **GitKraken**: Git GUI (`brew install --cask gitkraken`)

## 性能优化建议

### 1. 使用 sccache 加速 Rust 编译

```bash
# 安装 sccache
brew install sccache

# 配置环境变量
echo 'export RUSTC_WRAPPER=sccache' >> ~/.zshrc
source ~/.zshrc
```

### 2. 增加文件监视限制

```bash
# 增加文件监视数量 (对于大型项目)
echo kern.maxfiles=65536 | sudo tee -a /etc/sysctl.conf
echo kern.maxfilesperproc=65536 | sudo tee -a /etc/sysctl.conf
sudo sysctl -w kern.maxfiles=65536
sudo sysctl -w kern.maxfilesperproc=65536
```

### 3. 启用增量编译

在 `~/.cargo/config.toml` 中添加：

```toml
[build]
incremental = true
```

## macOS 系统集成

### 添加到 Dock

```bash
# 创建启动脚本
cat > ~/start-classtop-dev.command << 'EOF'
#!/bin/bash
cd ~/path/to/classtop
npm run tauri dev
EOF

chmod +x ~/start-classtop-dev.command
# 将 .command 文件拖到 Dock
```

### 添加到启动项

1. 打开"系统偏好设置" > "用户与群组" > "登录项"
2. 点击 "+" 添加 ClassTop.app

## 下一步

- 查看 [VSCode 配置指南](./VSCODE_SETUP.md) 设置开发环境
- 查看 [Xcode 配置指南](./XCODE_SETUP.md) 了解调试工具
- 阅读 [CLAUDE.md](../CLAUDE.md) 了解项目架构
- 查看 [API 文档](./API.md) 了解后端接口

## 参考链接

- [Tauri macOS Prerequisites](https://tauri.app/v1/guides/getting-started/prerequisites#macos)
- [Homebrew Documentation](https://docs.brew.sh/)
- [Rust Installation](https://www.rust-lang.org/tools/install)
- [PyTauri Documentation](https://pytauri.github.io/)
- [Apple Developer Documentation](https://developer.apple.com/documentation/)