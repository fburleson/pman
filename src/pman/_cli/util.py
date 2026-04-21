from enum import StrEnum

import click


class EMOJIS:
    PMAN: str = "😎"
    SAD_FACE: str = "😞"
    ROCKET: str = "🚀"
    WORKING: str = "🛠️"
    CHECK: str = "✅"
    CROSS: str = "❌"
    PACKAGE: str = "📦"
    MEGAPHONE: str = "📣"
    DRY_FACE: str = "😑"
    MAN_STANDING: str = "🧍"
    MONOCLE: str = "🧐"
    CONFUSED: str = "🤨"


class PyProject:
    CONFIG: str = "pyproject.toml"


def global_options(f):
    f = click.option(
        "--dry",
        default=False,
        is_flag=True,
        help=f"Perform a dry run, only showing the commands, not executing. {EMOJIS.DRY_FACE}",
    )(f)
    f = click.option(
        "--silent",
        is_flag=True,
        default=False,
        help=f"Do not display verbose output. {EMOJIS.MEGAPHONE}",
    )(f)
    f = click.option(
        "--ask / --no-ask",
        default=False,
        is_flag=True,
        help=f"Toggle confirmation at every step. {EMOJIS.MONOCLE}",
    )(f)
    return f


class BranchType(StrEnum):
    FEAT = "feat"
    FIX = "fix"
    REFACTOR = "refactor"
    CHORE = "chore"
    DOCS = "docs"
    STYLE = "style"
