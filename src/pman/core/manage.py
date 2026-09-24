from pathlib import Path

from pman import LIB_NAME
from pman.core.util import ConventionalType, SemVer, git, uv
from pman.core.util.util import (
    BRANCH_NAME_TEMPLATE,
    DEV_BRANCH,
    MAIN_BRANCH,
    PmanError,
    atomic,
    pman,
)


@pman
def workbranch(dir: Path, type: ConventionalType, name: str, *, checkout: bool = True):
    branch_name = BRANCH_NAME_TEMPLATE.substitute(type=type, name=name)
    git.branch(dir, branch_name)
    if checkout:
        git.checkout(dir, branch_name)


@atomic
@pman
def todev(
    dir: Path,
    message: str,
    *,
    branch: str | None = None,
    description: str | None = None,
    tag: str | None = None,
    delete: bool = False,
    worktree: bool = False,
):
    current_branch: str = git.branch_current(dir)
    if current_branch == DEV_BRANCH or current_branch == MAIN_BRANCH:
        raise PmanError(f"Cannot call `todev` on branch {current_branch}")
    _branch: str = current_branch if branch is None else branch
    git.checkout(dir, DEV_BRANCH)
    git.merge(dir, _branch, squash=True)
    # TODO(fburleson): handle merge conflicts
    uv.version_bump(dir, [SemVer.DEV])
    git.add(dir)
    git.commit(
        dir,
        ConventionalType(_branch.split("/")[0]),
        message=message,
        description=description,
        tag=tag,
    )
    if delete:
        if worktree:
            git.worktree_remove(dir, _branch)
        git.branch_delete(dir, _branch)


def _bump_version_dev(dir: Path, next_version: SemVer):
    git.checkout(dir, DEV_BRANCH)
    uv.version_bump(dir, [next_version, SemVer.DEV])
    git.add(dir)
    git.commit(
        dir,
        ConventionalType.CHORE,
        message=f"bump {DEV_BRANCH} branch to {uv.version(dir, short=True)}",
        tag=LIB_NAME,
    )


@atomic
@pman
def release(
    dir: Path, *, description: str | None = None, next_release: SemVer = SemVer.PATCH
):
    git.checkout(dir, MAIN_BRANCH)
    git.merge(dir, DEV_BRANCH, squash=True)
    uv.version_bump(dir, [SemVer.STABLE])
    git.commit(
        dir,
        ConventionalType.CHORE,
        message=f"v{uv.version(dir, short=True)}",
        description=description,
        tag=LIB_NAME,
    )
    _bump_version_dev(dir, next_release)
