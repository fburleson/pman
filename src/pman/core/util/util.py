from enum import StrEnum
from functools import wraps
from inspect import signature
from pathlib import Path
from string import Template

from dulwich import porcelain
from dulwich.index import Index
from dulwich.objects import ObjectID
from dulwich.refs import Ref
from dulwich.repo import Repo
from rich import print

from pman import LIB_NAME

DEV_BRANCH: str = "dev"
MAIN_BRANCH: str = "main"
BRANCH_NAME_TEMPLATE = Template("$type/$name")


class PmanError(Exception):
    pass


class ConventionalType(StrEnum):
    FEAT = "feat"
    FIX = "fix"
    REFACTOR = "refactor"
    DOCS = "docs"
    CHORE = "chore"


class SemVer(StrEnum):
    DEV = "dev"
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    STABLE = "stable"


def pman(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
        print(f"[blink][green][bold]Success for {LIB_NAME}[/]")

    return wrapper


def _is_remote(ref: Ref) -> bool:
    return ref.startswith(b"refs/remotes/")


class RepoSnapshot:
    """A snapshot of a repository's complete local git state.

    Remembers every local ref (branches, tags, ...) and the symbolic HEAD (or
    detached commit). ``restore`` returns the repository to exactly that state
    by restoring the refs, hard-resetting the index and working tree to the
    snapshotted commit, and removing new untracked files. Remote refs
    (``refs/remotes/*``) are neither stored nor restored, and the working tree
    is assumed clean at snapshot time (as guaranteed by ``atomic``).
    """

    def __init__(self, repo: Repo):
        self._repo = repo
        self._refs: dict[Ref, ObjectID] = {
            name: sha
            for name, sha in repo.refs.as_dict().items()
            if name != Ref(b"HEAD") and not _is_remote(name)
        }
        self._symrefs: dict[Ref, Ref] = {
            name: target
            for name, target in repo.refs.get_symrefs().items()
            if not _is_remote(name)
        }
        try:
            self._commit: bytes | None = repo.head()
        except KeyError:
            self._commit = None

    def restore(self):
        repo = Repo(self._repo.path)
        refs = repo.refs
        for name in refs.allkeys():
            if (
                name != Ref(b"HEAD")
                and not name.startswith(b"refs/remotes/")
                and name not in self._refs
                and name not in self._symrefs
            ):
                refs.remove_if_equals(name, None)
        for name, sha in self._refs.items():
            if name not in self._symrefs:
                refs.set_if_equals(name, None, sha)
        for name, target in self._symrefs.items():
            refs.set_symbolic_ref(name, target)
        head = self._symrefs.get(Ref(b"HEAD"))
        if head is not None:
            refs.set_symbolic_ref(Ref(b"HEAD"), head)
        elif self._commit is not None:
            porcelain.update_head(repo, self._commit, detached=True)
        if self._commit is not None:
            porcelain.reset(repo, "hard")
        else:
            Index(repo.index_path(), read=False).write()
        porcelain.clean(repo, repo.path)


def _has_uncommitted_changes(repo: Repo) -> bool:
    status = porcelain.status(repo)
    return any(status.staged.values()) or bool(status.unstaged or status.untracked)


def atomic(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        _dir: Path = signature(func).bind(*args, **kwargs).arguments["dir"]
        repo = Repo(_dir)
        if _has_uncommitted_changes(repo):
            raise PmanError("Cannot run atomically: uncommitted changes present")
        snapshot = RepoSnapshot(repo)
        try:
            func(*args, **kwargs)
        except Exception:
            snapshot.restore()
            raise

    return wrapper
