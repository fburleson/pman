from pman._core.cmd import AtomicCommand


class UV:
    CMD: str = "uv"
    CMD_TOOL = "uvx"
    LOCK: str = "uv.lock"

    @staticmethod
    def bump_version(*version_components) -> AtomicCommand:
        args: list[str] = list()
        for component in version_components:
            args.extend(["--bump", component])
        return AtomicCommand(
            [
                UV.CMD,
                "version",
                *args,
            ]
        )

    @staticmethod
    def version() -> AtomicCommand:
        return AtomicCommand([UV.CMD, "version"])
