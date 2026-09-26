import os
import shutil
import stat
import subprocess
from collections.abc import Callable, Iterable
from pathlib import Path


def _rmtree_force(path: Path) -> None:
    def _clear_readonly(
        func: Callable[[str], object],
        fspath: str,
        exc: BaseException,
    ) -> None:
        if not isinstance(exc, PermissionError):
            return
        try:
            os.chmod(
                fspath,
                os.stat(fspath).st_mode | stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH,
            )
        except OSError:
            return
        func(fspath)

    shutil.rmtree(path, onexc=_clear_readonly)


class TestProject:
    def __init__(self, dir: Path, *, name: str | None):
        self._path: Path = dir.resolve()
        self._name: str = dir.name if name is None else name
        if self.path.exists():
            _rmtree_force(self.path)
        self.path.mkdir(parents=True)
        subprocess.run(
            ("gh", "repo", "delete", f"fburleson/{self.name}", "--yes"), check=False
        )

    def open_vscode(self):
        subprocess.run(["code", self.path], check=True, shell=True)

    def exec_pman_cmd(self, cmd: Iterable[str]):
        subprocess.run(
            ["uv", "run", "--project", "C:/Users/Joel_/Documents/pman", *cmd],
            check=True,
            shell=True,
            cwd=str(self.path),
        )

    @property
    def path(self) -> Path:
        return self._path

    @property
    def name(self) -> str:
        return self._name
