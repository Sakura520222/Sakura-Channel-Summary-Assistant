---
name: run-debug
description: Start Sakura-Bot locally and diagnose runtime issues.
---

## Local Startup

### Prerequisites
- Python 3.11+ with venv at project root or `venv/`
- MySQL server running and accessible
- Telegram bot tokens configured

### Configuration Check
```bash
# Verify environment config exists
cat data/.env           # Must have TELEGRAM_BOT_TOKEN, LLM_API_KEY, MYSQL_*, etc.
cat data/config.json    # Channel list, schedule, forwarding rules
cat data/.env.example   # Reference template
```

### Start Commands
```bash
# Main bot (includes scheduler, forwarding, all features)
python main.py

# QA bot only (independent process)
python qa_bot.py

# Docker (full stack)
docker compose up --build
docker compose logs -f bot     # Follow bot logs
docker compose logs -f qa-bot  # Follow QA bot logs
```

### Start Script
```bash
# Windows
start.bat

# Linux (with PM2)
start.sh
```

## Diagnosing Issues

### 1. Check Logs
```bash
ls logs/                    # Log directory
# Format: sakura_bot_YYYYMMDD.log
```
Log levels: DEBUG (request details), INFO (state changes), WARNING (fallbacks), ERROR (failures with trace).

### 2. Common Failure Points

| Symptom | Check |
|---------|-------|
| Bot won't start | `data/.env` missing or invalid tokens; check `TELEGRAM_BOT_TOKEN` |
| Database connection failed | MySQL not running; check `MYSQL_HOST`, `MYSQL_PASSWORD` in `.env` |
| AI summaries fail | `LLM_API_KEY` invalid; `LLM_BASE_URL` unreachable (default: `api.deepseek.com`) |
| QA Bot crashes | `QA_BOT_TOKEN` missing; check `process_manager.py` logs for subprocess errors |
| UserBot login fails | `USERBOT_PHONE_NUMBER` not set; session file corrupted → delete `data/sessions/*.session` |
| Config hot-reload broken | Check `data/config.json` syntax; validator rejects → auto-rollback to `.last_valid` |
| Vector search empty | ChromaDB at `data/vectors/` may be empty; run initial embedding ingestion |

### 3. Telegram Session Issues
```bash
# Session files are in data/sessions/
# If UserBot session is corrupted, delete and re-authenticate:
rm data/sessions/*.session
# Bot will prompt for phone verification on next start
```

### 4. Database Migration
```bash
# Migrations run automatically on startup via DatabaseInitializer
# Check migration version in the database
```
