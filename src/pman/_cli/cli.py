import click

from pman._cli.atomic.git import Git
from pman._cli.atomic.uv import UV
from pman._cli.util import EMOJIS, BranchType, PyProject, global_options
from pman._core.cmd import Command, run_cmd


@click.command()
@click.argument("branch_type", type=click.Choice([type.value for type in BranchType]))
@click.argument("name")
@click.option(
    "--stay",
    is_flag=True,
    help=f"Stay on the current branch. {EMOJIS.MAN_STANDING}",
)
@global_options
def add(branch_type: BranchType, name: str, stay: bool, verbose: bool, dry: bool):
    """Add a work branch to your local git repo."""
    branch_type = BranchType(branch_type)
    branch_name: str = f"{branch_type}/{name}"
    init_branch: str = Git.current_branch().run().stdout.strip()
    cmds: list = [
        Git.branch(branch_name),
        Git.checkout(branch_name),
        UV.bump_version("dev"),
        Git.add(UV.LOCK, PyProject.CONFIG),
        Git.commit(BranchType("chore"), "bumped dev version", "version"),
    ]
    if stay:
        cmds.append(Git.checkout(init_branch))
    if verbose:
        cmds.append(Git.list_branches())
    cmd = Command(
        f"{EMOJIS.WORKING}  create work branch {branch_name}",
        *cmds,
    )
    run_cmd(cmd, verbose, dry)


@click.command()
@click.option(
    "--dest",
    default="dev",
    help="The branch to merge to.",
    show_default=True,
)
@click.option(
    "--remote",
    default="origin",
    help="Remote repository name.",
    show_default=True,
)
@global_options
def finish(dest: str, remote: str, verbose: bool, dry: bool):
    """Merge squash and delete branch."""
    init_branch: str = Git.current_branch().run().stdout.strip()
    remote_branches: list = Git.remote_branches().run().stdout.strip().split()
    remote_branches = [
        branch_name.removeprefix(remote + "/") for branch_name in remote_branches
    ]
    cmds: list = [
        Git.checkout(dest),
        Git.merge_squash(init_branch),
        Git.delete_branch(init_branch, force=True),
    ]
    if dest in remote_branches:
        cmds.insert(1, Git.pull())
    cmd = Command(
        f"{EMOJIS.PACKAGE} finish on branch {init_branch}",
        *cmds,
    )
    run_cmd(cmd, verbose, dry)


@click.command()
@click.option(
    "--dest",
    default="main",
    help="The branch to release to.",
    show_default=True,
)
@click.option(
    "--src",
    default="dev",
    help="The branch to merge from.",
    show_default=True,
)
@global_options
def release(dest: str, src: str, verbose: bool, dry: bool):
    """Merge squash to release branch and bump version to release."""
    cmds: list = [
        # UV.bump_version("dev", "patch"),
        Git.checkout(dest),
        Git.merge_squash(src),
        UV.bump_version("stable"),
        Git.add(UV.LOCK, PyProject.CONFIG),
    ]
    if verbose:
        cmds.append(UV.version())
    cmd = Command(
        f"{EMOJIS.ROCKET} release on branch {dest}",
        *cmds,
    )
    run_cmd(cmd, verbose, dry)
