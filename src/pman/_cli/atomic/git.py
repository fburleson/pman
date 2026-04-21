from pman._cli.util import BranchType
from pman._core.cmd import AtomicCommand


class Git:
    CMD: str = "git"

    @staticmethod
    def branch(name: str) -> AtomicCommand:
        return AtomicCommand([Git.CMD, "branch", name])

    @staticmethod
    def delete_branch(name: str, force: bool = False) -> AtomicCommand:
        return AtomicCommand([Git.CMD, "branch", "-D" if force else "-d", name])

    @staticmethod
    def checkout(name: str) -> AtomicCommand:
        return AtomicCommand([Git.CMD, "checkout", name])

    @staticmethod
    def list_branches() -> AtomicCommand:
        return AtomicCommand([Git.CMD, "branch", "--list"])

    @staticmethod
    def current_branch() -> AtomicCommand:
        return AtomicCommand([Git.CMD, "branch", "--show-current"])

    @staticmethod
    def merge_squash(from_branch: str) -> AtomicCommand:
        return AtomicCommand([Git.CMD, "merge", "--squash", from_branch])

    @staticmethod
    def pull() -> AtomicCommand:
        return AtomicCommand([Git.CMD, "pull"])

    @staticmethod
    def add(*files: str) -> AtomicCommand:
        return AtomicCommand([Git.CMD, "add", *files])

    @staticmethod
    def commit(tag: BranchType, msg: str, title: str | None = None) -> AtomicCommand:
        _title: str = f"({title})" if title is not None else str()
        tag = BranchType(tag)
        return AtomicCommand(
            [
                Git.CMD,
                "commit",
                "-m",
                f"{tag}{_title}: {msg}",
            ]
        )

    @staticmethod
    def remote_branches() -> AtomicCommand:
        return AtomicCommand([Git.CMD, "branch", "-r"])
