---
name: pytest
description: Write comprehensive pytest tests — happy path, edge cases, errors, and everything in between — with mocked external dependencies
license: MIT
metadata:
  audience: developers
  language: python
---

# Pytest Testing

## When to use

Use this skill when asked to write unit tests for Python code using pytest. Tests must cover every behaviour of the code under test — happy paths, edge cases, error conditions, and boundary values — while mocking all external API calls and I/O.

## Test structure

- Place tests in a `tests/` directory mirroring the source layout (e.g., `src/module.py` → `tests/test_module.py`).
- Name test files `test_<name>.py` and test functions `test_<name>`.
- Use classes only when grouping related tests that share fixtures (`class TestThing:`), not for mere organization.
- One assertion per test function where practical. If multiple related assertions are needed, use a descriptive function name.

## Fixtures

- Use `pytest.fixture` for reusable state, not `setup_module`/`setup_function`.
- Keep fixtures narrow — return only what the test needs.
- Use `conftest.py` for shared fixtures; define module-local fixtures in the test file itself.
- Autouse fixtures only when absolutely necessary (e.g., mocking a global side effect for every test).

```python
@pytest.fixture
def mock_response():
    with patch("path.to.requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"key": "value"}
        yield mock_get
```

## Mocking

- Always use `unittest.mock` (`from unittest.mock import patch, Mock, MagicMock`).
- Mock at the **import source** (where it's used), not where it's defined — `patch("myapp.module.requests.get")`, not `patch("requests.get")`.
- Never make real network calls, file writes, or database queries in tests.
- Use `MagicMock` for complex return values; use `Mock` for simple callables.
- Verify mock interactions with `assert_called_once_with`, `assert_not_called`, etc.
- Use `side_effect` to simulate errors, timeouts, or multiple return values:

```python
mock_get.side_effect = [mock_resp_1, mock_resp_2]          # sequence
mock_get.side_effect = TimeoutError("connection timed out") # exception
```

## Parametrization

- Use `@pytest.mark.parametrize` to test multiple inputs without duplicating code.
- Name each case clearly via the `ids` parameter or by including an identifier in the arg tuple.

```python
@pytest.mark.parametrize("input_val,expected", [
    (0, 0),
    (1, 1),
    (-1, -1),
    (None, TypeError),
], ids=["zero", "positive", "negative", "none"])
def test_transform(input_val, expected):
    if expected is TypeError:
        with pytest.raises(TypeError):
            transform(input_val)
    else:
        assert transform(input_val) == expected
```

## Temporary files / directories

- Use `tmp_path` (built-in fixture) for file I/O tests — never hardcode paths.
- Use `monkeypatch` for environment variables and `sys.path` modifications.

```python
def test_write_file(tmp_path):
    d = tmp_path / "subdir"
    d.mkdir()
    f = d / "output.txt"
    write_output(f, "hello")
    assert f.read_text() == "hello"
```

## Async tests

- Use `pytest.mark.anyio` or `pytest-asyncio` (`@pytest.mark.asyncio`).
- Mock async functions with `AsyncMock`:

```python
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_async_fetch():
    with patch("myapp.module.fetch", new=AsyncMock()) as mock_fetch:
        mock_fetch.return_value = {"ok": True}
        result = await my_func()
        assert result["ok"] is True
```

## Coverage checklist

Every test suite should include tests from each category below:

| Category | What to test |
|---|---|
| **Happy path** | Normal valid inputs produce the expected output. This is the baseline. |
| **Typical / realistic** | Inputs representative of real-world usage, not just trivial cases. |
| **Empty / zero** | Empty list, empty string, zero, `None`, empty dict, empty file. |
| **Boundary** | Min/max values, off-by-one, first/last element, saturation/clamping limits. |
| **Type mismatch** | Wrong type passed, `None` where iterable expected, invalid enum values. |
| **Error paths** | Network timeout, HTTP 4xx/5xx, file not found, permission denied, malformed data. |
| **State** | Repeated calls, unexpected call order, concurrent access, idempotency. |
| **Special values** | `NaN`, `Infinity`, negative numbers, unicode, escape characters, very large inputs. |
| **Idempotency** | Calling the function multiple times with the same input yields the same result. |
| **Side effects** | Does the function mutate inputs, create files, or change global state when it shouldn't? |

## What NOT to do

- Never call external APIs, filesystems beyond `tmp_path`, or databases.
- Never use `time.sleep` — use `mock.patch` to control time or `freezegun` if needed.
- Never depend on test execution order — each test must be independent.
- Never test implementation details (private functions prefixed with `_`) unless they have a dedicated public contract.
- Never use `pytest-xdist`-incompatible patterns (module-level state, shared globals).

## Running tests

- Run `pytest` from the project root.
- Use `pytest -v` for verbose output, `pytest -x` to stop on first failure, `pytest --cov` for coverage.
- Target `pytest --cov-fail-under=90` minimum coverage unless specified otherwise.
- Run `pytest --tb=short` for concise tracebacks during development.

## Example

```python
from unittest.mock import patch, MagicMock
import pytest

from myapp.service import fetch_user_data


@pytest.fixture
def mock_http():
    with patch("myapp.service.requests.get") as mock:
        yield mock


class TestFetchUserData:
    def test_success(self, mock_http):
        mock_http.return_value = MagicMock(
            status_code=200,
            json=lambda: {"id": 1, "name": "Alice"},
        )
        result = fetch_user_data(1)
        assert result["name"] == "Alice"
        mock_http.assert_called_once_with(
            "https://api.example.com/users/1", timeout=10
        )

    def test_not_found(self, mock_http):
        mock_http.return_value = MagicMock(status_code=404)
        with pytest.raises(RuntimeError, match="not found"):
            fetch_user_data(999)

    def test_timeout(self, mock_http):
        mock_http.side_effect = TimeoutError("timed out")
        with pytest.raises(TimeoutError):
            fetch_user_data(1)

    def test_multiple_users_idempotent(self, mock_http):
        mock_http.return_value = MagicMock(
            status_code=200,
            json=lambda: {"id": 1, "name": "Alice"},
        )
        r1 = fetch_user_data(1)
        r2 = fetch_user_data(1)
        assert r1 == r2
        assert mock_http.call_count == 2

    @pytest.mark.parametrize("user_id", [0, -1, None], ids=["zero", "negative", "none"])
    def test_invalid_user_id(self, mock_http, user_id):
        with pytest.raises(ValueError):
            fetch_user_data(user_id)
```
