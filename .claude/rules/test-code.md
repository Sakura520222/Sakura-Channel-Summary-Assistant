---
paths:
  - "tests/**/*.py"
---

# Test Code Rules

## Framework

- Use pytest + pytest-asyncio with `--asyncio-mode=auto`
- Mark tests with appropriate markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`, `@pytest.mark.telegram`, `@pytest.mark.database`
- Use `@pytest.mark.asyncio` for async test functions

## Fixtures

- Session-scoped fixtures exist in `tests/conftest.py`: environment setup, event loop, mock Telegram clients
- Reuse existing fixtures before creating new ones

## Mocking Guidelines

- Mock external services (OpenAI API, Telegram API, SiliconFlow, MySQL)
- Do NOT mock internal database layer — use the actual DatabaseManagerBase interface
- Use `pytest-mock` (`mocker` fixture) for patching

## Test Organization

- Test files mirror source structure: `tests/test_<module>.py` or `tests/core/config/test_<module>.py`
- Test function names: `test_<function>_<scenario>_<expected_result>`
- Cover: happy path, edge cases, error handling, concurrent access patterns

## Coverage

- Run: `pytest tests/ -v --cov=core --cov-report=term-missing`
- CI runs: `pytest tests/ -v -m "not slow and not integration"`
