import os
import subprocess
from collections.abc import Iterable
from pathlib import Path

from rich import print
from rich.status import Status
from rich.tree import Tree

from pman import LIB_NAME


class Command:
    class Error(Exception):
        def __init__(self, code: int, out: str):
            self._code: int = code
            self._out: str = out

        @property
        def code(self) -> int:
            return self._code

        @property
        def out(self) -> str:
            return self._out

    def __init__(self, commands: Iterable[str]):
        self._commands: tuple[str, ...] = tuple(commands)

    def __repr__(self):
        return f"{self.__class__.__name__}({self._commands})"

    def __str__(self):
        return f"{LIB_NAME}>\t" + "\t".join(self._commands)

    def __rich__(self):
        return f"[bold]{LIB_NAME}[/]>\t" + "\t".join(self._commands)

    def exec_raw(self, dir: Path | None = None) -> subprocess.CompletedProcess[str]:
        _dir: Path = Path.cwd() if dir is None else dir
        with Status(str(self.__rich__()), spinner="clock"):
            return subprocess.run(
                self._commands,
                text=True,
                shell=True,
                check=False,
                capture_output=True,
                cwd=str(_dir),
            )

    def exec_detached(self, dir: Path | None = None) -> None:
        _dir: Path = Path.cwd() if dir is None else dir
        if os.name == "nt":
            subprocess.Popen(
                self._commands,
                shell=True,
                cwd=str(_dir),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            )
        else:
            subprocess.Popen(
                self._commands,
                shell=True,
                cwd=str(_dir),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )

    def _print_info(self, result: subprocess.CompletedProcess[str]):
        if result.returncode == 0:
            out = Tree("[green]:heavy_check_mark:   [/green]" + str(self.__rich__()))
            if result.stdout is not None and result.stdout.strip():
                out.add(f"[dim]{result.stdout.strip()}\n[/]")
        else:
            out = Tree("[red]:x:   [/red]" + str(self.__rich__()))
            if result.stderr is not None and result.stderr.strip():
                out.add(f"[dim][red]{result.stderr.strip()}\n[/]")
        print(out)

    def exec(self, dir: Path | None = None, *, verbose: bool = True):
        result = self.exec_raw(dir)
        if verbose:
            self._print_info(result)
        if result.returncode != 0:
            raise Command.Error(result.returncode, result.stderr)
        return result
