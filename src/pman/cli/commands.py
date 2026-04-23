from pathlib import Path

import click
from click.core import ParameterSource

from pman.core.builtin.git import Git
from pman.core.builtin.uv import UV
from pman.core.cmd import CmdSequence
from pman.core.util import TaskType


@click.command()
@click.option(
    "--src",
    help="Copier template.",
    default="https://github.com/fburleson/pyuv-copier-template.git",
)
@click.option("--dest", help="Destination folder.", default=".", show_default=True)
@click.option("--trust", help="Toggle trust mode.", is_flag=True, default=False)
@click.option("--data", "-d", multiple=True)
@click.pass_context
def init(ctx, src: str, dest: str, trust: bool, data: tuple[str, ...]):
    """Initialize your project 🎬"""
    src_src = ctx.get_parameter_source("src")
    if src_src == ParameterSource.DEFAULT:
        data = tuple(list(data) + ["is_lib=True"])
    CmdSequence(
        f"🎬 INITIALZE PROJECT {Path(dest).relative_to('.')}",
        UV.Copier.copy(
            src,
            dest,
            trust=trust,
            **{value.partition("=")[0]: value.partition("=")[2] for value in data},
        ),
    ).run(verbose=ctx.obj["verbose"], dry=ctx.obj["dry"], askmode=ctx.obj["askmode"])


@click.command()
@click.argument("task", type=click.Choice([type.value for type in TaskType]))
@click.argument("name")
@click.option(
    "--stay",
    is_flag=True,
    help="Stay on the current branch. 🧍",
)
@click.pass_context
def work(ctx, task: TaskType, name: str, stay: bool):
    """Create a working branch 🛠️"""
    task = TaskType(task)
    branch_name: str = f"{task}/{name}"
    init_branch: str = Git.Branch.current().run().out
    cmd = CmdSequence(
        f"🛠️  CREATE NEW working BRANCH {branch_name}",
        Git.branch(branch_name),
        Git.checkout(branch_name),
        UV.Version.bump("dev"),
        Git.add(UV.LOCK, UV.PYPROJECT),
        Git.commit(
            TaskType.CHORE, UV.Version.bump("dev", dry=True).run().out, "version"
        ),
    )
    if stay:
        cmd.append(Git.checkout(init_branch))
    if ctx.obj["verbose"]:
        cmd.append(Git.Branch.list())
    cmd.run(verbose=ctx.obj["verbose"], dry=ctx.obj["dry"], askmode=ctx.obj["askmode"])


@click.command()
@click.option("--dest", help="Destination branch.", default="dev", show_default=True)
@click.option(
    "--remote", help="Remote repository name.", default="origin", show_default=True
)
@click.pass_context
def finish(ctx, remote: str, dest: str):
    """Finish work on a working branch 📦"""
    init_branch: str = Git.Branch.current().run().out
    remote_branches = list(Git.Branch.list(remote=True).run().out.split())
    remote_branches = [
        branch_name.removeprefix(remote + "/") for branch_name in remote_branches
    ]
    cmd = CmdSequence(
        f"📦 FINISH WORK on BRANCH {dest}",
        Git.checkout(dest),
        Git.merge(init_branch, squash=True),
        Git.Branch.delete(init_branch, force=True),
    )
    if len(remote_branches) > 0:
        cmd.append(Git.Branch.delete(init_branch, remote=True, repo=remote))
    if dest in remote_branches:
        cmd.insert(1, Git.pull())
    cmd.run(verbose=ctx.obj["verbose"], dry=ctx.obj["dry"], askmode=ctx.obj["askmode"])


@click.command()
@click.option(
    "--dest", help="The branch to release to.", default="main", show_default=True
)
@click.option(
    "--src", help="The branch to merge from.", default="dev", show_default=True
)
@click.pass_context
def release(ctx, dest: str, src: str):
    """Merge a branch with another branch as a release 🚀"""
    cmd = CmdSequence(
        f"🚀 RELEASE to BRANCH {dest}",
        Git.checkout(dest),
        Git.merge(src, squash=True),
        UV.Version.bump("stable"),
        Git.add(UV.LOCK, UV.PYPROJECT),
    )
    if ctx.obj["verbose"]:
        cmd.append(UV.version())
    cmd.run(verbose=ctx.obj["verbose"], dry=ctx.obj["dry"], askmode=ctx.obj["askmode"])
