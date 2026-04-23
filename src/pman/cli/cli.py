from importlib.metadata import metadata

import click

from pman.cli.commands import finish, init, release, work
from pman.core.cmd import AskMode


@click.group(help=metadata(str(__package__).partition(".")[0]).get("Summary"))
@click.option(
    "--verbose/--silent", default=True, show_default=True, help="Verbosity mode."
)
@click.option("--dry/--wet", default=False, show_default=True, help="Toggle execution.")
@click.option(
    "--ask",
    "askmode",
    flag_value="ask",
    help="Toggle confirmation at every step.",
)
@click.option(
    "--noask",
    "askmode",
    flag_value="noask",
    help="Toggle no confirmation at every step. This will also execute destructive commands.",
)
@click.pass_context
def pman(ctx, verbose: bool, dry: bool, askmode: AskMode):
    ctx.obj = {
        "verbose": verbose,
        "dry": dry,
        "askmode": AskMode(askmode) if askmode is not None else AskMode.DEFAULT,
    }


pman.add_command(init)
pman.add_command(work)
pman.add_command(finish)
pman.add_command(release)
