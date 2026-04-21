from importlib.metadata import metadata

import click

from pman._cli.cli import add, finish, init, release


@click.group(help=metadata(str(__package__)).get("Summary"))
def pman():
    pass


pman.add_command(add)
pman.add_command(finish)
pman.add_command(release)
pman.add_command(init)
