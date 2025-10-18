# Linux 开发环境搭建指南

本指南将帮助你在 Linux 系统上搭建 ClassTop 的完整开发环境。

## 系统要求

- **操作系统**: Ubuntu 20.04+, Fedora 36+, Arch Linux, 或其他主流 Linux 发行版
- **内存**: 至少 4GB RAM (推荐 8GB+)
- **磁盘空间**: 至少 5GB 可用空间

## 前置依赖安装

### 1. 系统依赖

不同发行版的安装命令：

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install -y \
    build-essential \
    curl \
    wget \
    file \
    libssl-dev \
    libgtk-3-dev \
    libayatana-appindicator3-dev \
    librsvg2-dev \
    libwebkit2gtk-4.0-dev \
    libsoup2.4-dev \
    libjavascriptcoregtk-4.0-dev \
    patchelf
```

#### Fedora

```bash
sudo dnf install -y \
    gcc-c++ \
    curl \
    wget \
    file \
    openssl-devel \
    gtk3-devel \
    libappindicator-gtk3-devel \
    librsvg2-devel \
    webkit2gtk4.0-devel \
    libsoup-devel \
    javascriptcoregtk4.0-devel
```

#### Arch Linux

```bash
sudo pacman -Syu
sudo pacman -S --needed \
    base-devel \
    curl \
    wget \
    file \
    openssl \
    gtk3 \
    libappindicator-gtk3 \
    librsvg \
    webkit2gtk \
    libsoup
```

### 2. Node.js 安装

推荐使用 nvm (Node Version Manager) 安装：

```bash
# 安装 nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# 重新加载 shell 配置
source ~/.bashrc  # 或 source ~/.zshrc

# 安装 Node.js 18 或更高版本
nvm install 18
nvm use 18
nvm alias default 18

# 验证安装
node --version  # 应显示 v18.x.x
npm --version
```

或者使用发行版包管理器：

```bash
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Fedora
sudo dnf install nodejs

# Arch
sudo pacman -S nodejs npm
```

### 3. Python 安装

```bash
# Ubuntu/Debian
sudo apt install -y python3 python3-pip python3-venv

# Fedora
sudo dnf install -y python3 python3-pip

# Arch
sudo pacman -S python python-pip

# 验证安装 (需要 3.10+)
python3 --version
```

### 4. Rust 安装

使用 rustup 安装 Rust：

```bash
# 安装 rustup
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 选择默认安装选项 (1)
# 安装完成后，重新加载环境变量
source $HOME/.cargo/env

# 验证安装
rustc --version
cargo --version
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
pip3 install --user -r requirements.txt
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

### 构建应用

```bash
npm run tauri build -- --config src-tauri/tauri.bundle.json --profile bundle-release
```

### 构建产物位置

构建完成后，可在以下目录找到：

```bash
# AppImage (通用 Linux 包)
src-tauri/target/bundle-release/appimage/

# deb 包 (Debian/Ubuntu)
src-tauri/target/bundle-release/deb/

# RPM 包 (Fedora/RHEL)
src-tauri/target/bundle-release/rpm/
```

### 安装构建的应用

```bash
# AppImage
chmod +x src-tauri/target/bundle-release/appimage/classtop_*.AppImage
./src-tauri/target/bundle-release/appimage/classtop_*.AppImage

# deb (Ubuntu/Debian)
sudo dpkg -i src-tauri/target/bundle-release/deb/classtop_*.deb

# RPM (Fedora)
sudo rpm -i src-tauri/target/bundle-release/rpm/classtop-*.rpm
```

## 常见问题

### 1. Webkit2GTK 错误

**错误**: `Package webkit2gtk-4.0 was not found`

**解决方案**:
```bash
# Ubuntu/Debian
sudo apt install libwebkit2gtk-4.0-dev

# Fedora
sudo dnf install webkit2gtk4.0-devel
```

### 2. Python 版本过低

**错误**: `Python 3.10+ required`

**解决方案**:
```bash
# Ubuntu 20.04 需要添加 deadsnakes PPA
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.10 python3.10-venv python3.10-dev
```

### 3. 权限问题

**错误**: `Permission denied` when running npm install

**解决方案**:
```bash
# 修复 npm 权限
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.profile
source ~/.profile
```

### 4. Rust 工具链问题

**错误**: `error: linker 'cc' not found`

**解决方案**:
```bash
# 安装构建工具
sudo apt install build-essential  # Ubuntu/Debian
sudo dnf groupinstall "Development Tools"  # Fedora
sudo pacman -S base-devel  # Arch
```

### 5. 系统托盘图标不显示

某些桌面环境 (如 GNOME) 默认不支持系统托盘。

**解决方案**:
```bash
# GNOME 用户安装扩展
sudo apt install gnome-shell-extension-appindicator  # Ubuntu
# 或手动从 https://extensions.gnome.org/ 安装 AppIndicator 扩展
```

## 开发工具推荐

- **VSCode**: 参见 [VSCode 配置指南](./VSCODE_SETUP.md)
- **Git GUI**: GitKraken, Sublime Merge
- **数据库工具**: DB Browser for SQLite

## 性能优化建议

### 1. 加速 Rust 编译

```bash
# 使用 sccache 缓存编译
cargo install sccache
echo 'export RUSTC_WRAPPER=sccache' >> ~/.bashrc
source ~/.bashrc
```

### 2. 使用更快的链接器

```bash
# 安装 mold (现代链接器)
# Ubuntu/Debian
sudo apt install mold

# Arch
sudo pacman -S mold

# 在 Cargo 配置中启用
mkdir -p ~/.cargo
cat >> ~/.cargo/config.toml << 'EOF'
[target.x86_64-unknown-linux-gnu]
linker = "clang"
rustflags = ["-C", "link-arg=-fuse-ld=mold"]
EOF
```

### 3. 调整并行编译

```bash
# 在 ~/.cargo/config.toml 中添加
[build]
jobs = 4  # 根据 CPU 核心数调整
```

## 下一步

- 查看 [VSCode 配置指南](./VSCODE_SETUP.md) 设置开发环境
- 阅读 [CLAUDE.md](../CLAUDE.md) 了解项目架构
- 查看 [API 文档](./API.md) 了解后端接口

## 参考链接

- [Tauri Linux Prerequisites](https://tauri.app/v1/guides/getting-started/prerequisites#linux)
- [Node.js Downloads](https://nodejs.org/)
- [Rust Installation](https://www.rust-lang.org/tools/install)
- [PyTauri Documentation](https://pytauri.github.io/)