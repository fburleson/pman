from pathlib import Path
from typing import Annotated

import typer

from pman.core.agent import deploy_to_worktree as core_deploy
from pman.core.init import init as core_init
from pman.core.manage import commit as core_commit
from pman.core.manage import release as core_release
from pman.core.manage import todev as core_todev
from pman.core.manage import workbranch as core_branch
from pman.core.todo import todo as core_todo
from pman.core.util import ConventionalType, SemVer

cli = typer.Typer(name="pman", no_args_is_help=True)


@cli.command()
def init(
    dir: Annotated[
        Path, typer.Argument(help="Directory to initialize the project in")
    ] = Path("."),
    lib: Annotated[bool, typer.Option(help="Create a library project")] = True,
    project_name: Annotated[
        str | None, typer.Option(help="Project name, defaults to the directory name")
    ] = None,
    author: Annotated[
        str, typer.Option(help="Author name used by the template")
    ] = "John Doe",
    trust: Annotated[
        bool, typer.Option(help="Trust the copier template source")
    ] = False,
    remote: Annotated[
        bool, typer.Option(help="Create a remote repository and push branches")
    ] = False,
):
    """Initialize a new project with uv, git, and the pman template."""
    core_init(
        dir.resolve(),
        lib=lib,
        project_name=project_name,
        author=author,
        trust=trust,
        remote=remote,
    )


@cli.command()
def branch(
    type: Annotated[
        ConventionalType,
        typer.Argument(help="Conventional commit type, e.g. feat, fix, chore"),
    ],
    name: Annotated[str, typer.Argument(help="Name of the branch")],
    dir: Annotated[Path, typer.Option(help="Directory of the project")] = Path("."),
    checkout: Annotated[
        bool, typer.Option(help="Checkout the new branch after creating it")
    ] = True,
):
    """Create a conventional branch (e.g. `feat/name`)."""
    core_branch(dir, type=type, name=name, checkout=checkout)


@cli.command()
def commit(
    type: Annotated[
        ConventionalType,
        typer.Argument(help="Conventional commit type, e.g. feat, fix, chore"),
    ],
    message: Annotated[str, typer.Argument(help="Commit message")],
    dir: Annotated[Path, typer.Option(help="Directory of the project")] = Path("."),
    description: Annotated[
        str | None, typer.Option(help="Additional commit description")
    ] = None,
    ai: Annotated[bool, typer.Option(help="Generate an AI commit description")] = False,
    tag: Annotated[
        str | None, typer.Option(help="Conventional commit tag, e.g. scope")
    ] = None,
) -> None:
    """Commit project changes using a conventional commit message."""
    core_commit(
        dir,
        type=type,
        message=message,
        description=description,
        tag=tag,
        ai=ai,
    )


@cli.command()
def todev(
    message: Annotated[str, typer.Argument(help="Commit message")],
    dir: Annotated[Path, typer.Option(help="Directory of the project")] = Path("."),
    description: Annotated[
        str | None, typer.Option(help="Additional commit description")
    ] = None,
    ai: Annotated[bool, typer.Option(help="Generate an AI commit description")] = False,
    tag: Annotated[
        str | None, typer.Option(help="Conventional commit tag, e.g. scope")
    ] = None,
    delete: Annotated[
        bool, typer.Option(help="Delete the current branch after merging into dev")
    ] = False,
    branch: Annotated[
        str | None, typer.Option(help="Branch to merge into dev, defaults to current")
    ] = None,
):
    """Merge a branch (current or worktree) into dev."""
    core_todev(
        dir,
        message=message,
        branch=branch,
        description=description,
        tag=tag,
        delete=delete,
        ai=ai,
    )


@cli.command()
def release(
    dir: Annotated[Path, typer.Option(help="Directory of the project")] = Path("."),
    description: Annotated[
        str | None, typer.Option(help="Additional commit description")
    ] = None,
    ai: Annotated[bool, typer.Option(help="Generate an AI commit description")] = False,
    next_release: Annotated[
        SemVer,
        typer.Option(help="Semver bump of the dev branch after the release"),
    ] = SemVer.PATCH,
):
    """Merge dev into main and cut a release."""
    core_release(dir, description=description, ai=ai, next_release=next_release)


@cli.command()
def deploy(
    type: Annotated[
        ConventionalType,
        typer.Argument(help="Conventional commit type, e.g. feat, fix, chore"),
    ],
    name: Annotated[str, typer.Argument(help="Name of the branch")],
    dir: Annotated[Path, typer.Option(help="Directory of the project")] = Path("."),
    *,
    prompt: Annotated[
        str | None, typer.Option(help="Prompt to show to the agent")
    ] = None,
    plan: Annotated[
        Path | None, typer.Option(help="Plan file to associate with the agent")
    ] = None,
):
    """Deploy a Pi agent into a worktree with a prompt and/or plan."""
    core_deploy(dir, type=type, name=name, prompt=prompt, plan=plan)


@cli.command()
def todo(
    dir: Annotated[Path, typer.Option(help="Directory of the project")] = Path("./src"),
):
    """List TODOs and FIXMEs found in the source tree."""
    core_todo(dir.resolve())


if __name__ == "__main__":
    cli()
