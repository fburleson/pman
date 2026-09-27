import re
from collections.abc import Iterable
from dataclasses import astuple, dataclass
from enum import StrEnum
from pathlib import Path

from rich import print
from rich.table import Table


@dataclass(frozen=True)
class Task:
    class Type(StrEnum):
        TODO = "TODO"
        FIXME = "FIXME"

        def __rich__(self):
            if self == self.TODO:
                return f"[green][bold]{self.__str__()}[/]"
            elif self == self.FIXME:
                return f"[yellow][bold]{self.__str__()}[/]"

    type: Type
    author: str
    task: str
    file: Path
    lineno: int


def _tasks_to_table(dir: Path, tasks: Iterable[Task]):
    table = Table(highlight=True, show_header=False, show_lines=True)
    table.add_column("type")
    table.add_column("author")
    table.add_column("task")
    table.add_column("location")
    for task in tasks:
        table.add_row(
            *astuple(task)[:-2],
            rf"{task.file.resolve().relative_to(dir)}:{task.lineno}",
        )
    return table


def _grep_dir(dir: Path) -> tuple[Task, ...]:
    tasks: list[Task] = []
    regex = re.compile(r"#\s*(?:TODO|FIXME)\s*\((?P<author>[^)]+)\)\s*:\s*(?P<task>.+)")
    for file_path in dir.rglob("*.py"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for lineno, line in enumerate(f, start=1):
                    if regex.search(line):
                        todo = re.split(r"[(): ]", line.strip())[1:]
                        tasks.append(
                            Task(
                                type=Task.Type(todo[0]),
                                author=todo[1],
                                task=" ".join(todo[3:]).strip(),
                                file=file_path,
                                lineno=lineno,
                            )
                        )
        except PermissionError, OSError:
            continue
    return tuple(tasks)


def todo(dir: Path):
    print(_tasks_to_table(dir, _grep_dir(dir)))
