import subprocess
import sys
from collections.abc import Iterable
from pathlib import Path

from rich.status import Status

from pman import LIB_NAME


class Command(list[str]):
    class Error(Exception):
        pass

    def __init__(self, cmds: Iterable[str]):
        self.extend(cmds)

    def __rich__(self) -> str:
        return f"[bold]{LIB_NAME}[/]>\t[italic]{'\t'.join(self)}[/]"

    def __format__(self, format_spec) -> str:
        return self.__rich__()

    def _exec(self, dir: Path = Path(".")):
        with Status(f"[dim]{self}[/]", spinner="dots"):
            return subprocess.run(
                self,
                capture_output=True,
                shell=True,
                text=True,
                check=False,
                cwd=str(dir),
            )

    def _exec_detached(self, dir: Path = Path(".")):
        kwargs = {
            "shell": True,
            "cwd": str(dir),
            "stdin": subprocess.DEVNULL,
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
        }
        if sys.platform == "win32":
            kwargs["creationflags"] = (
                subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
            )
        else:
            kwargs["start_new_session"] = True
        return subprocess.Popen(self, **kwargs)

    def run(self, dir: Path = Path("."), *, detached: bool = False):
        if detached:
            return self._exec_detached(dir)
        result = self._exec(dir)
        if result.returncode != 0:
            raise Command.Error(result)
        return self._exec(dir)
