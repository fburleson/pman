from collections.abc import Iterable
from pathlib import Path

from pman.core import Command
from pman.core.util import ConventionalType


def checkout(dir: Path, branch: str):
    return Command(("git", "checkout", branch)).exec(dir)


def add(dir: Path, files: Iterable[str] = ("*",)):
    return Command(("git", "add", *files)).exec(dir)


def branch(dir: Path, name: str):
    return Command(("git", "branch", name)).exec(dir)


def branch_rename(dir: Path, name: str):
    return Command(("git", "branch", "-M", name)).exec(dir)


def branch_current(dir: Path) -> str:
    result = Command(("git", "branch", "--show-current")).exec(dir)
    return str(result.stdout).strip()


def branch_delete(dir: Path, name: str):
    return Command(("git", "branch", "-D", name)).exec(dir)


def worktree(dir: Path, path: Path, branch: str):
    return Command(("git", "worktree", "add", "-b", branch, str(path))).exec(dir)


def worktree_remove(dir: Path, name: str):
    return Command(("git", "worktree", "remove", name)).exec(dir)


def tag(dir: Path, name: str, *, message: str | None = None):
    cmd: list[str] = ["git", "tag"]
    if message is None:
        cmd.append(name)
    else:
        cmd.extend(["-a", name, "-m", message])
    return Command(cmd).exec(dir)


def merge(dir: Path, merge_branch: str, *, squash: bool = True):
    if squash:
        Command(("git", "merge", merge_branch, "--squash")).exec(dir)
    else:
        Command(("git", "merge", merge_branch)).exec(dir)


def commit(
    dir: Path,
    type: ConventionalType,
    *,
    message: str,
    description: str | None = None,
    tag: str | None = None,
):
    # TODO(fburleson): add additional ai generated descriptions
    _tag: str = "" if tag is None else f"({tag})"
    cmd = ["git", "commit", "-m", f"{type}{_tag}: {message}"]
    if description is not None:
        cmd.extend(["-m", description])
    return Command(cmd).exec(dir)
