# 🌸 Sakura-Bot

[![Release](https://img.shields.io/github/v/release/Sakura520222/Sakura-Bot?style=flat-square)](https://github.com/Sakura520222/Sakura-Bot/releases)
[![License](https://img.shields.io/badge/License-AGPL--3.0-blue?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.13+-blue?style=flat-square&logo=python)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000?style=flat-square)](https://github.com/psf/black)
[![Docker](https://img.shields.io/badge/docker-20.10%2B-blue?style=flat-square&logo=docker)](https://www.docker.com/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)](https://github.com/Sakura520222/Sakura-Bot/pulls)
[![Stars](https://img.shields.io/github/stars/Sakura520222/Sakura-Bot?style=flat-square)](https://github.com/Sakura520222/Sakura-Bot/stargazers)

> **An intelligent Telegram channel management tool powered by AI** 🤖✨

[中文文档](README.md) | [Documentation](wiki) | [Report Bug](https://github.com/Sakura520222/Sakura-Bot/issues) | [Request Feature](https://github.com/Sakura520222/Sakura-Bot/issues)

---

## 📖 About

Sakura Channel Summary Assistant is a sophisticated Telegram channel management solution that leverages cutting-edge AI technology to automatically monitor, analyze, and summarize channel content. Designed for channel administrators, it provides an efficient way to stay updated with channel discussions through intelligent automation.

### ✨ Key Highlights

- 🎯 **AI-Powered Summarization** - Advanced language models extract key insights from conversations
- 🔍 **Intelligent Q&A System** - RAG-based natural language Q&A with semantic search and history queries
- ⏰ **Flexible Scheduling** - Daily, weekly, or multi-day automated summaries
- 🌐 **Multi-Channel Support** - Manage multiple channels simultaneously
- 🤖 **Customizable AI Configuration** - Support for OpenAI-compatible APIs (DeepSeek, OpenAI, etc.)
- 📊 **Interactive Polls** - Engage your community with AI-generated polls
- 📝 **History Management** - Track, export, and analyze all summaries

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.13+** or **Docker 20.10+**
- **Telegram Bot Token** from [@BotFather](https://t.me/BotFather)
- **Telegram API credentials** from [my.telegram.org](https://my.telegram.org)
- **OpenAI-compatible API Key** (e.g., [DeepSeek](https://platform.deepseek.com/), [OpenAI](https://platform.openai.com/))

### 🐳 Docker Deployment (Recommended)

```bash
# Clone the repository
git clone https://github.com/Sakura520222/Sakura-Bot.git
cd Sakura-Bot

# Configure environment variables
cp data/.env.example data/.env
# Edit data/.env with your credentials

# Start the service
docker-compose up -d

# View logs
docker-compose logs -f
```

### 💻 Local Installation

```bash
# Clone the repository
git clone https://github.com/Sakura520222/Sakura-Bot.git
cd Sakura-Bot

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp data/.env.example data/.env
# Edit data/.env with your credentials

# Run the application
python main.py
```

---

## 🎨 Features

### Core Capabilities

| Feature | Description | Status |
|---------|-------------|--------|
| **🤖 AI Summarization** | Advanced AI models analyze and extract key points from channel messages | ✅ |
| **🔍 Auto Monitoring** | Automatically fetches and organizes messages from monitored channels | ✅ |
| **⏰ Flexible Scheduling** | Support for daily, weekly, and multi-day automatic summary frequencies | ✅ |
| **⚡ Manual Trigger** | Generate summaries on-demand via admin commands | ✅ |

### AI & Configuration

| Feature | Description | Status |
|---------|-------------|--------|
| **🔧 Custom AI Config** | Support for multiple OpenAI-compatible API services | ✅ |
| **🎯 Custom Prompts** | Tailor summary style with customizable AI prompts | ✅ |
| **🎯 Poll Prompts** | Configure AI-generated poll content independently | ✅ |
| **🤖 QA Bot Persona** | Customizable persona for QA bot with tailored response style | ✅ |

### Channel Management

| Feature | Description | Status |
|---------|-------------|--------|
| **👥 Multi-Admin** | Configure multiple admin IDs for report distribution | ✅ |
| **🌐 Multi-Channel** | Monitor and summarize multiple channels simultaneously | ✅ |
| **📝 Message Splitting** | Intelligently handle long summaries with automatic segmentation | ✅ |
| **⏱️ Smart Timestamps** | Track summary time to only fetch new messages efficiently | ✅ |
| **🕐 Per-Channel Schedule** | Configure automatic summary times for each channel individually | ✅ |

### Advanced Features

| Feature | Description | Status |
|---------|-------------|--------|
| **🔍 Intelligent Q&A System** | RAG-based natural language Q&A with semantic search and history queries | ✅ |
| **🧠 Vector Storage** | ChromaDB-powered vector storage for semantic search | ✅ |
| **🎯 Reranking** | BGE-Reranker for precise result reordering, improving accuracy | ✅ |
| **💬 Multi-Turn Conversations** | Context-aware dialogue, AI understands pronoun references and conversation history | ✅ |
| **🛡️ Error Recovery** | Intelligent retry mechanism, health checks, and graceful shutdown | ✅ |
| **📊 Interactive Polls** | Auto-generate polls in discussion groups after summaries | ✅ |
| **🎯 Per-Channel Polls** | Configure poll settings independently for each channel | ✅ |
| **🔄 Poll Regeneration** | Admin can regenerate polls with a single button click | ✅ |
| **📜 History Tracking** | Automatic database storage with query, export, and statistics | ✅ |
| **🌍 Internationalization** | Complete multi-language support system, all modules internationalized | ✅ |
| **📢 User Subscription System** | Users can subscribe to channels and receive automatic notifications for new summaries | ✅ |
| **📝 Summary Request Feature** | Users can actively request channel summary generation, reviewed by main bot admin | ✅ |
| **🤖 Cross-Bot Communication** | QA bot and main bot communicate via database queue for inter-process communication | ✅ |
| **🔧 Code Optimization** | Modularized summary generation process with code reuse and unified management | ✅ |
| **📱 Command Menu** | QA Bot automatically registers command menu for direct access to all available commands | ✅ |
| **🗄️ MySQL Database Support** | New MySQL database support for improved performance and concurrency | ✅ |
| **🔄 Database Migration** | One-click migration from SQLite to MySQL with automatic backup and validation | ✅ |
| **📤 Channel Message Forwarding** | Intelligently forward channel messages to target channels with keyword and regex filtering | ✅ |
| **⚡ Startup Check** | Automatically detects old databases and notifies admins with migration suggestions | ✅ |

---

## 📋 Usage

### Command Reference

#### Basic Commands

| Command | Aliases | Description | Example |
|---------|---------|-------------|---------|
| `/start` | `/开始` | View welcome message and introduction | `/start` |
| `/help` | `/帮助` | Display complete command list and usage | `/help` |

#### Core Functions

| Command | Aliases | Description | Example |
|---------|---------|-------------|---------|
| `/summary` | `/立即总结` | Generate immediate weekly summary | `/summary` |

#### AI Configuration

| Command | Aliases | Description | Example |
|---------|---------|-------------|---------|
| `/showprompt` | `/查看提示词` | View current AI prompt | `/showprompt` |
| `/setprompt` | `/设置提示词` | Set custom AI prompt | `/setprompt` |
| `/showaicfg` | `/查看AI配置` | View current AI configuration | `/showaicfg` |
| `/setaicfg` | `/设置AI配置` | Configure custom AI settings | `/setaicfg` |

#### Channel Management

| Command | Aliases | Description | Example |
|---------|---------|-------------|---------|
| `/showchannels` | `/查看频道列表` | List all configured channels | `/showchannels` |
| `/addchannel` | `/添加频道` | Add channel to monitoring list | `/addchannel https://t.me/example` |
| `/deletechannel` | `/删除频道` | Remove channel from monitoring | `/deletechannel https://t.me/example` |

#### Schedule Configuration

| Command | Aliases | Description | Example |
|---------|---------|-------------|---------|
| `/showchannelschedule` | `/查看频道时间配置` | View channel schedule settings | `/showchannelschedule` |
| `/setchannelschedule` | `/设置频道时间配置` | Configure automatic summary time | `/setchannelschedule` |
| `/deletechannelschedule` | `/删除频道时间配置` | Remove channel schedule | `/deletechannelschedule` |
| `/clearsummarytime` | `/清除总结时间` | Clear last summary timestamp | `/clearsummarytime` |
| `/setsendtosource` | `/设置报告发送回源频道` | Toggle source channel reporting | `/setsendtosource` |

#### Poll Configuration

| Command | Aliases | Description | Example |
|---------|---------|-------------|---------|
| `/channelpoll` | `/查看频道投票配置` | View channel poll settings | `/channelpoll` |
| `/setchannelpoll` | `/设置频道投票配置` | Configure channel poll settings | `/setchannelpoll` |
| `/deletechannelpoll` | `/删除频道投票配置` | Remove channel poll configuration | `/deletechannelpoll` |

#### Comment Welcome Configuration

| Command | Aliases | Description | Example |
|---------|---------|-------------|---------|
| `/showcommentwelcome` | `/查看评论区欢迎` | View channel comment welcome settings | `/showcommentwelcome` |
| `/setcommentwelcome` | `/设置评论区欢迎` | Configure channel comment welcome message | `/setcommentwelcome` |
| `/deletecommentwelcome` | `/删除评论区欢迎` | Remove channel comment welcome configuration | `/deletecommentwelcome` |

**Feature Description**:
- Configure welcome messages for each channel's comment section independently
- Support custom welcome message content and button text
- Can disable welcome message feature for specific channels
- Default message: "🌸 评论区已开放，快来抢占沙发吧～"
- Default button: "申请周报总结"

#### System Control

| Command | Aliases | Description | Example |
|---------|---------|-------------|---------|
| `/pause` | `/暂停` | Pause all scheduled tasks | `/pause` |
| `/resume` | `/恢复` | Resume all scheduled tasks | `/resume` |
| `/restart` | `/重启` | Restart the bot | `/restart` |
| `/shutdown` | `/关机` | Shutdown the bot completely | `/shutdown` |

#### QA Bot Control

| Command | Aliases | Description | Example |
|---------|---------|-------------|---------|
| `/qa_status` | `/qa_状态` | View QA bot running status | `/qa_status` |
| `/qa_start` | `/qa_启动` | Start QA bot | `/qa_start` |
| `/qa_stop` | `/qa_停止` | Stop QA bot | `/qa_stop` |
| `/qa_restart` | `/qa_重启` | Restart QA bot | `/qa_restart` |
| `/qa_stats` | `/qa_统计` | View QA bot detailed statistics | `/qa_stats` |

#### Debug & Logs

| Command | Aliases | Description | Example |
|---------|---------|-------------|---------|
| `/showloglevel` | `/查看日志级别` | View current log level | `/showloglevel` |
| `/setloglevel` | `/设置日志级别` | Set log level | `/setloglevel` |
| `/clearcache` | `/清除缓存` | Clear discussion group ID cache | `/clearcache` |
| `/changelog` | `/更新日志` | View update changelog | `/changelog` |

#### History Management

| Command | Aliases | Description | Example |
|---------|---------|-------------|---------|
| `/history` | `/历史` | View historical summaries | `/history` |
| `/export` | `/导出` | Export history records | `/export channel1 csv` |
| `/stats` | `/统计` | View statistics | `/stats` |

#### Language Settings

| Command | Aliases | Description | Example |
|---------|---------|-------------|---------|
| `/language` | `/语言` | View or switch interface language | `/language` / `/language en-US` |

#### Database Migration

| Command | Aliases | Description | Example |
|---------|---------|-------------|---------|
| `/migrate_check` | `/迁移检查` | Check migration readiness | `/migrate_check` |
| `/migrate_start` | `/开始迁移` | Start database migration | `/migrate_start` |
| `/migrate_status` | `/迁移状态` | View migration progress | `/migrate_status` |

**Migration Notes**:
- Support one-click migration from SQLite to MySQL database
- Automatic backup before migration, safe and reliable
- Suitable for production environments and high-concurrency scenarios

**MySQL Configuration Example**:
```env
# ===== Database Configuration =====
DATABASE_TYPE=mysql  # sqlite or mysql

# MySQL Configuration (required when using MySQL)
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=your_mysql_user
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=sakura_bot_db
MYSQL_CHARSET=utf8mb4
MYSQL_POOL_SIZE=5
MYSQL_MAX_OVERFLOW=10
MYSQL_POOL_TIMEOUT=30
```

**Migration Steps**:
1. Create MySQL database: `CREATE DATABASE sakura_bot_db CHARACTER SET utf8mb4;`
2. Configure MySQL connection in `.env`
3. Use `/migrate_check` to check readiness
4. Use `/migrate_start` to begin migration

#### Channel Message Forwarding

| Command | Aliases | Description | Example |
|---------|---------|-------------|---------|
| `/forwarding` | `/转发状态` | View forwarding status and rules list | `/forwarding` |
| `/forwarding_enable` | `/启用转发` | Enable forwarding feature | `/forwarding_enable` |
| `/forwarding_disable` | `/禁用转发` | Disable forwarding feature | `/forwarding_disable` |
| `/forwarding_stats [channel]` | `/转发统计` | View forwarding statistics | `/forwarding_stats` / `/forwarding_stats channel1` |

**Feature Description**:
- Intelligently forward channel messages to target channels
- Support keyword whitelist and blacklist filtering
- Support regex pattern matching
- Support forward mode (show source) and copy mode (no source)
- Automatically record forwarded messages to avoid duplicates
- Provide detailed forwarding statistics

**Configuration**:
Configure forwarding rules in `data/config.json`:

```json
{
  "forwarding": {
    "enabled": true,
    "rules": [
      {
        "source_channel": "https://t.me/source_channel",
        "target_channel": "https://t.me/my_channel",
        "keywords": ["重要", "新闻", "更新"],
        "blacklist": ["广告", "垃圾"],
        "patterns": [],
        "blacklist_patterns": [],
        "copy_mode": false,
        "forward_original_only": false
      }
    ]
  }
}
```

**Configuration Options**:
- `enabled`: Enable forwarding feature (true/false)
- `source_channel`: Source channel URL
- `target_channel`: Target channel URL
- `keywords`: Whitelist keyword list (forward if any keyword matches)
- `blacklist`: Blacklist keyword list (skip if any keyword matches)
- `patterns`: Regex whitelist (forward if any pattern matches)
- `blacklist_patterns`: Regex blacklist (skip if any pattern matches)
- `copy_mode`: Copy mode (true=no source shown, false=show source)
- `forward_original_only`: Only forward original messages (true=only channel original messages, no forwarded messages; false=all messages, default false)

#### UserBot Management

| Command | Aliases | Description | Example |
|---------|---------|-------------|---------|
| `/userbot_status` | `/userbot_状态` | View UserBot status and user info | `/userbot_status` |
| `/userbot_join <channel_link>` | `/userbot_加入` | Manually join a channel (supports public and private channels) | `/userbot_join https://t.me/channel` |
| `/userbot_leave <channel_link>` | `/userbot_离开` | Manually leave a channel | `/userbot_leave https://t.me/channel` |
| `/userbot_list` | `/userbot_列表` | List all channels UserBot has joined | `/userbot_list` |

**Feature Description**:
- **UserBot Auto-Join**: When forwarding is enabled, UserBot automatically joins all source channels in forwarding rules
- **Supported Channel Link Formats**:
  - Public channels: `https://t.me/channelname` or `@channelname`
  - Private channels: `https://t.me/+invitecode` (invite link)
- **Smart Error Handling**:
  - Prompts manual invitation when private channels cannot be auto-joined
  - Shows detailed error info when channel doesn't exist or no permission
  - Prompts correct usage for invalid link formats
- **Automated Notifications**:
  - Notifies admin when auto-join starts
  - Sends result summary after auto-join completes
  - Failed channels list with detailed failure reasons

**Notes**:
- Private channels cannot be auto-joined; UserBot must be manually added as a member
- UserBot must have permission to join channels
- Auto-join only triggers when forwarding feature is enabled
- Can manually manage UserBot's joined channels via commands

### QA Bot Commands

The QA Bot is a standalone Q&A bot (requires a separate `QA_BOT_TOKEN`) and supports the following commands:

#### Basic Commands

| Command | Description |
|---------|-------------|
| `/start` | View welcome message and feature introduction |
| `/help` | Display complete help documentation |
| `/status` | View current quota usage and session status |
| `/clear` | Clear current conversation history and start a new session |
| `/view_persona` | View the current QA bot persona |

#### Subscription Management

| Command | Description | Example |
|---------|-------------|---------|
| `/listchannels` | List available channels for subscription (auto-register) | `/listchannels` |
| `/subscribe <channel_link>` | Subscribe to channel summary notifications (auto-register) | `/subscribe https://t.me/channel` |
| `/unsubscribe <channel_link>` | Unsubscribe from channel | `/unsubscribe https://t.me/channel` |
| `/mysubscriptions` | View my subscription list | `/mysubscriptions` |
| `/request_summary <channel_link>` | Request channel summary generation (auto-register) | `/request_summary https://t.me/channel` |

**Note**: Users are automatically registered when first using subscription features. No separate registration command is needed.

### Configuration Example

Create or edit `data/.env`:

```env
# ===== Telegram Configuration =====
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_BOT_TOKEN=your_bot_token_here

# ===== Language Configuration =====
LANGUAGE=en-US  # Interface language: en-US (English) or zh-CN (Simplified Chinese)

# ===== AI Configuration (OpenAI-compatible APIs) =====
# Option 1: DeepSeek (Recommended)
LLM_API_KEY=your_deepseek_api_key
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat

# Option 2: OpenAI
# LLM_API_KEY=your_openai_api_key
# LLM_BASE_URL=https://api.openai.com/v1
# LLM_MODEL=gpt-4o

# ===== Admin Configuration =====
REPORT_ADMIN_IDS=your_admin_id_here,another_admin_id_here

# ===== Log Level =====
LOG_LEVEL=INFO

# ===== Poll Feature =====
ENABLE_POLL=True

# ===== Q&A Bot Configuration (Optional) =====
QA_BOT_ENABLED=True
QA_BOT_TOKEN=your_qa_bot_token_here  # Get from @BotFather, must differ from main bot
QA_BOT_USER_LIMIT=3                  # Per-user daily quota (default: 3)
QA_BOT_DAILY_LIMIT=200               # Global daily quota (default: 200)

# QA Bot persona (choose one, priority from high to low)
# Option 1: Inline persona text (highest priority)
# QA_BOT_PERSONA=You are a professional technical consultant...
# Option 2: Path to a custom persona file
# QA_BOT_PERSONA=data/custom_persona.txt
# Option 3: Leave unset to use data/qa_persona.txt (default)

# ===== RAG Intelligent Q&A System Configuration (Optional) =====
# Embedding Model Configuration (Required for vector search)
EMBEDDING_API_KEY=your_siliconflow_api_key
EMBEDDING_API_BASE=https://api.siliconflow.cn/v1
EMBEDDING_MODEL=BAAI/bge-m3
EMBEDDING_DIMENSION=1024

# Reranker Configuration (Optional, for improving retrieval accuracy)
RERANKER_API_KEY=your_siliconflow_api_key
RERANKER_API_BASE=https://api.siliconflow.cn/v1/rerank
RERANKER_MODEL=BAAI/bge-reranker-v2-m3
RERANKER_TOP_K=20
RERANKER_FINAL=5

# Vector Database Configuration
VECTOR_DB_PATH=data/vectors
```

> **Note**: The RAG system requires additional API keys. We recommend using [SiliconFlow](https://siliconflow.cn/) for Embedding and Reranker services. For detailed configuration, please refer to the [RAG Quick Start Guide](wiki/RAG_QUICKSTART.md).

---

## 🏗️ Project Structure

```
Sakura-Bot/
│
├── 📁 core/                          # Core modules
│   ├── ai_client.py                  # AI client module
│   ├── process_manager.py            # Process manager (QA Bot subprocess)
│   ├── command_handlers/             # Command handlers
│   ├── telegram/                     # Telegram client
│   └── utils/                        # Utility functions
│
├── 📁 data/                          # Data directory
│   ├── .env                          # Environment configuration
│   ├── config.json                   # AI configuration
│   ├── prompt.txt                    # Summary prompt
│   ├── poll_prompt.txt               # Poll prompt
│   ├── qa_persona.txt                # QA bot persona configuration
│   ├── summaries.db                  # SQLite database
│   └── sessions/                     # Telegram sessions
│
├── 📁 wiki/                          # Documentation
├── 📁 .github/                       # GitHub workflows
│
├── 📄 main.py                        # Entry point
├── 📄 qa_bot.py                      # QA Bot entry point
├── 📄 requirements.txt               # Dependencies
├── 📄 docker-compose.yml             # Docker Compose config
├── 📄 Dockerfile                     # Docker image build
└── 📄 README_EN.md                   # This file
```

---

## 🔧 Tech Stack

| Technology | Purpose | Version |
|------------|---------|---------|
| **Python** | Main language | 3.13+ |
| **Telethon** | Telegram MTProto API client (Main Bot) | 1.34+ |
| **python-telegram-bot** | Telegram Bot API client (QA Bot) | 20.0+ |
| **OpenAI SDK** | AI API integration | 1.0+ |
| **APScheduler** | Task scheduling | 3.10+ |
| **ChromaDB** | Vector database (RAG system) | 0.4+ |
| **aiosqlite** | Async SQLite database | 0.20+ |
| **Pydantic** | Configuration management & validation | 2.0+ |
| **httpx** | HTTP client (Reranker calls) | 0.27+ |
| **python-dotenv** | Environment management | 1.0+ |
| **Docker** | Containerization | 20.10+ |

---

## ❓ FAQ

### Do I need to login on first run?

Yes, first run requires Telegram authentication (phone number + verification code). Session files will be generated for subsequent runs without re-authentication.

### How to get Telegram API credentials?

1. Visit [my.telegram.org](https://my.telegram.org)
2. Login to your Telegram account
3. Click "API development tools"
4. Create an app to get `api_id` and `api_hash`

### Which AI services are supported?

All OpenAI-compatible APIs, including:
- **DeepSeek** (Recommended, cost-effective)
- **OpenAI** official API
- Any third-party OpenAI-compatible service

### How to customize the QA Bot persona?

There are three ways (priority from high to low):

1. **Environment variable**: Set `QA_BOT_PERSONA=You are a professional...` in `.env`
2. **Persona file**: Edit `data/qa_persona.txt` (auto-created on first run)
3. **Config file**: Set the `qa_bot_persona` field in `data/config.json`

Restart the bot for changes to take effect. Use `/view_persona` to check the active persona.

### How to backup data?

```bash
# Backup data directory
tar -czf backup-$(date +%Y%m%d).tar.gz data/
```

---

## 🤝 Contributing

We welcome contributions! Please check our [Contributing Guidelines](CONTRIBUTING.md) and [Code of Conduct](wiki/CODE_OF_CONDUCT.md).

### How to Contribute

#### 📝 Report Issues

If you've found a bug or have a feature suggestion:

1. Check [existing issues](https://github.com/Sakura520222/Sakura-Bot/issues) to ensure it hasn't been reported
2. Use the appropriate [Issue template](.github/ISSUE_TEMPLATE/) to create a new issue
3. Provide as much detail as possible (environment, logs, reproduction steps, etc.)

#### 💻 Submit Code

1. **Fork the repository** - Click the Fork button on GitHub
2. **Clone to local**
   ```bash
   git clone https://github.com/YOUR_USERNAME/Sakura-Bot.git
   cd Sakura-Bot
   ```
3. **Create a feature branch**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/your-feature-name
   ```
4. **Make your changes**
   - Follow [code style guidelines](CONTRIBUTING.md#代码规范)
   - Write meaningful commit messages
   - Add necessary tests
   - Update relevant documentation

5. **Local pre-check** (recommended)
   ```bash
   # Code style check
   ruff check .
   
   # Run tests
   pytest tests/ -v
   ```

6. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat(scope): describe your changes"
   ```

7. **Push to your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request**
   - Create a PR to `main` branch on GitHub
   - Use the [PR template](.github/PULL_REQUEST_TEMPLATE.md)
   - Add appropriate PR labels (e.g., `enhancement`, `bug`)
   - Wait for CI checks and code review

> **Important**: All PRs should be submitted to the `main` branch. Changes to main are automatically synced to the dev branch.

#### 📚 Documentation Contributions

Documentation is equally important! You can:

1. Fix typos and errors
2. Improve clarity of existing documentation
3. Add usage examples
4. Translate documentation

### Development Standards

- **Commit messages**: Follow [Conventional Commits](https://www.conventionalcommits.org/) specification
- **Code style**: Use Ruff for code checking
- **Test requirements**: Ensure all tests pass
- **CI checks**: PRs must pass CI checks (code quality, security scan, Docker build, unit tests)

For detailed information, please refer to the [Contributing Guidelines](CONTRIBUTING.md).

---

## 📄 License

This project is licensed under **GNU Affero General Public License Version 3.0 (AGPL-3.0)**.

### Key Points

- **AGPL-3.0**: Requires source code disclosure for modifications and network services
- **Attribution**: All derivatives must retain original project links and author credits
- **API Responsibility**: Users are responsible for API costs and legal compliance

### Important Notice

- This project is for **personal learning** only; illegal use is prohibited.
- When using code or derivatives, you must cite the original repository
- Network service providers must provide source code per AGPL-3.0
- Project source: https://github.com/Sakura520222/Sakura-Bot

See [LICENSE](LICENSE) for the full license text.

---

## 🙏 Acknowledgments

- [Telethon](https://github.com/LonamiWebs/Telethon) - Powerful Telegram MTProto API framework
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Full-featured Telegram Bot API library
- [OpenAI](https://openai.com/) - Leading AI research and API services
- [DeepSeek](https://www.deepseek.com/) - Cost-effective AI API provider
- [SiliconFlow](https://siliconflow.cn/) - Embedding and Reranker API services
- All [contributors](https://github.com/Sakura520222/Sakura-Bot/graphs/contributors) who helped improve this project

---

## 📞 Support

- 📧 Email: [sakura520222@outlook.com](mailto:sakura520222@outlook.com)
- 🐛 Issues: [GitHub Issues](https://github.com/Sakura520222/Sakura-Bot/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/Sakura520222/Sakura-Bot/discussions)

---

<div align="center">

**🌸 Sakura Channel Summary Assistant** · Making Channel Management Smarter

Made with ❤️ by [Sakura520222](https://github.com/Sakura520222)

[⭐ Star](https://github.com/Sakura520222/Sakura-Bot) · [🍴 Fork](https://github.com/Sakura520222/Sakura-Bot/fork) · [📖 Documentation](wiki) · [🐛 Report Issues](https://github.com/Sakura520222/Sakura-Bot/issues)

</div>
