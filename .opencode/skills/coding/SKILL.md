---
name: coding
description: Python coding conventions — type hints, naming, error handling, logging
license: MIT
metadata:
  audience: developers
  language: python
---

# Python Coding Conventions

Things **not** enforced by pre-commit, ruff, pyright, AGENTS.md, or companion skills.
Try to follow conventions seen within already existing code.

## Type hints

Every function signature **must** have full type annotations — parameters and return type. No exceptions.

- Prefer modern syntax: `list[str]` over `List[str]`, `str | None` over `Optional[str]`.
- Use `Self` for `@classmethod` and methods returning `self`.
- Use `typing.Protocol` for duck typing.
- Use `TYPE_CHECKING` to guard imports only needed by the type checker.

## Naming

| Element | Convention |
|---|---|
| Package / module | `short_lower_snake` |
| Class | `PascalCase` |
| Function / method / variable | `snake_case` |
| Constant | `UPPER_SNAKE` |
| Private (module/class) | `_leading_underscore` |
| Booleans | prefix with `is_`, `has_`, `should_` |

## Error handling

- Define a project-level base exception: `class MyError(Exception):`.
- Raise early, catch late. Never bare `except:`.

## Companion skills

- **Documentation** → document skill (Google-style docstrings)
- **Testing** → pytest skill (pytest, mocks, >= 90% coverage)
