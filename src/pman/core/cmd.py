import subprocess
from dataclasses import dataclass
from enum import IntEnum, StrEnum

from rich import get_console, print
from rich.prompt import Confirm
from rich.status import Status
from rich.tree import Tree


class ReturnCode(IntEnum):
    SUCCESS = 0
    CANCEL = -1


class AskMode(StrEnum):
    ASK = "ask"
    NOASK = "noask"
    DEFAULT = "default"


@dataclass(frozen=True)
class Flags:
    destructive: bool = False


class Result(subprocess.CompletedProcess):
    def __format__(self, format_spec) -> str:
        if format_spec == "out":
            return self.out
        elif format_spec == "outrich":
            return self.outrich
        return super().__format__(format_spec)

    @property
    def out(self) -> str:
        if self.returncode == 0:
            return self.stdout.rstrip()
        return self.stderr.rstrip()

    @property
    def outrich(self) -> str:
        if self.returncode == 0:
            return f"[dim]{self.stdout.rstrip()}[/]"
        return f"[dim red bold]{self.stderr.rstrip()}[/]"


class Command(list[str]):
    def __init__(self, *cmd: str, flags: Flags = Flags()):
        self.extend(cmd)
        self._flags: Flags = flags

    def __rich__(self) -> str:
        return (
            f"[bold]{__package__.partition('.')[0]}[/]>\t[italic]{'\t'.join(self)}[/]"  # type: ignore
        )

    def __format__(self, format_spec) -> str:
        if format_spec == "rich":
            return self.__rich__()
        return super().__format__(format_spec)

    def _exec_cmd(self) -> Result:
        with Status(f"[dim]{self:rich}[/]", spinner="dots"):
            try:
                result = subprocess.run(self, capture_output=True, text=True)
            except FileNotFoundError:
                result = subprocess.run(
                    self, capture_output=True, shell=True, text=True
                )
        return Result(result.args, result.returncode, result.stdout, result.stderr)

    def run(
        self,
        *,
        verbose: bool = True,
        dry: bool = False,
        askmode: AskMode = AskMode.DEFAULT,
    ) -> Result:
        if dry:
            result = Result(self, ReturnCode.SUCCESS, "No output from dry run.")
        else:
            is_confirmed: bool = True
            if askmode is AskMode.ASK or (
                askmode is AskMode.DEFAULT and self.flags.destructive
            ):
                is_confirmed = Confirm.ask(f"[bold red]{self:rich}[/]")
            if is_confirmed:
                result = self._exec_cmd()
            else:
                result = Result(self, ReturnCode.CANCEL, stderr="Cancelled.")
        if verbose or result.returncode != ReturnCode.SUCCESS:
            out: str = f"{result:outrich}"
            if out.isspace() or not out:
                print(self)
            else:
                out_tree = Tree(self)
                out_tree.add(get_console().render_str(out))
                print(out_tree)
        return result

    @property
    def flags(self) -> Flags:
        return self._flags


class CmdSequence(list[Command]):
    def __init__(self, name: str, *cmds: Command):
        self._name: str = name
        self.extend(cmds)

    def __rich__(self) -> str:
        return f"[bold]{self.name}[/]"

    def __format__(self, format_spec) -> str:
        if format_spec == "rich":
            return self.__rich__()
        return super().__format__(format_spec)

    def run(
        self,
        *,
        verbose: bool = True,
        dry: bool = False,
        askmode: AskMode = AskMode.DEFAULT,
    ) -> tuple[Result, ...]:
        if verbose:
            print(f"{self:rich} {'(Dry [blink]🥱[/])' if dry else str()}")
        results: list = list()
        for cmd in self:
            result = cmd.run(verbose=verbose, dry=dry, askmode=askmode)
            results.append(result)
            if result.returncode != ReturnCode.SUCCESS:
                return tuple(results)
        print(
            f"[bold {'yellow' if dry else 'green'}]Success for pman{'? [blink]🤷[/]' if dry else ' [blink]😎[/]'}[/]"
        )
        return tuple(results)

    @property
    def name(self) -> str:
        return self._name
