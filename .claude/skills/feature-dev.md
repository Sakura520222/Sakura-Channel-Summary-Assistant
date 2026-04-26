---
name: feature-dev
description: Guided feature development following Sakura-Bot's standard workflow — i18n, async implementation, tests, lint, changelog.
---

You are developing a new feature for Sakura-Bot. Follow these steps in order. Do NOT skip steps.

## Step 1: i18n Keys

Before writing any user-facing code:

1. Identify all new user-facing strings the feature needs
2. Add translation keys to both `MESSAGE_ZH_CN` and `MESSAGE_EN_US` in `core/i18n/i18n.py`
3. Use the key naming convention: `模块.类别.具体项` (e.g., `forwarding.filter.keyword_added`)
4. Use `{variable}` placeholders for dynamic values

```python
# In core/i18n/i18n.py
MESSAGE_ZH_CN["feature.action_label"] = "操作成功：{name}"
MESSAGE_EN_US["feature.action_label"] = "Success: {name}"

# In code
from core.i18n import t
text = t("feature.action_label", name=value)
```

## Step 2: Async Implementation

- All IO must be async (database, HTTP, file operations)
- Use `TYPE_CHECKING` guard for type-only imports
- Follow the singleton pattern: module-level `_instance` + `get_xxx()` factory
- Handle errors with `logger.error(f"...: {type(e).__name__}: {e}", exc_info=True)`
- For config-dependent features, subscribe to `AsyncIOEventBus` events
- For new initializers, create a class in `core/initializers/` and register in `AppBootstrap`

## Step 3: Unit Tests

- Create `tests/test_<module>.py` or mirror the source path
- Use `@pytest.mark.asyncio` for async tests
- Mark with appropriate markers: `unit`, `integration`, etc.
- Mock external services (OpenAI, Telegram, SiliconFlow) — not internal DB layer
- Cover: happy path, edge cases, error handling

## Step 4: Lint Check

```bash
ruff check . && ruff format --check .
```

Fix any issues before proceeding.

## Step 5: Changelog & Docs

- Update `CHANGELOG.md` with the new feature under current version
- If adding/modifying bot commands, update:
  - `README.md` command reference section
  - Bot `/start` and `/help` output (in i18n dictionaries)

## Step 6: Commit

Use Conventional Commits with English description:
```
feat(scope): brief description of the feature
```
