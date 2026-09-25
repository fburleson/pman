# pman 😎

**pman** is a CLI that automates the lifecycle of a Python project using `uv`, `git`, `gh-cli`, `github` and `pi` agent CLI.

## Features

- **`pman init`** — Initialize a Python project with `uv` and `copier`, including pre-commit hooks, dev dependencies, agent skills, and more.

- **`pman branch`** — Create a conventional-named feature branch like `feat/name` (`feat`, `fix`, `refactor`, `docs`, `chore`).

- **`pman deploy`** — Deploy a [`pi`](https://pi.dev/) AI agent into an isolated git worktree and launch it in the background with a prompt and/or plan file.

- **Atomic operations** — Failed operations fully restore the repo to its prior state.
- **Semantic versioning automation** — versions managed via `uv version`, keeping `main` and `dev` in sync.

…and more!


## Install

Requires Python 3.14+, [`git`](https://git-scm.com/), [`gh-cli`](https://cli.github.com/), [`uv`](https://docs.astral.sh/uv/#installation), and [`pi`](https://pi.dev/)

```bash
uv tool install pman   # or: pip install pman
```

## Quick Start

```bash
pman init my_project --author "Jane Doe" --trust
cd my_project

pman --help
```


## Tech Stack

| Layer | Choice |
| --- | --- |
| CLI | Typer |
| UI | Rich |
| Git internals | Dulwich (pure Python) |
| Scaffolding | Copier with a bundled Jinja2 template |
| Tooling | `uv`, `ruff`, `pyright`, `pytest`, `pre-commit` |


## License

[MIT](LICENSE.md)