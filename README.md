# pman

**pman** is a Command-Line Interface that automates the full lifecycle of a Python project: scaffolding, branch-driven development, releases, and AI-agent deployment — all built around a strict `main` → `dev` → feature branch git workflow.

Every mutating command is **atomic and failure-safe**: if anything goes wrong mid-operation, pman restores your repository to its exact pre-command state — branches, refs, index, working tree, and untracked files. No partial merges, no ghost commits, no mess to clean up.

---

## Table of Contents

- [Why pman?](#why-pman)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Workflow](#workflow)
- [Commands](#commands)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Development](#development)
- [License](#license)

---

## Why pman?

Starting a new Python project means repeating the same setup over and over: `uv init`, a git branch strategy, pre-commit hooks, a license, tests, a versioning scheme. And once the project exists, every feature and release is a ritual of tedious, error-prone git commands.

pman codifies that entire workflow into a few commands and makes it *safe to automate*:

- **`pman init`** scaffolds a production-ready project with a single command.
- **`pman branch` → `pman todev` → `pman release`** drive every feature from creation to release with conventional commits and automatic semver bumps.
- **`pman deploy`** sends an AI coding agent into an isolated worktree so it can work without touching your main tree.
- Every step is **atomic** — failures restore the repository instead of leaving it broken.

---

## Features

### Project scaffolding (`init`)
- Bootstraps a project with `uv`, choosing between a **library** (`src/` layout) or an **application** (`src/main.py`) structure.
- Generates via an embedded [Copier](https://copier.readthedocs.io/) template: `.gitignore`, `LICENSE.md`, `AGENT.md`, `tests/`, and a `.pre-commit-config.yaml` wired for Conventional Commits, `ruff`, `pyright`, and `pytest`.
- Sets up `main` + `dev` branches and commits a versioned first commit.
- Cleans up completely if any step fails (including Windows read-only files).

### Branch-driven development (`branch`, `todev`)
- Branch names follow conventional types: `feat/name`, `fix/name`, ...
- Merging a feature into `dev` uses a **squash merge**, a `dev` pre-release bump (`0.1.0.dev1`), and a Conventional Commit message derived from the branch type.
- Safe to run: refuses to operate on a dirty repository and rolls everything back on failure.

### Releases (`release`)
- Merges `dev` into `main`, bumps to a stable version (`uv version --bump stable`), and commits `chore(pman): vX.Y.Z`.
- Then bumps `dev` forward to the *next* release so development continues from a clean state.

### AI-agent deployment (`deploy`)
- Creates an isolated git worktree under `.agents/worktrees/<type>/<name>` with its own branch.
- Launches an external agent CLI (`pi`) detached in that worktree, optionally paired with a prompt and/or plan file.
- If setup fails, the worktree and branch are removed — no orphans left behind.

### Failure-safe atomic operations
The standout design feature. `RepoSnapshot` (built on [dulwich](https://www.dulwich.io/), a pure-Python git implementation) captures the entire local git state — refs, symbolic refs, HEAD — before a command runs. On any error it restores everything: removes new refs, resets branches, hard-resets the index and working tree, and cleans untracked files. **Failed commands leave the repository exactly as they found it.**

---

## Installation

### Requirements

- Python 3.14+
- [`uv`](https://docs.astral.sh/uv/) (recommended)
- [`git`](https://git-scm.com/)

### Install

```bash
# uv
uv tool install pman

# pip
pip install pman
```

> The `deploy` command additionally expects the `pi` agent CLI to be available on your `PATH`.

---

## Quick Start

```bash
# 1. Scaffold a new project
pman init my_project --author "Jane Doe" --trust

# 2. Create a feature branch
cd my_project
pman branch feat awesome-feature

# 3. ... make your changes, commit, ...

# 4. Merge into dev (with an automatic version bump)
pman todev "add the awesome feature" --delete

# 5. Cut a release when dev is ready
pman release
```

---

## Workflow

pman enforces a clean `main` → `dev` → feature pipeline:

```
main  ──────────────────────────────────────────── v1.0.0
       └─────────────── release (squash merge, stable bump)
dev   ────── v0.1.0.dev1 ──── dev2 ──── ... ────── pre-release bumps
           ┌────────────────────┘
           feat/awesome      ── todev (squash merge) ──┐
fix/bug    ─────────────────────────────────────────────┘
```

- **`main`** — always stable, versioned releases only.
- **`dev`** — integration branch, each merge bumps the pre-release counter.
- **`feat/`**, **`fix/`**, ... — short-lived feature branches.

Conventional Commits are enforced at every layer: branch naming, commit formatting (`type(scope): message`), and pre-commit hooks.

---

## Commands

```bash
pman init [dir]                       # Scaffold a new uv + git project
pman branch {feat|fix|refactor|docs|chore} NAME   # Create a conventional branch
pman todev MESSAGE                    # Squash-merge current branch (or --branch) into dev
pman release                          # Merge dev into main and cut a release
pman deploy {feat|fix|...} NAME       # Deploy an agent into a worktree
```

| Command | Description |
| --- | --- |
| `pman init [dir]` | Initialize a new project. Flags: `--lib/--no-lib`, `--project-name`, `--author`, `--trust`. |
| `pman branch {type} {name}` | Create a `type/name` branch. Flags: `--dir`, `--no-checkout`. |
| `pman todev {message}` | Merge into `dev` with squash + dev-version bump. Flags: `--dir`, `--description`, `--tag`, `--delete`, `--branch`, `--worktree`. |
| `pman release` | Release: `dev → main`, stable bump, bump `dev` to next release. Flags: `--dir`, `--description`, `--next-release` (`dev\|major\|minor\|patch\|stable`). |
| `pman deploy {type} {name}` | Deploy the `pi` agent into a worktree. Flags: `--dir`, `--prompt`, `--plan`. |

Run `pman --help` for the full reference.

---

## Design highlights

- **Decorator-driven safety.** `@atomic` wraps each workflow command to snapshot/restore repository state; `@pman` wraps it with a success banner. Workflow commands are literally `@atomic @pman def todev(...)`.
- **Separation of concerns.** `Command` handles *how* we run subprocesses (with `rich` status spinners and result trees); `git.py`/`uv.py` handle *what* we run; `manage.py` orchestrates the workflow.
- **Pure-Python git.** `dulwich` powers atomic snapshots and low-level restore without shelling out to `libgit2`.
- **Error-first UX.** `Command.Error` carries the exit code and captured output into a rich failure tree; `PmanError` expresses domain violations (e.g. running `todev` on `dev` itself).
- **Conventional Commits everywhere** — branch names, commit messages, and the generated `.pre-commit-config.yaml` all agree on the convention.

---

## Tech Stack

| Layer | Choice |
| --- | --- |
| Language | Python 3.14 (PEP 517 `src/` layout, PEP 561 `py.typed`) |
| CLI | [Typer](https://typer.tiangolo.com/) |
| UI | [Rich](https://rich.readthedocs.io/) |
| Git internals | [Dulwich](https://www.dulwich.io/) (pure Python) |
| Scaffolding | [Copier](https://copier.readthedocs.io/) with a bundled Jinja2 template |
| Tooling | `uv` (build/lock), `ruff`, `pyright`, `pytest`, `pre-commit` |

---

## Development

```bash
uv sync                     # install dependencies
uv run pman --help          # run the CLI
uv run pytest               # run tests
uv run ruff check .         # lint
uv run pyright              # type-check
uv run pre-commit run --all-files   # full pre-commit hook pass
```

---

## License

[MIT](LICENSE.md)