from enum import StrEnum


class TaskType(StrEnum):
    FEAT = "feat"
    FIX = "fix"
    REFACTOR = "refactor"
    CHORE = "chore"
    DOCS = "docs"
    STYLE = "style"
    TEST = "test"
