from pathlib import Path

from pman.core.command import Command


def create_remote(dir: Path):
    Command(
        (
            "gh",
            "repo",
            "create",
            "--private",
            f"--source={dir.resolve()}",
            "--remote=origin",
        )
    ).exec(dir)
