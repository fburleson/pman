from pathlib import Path

from dulwich import porcelain

from pman.core import Command
from pman.core.util import git
from pman.core.util.util import BRANCH_NAME_TEMPLATE, ConventionalType

AGENT_WORKTREE_DIR = Path("./.agents/worktrees/")


def deploy_to_worktree(
    dir: Path,
    type: ConventionalType,
    name: str,
    *,
    prompt: str | None,
    plan: Path | None,
):
    if prompt is None and plan is None:
        return
    branch_name: str = BRANCH_NAME_TEMPLATE.substitute(type=type, name=name)
    worktree_dir = AGENT_WORKTREE_DIR / branch_name
    git.worktree(dir, worktree_dir, branch_name)
    try:
        cmd_parts = ["pi", "--print"]
        if plan is not None:
            cmd_parts.append(f"@{plan}")
        if prompt is not None:
            cmd_parts.append(prompt)
        Command(cmd_parts).exec_detached(worktree_dir)
    except Exception:
        _remove_worktree(dir, worktree_dir, branch_name)
        raise


def _remove_worktree(dir: Path, worktree_dir: Path, branch_name: str) -> None:
    porcelain.worktree_remove(dir, worktree_dir, force=True)
    porcelain.branch_delete(dir, branch_name)
