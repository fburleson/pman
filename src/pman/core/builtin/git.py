from pman.core.cmd import Command, Flags
from pman.core.util import TaskType


class Git:
    CMD: str = "git"

    @staticmethod
    def checkout(name: str):
        return Command(Git.CMD, "checkout", name)

    @staticmethod
    def branch(name: str) -> Command:
        return Command(Git.CMD, Git.Branch.CMD, name)

    class Branch:
        CMD: str = "branch"

        @staticmethod
        def current() -> Command:
            return Git.branch("--show-current")

        @staticmethod
        def list(*, remote: bool = False, all: bool = False) -> Command:
            cmd = Command(Git.CMD, Git.Branch.CMD)
            if all:
                cmd.append("-a")
            elif remote:
                cmd.append("-r")
            else:
                cmd.append("--list")
            return cmd

        @staticmethod
        def delete(
            name, *, force: bool = False, remote: bool = False, repo: str = "origin"
        ) -> Command:
            if remote:
                return Command(
                    Git.CMD,
                    "push",
                    repo,
                    "--delete",
                    name,
                    flags=Flags(destructive=True),
                )
            return Command(
                Git.CMD,
                "branch",
                "-D" if force else "-d",
                name,
                flags=Flags(destructive=force),
            )

    @staticmethod
    def add(*files) -> Command:
        return Command(Git.CMD, "add", *files)

    @staticmethod
    def commit(task: TaskType, msg: str, title: str | None = None) -> Command:
        _title: str = f"({title})" if title is not None else str()
        return Command(Git.CMD, "commit", "-m", f"{TaskType(task)}{_title}: {msg}")

    @staticmethod
    def pull() -> Command:
        return Command(Git.CMD, "pull")

    @staticmethod
    def merge(src: str, *, squash: bool = False) -> Command:
        cmd = Command(Git.CMD, "merge", src)
        if squash:
            cmd.append("--squash")
        return cmd
