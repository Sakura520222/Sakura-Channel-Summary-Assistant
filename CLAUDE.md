# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Sakura-Bot — AI-powered Telegram channel management bot. Automates summarization, RAG Q&A, interactive polls, and multi-channel message forwarding. Licensed under AGPL-3.0.

## Tech Stack

- **Language**: Python 3.11+ (uses `X | Y` union syntax)
- **Telegram**: Telethon (Main Bot + UserBot), python-telegram-bot (QA Bot)
- **AI/LLM**: OpenAI SDK (DeepSeek/OpenAI compatible), AsyncOpenAI
- **RAG**: ChromaDB + BGE-M3 embeddings + BGE-Reranker-V2-M3 (via SiliconFlow)
- **Database**: aiomysql (MySQL), ChromaDB (vectors)
- **Config**: Pydantic Settings + JSON config with hot-reload (watchdog)
- **Scheduler**: APScheduler
- **Lint/Format**: Ruff, isort, pre-commit hooks

## Architecture

Two cooperating processes communicating via MySQL queue:

1. **Main Bot** (`main.py` → `AppBootstrap`) — Channel management, AI summaries, polls, scheduling, forwarding. Uses Telethon MTProto.
2. **QA Bot** (`qa_bot.py`, subprocess) — RAG-based Q&A, user subscriptions. Uses python-telegram-bot Bot API.
3. **UserBot** (optional, in-process) — Real Telegram account for private channel access. Communicates with Main Bot via in-memory callbacks.

### Key Modules (`core/`)

| Module | Role |
|--------|------|
| `bootstrap/` | AppBootstrap orchestrates 13 initialization steps via initializer classes |
| `config/` | AsyncIOEventBus (pub/sub), FileWatcher (hot-reload), ConfigManager (atomic updates with rollback), ConfigValidator |
| `ai/` | AI client, QAEngineV3 (Agentic RAG with tool-calling + fixed pipeline fallback), vector store, embeddings, reranker, agent tools |
| `commands/` | Bot command handlers grouped by feature area |
| `forwarding/` | Channel forwarding with keyword/regex/blacklist filters, download manager, media utils |
| `handlers/` | Event handlers: UserBot, cross-bot push/request, channel welcome |
| `infrastructure/` | Database abstraction (DatabaseManagerBase → MySQLManager), logging, i18n, exceptions, utilities |
| `system/` | Scheduler, error handler (retry with backoff), process manager, shutdown manager |
| `i18n/` | i18n system (zh-CN, en-US) with `t()` lookup function |

### Key Patterns

- **Module-level singletons**: `get_settings()`, `get_db_manager()`, `get_vector_store()`, etc. — lazy init, one instance per process.
- **TYPE_CHECKING guards**: Avoid circular imports; import types only under `if TYPE_CHECKING:`.
- **Event-driven config**: Changes flow through `AsyncIOEventBus` with priority-ordered subscribers and timeout protection.
- **Tuple return pattern**: Functions return `(bool, str)` for success/failure with message.
- **Custom exception hierarchy**: `SakuraBotError` → `DatabaseError`, `ConfigError`, `AIError`, `TelegramError`, `ValidationError`, `InitializationError`.

## Commands

```bash
# Lint & Format
python run_ruff.py              # Auto-locate venv, run ruff check + format, log to logs/
ruff check .                    # Direct lint
ruff format .                   # Direct format

# Tests
pytest tests/ -v                                    # All tests
pytest tests/ -v -m "not slow and not integration"  # Unit tests only (CI default)
pytest tests/ -v --cov=core --cov-report=term-missing  # With coverage
pytest tests/test_ai_client.py -v -k "test_func"    # Single test file / test function

# Docker
docker compose up --build       # Build and run
docker compose logs -f          # Follow logs

# Run locally
python main.py                  # Main bot
python qa_bot.py                # QA bot (separate process)
```

## Code Style

- **Indentation**: 4 spaces
- **Line length**: 100 chars (enforced by Ruff)
- **Quotes**: Double quotes (enforced by Ruff)
- **Naming**: PascalCase classes, snake_case functions/variables, UPPER_SNAKE_CASE constants, `cmd_` prefix for command handlers, `_` prefix for private
- **Docstrings**: Google-style in Chinese (`Args:`, `Returns:`, `Raises:`)
- **Comments & logs**: Chinese
- **Imports**: stdlib / third-party / local, ordered by isort; relative imports within sub-packages
- **Copyright header**: Every source file starts with AGPL-3.0 copyright block

## Commit Convention

Conventional Commits with English descriptions:
```
feat(ai): add agentic RAG loop with tool-calling
fix(forwarding): resolve media group deduplication race condition
refactor(config): extract event bus from monolithic config module
```

## i18n

All user-facing strings must use the i18n system (`core/i18n/`). Add keys to both `MESSAGE_ZH_CN` and `MESSAGE_EN_US` dictionaries. Use `t("module.action", var=value)` for lookups with interpolation.

## Testing

- Framework: pytest + pytest-asyncio (auto mode)
- Markers: `unit`, `integration`, `slow`, `telegram`, `database`
- Fixtures: session-scoped in `conftest.py` (env setup, event loop, mock clients)
- Coverage target: `core/` package
