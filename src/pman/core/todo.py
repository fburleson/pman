import re
from dataclasses import astuple, dataclass
from enum import StrEnum
from pathlib import Path

from rich import print
from rich.table import Table


@dataclass(frozen=True)
class Task:
    """
    A TODO or FIXME found in the source tree.

    Attributes:
        type (Task.Type): Whether the task is a TODO or a FIXME.
        author (str): Author credited on the comment.
        task (str): Description of the task.
    """

    class Type(StrEnum):
        TODO = "[green]TODO[/]"
        FIXME = "[yellow]FIXME[/]"

    def __str__(self):
        return f"{self.type}({self.author}): {self.task}"

    def __rich__(self):
        return self.__str__()

    type: Type
    author: str
    task: str


_PATTERN = re.compile(
    r"(?:^|[ \t])#[ \t]*"
    r"(?P<tag>TODO|FIXME)[ \t]*"
    r"(?:\((?P<paren>[^)]+)\)|@(?P<at>[^\s:]+))"
    r":[ \t]+(?P<task>\S.*)$"
)


def _parse(line: str) -> Task | None:
    """Parse a single line into a Task if it holds a valid ruff TODO comment."""
    match = _PATTERN.search(line)
    if match is None:
        return None
    author = (match.group("paren") or match.group("at")).strip()
    return Task(
        type=Task.Type[match.group("tag")],
        author=author,
        task=match.group("task").strip(),
    )


def _tasks_in(path: Path) -> list[Task]:
    """Extract all TODOs and FIXMEs from a single Python module."""
    try:
        content = path.read_text(encoding="utf-8")
    except OSError, UnicodeDecodeError:
        return []
    return [task for line in content.splitlines() if (task := _parse(line)) is not None]


def todo(dir: Path):
    src = dir / "src"
    if not src.is_dir():
        return []
    tasks: list[Task] = []
    for path in sorted(src.rglob("*.py")):
        tasks.extend(_tasks_in(path))
    table = Table(title="tasks")
    table.add_column("type")
    table.add_column("author")
    table.add_column("task")
    for task in tasks:
        table.add_row(*astuple(task))
    print(table)
    return tasks
