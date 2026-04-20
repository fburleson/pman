# AGENTS.md

## Project Overview

Refer to `./README.md` for a project overview.

## Environment

- **Python**: see `./.python-version`
- **Package Manager**: uv (all python commands must use `uv run`)

### Command examples

```bash
# correct
uv run pytest
uv run pyright
uv run main.py
```

```bash
# incorrect
pytest
pyright
python main.py
```

## Code style

- Always use snake_case for variable names and function names
- Always use PascalCase for class names
- Always use type hints

```py
# correct
class MyClass:
    def my_func(a: int, b: int) -> str:
        my_result = a * b
        return str(my_result)
```
```py
# incorrect
class my_class:
    def myFunc(a, b):
        MyResult =  a * b
        return str(MyResult)
```

## Constraints

- Never delete files
- Never add new dependencies
- Never use any git commands except the ones in Build and Test

## Build and Test

### Stage changed files

Stage all changes made

```bash
#example
git add ./src/main.py ./src/new_module ./src/old_module/__init__.py 
```

### Commit stages files

Make sure it passes the pre-commit hook.

Use one of the following commit tags depending on the commit:
- **feat** for features
- **fix** for bug fixes
- **docs** for documentation
- **refactor** for code improvements that is not a bug fix or feature
- **test** for tests


```bash
# examples
git commit -m "docs(readme): add installation instructions"
git commit -m "fix(parsing): fix data not being parsed correctly"
fir commit -m "feat(bot): add bot class to automate flow"
```

