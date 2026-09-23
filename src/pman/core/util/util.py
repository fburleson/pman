from enum import StrEnum
from string import Template

DEV_BRANCH: str = "dev"
MAIN_BRANCH: str = "main"
BRANCH_NAME_TEMPLATE = Template("$type/$name")


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
