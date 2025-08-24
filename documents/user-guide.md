# Claude CLI Tools 使用手册

Claude CLI Tools 是一个现代的 AI 驱动命令行工具集合，用于文档处理、内容生成等任务。支持多种 AI 服务提供商（Gemini、Ollama、Anthropic Claude）。

## 📋 目录

1. [功能特性](#功能特性)
2. [系统要求](#系统要求)
3. [安装方法](#安装方法)
4. [快速开始](#快速开始)
5. [核心工具](#核心工具)
6. [配置管理](#配置管理)
7. [文档转换工具（doc2md）](#文档转换工具doc2md)
8. [Claude Code 集成](#claude-code-集成)
9. [故障排除](#故障排除)
10. [开发指南](#开发指南)

## ✨ 功能特性

- **多 AI 服务商支持**：在 Gemini、Ollama 和 Anthropic Claude 之间无缝切换
- **智能文档转换**：将 PDF 和 DOCX 文件转换为清晰、结构化的 Markdown 格式
- **现代 Python 架构**：使用 Python 3.11+，完整类型注解和现代最佳实践
- **简便配置管理**：基于 YAML 的配置文件，支持环境变量
- **类型安全**：完整的类型注解，使用 mypy 验证
- **高性能包管理**：使用 uv 进行快速、可靠的依赖管理

## 📦 系统要求

- **Python 版本**：3.11 或更高版本
- **包管理器**：推荐使用 [uv](https://github.com/astral-sh/uv)
- **操作系统**：支持 Windows、macOS、Linux

## 🚀 安装方法

### 方法一：使用 pipx（推荐）

[pipx](https://pipx.pypa.io/) 是安装 CLI 工具的最佳方式，它为每个工具创建独立环境，同时让命令全局可用。

```bash
# 安装 pipx（如果尚未安装）
pip install pipx
pipx ensurepath

# 从 PyPI 安装 claude-clis（发布后）
pipx install claude-clis

# 或直接从 GitHub 安装
pipx install git+https://github.com/ZhenchongLi/claude-clis.git

# 升级到最新版本
pipx upgrade claude-clis

# 干净卸载
pipx uninstall claude-clis
```

**pipx 的优势：**
- ✅ 隔离环境，避免依赖冲突
- ✅ 命令全局可用
- ✅ 易于升级和卸载
- ✅ 专为 CLI 工具设计

### 方法二：使用 uv

```bash
# 克隆项目
git clone https://github.com/ZhenchongLi/claude-clis.git
cd claude-clis

# 开发模式安装
uv pip install -e .

# 或从 PyPI 安装（发布后）
uv add claude-clis
```

### 方法三：使用 pip

```bash
# 从 PyPI 安装（发布后）
pip install claude-clis

# 或从源码安装
pip install git+https://github.com/ZhenchongLi/claude-clis.git
```

### 安装方式对比

| 安装方式 | 适用场景 | 优点 | 缺点 |
|---------|---------|------|------|
| **pipx** | 普通用户 | 环境隔离，全局命令 | 需要安装 pipx |
| **uv** | 开发者 | 快速，现代化 | 相对较新的工具 |
| **pip** | 传统方式 | 广泛支持 | 可能有依赖冲突 |

## 🎯 快速开始

### 1. 初始化配置

```bash
# 引导式配置设置
claude-clis config init

# 或手动配置 AI 服务商
claude-clis config set ai.provider gemini
claude-clis config set ai.gemini.api_key YOUR_API_KEY
```

### 2. 转换第一个文档

```bash
# 将 PDF 转换为 Markdown
claude-clis doc2md convert document.pdf

# 转换前查看文档信息
claude-clis doc2md info document.pdf

# 测试系统设置
claude-clis doc2md test
```

### 3. 探索可用工具

```bash
# 列出所有可用工具
claude-clis list

# 获取任意命令的帮助
claude-clis doc2md --help
claude-clis config --help
```

## ⚙️ 配置管理

Claude CLI Tools 使用位于 `~/.claude-clis/config.yaml` 的 YAML 配置文件。

### AI 服务商设置

#### Gemini（推荐 - 有免费额度）

```bash
claude-clis config set ai.provider gemini
claude-clis config set ai.gemini.api_key YOUR_GEMINI_API_KEY
```

获取 API 密钥：[Google AI Studio](https://makersuite.google.com/app/apikey)

#### Ollama（本地/隐私优先）

```bash
# 安装并启动 Ollama
ollama serve
ollama pull llama3.2

# 配置 Claude CLI Tools
claude-clis config set ai.provider ollama
claude-clis config set ai.ollama.model llama3.2:latest
```

#### Anthropic Claude

```bash
claude-clis config set ai.provider anthropic
claude-clis config set ai.anthropic.api_key YOUR_CLAUDE_API_KEY
```

获取 API 密钥：[Anthropic Console](https://console.anthropic.com/)

### 配置命令

```bash
# 设置配置值
claude-clis config set key value

# 获取配置值
claude-clis config get key

# 显示所有配置（表格格式）
claude-clis config show

# 显示配置（YAML 格式）
claude-clis config show --format yaml
```

## 📄 文档转换工具（doc2md）

doc2md 是核心工具，用于将各种文档格式转换为 Markdown。

### 支持的文件格式

- **PDF** (.pdf)
- **Microsoft Word** (.docx, .doc)
- **纯文本** (.txt)
- **Markdown** (.md)

### 单文件转换

```bash
# 基本转换
claude-clis doc2md convert document.pdf

# 指定输出文件
claude-clis doc2md convert document.pdf -o output.md

# 使用特定 AI 服务商
claude-clis doc2md convert document.pdf --ai-provider ollama

# 选择输出风格
claude-clis doc2md convert document.pdf --style academic

# 设置文本块大小
claude-clis doc2md convert document.pdf --chunk-size 2000

# 不保留原始格式
claude-clis doc2md convert document.pdf --no-formatting
```

### 批量转换

```bash
# 转换目录中的所有文档
claude-clis doc2md batch /path/to/docs/

# 指定输出目录
claude-clis doc2md batch /path/to/docs/ --output-dir ./markdown/

# 使用文件模式匹配
claude-clis doc2md batch /path/to/docs/ --pattern "*.pdf"

# 设置并发转换数量
claude-clis doc2md batch /path/to/docs/ --max-concurrent 5
```

### 输出风格选项

- **technical**（默认）：适合技术文档
- **academic**：学术论文风格
- **business**：商务文档风格
- **casual**：轻松随意风格

### 文档信息查看

```bash
# 查看文档详细信息
claude-clis doc2md info document.pdf
```

显示信息包括：
- 文件格式和大小
- 页数（PDF）或段落数（Word）
- 文档元数据（标题、作者等）
- 内容可读性状态

### 系统测试

```bash
# 测试所有组件
claude-clis doc2md test
```

检查项目：
- 文档读取器可用性
- AI 服务商配置状态
- 当前配置设置

## 🔧 Claude Code 集成

将 claude-clis 命令注册到 Claude Code 中，使其在 Claude Code 会话中直接可用。

### 注册命令

```bash
# 注册所有 claude-clis 命令到 Claude Code
claude-clis claude-code register

# 使用自定义名称
claude-clis claude-code register --name my-tools

# 强制覆盖已存在的命令
claude-clis claude-code register --force
```

### 管理已注册的命令

```bash
# 列出已注册的命令
claude-clis claude-code list

# 查看集成状态
claude-clis claude-code status

# 注销命令
claude-clis claude-code unregister

# 注销所有命令
claude-clis claude-code unregister --all
```

### 在 Claude Code 中使用

注册后，可以在 Claude Code 中使用这些斜杠命令：

```
/claude-clis-doc2md document.pdf
/claude-clis-doc2md-batch /path/to/docs/
/claude-clis-config show
/claude-clis-help
```

## 🛠️ 故障排除

### 常见问题

#### 1. AI 服务商配置错误

**错误信息**：`AI provider 'gemini' is not properly configured`

**解决方案**：
```bash
# 检查当前配置
claude-clis config show

# 重新初始化配置
claude-clis config init

# 手动设置 API 密钥
claude-clis config set ai.gemini.api_key YOUR_API_KEY
```

#### 2. 文档格式不支持

**错误信息**：`Unsupported file format`

**解决方案**：
- 检查文件扩展名是否为支持的格式
- 使用 `claude-clis doc2md info filename` 检查文件状态

#### 3. 依赖包缺失

**错误信息**：`Failed to load doc2md tool`

**解决方案**：
```bash
# 重新安装依赖
uv pip install -e .

# 或安装特定可选依赖
uv add python-docx pymupdf
```

#### 4. Claude Code 未找到

**错误信息**：`Claude Code not found`

**解决方案**：
- 确保已安装 Claude Code
- 检查 Claude Code 配置目录：`~/.claude`

### 调试技巧

```bash
# 启用详细输出
claude-clis --verbose doc2md convert file.pdf

# 静默模式（仅显示错误）
claude-clis --quiet doc2md convert file.pdf

# 测试系统状态
claude-clis doc2md test
```

## 💻 开发指南

### 开发环境设置

```bash
# 克隆并设置项目
git clone https://github.com/ZhenchongLi/claude-clis.git
cd claude-clis

# 安装开发依赖
uv pip install -e .
uv add --dev pytest mypy black ruff pytest-cov
```

### 运行测试

```bash
# 运行所有测试
uv run pytest

# 运行测试并生成覆盖率报告
uv run pytest --cov=claude_clis

# 类型检查
uv run mypy src/

# 代码规范检查
uv run ruff check src/
uv run black src/
```

### 项目结构

```
claude-clis/
├── src/
│   └── claude_clis/
│       ├── main.py              # 主入口点
│       ├── commands/            # 命令模块
│       │   └── claude_code.py   # Claude Code 集成
│       ├── shared/              # 共享工具
│       │   ├── ai_client.py     # AI 客户端
│       │   ├── config.py        # 配置管理
│       │   └── utils.py         # 工具函数
│       └── tools/               # 工具模块
│           └── doc2md/          # 文档转换工具
├── tests/                       # 测试目录
├── pyproject.toml              # 项目配置
└── README.md                   # 项目说明
```

### 添加新工具

1. 在 `src/claude_clis/tools/` 下创建新目录
2. 实现工具的核心功能和 CLI 接口
3. 在 `src/claude_clis/main.py` 中注册工具
4. 添加相应的测试

### 贡献指南

1. Fork 项目
2. 创建特性分支：`git checkout -b feature/new-tool`
3. 提交更改：`git commit -am 'Add new tool'`
4. 推送分支：`git push origin feature/new-tool`
5. 创建 Pull Request

## 📚 更多资源

- **项目主页**：https://github.com/ZhenchongLi/claude-clis
- **问题报告**：https://github.com/ZhenchongLi/claude-clis/issues
- **API 文档**：查看源代码中的详细注释

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。