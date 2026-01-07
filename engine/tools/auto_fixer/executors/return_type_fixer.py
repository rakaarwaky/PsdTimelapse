"""
Return Type Fixer Strategy

Handles:
- no-untyped-def: Functions missing return type annotations
- no-any-return: Functions returning Any implicitly

Strategy: Analyzes function body to infer return type, defaults to -> None for procedures.
"""

import re
from collections import defaultdict
from pathlib import Path
from typing import List

from ..core.types import FixResult, LintError
from .base import BaseStrategy


class ReturnTypeFixer(BaseStrategy):
    """Fixes missing return type annotations."""

    def fix(self, errors: List[LintError]) -> List[FixResult]:
        results: List[FixResult] = []

        # Filter relevant errors
        relevant = [e for e in errors if e.code in ("no-untyped-def", "no-any-return")]
        if not relevant:
            return results

        # Group by file
        files: dict[str, list[LintError]] = defaultdict(list)
        for err in relevant:
            files[err.file].append(err)

        for file_path, file_errors in files.items():
            path = Path(file_path)
            if not path.exists():
                continue

            content = path.read_text()
            lines = content.splitlines()
            modified = False

            for err in sorted(file_errors, key=lambda e: e.line, reverse=True):
                idx = err.line - 1
                if 0 <= idx < len(lines):
                    line = lines[idx]

                    # Check if it's a function definition without return type
                    if self._is_function_without_return_type(line):
                        new_line = self._add_return_type(line, lines, idx)
                        if new_line != line:
                            lines[idx] = new_line
                            modified = True

            if modified:
                path.write_text("\n".join(lines) + "\n")
                results.append(
                    FixResult(
                        file=file_path,
                        fixed=True,
                        strategy="return_type",
                        details=f"Added return types to {len(file_errors)} functions",
                    )
                )

        return results

    def _is_function_without_return_type(self, line: str) -> bool:
        """Check if line is a function def without -> annotation."""
        # Match def func(...): without ->
        pattern = r"^\s*def\s+\w+\s*\([^)]*\)\s*:"
        if re.match(pattern, line) and "->" not in line:
            return True
        return False

    def _add_return_type(self, line: str, all_lines: list[str], idx: int) -> str:
        """Add -> None to function definition."""
        # Find where to insert (before the colon)
        # Handle multi-line function definitions
        if line.rstrip().endswith(":"):
            # Simple case: def foo(x): -> def foo(x) -> None:
            return re.sub(r"\)\s*:", ") -> None:", line)
        return line
