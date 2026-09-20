---
name: document
description: Write Google-style Python docstrings for functions, classes, and modules
license: MIT
metadata:
  audience: developers
  language: python
---

# Google-Style Python Docstrings

## When to use

Use this skill when asked to document Python code — functions, classes, modules, or methods. Generate docstrings in the Google style unless another style is explicitly requested.

## Google Style Rules

### General
- Each `"""` should be on it's own line
- Start with a single-line summary ending in a period.
- Leave a blank line after the summary, then add detailed description paragraphs as needed.

### Sections (separated by blank lines)
- **Args:** — One line per parameter: `param_name (type): Description.` Include `type` only if non-obvious.
- **Returns:** — `Type: Description.` or just the description if type is obvious.
- **Raises:** — `ExceptionType: Description.` One line per exception.
- **Yields:** — Same format as Returns (for generators).
- **Attributes:** — For classes, document public instance attributes here.
- **Note:** — Optional section for additional notes.
- **Example:** — Optional section with a minimal code snippet.

### Modules
- Place at the top of the file after any shebang or encoding declaration.
- Describe the module's purpose, public API, and any usage notes.

### Classes
- Place right after the class definition line.
- Describe the class purpose and optionally document attributes in an `Attributes:` section.

### Functions / Methods
- Document what the function does, its parameters, return value, and exceptions raised.
- Omit `Args:` / `Returns:` / `Raises:` sections that would be empty.
- For abstract/trivial methods (e.g., `__init__` that just assigns fields), a single-line docstring is acceptable.
- Omit implementation details, describe behaviour

## Examples

```python
def fetch_data(url, timeout=30):
    """
    Fetch data from a URL and return parsed JSON.

    Handles HTTP errors and timeouts gracefully, logging
    any failures before re-raising.

    Args:
        url (str): The endpoint to fetch from.
        timeout (int): Request timeout in seconds. Defaults to 30.

    Returns:
        dict: The parsed JSON response.

    Raises:
        requests.RequestException: On network or HTTP errors.
        ValueError: If the response body is not valid JSON.
    """
```

```python
class CircularBuffer:
    """
    Fixed-size buffer that overwrites oldest entries.

    Attributes:
        capacity (int): Maximum number of items the buffer can hold.
        size (int): Current number of items in the buffer.
    """

    def __init__(self, capacity):
        self.capacity = capacity
        self._buffer = []
```

```python
"""
Utilities for working with file paths.

This module provides helpers for path normalization, joining,
and discovery of project-relative paths.

Public functions:
    - normalize_path: Remove redundant separators and resolve ``..``.
    - find_config: Walk up the directory tree looking for a config file.
"""
```
