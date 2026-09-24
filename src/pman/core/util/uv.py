from collections.abc import Iterable
from pathlib import Path

from pman.core import Command
from pman.core.util.util import SemVer


def init(dir: Path, *, lib: bool = True, project_name: str | None = None):
    cmd: list[str] = ["uv", "init", str(dir)]
    if project_name is not None:
        cmd.extend(["--name", project_name])
    if lib:
        cmd.append("--lib")
    return Command(cmd).exec(dir)


def add(dir: Path, packages: Iterable[str], *, dev: bool = False):
    cmd: list[str] = ["uv", "add", *packages]
    if dev:
        cmd.append("--dev")
    return Command(cmd).exec(dir)


def run(dir: Path, args: Iterable[str]):
    return Command(("uv", "run", *args)).exec(dir)


def version(dir: Path, *, short: bool = False) -> str:
    cmd: list[str] = ["uv", "version"]
    if short:
        cmd.append("--short")
    result = Command(cmd).exec(dir)
    return str(result.stdout).strip()


def version_set(dir: Path, version: str):
    return Command(("uv", "version", version)).exec(dir)


def version_bump(dir: Path, versions: Iterable[SemVer]):
    cmd: list[str] = ["uv", "version"]
    for version in versions:
        cmd.extend(["--bump", version])
    return Command(cmd).exec(dir)
