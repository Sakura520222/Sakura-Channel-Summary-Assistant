---
paths:
  - "**/*.py"
---

# Python Code Rules

## Async Discipline

- All IO operations must be async: database (aiomysql), HTTP (httpx/aiohttp), file reads (aiofiles where needed)
- Never use blocking calls in async functions (no `requests`, no `time.sleep`, no sync DB drivers)
- Use `asyncio.Lock` instead of `threading.Lock` in async code
- Wrap all `await` expressions in try/except with proper logging

## Imports

- Use `TYPE_CHECKING` guard for type-only imports that might cause circular dependencies
- Import order enforced by isort: stdlib → third-party → local
- Relative imports within sub-packages, absolute imports from project root

## Error Handling

- Use the project's custom exception hierarchy from `core/infrastructure/exceptions.py`
- Log errors with `f"{type(e).__name__}: {e}"` and `exc_info=True`
- Functions typically return safe defaults on error rather than re-raising
- Use `@retry_with_backoff` decorator for external API calls

## Singletons

- Use module-level `get_xxx()` factory functions for shared instances
- Pattern: module-level `_instance: ClassName | None = None` + `get_xxx()` with lazy init

## Logging

- Create logger per module: `logger = logging.getLogger(__name__)`
- Log messages in Chinese
- Suppress third-party loggers (telethon, httpx, openai) to WARNING level
