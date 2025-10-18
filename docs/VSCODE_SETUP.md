# VSCode 开发配置指南

本指南将帮助你在 Visual Studio Code 中配置完整的 ClassTop 开发环境，包括 Vue、Rust、Python 和 Tauri 支持。

## 安装 VSCode

### Windows

从 [Visual Studio Code 官网](https://code.visualstudio.com/) 下载安装器并运行。

### macOS

```bash
# 使用 Homebrew 安装
brew install --cask visual-studio-code

# 或从官网下载 DMG 安装
```

### Linux

```bash
# Ubuntu/Debian
sudo snap install code --classic

# 或使用 apt
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
sudo sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'
sudo apt update
sudo apt install code

# Fedora
sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc
sudo sh -c 'echo -e "[code]\nname=Visual Studio Code\nbaseurl=https://packages.microsoft.com/yumrepos/vscode\nenabled=1\ngpgcheck=1\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc" > /etc/yum.repos.d/vscode.repo'
sudo dnf install code

# Arch
yay -S visual-studio-code-bin
```

## 必备扩展安装

打开 VSCode 后，按 `Ctrl+Shift+X` (macOS: `Cmd+Shift+X`) 打开扩展面板，搜索并安装以下扩展：

### 核心扩展

#### 1. Vue 开发

```
名称: Vue Language Features (Volar)
ID: Vue.volar
描述: Vue 3 官方语言支持
```

```
名称: TypeScript Vue Plugin (Volar)
ID: Vue.vscode-typescript-vue-plugin
描述: Vue 的 TypeScript 支持
```

**重要**: 如果之前安装了 Vetur，请禁用它，因为 Volar 是 Vue 3 的官方推荐。

#### 2. Rust 开发

```
名称: rust-analyzer
ID: rust-lang.rust-analyzer
描述: Rust 官方语言服务器
```

配置建议（添加到 settings.json）：
```json
{
  "rust-analyzer.check.command": "clippy",
  "rust-analyzer.cargo.features": "all",
  "rust-analyzer.procMacro.enable": true
}
```

#### 3. Python 开发

```
名称: Python
ID: ms-python.python
描述: 官方 Python 支持
```

```
名称: Pylance
ID: ms-python.vscode-pylance
描述: Python 语言服务器（快速类型检查）
```

#### 4. Tauri 支持

```
名称: Tauri
ID: tauri-apps.tauri-vscode
描述: Tauri 框架支持
```

### 推荐扩展

#### 代码质量

```
名称: ESLint
ID: dbaeumer.vscode-eslint
描述: JavaScript/Vue 代码检查
```

```
名称: Prettier - Code formatter
ID: esbenp.prettier-vscode
描述: 代码格式化
```

#### 开发效率

```
名称: Path Intellisense
ID: christian-kohler.path-intellisense
描述: 文件路径自动补全
```

```
名称: Auto Rename Tag
ID: formulahendry.auto-rename-tag
描述: 自动重命名配对的 HTML/Vue 标签
```

```
名称: GitLens
ID: eamodio.gitlens
描述: 强化的 Git 功能
```

```
名称: Error Lens
ID: usernamehw.errorlens
描述: 在行内显示诊断信息
```

#### 代码片段

```
名称: Vue VSCode Snippets
ID: sdras.vue-vscode-snippets
描述: Vue 代码片段
```

#### 数据库

```
名称: SQLite
ID: alexcvzz.vscode-sqlite
描述: SQLite 数据库查看和编辑
```

## 快速安装所有扩展

打开 VSCode 终端 (`Ctrl+\`` 或 `Cmd+\``)，运行：

```bash
# 安装所有推荐扩展
code --install-extension Vue.volar
code --install-extension Vue.vscode-typescript-vue-plugin
code --install-extension rust-lang.rust-analyzer
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension tauri-apps.tauri-vscode
code --install-extension dbaeumer.vscode-eslint
code --install-extension esbenp.prettier-vscode
code --install-extension christian-kohler.path-intellisense
code --install-extension formulahendry.auto-rename-tag
code --install-extension eamodio.gitlens
code --install-extension usernamehw.errorlens
code --install-extension sdras.vue-vscode-snippets
code --install-extension alexcvzz.vscode-sqlite
```

## 项目配置

### 1. 创建 `.vscode` 目录

在项目根目录创建 `.vscode` 文件夹（如果不存在）：

```bash
mkdir -p .vscode
```

### 2. 配置 `settings.json`

创建或编辑 `.vscode/settings.json`：

```json
{
  // Vue 配置
  "volar.takeOverMode.enabled": false,
  "[vue]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "editor.formatOnSave": true
  },

  // JavaScript/TypeScript 配置
  "[javascript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "editor.formatOnSave": true
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "editor.formatOnSave": true
  },

  // Rust 配置
  "rust-analyzer.check.command": "clippy",
  "rust-analyzer.cargo.features": "all",
  "rust-analyzer.procMacro.enable": true,
  "rust-analyzer.inlayHints.enable": true,
  "[rust]": {
    "editor.defaultFormatter": "rust-lang.rust-analyzer",
    "editor.formatOnSave": true
  },

  // Python 配置
  "python.defaultInterpreterPath": "python3",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "[python]": {
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  },

  // 文件关联
  "files.associations": {
    "*.vue": "vue",
    "Cargo.lock": "toml",
    "tauri.conf.json": "jsonc"
  },

  // 编辑器配置
  "editor.tabSize": 2,
  "editor.insertSpaces": true,
  "editor.formatOnPaste": true,
  "editor.rulers": [80, 120],
  "editor.minimap.enabled": true,
  "editor.linkedEditing": true,
  "editor.bracketPairColorization.enabled": true,

  // 文件监视排除
  "files.watcherExclude": {
    "**/.git/objects/**": true,
    "**/.git/subtree-cache/**": true,
    "**/node_modules/**": true,
    "**/target/**": true,
    "**/.venv/**": true,
    "**/__pycache__/**": true
  },

  // 搜索排除
  "search.exclude": {
    "**/node_modules": true,
    "**/bower_components": true,
    "**/target": true,
    "**/.venv": true,
    "**/__pycache__": true,
    "**/dist": true
  },

  // 终端配置
  "terminal.integrated.env.osx": {
    "RUST_BACKTRACE": "1"
  },
  "terminal.integrated.env.linux": {
    "RUST_BACKTRACE": "1"
  },
  "terminal.integrated.env.windows": {
    "RUST_BACKTRACE": "1"
  }
}
```

### 3. 配置 `extensions.json`

创建 `.vscode/extensions.json` 推荐扩展给团队成员：

```json
{
  "recommendations": [
    "vue.volar",
    "vue.vscode-typescript-vue-plugin",
    "rust-lang.rust-analyzer",
    "ms-python.python",
    "ms-python.vscode-pylance",
    "tauri-apps.tauri-vscode",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "christian-kohler.path-intellisense",
    "formulahendry.auto-rename-tag",
    "eamodio.gitlens",
    "usernamehw.errorlens",
    "sdras.vue-vscode-snippets",
    "alexcvzz.vscode-sqlite"
  ]
}
```

### 4. 配置任务 `tasks.json`

创建 `.vscode/tasks.json` 用于快速执行常用命令：

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Tauri Dev",
      "type": "shell",
      "command": "npm",
      "args": ["run", "tauri", "dev"],
      "problemMatcher": [],
      "group": {
        "kind": "build",
        "isDefault": true
      },
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "Vite Dev",
      "type": "shell",
      "command": "npm",
      "args": ["run", "dev"],
      "problemMatcher": [],
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "Tauri Build",
      "type": "shell",
      "command": "npm",
      "args": [
        "run",
        "tauri",
        "build",
        "--",
        "--config",
        "src-tauri/tauri.bundle.json",
        "--profile",
        "bundle-release"
      ],
      "problemMatcher": [],
      "group": "build"
    },
    {
      "label": "Cargo Check",
      "type": "shell",
      "command": "cargo",
      "args": ["check"],
      "options": {
        "cwd": "${workspaceFolder}/src-tauri"
      },
      "problemMatcher": ["$rustc"]
    },
    {
      "label": "Cargo Clippy",
      "type": "shell",
      "command": "cargo",
      "args": ["clippy"],
      "options": {
        "cwd": "${workspaceFolder}/src-tauri"
      },
      "problemMatcher": ["$rustc"]
    },
    {
      "label": "Python Type Check",
      "type": "shell",
      "command": "mypy",
      "args": ["src-tauri/python"],
      "problemMatcher": []
    }
  ]
}
```

运行任务：按 `Ctrl+Shift+B` (macOS: `Cmd+Shift+B`) 选择任务。

### 5. 配置调试 `launch.json`

创建 `.vscode/launch.json` 用于调试：

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "lldb",
      "request": "launch",
      "name": "Tauri Debug",
      "cargo": {
        "args": [
          "build",
          "--manifest-path=./src-tauri/Cargo.toml",
          "--no-default-features"
        ]
      },
      "preLaunchTask": "Vite Dev"
    },
    {
      "type": "python",
      "request": "launch",
      "name": "Python: Current File",
      "program": "${file}",
      "console": "integratedTerminal",
      "justMyCode": false
    }
  ]
}
```

**注意**: Rust 调试需要安装 CodeLLDB 扩展：
```bash
code --install-extension vadimcn.vscode-lldb
```

## 代码片段

创建自定义代码片段以提高效率。

### Vue 组件片段

按 `Ctrl+Shift+P` (macOS: `Cmd+Shift+P`)，输入 "Preferences: Configure User Snippets"，选择 "vue.json"：

```json
{
  "Vue 3 Component": {
    "prefix": "v3",
    "body": [
      "<template>",
      "  <div>",
      "    $0",
      "  </div>",
      "</template>",
      "",
      "<script setup>",
      "import { ref, reactive, computed, onMounted } from 'vue'",
      "",
      "</script>",
      "",
      "<style scoped>",
      "",
      "</style>"
    ],
    "description": "Vue 3 Composition API component"
  },
  "PyInvoke Call": {
    "prefix": "pyinvoke",
    "body": [
      "const result = await pyInvoke('${1:command_name}', {",
      "  $0",
      "})"
    ],
    "description": "PyTauri invoke call"
  }
}
```

### Rust 片段

选择 "rust.json"：

```json
{
  "PyTauri Command": {
    "prefix": "pytcmd",
    "body": [
      "#[commands.command()]",
      "async def ${1:command_name}(${2:params}) -> ${3:Response}:",
      "    \"\"\"$0\"\"\"",
      "    pass"
    ],
    "description": "PyTauri command function"
  }
}
```

## 键盘快捷键

### 常用快捷键

| 操作 | Windows/Linux | macOS |
|------|---------------|-------|
| 命令面板 | `Ctrl+Shift+P` | `Cmd+Shift+P` |
| 快速打开文件 | `Ctrl+P` | `Cmd+P` |
| 终端 | ``Ctrl+` `` | ``Cmd+` `` |
| 侧边栏 | `Ctrl+B` | `Cmd+B` |
| 搜索 | `Ctrl+Shift+F` | `Cmd+Shift+F` |
| 运行任务 | `Ctrl+Shift+B` | `Cmd+Shift+B` |
| 转到定义 | `F12` | `F12` |
| 查找引用 | `Shift+F12` | `Shift+F12` |
| 重命名符号 | `F2` | `F2` |
| 格式化文档 | `Shift+Alt+F` | `Shift+Option+F` |

### 自定义快捷键

按 `Ctrl+K Ctrl+S` (macOS: `Cmd+K Cmd+S`) 打开快捷键设置，添加自定义绑定。

推荐添加（在 `keybindings.json` 中）：

```json
[
  {
    "key": "ctrl+shift+d",
    "command": "workbench.action.tasks.runTask",
    "args": "Tauri Dev"
  },
  {
    "key": "ctrl+shift+r",
    "command": "rust-analyzer.reload"
  }
]
```

## 多根工作区配置

如果你在开发多个相关项目，可以创建多根工作区。

创建 `classtop.code-workspace`：

```json
{
  "folders": [
    {
      "path": "."
    },
    {
      "name": "Frontend",
      "path": "./src"
    },
    {
      "name": "Backend",
      "path": "./src-tauri"
    }
  ],
  "settings": {
    // 工作区级别的设置
  }
}
```

## 性能优化

### 排除大型目录

在 `settings.json` 中添加：

```json
{
  "files.watcherExclude": {
    "**/target/**": true,
    "**/node_modules/**": true,
    "**/.venv/**": true
  }
}
```

### 禁用不需要的功能

```json
{
  "editor.minimap.enabled": false,
  "editor.guides.indentation": false,
  "telemetry.telemetryLevel": "off"
}
```

### Rust Analyzer 优化

```json
{
  "rust-analyzer.checkOnSave.command": "check",  // 使用 check 而不是 clippy 以提速
  "rust-analyzer.cargo.loadOutDirsFromCheck": true,
  "rust-analyzer.files.excludeDirs": ["target"]
}
```

## 开发工作流

### 1. 启动开发环境

按 `Ctrl+Shift+B` (macOS: `Cmd+Shift+B`)，选择 "Tauri Dev"。

### 2. 编辑代码

- Vue 文件：`src/` 目录
- Rust 代码：`src-tauri/src/` 目录
- Python 代码：`src-tauri/python/tauri_app/` 目录

### 3. 查看日志

使用 VSCode 内置终端查看输出：
- 前端日志：浏览器开发者工具
- 后端日志：VSCode 终端

### 4. 调试

- **前端**: 使用浏览器开发者工具 (F12)
- **Rust**: 使用 CodeLLDB 扩展 (需要配置 launch.json)
- **Python**: 使用 Python 调试器 (添加断点后按 F5)

### 5. 代码检查

运行任务 "Cargo Clippy" 检查 Rust 代码质量。

## 问题排查

### 1. Volar 与 Vetur 冲突

**问题**: Vue 文件显示重复错误

**解决方案**: 禁用 Vetur 扩展
```
Ctrl+Shift+P -> Extensions: Show Built-in Extensions -> 搜索 Vetur -> 禁用
```

### 2. Rust Analyzer 无法工作

**问题**: 无法跳转到定义或显示错误

**解决方案**: 重新加载 rust-analyzer
```
Ctrl+Shift+P -> rust-analyzer: Restart server
```

### 3. Python 解释器未找到

**问题**: Python 文件显示 "No Python interpreter"

**解决方案**:
```
Ctrl+Shift+P -> Python: Select Interpreter -> 选择 Python 3.10+
```

### 4. 终端找不到命令

**问题**: `npm` 或 `cargo` 命令不存在

**解决方案**: 重启 VSCode 或重新加载窗口
```
Ctrl+Shift+P -> Developer: Reload Window
```

## 附加资源

- [VSCode 官方文档](https://code.visualstudio.com/docs)
- [Vue 3 风格指南](https://vuejs.org/style-guide/)
- [Rust Analyzer 手册](https://rust-analyzer.github.io/manual.html)
- [Tauri 开发指南](https://tauri.app/v1/guides/)

## 下一步

- 阅读 [CLAUDE.md](../CLAUDE.md) 了解项目架构
- 查看 [API 文档](./API.md) 了解后端接口
- 尝试添加新功能或修复 bug
