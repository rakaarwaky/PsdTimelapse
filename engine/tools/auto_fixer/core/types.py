from dataclasses import dataclass, field
from typing import Any


@dataclass
class LintError:
    file: str
    line: int
    column: int
    code: str
    message: str
    source: str  # "mypy" or "ruff"
    severity: str = "error"


@dataclass
class FixResult:
    file: str
    fixed: bool
    strategy: str
    details: str = ""


@dataclass
class Pattern:
    code: str
    count: int
    source: str
    category: str
    auto_fixable: bool
    severity: str
    description: str
    fix_strategy: str
    fix_details: dict[str, Any] = field(default_factory=dict)
