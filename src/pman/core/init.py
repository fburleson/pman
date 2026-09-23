import os
from datetime import UTC
from pathlib import Path

import copier
from copier.user_data import datetime

from pman import LIB_NAME
from pman.core.util import ConventionalType, git, uv
from pman.core.util.util import DEV_BRANCH, MAIN_BRANCH
from pman.template import TEMPLATE_DIR

ADD_GITIGNORE: tuple[str, ...] = (".dev/", ".agents/plans/", ".agents/worktrees/")
DEV_DEPS: tuple[str, ...] = (
    "ruff",
    "pyright",
    "pytest",
    "pre-commit",
    "conventional-pre-commit",
)
INIT_DEV_VERSION: str = ".dev1"


def _init_gitignore(dir: Path):
    with open(dir / ".gitignore", "a", encoding="utf-8") as gitignore:
        gitignore.write(f"\n# {LIB_NAME}\n")
        gitignore.writelines(i + "\n" for i in ADD_GITIGNORE)


def _init_copier(
    dir: Path,
    src: Path | str,
    *,
    project_name: str,
    author: str,
    trust: bool = False,
    lib: bool = True,
):
    copier.run_copy(
        src_path=str(src),
        dst_path=dir,
        data={
            "author_name": author,
            "project_name": project_name,
            "year": str(datetime.now(UTC).year),
            "lib": lib,
        },
        unsafe=trust,
        quiet=True,
    )


def init(
    dir: Path,
    *,
    lib: bool = True,
    project_name: str | None = None,
    author: str = "John Doe",
    trust: bool = False,
):
    # TODO(fburleson): run this function in a temp dir first, so exceptions do not leave a half-init dir, but a empty one
    _project_name = dir.name if project_name is None else project_name
    uv.init(dir, lib=lib, project_name=_project_name)
    git.branch(dir, MAIN_BRANCH, rename=True)

    # enforce better file structure for non-lib projects
    if not lib:
        os.makedirs(dir / "src", exist_ok=True)
        os.replace(dir / "main.py", dir / "src/main.py")
    _init_gitignore(dir)
    uv.add(dir, DEV_DEPS, dev=True)
    _init_copier(
        dir,
        TEMPLATE_DIR,
        project_name=_project_name,
        author=author,
        trust=trust,
        lib=lib,
    )

    # install pre-commit hooks
    uv.run(
        dir,
        [
            "pre-commit",
            "install",
            "--hook-type",
            "commit-msg",
            "--hook-type",
            "pre-commit",
        ],
    )
    git.add(dir)
    git.commit(
        dir,
        ConventionalType.CHORE,
        tag=LIB_NAME,
        message="first commit",
        description=(
            f"Initialize project with {LIB_NAME}\n"
            "-\tInitialize uv\n"
            "-\tApply copier template\n"
            "-\tAdd .gitignore rules"
        ),
    )

    # setup dev branch
    git.branch(dir, DEV_BRANCH)
    git.checkout(dir, DEV_BRANCH)
    uv.version_set(dir, uv.version(dir, short=True) + INIT_DEV_VERSION)
    git.add(dir)
    git.commit(
        dir,
        ConventionalType.CHORE,
        tag=LIB_NAME,
        message="setup dev branch",
        description=f"Setup the dev branch '{DEV_BRANCH}'\n-\tUpdate the version to a dev version",
    )
