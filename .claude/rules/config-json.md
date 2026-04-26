---
paths:
  - "data/config*.json"
---

# Config JSON Rules

## Schema Changes

- When adding/removing/renaming fields in `config.json`, update `ConfigValidator` in `core/config/validator.py` accordingly
- New config fields must have sensible defaults so existing configs remain valid
- Type changes require validation logic in `ConfigValidator`

## Validation

- Config changes are validated on hot-reload; invalid configs trigger auto-rollback to `config.json.last_valid`
- Business logic validation: valid log levels, schedule frequency/day values, proper channel ID formats

## Hot-Reload

- `FileWatcher` monitors `data/` directory with 500ms debounce
- Changes publish `ConfigChangedEvent` through `AsyncIOEventBus`
- Prompt files (`prompt.txt`, `poll_prompt.txt`, `qa_persona.txt`) publish `PromptChangedEvent`

## Config Reference

- Template: `data/.env.example` for environment variables
- Example: `data/config.example.json` for JSON config structure
- Settings schema: `core/settings.py` (Pydantic models for `.env` variables)
