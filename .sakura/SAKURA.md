# Sakura-Bot 项目概述

## 项目简介
Sakura-Bot 是一款基于 AI 技术的智能 Telegram 频道管理工具，面向频道管理员，提供自动内容总结、智能问答、互动投票生成与历史记录分析等能力，大幅提升社群内容运营效率。

## 技术栈
- **编程语言**：Python 3.13+（代码体量约 150 万行）
- **核心交互**：Telegram Bot API（消息监听、命令分发、频道转发等）
- **AI 与智能**：OpenAI 兼容 API（支持 DeepSeek、OpenAI 等），RAG 检索增强生成技术（语义检索、历史问答），独立提示词系统
- **任务调度**：内置定时调度器，支持每日、每周、多天等频率自动触发总结
- **数据管理**：基于文件或轻量存储的历史记录管理，对话总结持久化
- **测试**：pytest + 集成测试，覆盖率分析（`analyze_coverage.py`）
- **代码质量**：Ruff linter、Black formatter、pre-commit 钩子
- **部署运行**：Docker & Docker Compose，支持本地 Python 运行，提供 shell 脚本和 Windows 批处理启动
- **配置管理**：dotenv 环境变量 + JSON 配置文件

## 项目结构
```
Sakura-Bot/
├── core/                        # 核心业务逻辑
│   ├── ai/                      # AI 客户端、总结、问答、RAG 实现
│   ├── bootstrap/               # 启动初始化与依赖组装
│   ├── commands/                # 命令处理（手动触发总结等）
│   ├── config/                  # 配置解析子模块
│   ├── config.py                # 配置加载入口
│   ├── forwarding/              # 频道消息转发逻辑
│   ├── handlers/                # Telegram 事件处理器（消息、回调等）
│   ├── history_handlers.py      # 历史记录管理
│   └── bot_commands.py          # Bot 命令注册与路由
├── data/                        # 模板与示例文件
│   ├── .env.example             # 环境变量模板
│   ├── config.example.json      # JSON 配置示例
│   ├── prompt.txt               # AI 总结提示词
│   ├── poll_prompt.txt          # 投票问题提示词
│   └── qa_persona.txt           # 问答 Bot 人格设定
├── tests/                       # 测试套件
│   ├── core/                    # 核心模块单元测试
│   ├── integration/             # 集成测试
│   └── test_ai_client.py 等     # 针对性功能测试
├── wiki/                        # 开发者与用户文档
├── main.py                      # 主 Bot 入口
├── qa_bot.py                    # 独立问答 Bot 入口
├── Dockerfile                   # 容器镜像定义
├── docker-compose.yml           # 多服务编排
├── start.sh / start.bat         # 跨平台启动脚本
├── pyproject.toml               # 项目元数据与工具配置
├── requirements.txt             # Python 依赖清单
├── pytest.ini                   # Pytest 配置
├── .pre-commit-config.yaml      # 预提交检查规则
├── run_ruff.py                  # Ruff 执行封装
├── analyze_coverage.py          # 覆盖率分析脚本
├── CHANGELOG.md                 # 版本变更记录
├── CONTRIBUTING.md              # 贡献指南
├── LICENSE                      # AGPL-3.0 许可证
└── README.md / README_EN.md     # 中英文项目说明
```

## 开发约定
- **代码风格**：强制使用 Black 格式化，Ruff 进行静态检查，配置集中在 `pyproject.toml`。所有提交前通过 `pre-commit` 钩子执行代码规范化检查，确保风格统一。
- **测试规范**：以 `pytest` 为主要测试框架，测试文件遵循 `test_*.py` 命名，共享固件定义于 `conftest.py`。同时要求运行覆盖率分析（`analyze_coverage.py`），维持核心逻辑的高测试覆盖。
- **模块化设计**：按功能划分 `core/` 子包，AI、命令、配置、事件处理、转发等职责分离。`main.py` 与 `qa_bot.py` 作为不同服务入口，按需加载模块，避免耦合。
- **配置管理约定**：敏感凭证（Bot Token、API Key 等）通过 `.env` 环境变量注入，非敏感项使用 JSON 配置文件。所有配置统一经 `core/config.py` 校验与加载，降低误配风险。
- **AI 集成约定**：提示词与人格设定独立存放于 `data/` 目录，便于调优与版本管理。AI 客户端抽象在 `core/ai` 中，支持多种 OpenAI 兼容后端，新增模型只需扩展配置，无需修改核心逻辑。
- **文档体系**：提供中英文 README，`wiki/` 目录下沉淀开发者架构、入门说明、CI 修复记录及模块拆分总结。重要改动记录于 `CHANGELOG.md`，贡献流程在 `CONTRIBUTING.md` 中明确。
- **贡献流程**：接受社区 PR，Issue 按模板分类，鼓励功能建议与问题反馈。开发者需遵循测试与代码规范，所有合并前应通过 CI 检查。

本项目以清晰的模块边界、完善的自动化测试和严格的代码质量控制，为多频道 AI 辅助运营提供了一个可扩展、易维护的开源解决方案。