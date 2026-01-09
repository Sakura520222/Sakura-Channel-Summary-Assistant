# Sakura-频道总结助手 v1.1.3

Sakura-频道总结助手是一个基于Telegram API和AI技术的智能频道内容管理工具，专为Telegram频道管理员设计，提供自动化的消息汇总和报告生成服务。支持多种OpenAI兼容的AI服务，包括DeepSeek、OpenAI等。

## 最新更新 (v1.1.3)

### 🚀 新增功能
- **完整的Web管理界面**：提供直观的浏览器界面管理机器人所有功能
- **Docker容器化支持**：Web管理界面完全支持Docker部署
- **自动化发布流程**：GitHub工作流自动打包和发布

### 🔧 技术改进
- **线程安全通信**：Web界面和Telegram客户端通过队列安全通信
- **全面的错误处理**：防止程序崩溃，提高系统稳定性
- **生产就绪配置**：Docker Compose包含健康检查、资源限制、日志配置

### 📦 部署方式
- **本地运行**：`python main.py`，访问 http://localhost:8000
- **Docker运行**：`docker-compose up -d`，访问 http://localhost:8000
- **默认密码**：Sakura

### 🐛 问题修复
- 修复了Web管理界面触发总结时的数据库锁定问题
- 修复了身份验证和事件循环冲突问题
- 修复了控制台闪退和任务结果反馈问题

## 功能特性

- 🔍 **自动消息抓取**：定期监控指定Telegram频道，自动抓取并整理消息内容
- 🤖 **AI智能总结**：利用AI大模型对消息进行深度分析，提取核心要点
- 🔧 **自定义AI配置**：支持通过指令灵活配置API Key、Base URL和Model，兼容多种OpenAI API服务
- ⏰ **定时周报推送**：每周一早上9点自动生成并发送频道周报
- ⚡ **手动触发总结**：支持管理员通过命令随时生成总结
- 🎯 **自定义提示词**：允许管理员设置专属提示词，灵活调整总结风格和重点
- 👥 **多管理员支持**：可配置多个管理员ID，报告将同时发送给所有管理员
- 📝 **长消息分段发送**：智能处理超长总结内容，自动分段发送，确保完整送达
- 📊 **灵活日志级别控制**：支持通过环境变量、配置文件或Telegram指令动态调整日志级别，便于调试和生产环境使用
- 🌐 **多频道支持**：支持配置多个Telegram频道，同时监控和总结多个频道的内容
- 📋 **频道管理命令**：提供便捷的指令用于查看、添加和删除频道，方便管理员管理频道列表
- ⏱️ **智能总结时间记录**：自动记录每次总结的时间，下次总结时仅获取自上次总结以来的新消息，提高总结效率和准确性
- ⏰ **频道级时间配置**：支持为每个频道单独配置自动总结时间，不同频道可在不同时间执行总结
- 🛡️ **错误处理与恢复**：智能重试机制、错误统计、健康检查和优雅关闭，提高系统稳定性
- 🌐 **完整的Web管理界面**：提供直观的Web界面管理机器人配置和功能
  - **仪表板**：系统概览、健康状态、错误统计
  - **频道管理**：添加/删除频道，设置自动总结时间
  - **配置管理**：查看和修改AI配置
  - **任务管理**：手动触发总结，查看定时任务和下次执行时间
  - **日志查看**：查看系统日志，支持搜索和清空
  - **系统信息**：API凭证、管理员列表、错误统计详情

## 技术栈

- Python 3.13
- Telethon（Telegram API客户端）
- OpenAI SDK（调用DeepSeek API）
- APScheduler（定时任务调度）
- python-dotenv（环境变量管理）
- 自定义错误处理模块（智能重试、健康检查、优雅关闭）

## 快速开始

### 环境要求

- Python 3.13或更高版本
- 一个Telegram Bot Token（从@BotFather获取）
- Telegram API ID和API Hash（从https://my.telegram.org 获取）
- 一个OpenAI兼容的API Key（如DeepSeek、OpenAI等）

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置文件

创建`.env`文件，并填写以下配置：

```env
# Telegram配置
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_BOT_TOKEN=your_bot_token

# AI配置（支持DeepSeek、OpenAI等OpenAI兼容API）
# 方式1：使用DeepSeek专属配置（兼容旧版本）
DEEPSEEK_API_KEY=your_deepseek_api_key

# 方式2：使用通用LLM配置（推荐，支持任意OpenAI兼容API）
# LLM_API_KEY=your_llm_api_key
# LLM_BASE_URL=https://api.deepseek.com  # 或 https://api.openai.com/v1 等
# LLM_MODEL=deepseek-chat  # 或 gpt-3.5-turbo 等

# 频道配置
TARGET_CHANNEL=https://t.me/your_channel

# 管理员配置（支持多个ID，用逗号分隔）
REPORT_ADMIN_IDS=admin_id1,admin_id2

# 日志级别配置（可选，默认DEBUG）
# 可用值：DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO
```

### 运行项目

```bash
python main.py
```

## Docker 部署

本项目提供完整的 Docker 部署方案，支持一键部署和持久化数据存储。

### 环境要求

- Docker 20.10+ 和 Docker Compose 2.0+
- 已配置好的 `.env` 文件（参考上方配置文件部分）

### 快速部署

1. **准备环境文件**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，填写您的配置
   ```

2. **使用 Docker Compose 一键部署**
   ```bash
   # 构建并启动容器
   docker-compose up -d
   
   # 查看容器日志
   docker-compose logs -f
   
   # 停止容器
   docker-compose down
   ```

3. **首次运行登录**
   - 首次运行需要Telegram登录授权
   - 查看容器日志获取登录二维码或链接
   ```bash
   docker-compose logs -f
   ```
   - 按照提示完成登录流程

### 手动构建 Docker 镜像

```bash
# 构建镜像
docker build -t sakura-summary-bot .

# 运行容器
docker run -d \
  --name sakura-summary-bot \
  --restart unless-stopped \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/bot_session.session:/app/bot_session.session \
  --env-file .env \
  sakura-summary-bot
```

### 数据持久化

容器使用以下卷进行数据持久化，所有数据都保存在本地主机上：

| 本地路径 | 容器内路径 | 说明 |
|----------|------------|------|
| `./data/` | `/app/data` | 配置文件目录，包含：<br>- `config.json`: AI配置（API Key、Base URL、Model等）<br>- `prompt.txt`: 自定义提示词<br>- `.last_summary_time.json`: 上次总结时间记录 |
| `./bot_session.session` | `/app/bot_session.session` | Telegram会话文件，避免重复登录 |

#### 文件位置说明
- **所有配置文件都保存在本地**：容器重启或重新部署时，配置不会丢失
- **本地文件结构**：
  ```
  tg-bot/
  ├── data/                    # 数据目录（自动创建）
  │   ├── config.json         # AI配置
  │   ├── prompt.txt          # 提示词
  │   └── .last_summary_time.json # 总结时间记录
  ├── bot_session.session     # Telegram会话文件
  ├── .env                    # 环境变量配置
  └── docker-compose.yml      # Docker部署配置
  ```

#### 配置文件管理
1. **初始配置**：首次运行前，复制`.env.example`为`.env`并填写配置
2. **运行时配置**：通过Telegram命令设置的AI配置会保存到`./data/config.json`
3. **手动修改**：可以直接编辑本地文件，重启容器后生效
4. **备份恢复**：备份`./data/`目录和`./bot_session.session`文件即可备份所有配置

### 管理命令

```bash
# 查看容器状态
docker-compose ps

# 查看实时日志
docker-compose logs -f

# 进入容器
docker-compose exec sakura-summary-bot bash

# 重启服务
docker-compose restart

# 停止并删除容器
docker-compose down

# 更新服务（重新构建镜像）
docker-compose up -d --build
```

### 健康检查

容器包含健康检查机制，可通过以下命令查看健康状态：

```bash
docker inspect --format='{{json .State.Health}}' sakura-summary-bot
```

### 故障排除

1. **容器启动失败**
   ```bash
   # 查看详细日志
   docker-compose logs --tail=100
   ```

2. **Telegram登录问题**
   - 确保 `.env` 文件中的 API 凭证正确
   - 删除 `bot_session.session` 文件重新登录
   ```bash
   rm bot_session.session
   docker-compose restart
   ```

3. **权限问题**
   ```bash
   # 修复数据目录权限
   sudo chown -R $USER:$USER data/
   ```

## Web管理界面

Sakura-频道总结助手提供了完整的Web管理界面，可以通过浏览器直观地管理机器人配置和功能。

### 访问方式

1. **启动机器人**：`python main.py`（Web服务自动在端口8000启动）
2. **访问Web管理界面**：http://localhost:8000
3. **登录**：使用默认密码"Sakura"

### 功能页面

#### 1. 仪表板 (`/`)
- **系统概览**：显示机器人状态、频道数量、管理员数量
- **健康状态**：显示系统健康检查结果
- **错误统计**：显示错误类型和数量统计
- **AI配置**：显示当前AI模型和基础URL

#### 2. 频道管理 (`/channels`)
- **频道列表**：查看所有已配置的频道
- **添加频道**：通过表单添加新的频道
- **删除频道**：一键删除不需要的频道
- **时间配置**：为每个频道单独设置自动总结时间
  - 支持设置星期几（周一至周日）
  - 支持设置具体时间（小时和分钟）
  - 实时保存配置到`config.json`

#### 3. 配置管理 (`/config`)
- **AI配置管理**：查看和修改AI配置
  - API密钥（部分隐藏显示）
  - 基础URL（支持DeepSeek、OpenAI等）
  - 模型名称
- **配置同步**：所有更改实时保存到`config.json`文件
- **与Telegram命令兼容**：Web界面和Telegram命令通过相同的配置文件同步

#### 4. 任务管理 (`/tasks`)
- **手动触发总结**：为指定频道立即生成总结报告
- **定时任务列表**：查看所有频道的定时任务配置
- **下次执行时间**：实时计算并显示每个频道的下次执行时间
  - 显示相对时间（如"3天2小时后"）
  - 显示具体日期和时间
  - 每分钟自动更新
- **任务执行历史**：查看最近的任务执行记录

#### 5. 日志查看 (`/logs`)
- **日志内容**：查看系统日志文件内容
- **行数控制**：支持指定显示的行数
- **搜索过滤**：支持关键词搜索
- **清空日志**：一键清空日志文件（自动备份）

#### 6. 系统信息 (`/system`)
- **API凭证信息**：显示Telegram API ID、API Hash和Bot Token
- **管理员列表**：显示所有管理员ID
- **错误统计详情**：显示详细的错误类型分布和统计
- **系统诊断**：运行系统健康检查和诊断
- **系统操作**：支持清空错误统计、运行健康检查等操作

### 技术特性

- **完整的导航系统**：7个功能页面，响应式设计
- **实际功能集成**：所有配置更改实时保存到`config.json`
- **认证系统**：会话管理，默认密码"Sakura"
- **重启功能**：精确停止当前进程，启动新进程，发送通知
- **API端点**：支持频道管理、配置更新、任务触发等操作
- **错误处理**：集成现有的错误处理系统
- **与Telegram命令兼容**：通过相同的`config.json`文件同步配置
- **实时时间计算**：定时任务页面实时计算并显示下次执行时间

### 文件结构

```
e:/项目/tg-bot/
├── web_app.py              # Web服务器主文件
├── restart_bot_improved.py # 改进的重启脚本（精确停止进程）
├── main.py                 # 主程序（支持Web重启通知）
├── templates/              # HTML模板（7个完整页面）
│   ├── base.html          # 基础模板
│   ├── dashboard.html     # 仪表板
│   ├── channels.html      # 频道管理
│   ├── config.html        # 配置管理
│   ├── tasks.html         # 任务管理
│   ├── logs.html          # 日志查看
│   ├── system.html        # 系统信息
│   └── login.html         # 登录页面
├── static/                 # 静态资源
│   ├── css/style.css     # 样式表
│   └── js/script.js      # JavaScript
└── config.json            # 配置文件（双向同步）
```

## 使用说明

### 命令列表

| 命令 | 别名 | 功能 |
|------|------|------|
| `/summary` | `/立即总结` | 立即生成本周频道消息汇总 |
| `/showprompt` | `/查看提示词` | 显示当前使用的提示词 |
| `/setprompt` | `/设置提示词` | 设置自定义提示词 |
| `/showaicfg` | `/查看AI配置` | 查看当前AI配置信息 |
| `/setaicfg` | `/设置AI配置` | 设置自定义AI配置（API Key、Base URL、Model） |
| `/showloglevel` | `/查看日志级别` | 查看当前日志级别 |
| `/setloglevel <级别>` | `/设置日志级别 <级别>` | 设置日志级别（支持DEBUG、INFO、WARNING、ERROR、CRITICAL） |
| `/restart` | `/重启` | 重启机器人 |
| `/showchannels` | `/查看频道列表` | 查看当前配置的所有频道 |
| `/addchannel <频道URL>` | `/添加频道 <频道URL>` | 添加新的频道到监控列表 |
| `/deletechannel <频道URL>` | `/删除频道 <频道URL>` | 从监控列表中删除指定频道 |
| `/clearsummarytime` | `/清除总结时间` | 清除上次总结时间记录，下次总结将重新抓取过去一周的消息 |
| `/showchannelschedule` | `/查看频道时间配置` | 查看频道的自动总结时间配置 |
| `/setchannelschedule <频道> <星期几> <小时> <分钟>` | `/设置频道时间配置 <频道> <星期几> <小时> <分钟>` | 设置频道的自动总结时间 |
| `/deletechannelschedule <频道>` | `/删除频道时间配置 <频道>` | 删除频道的自动总结时间配置，恢复为默认时间 |
| `/changelog` | `/更新日志` | 查看更新日志 |

### 自定义提示词

1. 发送`/setprompt`或`/设置提示词`命令
2. 机器人会回复当前提示词，并等待您发送新的提示词
3. 发送您想要设置的新提示词
4. 机器人会确认提示词已更新

### AI配置管理

#### 查看AI配置
1. 发送`/showaicfg`或`/查看AI配置`命令
2. 机器人会回复当前AI配置信息，包括API Key（部分隐藏）、Base URL和Model

#### 设置AI配置
1. 发送`/setaicfg`或`/设置AI配置`命令
2. 机器人会引导您依次设置以下参数：
   - API Key（输入新的API Key或发送`/skip`保留当前值）
   - Base URL（输入新的Base URL或发送`/skip`保留当前值）
   - Model（输入新的Model或发送`/skip`保留当前值）
3. 发送`/cancel`可以随时取消设置过程
4. 所有参数设置完成后，机器人会确认配置已更新

### 日志级别管理

#### 查看日志级别
1. 发送`/showloglevel`或`/查看日志级别`命令
2. 机器人会回复当前日志级别以及可用的日志级别选项

#### 设置日志级别
1. 发送`/setloglevel <级别>`或`/设置日志级别 <级别>`命令，其中`<级别>`为以下值之一：
   - `DEBUG`：最详细的日志，包含所有调试信息
   - `INFO`：普通信息日志，记录主要操作
   - `WARNING`：警告日志，仅记录警告和错误信息
   - `ERROR`：错误日志，仅记录错误和严重错误信息
   - `CRITICAL`：严重错误日志，仅记录最严重的错误信息
2. 机器人会确认日志级别已更新，并显示之前的日志级别
3. 设置的日志级别会永久保存到配置文件中，重启后依然有效

#### 日志级别优先级
- 配置文件（config.json）中的`log_level`字段优先级最高
- 环境变量（.env）中的`LOG_LEVEL`次之
- 默认为`DEBUG`级别

#### 日志级别应用场景
- **开发调试**：使用`DEBUG`级别，查看所有详细日志
- **生产环境**：建议使用`INFO`或`WARNING`级别，减少日志输出
- **故障排查**：临时调整为`DEBUG`级别，获取详细调试信息

### 频道管理

#### 查看频道列表
1. 发送`/showchannels`或`/查看频道列表`命令
2. 机器人会回复当前配置的所有频道列表
3. 如果没有配置任何频道，会显示"当前没有配置任何频道"

#### 添加频道
1. 发送`/addchannel <频道URL>`或`/添加频道 <频道URL>`命令，其中`<频道URL>`为Telegram频道的完整URL
2. 例如：`/addchannel https://t.me/examplechannel`
3. 机器人会确认频道是否添加成功，并显示当前频道数量
4. 支持同时添加多个频道，每个频道需要单独发送命令

#### 删除频道
1. 发送`/deletechannel <频道URL>`或`/删除频道 <频道URL>`命令，其中`<频道URL>`为已添加的频道完整URL
2. 例如：`/deletechannel https://t.me/examplechannel`
3. 机器人会确认频道是否删除成功，并显示当前频道数量
4. 如果尝试删除不存在的频道，机器人会给出提示

#### 频道配置说明
- 支持从环境变量`TARGET_CHANNEL`加载单个默认频道
- 支持通过命令动态添加和删除频道
- 所有频道配置会永久保存到`config.json`文件中
- 重启机器人后，所有配置的频道会自动加载
- 消息抓取时会遍历所有配置的频道，汇总所有消息

### 智能总结时间记录

#### 功能说明
机器人会自动记录每次总结的时间（包括定时总结和手动触发的总结），并将时间存储在`.last_summary_time`文件中。下次总结时，机器人会从该时间点开始获取消息，只处理自上次总结以来的新消息。

#### 工作原理
1. 每次执行总结任务时，机器人会先读取`.last_summary_time`文件中的时间
2. 从该时间点开始抓取所有新消息
3. 生成并发送总结报告
4. 将当前时间保存到`.last_summary_time`文件中，覆盖原有时间
5. 下次总结时重复上述步骤

#### 首次使用
- 首次运行机器人时，`.last_summary_time`文件不存在
- 机器人会默认抓取过去一周的消息进行总结
- 总结完成后，会将当前时间保存到`.last_summary_time`文件中
- 后续总结将从该时间点开始

#### 注意事项
- `.last_summary_time`文件会自动生成，无需手动创建
- 该文件存储的是UTC时间，确保跨时区使用时的准确性
- 删除该文件会重置总结时间，机器人将重新抓取过去一周的消息
- 支持同时为所有配置的频道记录统一的总结时间

#### 清除总结时间记录

**命令**：`/clearsummarytime` 或 `/清除总结时间`

**功能**：清除上次总结时间记录，下次总结将重新抓取过去一周的消息

**使用场景**：
- 当您希望重新总结过去一周的消息时
- 当您认为当前的总结时间记录不准确时
- 当您想重置总结周期时

**使用方法**：
1. 发送`/clearsummarytime`或`/清除总结时间`命令
2. 机器人会回复清除结果
3. 下次总结将从过去一周的时间点开始抓取消息

**执行结果**：
- 如果清除成功，机器人会回复："已成功清除上次总结时间记录。下次总结将重新抓取过去一周的消息。"
- 如果记录文件不存在，机器人会回复："上次总结时间记录文件不存在，无需清除。"

#### 频道级自动总结时间配置

**功能说明**：支持为每个频道单独配置自动总结的执行时间，不同频道可以在不同的时间执行自动总结。

**默认配置**：所有频道默认在每周一早上9点执行自动总结。

**时间格式**：
- **星期几**：使用英文缩写，支持 `mon`（周一）、`tue`（周二）、`wed`（周三）、`thu`（周四）、`fri`（周五）、`sat`（周六）、`sun`（周日）
- **小时**：0-23（24小时制）
- **分钟**：0-59

##### 查看频道时间配置

**命令**：`/showchannelschedule` 或 `/查看频道时间配置`

**功能**：查看频道的自动总结时间配置

**使用方法**：
1. 发送`/showchannelschedule`或`/查看频道时间配置`命令
2. 如果不指定频道，机器人会显示所有频道的配置
3. 如果指定频道，机器人会显示该频道的详细配置

**示例**：
- `/showchannelschedule` - 查看所有频道的配置
- `/showchannelschedule FireflyLeak` - 查看FireflyLeak频道的配置
- `/showchannelschedule https://t.me/FireflyLeak` - 使用完整URL查看配置

##### 设置频道时间配置

**命令**：`/setchannelschedule <频道> <星期几> <小时> <分钟>` 或 `/设置频道时间配置 <频道> <星期几> <小时> <分钟>`

**功能**：设置频道的自动总结时间

**参数说明**：
- `<频道>`：频道名称（如`FireflyLeak`）或完整URL（如`https://t.me/FireflyLeak`）
- `<星期几>`：星期几的英文缩写（`mon`、`tue`、`wed`、`thu`、`fri`、`sat`、`sun`）
- `<小时>`：0-23之间的整数
- `<分钟>`：0-59之间的整数（可选，默认为0）

**使用方法**：
1. 发送`/setchannelschedule <频道> <星期几> <小时> <分钟>`命令
2. 机器人会验证时间配置的有效性
3. 如果配置有效，机器人会保存配置并确认

**示例**：
- `/setchannelschedule FireflyLeak tue 10 30` - 设置FireflyLeak频道每周二10:30执行自动总结
- `/setchannelschedule Nahida_Leak fri 14` - 设置Nahida_Leak频道每周五14:00执行自动总结
- `/setchannelschedule https://t.me/examplechannel wed 9 15` - 使用完整URL设置频道时间

##### 删除频道时间配置

**命令**：`/deletechannelschedule <频道>` 或 `/删除频道时间配置 <频道>`

**功能**：删除频道的自动总结时间配置，恢复为默认时间（每周一9:00）

**使用方法**：
1. 发送`/deletechannelschedule <频道>`命令
2. 机器人会删除该频道的时间配置
3. 该频道将恢复使用默认时间配置

**示例**：
- `/deletechannelschedule FireflyLeak` - 删除FireflyLeak频道的时间配置
- `/deletechannelschedule https://t.me/FireflyLeak` - 使用完整URL删除配置

##### 配置存储
- 所有频道的时间配置保存在`config.json`文件的`summary_schedules`字段中
- 配置格式示例：
  ```json
  "summary_schedules": {
    "https://t.me/FireflyLeak": {
      "day": "tue",
      "hour": 10,
      "minute": 30
    },
    "https://t.me/Nahida_Leak": {
      "day": "fri",
      "hour": 14,
      "minute": 0
    }
  }
  ```
- 未配置的频道使用默认时间：每周一9:00

##### 调度器行为
- 每个频道都有独立的定时任务
- 调度器会根据每个频道的配置创建对应的cron任务
- 任务ID格式：`summary_job_{频道URL}`
- 修改配置后，需要重启机器人或等待下次调度器重新加载配置

## 项目结构

```
tg-bot/
├── main.py               # 主程序文件（重构后，模块化入口）
├── config.py             # 配置管理模块
├── prompt_manager.py     # 提示词管理模块
├── summary_time_manager.py # 总结时间管理模块
├── ai_client.py          # AI客户端模块
├── telegram_client.py    # Telegram客户端模块
├── command_handlers.py   # 命令处理模块
├── scheduler.py          # 调度器模块
├── error_handler.py      # 错误处理模块（新增）
├── prompt.txt            # 提示词存储文件
├── config.json           # AI配置存储文件（自动生成）
├── .env                  # 环境变量配置
├── .last_summary_time.json # 上次总结时间存储文件（自动生成）
├── .restart_flag         # 重启标记文件（临时生成）
├── .gitignore            # Git忽略规则
├── requirements.txt      # 依赖列表
├── README.md             # 项目说明文档
├── MODULE_SPLIT_SUMMARY.md # 模块拆分总结文档
├── ERROR_HANDLING_IMPROVEMENTS.md # 错误处理改进文档（新增）
├── Dockerfile            # Docker镜像构建文件
├── docker-compose.yml    # Docker Compose配置文件
└── docker-entrypoint.sh  # Docker容器启动脚本
```

### 模块说明

- **main.py** - 主程序入口，负责模块初始化和主流程控制
- **config.py** - 配置管理，加载环境变量和配置文件
- **prompt_manager.py** - 提示词管理，加载和保存提示词
- **summary_time_manager.py** - 总结时间管理，记录和管理上次总结时间
- **ai_client.py** - AI客户端，初始化AI客户端并进行消息分析
- **telegram_client.py** - Telegram客户端，消息抓取和发送功能
- **command_handlers.py** - 命令处理，处理所有Telegram命令
- **scheduler.py** - 调度器，定时任务调度和执行
- **error_handler.py** - 错误处理模块，提供智能重试、错误统计、健康检查和优雅关闭功能

### 模块依赖关系

```
main.py
├── config.py (基础配置)
├── scheduler.py (定时任务)
├── command_handlers.py (命令处理)
│   ├── prompt_manager.py (提示词管理)
│   ├── summary_time_manager.py (时间管理)
│   ├── ai_client.py (AI分析)
│   └── telegram_client.py (Telegram操作)
├── error_handler.py (错误处理)
└── 其他第三方库依赖
```

## 注意事项

1. 确保您的Bot已被添加到目标频道，并且具有读取消息的权限
2. 首次运行时，需要手动授权登录Telegram账号
3. 请妥善保管您的API凭证，不要泄露给他人
4. 建议定期备份会话文件，避免重复登录
5. 总结内容的质量取决于提示词的设计和AI模型的选择，请根据实际需求调整
6. 支持的AI服务包括DeepSeek、OpenAI以及其他兼容OpenAI API的服务
7. 通过指令设置的AI配置会保存到config.json文件中，重启后依然有效
8. 环境变量和配置文件的优先级：config.json > 环境变量 > 默认值
9. 项目已采用模块化架构，便于维护和扩展。各模块功能独立，便于单独测试和修改
10. 增强的错误处理与恢复机制，提高系统稳定性和可靠性

## 许可证

Apache-2.0 许可证

## 贡献

欢迎提交Issue和Pull Request，一起完善这个项目！

## 联系方式

如有问题或建议，请通过GitHub Issues联系我们。