from collections.abc import Iterable
from pathlib import Path

from pman import LIB_NAME
from pman.core import Command
from pman.core.util import ConventionalType

_AI_DESCRIPTION_PROMPT = (
    "Write a concise description of the staged git changes for a commit. You can use bullet points. "
    "Return only the description, without a heading or commentary."
)


def _generate_ai_description(dir: Path) -> str:
    diff = Command(("git", "diff", "--cached")).exec(dir, verbose=False)
    result = Command(
        (
            "pi",
            "--no-session",
            "--no-tools",
            "--print",
            _AI_DESCRIPTION_PROMPT,
        )
    ).exec(dir, verbose=False, input=str(diff.stdout))
    description = str(result.stdout).strip()
    if not description:
        raise Command.Error(1, "Pi returned an empty description")
    return description


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
        return Command(("git", "merge", merge_branch, "--squash")).exec(dir)
    else:
        return Command(("git", "merge", merge_branch)).exec(dir)


def push_upstream(dir: Path, branches: Iterable[str]):
    return Command(("git", "push", "-u", "origin", *branches)).exec(dir)


def commit(
    dir: Path,
    type: ConventionalType,
    *,
    message: str,
    description: str | None = None,
    tag: str | None = None,
    ai: bool = False,
):
    _tag: str = "" if tag is None else f"({tag})"
    cmd = ["git", "commit", "-m", f"{type}{_tag}: {message}"]
    if description is not None:
        for line in description.split("\n"):
            cmd.extend(["-m", line])
    if ai:
        ai_description = _generate_ai_description(dir)
        cmd.extend(["-m", f"AI description by {LIB_NAME}:"])
        for line in ai_description.split("\n"):
            cmd.extend(["-m", line])
    return Command(cmd).exec(dir)
