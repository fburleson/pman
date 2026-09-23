from collections.abc import Iterable
from pathlib import Path

from pman.core.command.command import Command
from pman.core.util.util import ConventionalType


def checkout(dir: Path, branch: str):
    return Command(("git", "checkout", branch)).run(dir)


def add(dir: Path, files: Iterable[str] = ("*",)):
    return Command(("git", "add", *files)).run(dir)


def branch(dir: Path, name: str, *, rename: bool = False):
    if rename:
        return Command(("git", "branch", "-M", name)).run(dir)
    else:
        return Command(("git", "branch", name)).run(dir)


def branch_current(dir: Path) -> str:
    result = Command(["git", "branch", "--show-current"]).run(dir)
    return str(result.stdout).strip()


def branch_delete(dir: Path, name: str):
    return Command(["git", "branch", "-D", name]).run(dir)


def worktree(dir: Path, path: Path, branch: str):
    return Command(("git", "worktree", "add", "-b", branch, str(path))).run(dir)


def worktree_remove(dir: Path, name: str):
    return Command(("git", "worktree", "remove", name)).run(dir)


def merge(dir: Path, merge_branch: str, *, squash: bool = True):
    if squash:
        Command(["git", "merge", merge_branch, "--squash"]).run(dir)
    else:
        Command(["git", "merge", merge_branch]).run(dir)


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
    return Command(cmd).run(dir)
