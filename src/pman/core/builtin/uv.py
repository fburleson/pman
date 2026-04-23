from pman.core.cmd import Command


class UV:
    CMD: str = "uv"
    CMD_TOOLS: str = "uvx"
    LOCK: str = "uv.lock"
    PYPROJECT: str = "pyproject.toml"

    class Copier:
        CMD: str = "copier"

        @staticmethod
        def copy(src: str, dest: str = ".", trust: bool = False, **data) -> Command:
            cmd = Command(
                UV.CMD_TOOLS,
                UV.Copier.CMD,
                "copy",
                src,
                dest,
            )
            if trust:
                cmd.append("--trust")
            for k, v in data.items():
                cmd.extend(["--data", f"{k}={v}"])
            return cmd

    @staticmethod
    def version() -> Command:
        return Command(UV.CMD, UV.Version.CMD)

    class Version:
        CMD: str = "version"

        @staticmethod
        def bump(first, *compenents: str, dry: bool = False) -> Command:
            cmd = Command(
                UV.CMD,
                UV.Version.CMD,
                "--bump",
                first,
            )
            for component in compenents:
                cmd.extend(["--bump", component])
            if dry:
                cmd.append("--dry-run")
            return cmd
