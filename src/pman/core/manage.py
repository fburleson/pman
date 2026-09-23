from pathlib import Path

from pman import LIB_NAME
from pman.core.util import ConventionalType, SemVer, git, uv
from pman.core.util.util import BRANCH_NAME_TEMPLATE, DEV_BRANCH, MAIN_BRANCH

# TODO(fburleson): add atomicity to certain functions, to avoid invalid states after failure


def workbranch(dir: Path, type: ConventionalType, name: str, *, checkout: bool = True):
    branch_name = BRANCH_NAME_TEMPLATE.substitute(type=type, name=name)
    git.branch(dir, branch_name)
    if checkout:
        git.checkout(dir, branch_name)


def todev(
    dir: Path,
    *,
    message: str,
    description: str | None = None,
    tag: str | None = None,
    delete: bool = False,
    branch: str | None = None,
    worktree: bool = False,
):
    if branch is None:
        branch_to_merge: str = git.branch_current(dir)
    else:
        branch_to_merge: str = branch
    git.checkout(dir, DEV_BRANCH)
    # TODO(fburleson): stash uncomitted changes
    git.merge(dir, branch_to_merge, squash=True)
    uv.version_bump(dir, [SemVer.DEV])
    # TODO(fburleson): handle merge conflicts
    git.add(dir)
    git.commit(
        dir,
        ConventionalType(branch_to_merge.split("/")[0]),
        message=message,
        description=description,
        tag=tag,
    )
    if delete:
        if worktree:
            git.worktree_remove(dir, branch_to_merge)
        git.branch_delete(dir, branch_to_merge)


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
