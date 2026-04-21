from enum import StrEnum

import click

from pman._core.cmd import Command


class PyProject:
    CONFIG: str = "pyproject.toml"


def run_cmd(cmd: Command, verbose: bool, dry: bool):
    cmd.run_dry() if dry else cmd.run(verbose=verbose)


def global_options(f):
    f = click.option(
        "--dry",
        default=False,
        is_flag=True,
        help="Perform a dry run, only showing the commands, but not executing.",
    )(f)
    f = click.option(
        "--verbose", is_flag=True, default=False, help="Display verbose output."
    )(f)
    return f


class BranchType(StrEnum):
    FEAT = "feat"
    FIX = "fix"
    REFACTOR = "refactor"
    CHORE = "chore"
    DOCS = "docs"
    STYLE = "style"
