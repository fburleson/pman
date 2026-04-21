import subprocess
from dataclasses import dataclass
from typing import Iterable

from rich import print
from rich.prompt import Confirm
from rich.status import Status

from pman._cli.util import EMOJIS


class Result(subprocess.CompletedProcess[str]):
    def _print_fmt(self, text: str) -> str:
        return f"\t\t{text.replace('\n', '\n\t\t').strip()}"

    def __str__(self) -> str:
        return self._print_fmt(self.stdout)

    def __rich__(self) -> str:
        return f"[dim]{self._print_fmt(self.stdout)}[/]"

    def __format__(self, format_spec):
        if format_spec == "stdout":
            return str(self)
        elif format_spec == "stderr":
            return self._print_fmt(self.stderr)
        return super().__format__(format_spec)


class AtomicCommand:
    class RuntimeError(RuntimeError):
        def __init__(self, result: Result):
            super().__init__(result.stderr)
            self._result: Result = result

        def __str__(self) -> str:
            return f"{self._result:stderr}"

        def __rich__(self) -> str:
            return f"[dim bold red]{self._result:stderr}[/]"

        @property
        def result(self) -> Result:
            return self._result

    def __init__(self, cmd: Iterable[str]):
        self._cmd: tuple[str, ...] = tuple(cmd)

    def __str__(self) -> str:
        return f"{__package__.partition('.')[0]}>\t{'\t'.join(self._cmd)}"  # type: ignore

    def __rich__(self) -> str:
        return f"[bold]{__package__.partition('.')[0]}[/]>\t[italic]{'\t'.join(self._cmd)}[/]"  # type: ignore

    def run(
        self, *, verbose: bool = True, dry: bool = False, ask: bool = False
    ) -> Result:
        if verbose:
            print(f"[{'dim' if dry else 'none'}]{self.__rich__()}[/]")
        if dry:
            result = Result(self._cmd, returncode=0, stdout=str(), stderr=str())
        else:
            if ask:
                if not verbose:
                    print(f"[{'dim' if dry else 'none'}]{self.__rich__()}[/]")
                is_confirmed = Confirm.ask("execute?")
                if not is_confirmed:
                    raise AtomicCommand.RuntimeError(
                        Result(
                            self._cmd,
                            returncode=1,
                            stdout=str(),
                            stderr=f"You canceled {EMOJIS.CONFUSED}",
                        )
                    )
            with Status("[bold green][/]", spinner="dots"):
                try:
                    result = subprocess.run(self._cmd, capture_output=True, text=True)
                except FileNotFoundError:
                    result = subprocess.run(
                        self._cmd, capture_output=True, shell=True, text=True
                    )
        result = Result(**vars(result))
        if result.returncode != 0:
            raise AtomicCommand.RuntimeError(result)
        if verbose and not str(result).isspace():
            print(result, end="\n\n")
        elif ask:
            print("")
        return result


class Command:
    @dataclass
    class Settings:
        verbose_cmd: bool = True
        verbose_output: bool = False

    def __init__(self, name: str, *cmds: AtomicCommand):
        self._name = name
        self._cmds: tuple[AtomicCommand, ...] = cmds
        self._settings = Command.Settings()

    def __str__(self) -> str:
        return self._name

    def __rich__(self) -> str:
        return f"[bold]{self}[/]"

    def run(
        self, *, verbose: bool = True, dry: bool = False, ask: bool = False
    ) -> tuple[Result, ...]:
        if verbose:
            print(f"{self.__rich__()} {f'(dry {EMOJIS.DRY_FACE})' if dry else str()}")
        results: list[Result] = list()
        for atomic_cmd in self.atomic_commands:
            try:
                result: Result = atomic_cmd.run(verbose=verbose, dry=dry, ask=ask)
            except AtomicCommand.RuntimeError as e:
                results.append(e.result)
                if not verbose:
                    print(f"{self.__rich__()} {EMOJIS.CROSS}")
                print(e)
                print(f"[bold blink red]pman has failed[/] {EMOJIS.SAD_FACE}")
                return tuple(results)
            results.append(result)
        print(
            f"[bold blink {'yellow' if dry else 'green'}]Success for pman {'?' if dry else EMOJIS.PMAN}[/]"
        )
        return tuple(results)

    @property
    def name(self) -> str:
        return self._name

    @property
    def atomic_commands(self) -> tuple[AtomicCommand, ...]:
        return self._cmds
