import subprocess
from dataclasses import dataclass
from typing import Iterable


class Result(subprocess.CompletedProcess[str]):
    def _print_fmt(self, text: str) -> str:
        return f"\t\t{text.replace('\n', '\n\t\t').strip()}"

    def __str__(self) -> str:
        return self._print_fmt(self.stdout)

    def __format__(self, format_spec):
        if format_spec == "stdout":
            return str(self)
        elif format_spec == "stderr":
            return self._print_fmt(self.stderr)
        return super().__format__(format_spec)


class AtomicCommand:
    class AtomicCommandError(RuntimeError):
        def __init__(self, result: Result):
            super().__init__(result.stderr)
            self._result: Result = result

        def __str__(self) -> str:
            return f"{self._result:stderr}"

        @property
        def result(self) -> Result:
            return self._result

    def __init__(self, cmd: Iterable[str]):
        self._cmd: tuple[str, ...] = tuple(cmd)

    def __str__(self):
        return f">\t{'\t'.join(self._cmd)}"

    def run(self) -> Result:
        try:
            result = subprocess.run(self._cmd, capture_output=True, text=True)
        except FileNotFoundError:
            result = subprocess.run(
                self._cmd, capture_output=True, shell=True, text=True
            )
        result = Result(**vars(result))
        if result.returncode != 0:
            raise AtomicCommand.AtomicCommandError(result)
        return result


class Command:
    @dataclass
    class Settings:
        verbose_cmd: bool = True
        verbose_output: bool = True

    def __init__(self, name: str, *cmds: AtomicCommand):
        self._name = name
        self._cmds: tuple[AtomicCommand, ...] = cmds
        self._settings = Command.Settings()

    def __str__(self) -> str:
        return self._name

    def run(self) -> tuple[Result, ...]:
        if self._settings.verbose_cmd:
            print(self)
        results: list[Result] = list()
        for i, atomic_cmd in enumerate(self.atomic_commands):
            try:
                result: Result = atomic_cmd.run()
            except AtomicCommand.AtomicCommandError as e:
                results.append(e.result)
                if not self._settings.verbose_cmd:
                    print(self)
                print(atomic_cmd)
                print(e)
                return tuple(results)
            results.append(result)
            if self._settings.verbose_cmd:
                print(atomic_cmd)
                if self._settings.verbose_output:
                    if not str(result).isspace():
                        if i == len(self.atomic_commands) - 1:
                            print(result)
                        else:
                            print(result, end="\n\n")
        return tuple(results)

    @property
    def name(self) -> str:
        return self._name

    @property
    def atomic_commands(self) -> tuple[AtomicCommand, ...]:
        return self._cmds
