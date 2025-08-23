# 项目初始化请求

请帮我创建一个 Python CLI 工具集项目，具体要求如下：

## 项目概述
- **项目名**: `claude-clis`
- **功能**: 一个包含多个 AI 驱动的 CLI 工具的工具集，第一个工具是 `doc2md`
- **技术栈**: Python + Click + 多 AI 提供商支持
- **架构**: 单仓库多工具模式（monorepo）

## 项目结构要求
```
claude-clis/
├── pyproject.toml          # 现代 Python 项目配置
├── README.md               # 项目说明文档
├── src/
│   └── claude_clis/
│       ├── __init__.py
│       ├── main.py         # 主入口，工具选择器
│       ├── shared/         # 共享模块
│       │   ├── __init__.py
│       │   ├── config.py   # 全局配置管理
│       │   ├── ai_client.py # 多 AI 提供商统一客户端
│       │   └── utils.py    # 通用工具函数
│       └── tools/          # 各个 CLI 工具
│           ├── __init__.py
│           └── doc2md/     # 第一个工具：文档转换
│               ├── __init__.py
│               ├── cli.py  # doc2md 命令行入口
│               ├── readers/
│               │   ├── __init__.py
│               │   ├── word.py
│               │   └── pdf.py
│               ├── processor.py  # AI 处理逻辑
│               └── markdown_writer.py
└── tests/                  # 测试目录
    ├── __init__.py
    ├── shared/
    └── tools/
        └── doc2md/
```

## CLI 接口设计
需要支持以下命令：

```bash
# 主工具入口（显示所有可用工具）
claude-clis --help
claude-clis list

# doc2md 工具
claude-clis doc2md convert input.docx -o output.md
claude-clis doc2md convert input.pdf --style academic --sections auto -o result.md
claude-clis doc2md convert input.pdf --ai-provider ollama -o result.md
claude-clis doc2md batch /path/to/docs/ --output-dir ./markdown/

# 全局配置管理
claude-clis config set api_key your-api-key
claude-clis config set ai.provider gemini
claude-clis config show

# 工具管理
claude-clis install-tool tool-name  # 为未来扩展预留
```

## 依赖包要求
在 pyproject.toml 中包含：

**核心依赖**:
- `click>=8.1.0` - CLI 框架
- `rich>=13.8.0` - 美化输出和进度条
- `python-docx>=1.2.0` - Word 文档处理
- `pymupdf>=1.26.3` - PDF 处理
- `pydantic-ai>=0.0.14` - 现代 AI 框架，支持多提供商
- `pydantic>=2.11.0` - 数据验证和类型安全
- `pyyaml>=6.0.2` - 配置文件处理
- `httpx>=0.27.0` - HTTP 客户端（用于 Ollama）

**AI 提供商依赖**:
- `google-generativeai>=0.8.0` - Gemini API 客户端
- `anthropic>=0.34.0` - Claude API 客户端（备用）

**可选增强依赖**:
- `pymupdf4llm` - 专门为 LLM 优化的 PDF 处理
- `rich-click>=1.8.0` - Rich 风格的 Click 帮助输出

**开发依赖**:
- `pytest>=8.0` - 测试框架
- `mypy>=1.11` - 类型检查
- `black>=24.0` - 代码格式化
- `ruff>=0.6.0` - 现代 linter
- `pytest-cov>=5.0` - 测试覆盖率

## 开发环境要求
- **Python 版本: 3.9+**（充分利用现代类型系统特性）
- **必须使用 uv 作为包管理器**
- 包含基本的测试结构
- 使用 uv 的项目初始化和依赖管理
- **启用严格的类型检查和现代 Python 特性**

## uv 项目配置要求
1. 使用 `uv init claude-clis --python 3.9` 初始化项目
2. 使用 `uv add` 命令添加所有依赖
3. 在 pyproject.toml 中正确配置 uv 相关设置
4. 支持开发依赖分组：`uv add --dev pytest black ruff mypy pytest-cov`
5. **配置 Python 版本约束为 3.9+**
6. **在 pyproject.toml 中设置 `requires-python = ">=3.9"`**

## 具体实现要求

### 1. pyproject.toml 配置
- 使用现代 Python 项目配置格式
- **设置 Python 版本要求: `requires-python = ">=3.9"`**
- 设置正确的项目入口点 `claude-clis = "claude_clis.main:main"`
- 包含所有必要依赖
- 支持可选依赖分组（如 `doc2md` 相关的依赖）
- **配置 mypy 和其他工具的设置**

### 2. 主 CLI 框架（main.py）
- 使用 Click 创建主命令组
- 实现工具发现和路由机制
- 提供 `list` 命令显示所有可用工具
- 全局配置管理（config 子命令）
- 美化的帮助信息和工具描述

### 3. 共享模块设计
- **config.py**: 统一的配置管理，支持多 AI 提供商配置
- **ai_client.py**: 多 AI 提供商统一接口（使用 Pydantic AI）
- **utils.py**: 通用工具函数（文件处理、格式化等）

### 4. AI 提供商集成要求
- **使用 Pydantic AI 框架**实现统一的 AI 接口
- **支持三种提供商**：
  - Gemini (google-generativeai)
  - 本地 Ollama (通过 HTTP 客户端)
  - Anthropic Claude (备用选项)
- **配置驱动的提供商切换**：
  - 支持配置文件、环境变量、命令行参数
  - 优先级：命令行 > 环境变量 > 配置文件
- **统一的错误处理和重试机制**
- **类型安全的 AI 响应处理**

### 5. doc2md 工具实现
- 独立的 CLI 接口，通过主入口调用
- 实现 convert、batch 等子命令
- **集成多 AI 提供商支持**：
  - 支持 `--ai-provider` 参数临时切换
  - 智能文档分块和上下文管理
  - 针对不同提供商优化的 prompt 模板
- 集成共享的配置管理系统

### 6. 工具注册机制
- 每个工具都要在主入口注册
- 支持工具的动态发现和加载
- 为未来添加新工具预留接口

### 7. README.md
- 包含项目介绍、安装方法、使用示例
- 工具集概览和各工具的功能说明
- 多 AI 提供商的配置和切换说明
- 为添加新工具提供指导

## 配置文件示例
`~/.claude-clis/config.yaml`:
```yaml
ai:
  provider: "gemini"  # 默认使用 Gemini (gemini | ollama | anthropic)

  # Gemini 配置
  gemini:
    api_key: "your-gemini-api-key"
    model: "gemini-1.5-pro"
    temperature: 0.3
    max_tokens: 4096

  # 本地 Ollama 配置
  ollama:
    base_url: "http://localhost:11434"
    model: "llama3.2:latest"
    temperature: 0.3
    timeout: 120

  # Anthropic 配置（备用）
  anthropic:
    api_key: "your-anthropic-api-key"
    model: "claude-3-sonnet-20240229"
    temperature: 0.3
    max_tokens: 4096

tools:
  doc2md:
    default_style: "technical"
    chunk_size: 4000
    preserve_formatting: true
    output_format: "markdown"
```

## 代码质量要求
- **使用现代 Python 类型系统**：
  - 所有函数和方法都要有完整的类型注解
  - 使用 `from __future__ import annotations` 启用延迟求值
  - 利用 Python 3.9+ 的内置泛型（如 `list[str]` 而不是 `List[str]`）
  - 使用 `typing.Protocol` 定义接口
  - 适当使用 `Union`, `Optional`, `Literal` 等高级类型

- **代码结构**：
  - 每个模块都要有完整的类型注解
  - 使用 Pydantic 模型进行数据验证
  - 适当的错误处理和异常类型定义
  - 遵循现代 Python 最佳实践

## 类型检查配置
在 pyproject.toml 中添加 mypy 配置：
```toml
[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
strict_equality = true
```

## AI 提供商集成要求

### 1. 多提供商支持架构
- **使用 Pydantic AI 作为统一框架**
- **支持的提供商**：
  - **Gemini**: 作为主要提供商（免费额度大，性能好）
  - **Ollama**: 本地部署选项（隐私保护，离线工作）
  - **Anthropic Claude**: 备用选项（文档处理专长）

### 2. 提供商切换机制
- **配置文件默认**: `~/.claude-clis/config.yaml` 中设置默认提供商
- **环境变量覆盖**: `CLAUDE_CLIS_AI_PROVIDER=ollama`
- **命令行参数**: `--ai-provider gemini`
- **优先级**: 命令行参数 > 环境变量 > 配置文件

### 3. AI 客户端设计要求
- **类型安全的统一接口**: 使用 Pydantic AI 的 Agent 模式
- **智能错误处理**: 自动重试、降级策略
- **性能优化**: 连接池、请求缓存
- **上下文管理**: 长文档的智能分块处理
- **Provider 抽象**: 便于后续添加新的 AI 提供商

### 4. 文档处理 AI 优化
- **智能分块策略**: 根据文档结构和 AI 模型上下文限制
- **上下文保持**: 确保分块处理时不丢失文档连贯性
- **格式优化**: 针对不同 AI 提供商调优 prompt 模板
- **质量验证**: AI 输出的 Markdown 格式验证

## 扩展性设计
- 支持插件式添加新工具
- 统一的工具接口规范
- **共享的多 AI 提供商处理能力**
- 一致的用户体验
- **AI 提供商的热切换**（无需重启）

## 实现重点
1. **多 AI 提供商无缝切换**: 用户可以根据需求、成本、隐私要求选择不同提供商
2. **智能文档处理**: 自动识别文档类型，选择最佳的提取和处理策略
3. **类型安全的开发体验**: 充分利用 Python 3.9+ 类型系统和 Pydantic AI 的类型安全特性
4. **可扩展架构**: 便于后续添加新的文档格式支持和 AI 提供商

## 预期的 uv 工作流程
```bash
# 项目初始化（指定 Python 3.9+）
uv init claude-clis --python 3.9
cd claude-clis

# 添加核心依赖
uv add "click>=8.1.0" "rich>=13.8.0" "python-docx>=1.2.0" "pymupdf>=1.26.3" "pydantic>=2.11.0" "pyyaml>=6.0.2" "httpx>=0.27.0"

# 添加 AI 相关依赖
uv add "pydantic-ai>=0.0.14" "google-generativeai>=0.8.0" "anthropic>=0.34.0"

# 添加可选增强依赖
uv add "pymupdf4llm" "rich-click>=1.8.0"

# 添加开发依赖
uv add --dev "pytest>=8.0" "mypy>=1.11" "black>=24.0" "ruff>=0.6.0" "pytest-cov>=5.0"

# 开发模式安装
uv install -e .

# 运行工具
uv run claude-clis --help
uv run claude-clis doc2md convert sample.pdf --ai-provider gemini

# 类型检查
uv run mypy src/

# 代码格式化
uv run black src/
uv run ruff check src/
```

## 注意事项
1. **必须使用 uv 包管理器进行项目初始化和依赖管理**
2. 所有模块都要有适当的错误处理
3. CLI 要有友好的用户提示和进度显示
4. 代码结构要便于后续扩展
5. 遵循 Python 最佳实践和 PEP 8 规范
6. 使用 uv 的最佳实践：
   - 使用 `uv init --python 3.9` 创建项目
   - 使用 `uv add` 管理依赖
   - 使用 `uv run` 执行脚本
   - 配置适当的 Python 版本约束
7. **在 pyproject.toml 中设置 `requires-python = ">=3.9"`**
8. **实现多 AI 提供商的无缝切换机制**

请特别注意 AI 提供商的统一接口设计，确保切换提供商时用户体验一致，同时充分发挥每个提供商的特长。使用 uv 创建完整的项目结构和基础代码框架，确保项目可以通过 `uv install -e .` 安装并运行基本命令。