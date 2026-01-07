"""
Unused Import Fixer Strategy
============================
Fixes F401 (unused import) errors by removing or commenting out unused imports.
Handles special cases like try-blocks and __all__ exports.
"""

import re
from typing import List, Optional

from ..core.types import FixResult, LintError
from .base import BaseStrategy


class UnusedImportFixer(BaseStrategy):
    """
    Fixes F401 unused import errors.
    """

    def fix(self, errors: List[LintError]) -> List[FixResult]:
        results: List[FixResult] = []
        f401_errors = [e for e in errors if e.code == "F401"]

        # Group by file
        errors_by_file: dict[str, list[LintError]] = {}
        for err in f401_errors:
            if err.file not in errors_by_file:
                errors_by_file[err.file] = []
            errors_by_file[err.file].append(err)

        for file_path, file_errors in errors_by_file.items():
            result = self._fix_file(file_path, file_errors)
            if result:
                results.append(result)

        return results

    def _fix_file(self, file_path: str, errors: List[LintError]) -> Optional[FixResult]:
        try:
            with open(file_path, "r") as f:
                lines = f.read().split("\n")
        except Exception:
            return None

        lines_to_remove: set[int] = set()
        modified = False
        content = "\n".join(lines)

        for err in errors:
            if self._process_error(err, lines, content, lines_to_remove):
                modified = True

        if lines_to_remove:
            lines = [line for i, line in enumerate(lines) if i not in lines_to_remove]
            modified = True

        if modified:
            try:
                with open(file_path, "w") as f:
                    f.write("\n".join(lines))
                return FixResult(
                    file=file_path,
                    fixed=True,
                    strategy="unused_import",
                    details="Removed unused imports",
                )
            except Exception as e:
                return FixResult(
                    file=file_path,
                    fixed=False,
                    strategy="unused_import",
                    details=f"Write error: {e}",
                )

        return None

    def _process_error(
        self, err: LintError, lines: List[str], content: str, lines_to_remove: set[int]
    ) -> bool:
        line_idx = err.line - 1
        if not (0 <= line_idx < len(lines)):
            return False

        line = lines[line_idx]
        match = re.search(r"`([^`]+)` imported but unused", err.message)
        if not match:
            return False

        unused_name = match.group(1)

        if self._is_in_try_block(lines, line_idx):
            return False

        if self._is_exported(unused_name, content):
            return False

        # Apply removal logic
        if f"import {unused_name}" in line and "," not in line:
            lines_to_remove.add(line_idx)
            return True
        elif "," in line:
            return self._remove_from_multi_import(lines, line_idx, unused_name, line)

        return False

    def _is_in_try_block(self, lines: List[str], line_idx: int) -> bool:
        for i in range(max(0, line_idx - 5), line_idx):
            if lines[i].strip().startswith("try:"):
                return True
        return False

    def _is_exported(self, name: str, content: str) -> bool:
        if f'"{name}"' in content or f"'{name}'" in content:
            if re.search(r'__all__\s*=.*["\']' + re.escape(name) + r'["\']', content):
                return True
        return False

    def _remove_from_multi_import(
        self, lines: List[str], line_idx: int, name: str, original_line: str
    ) -> bool:
        new_line = re.sub(rf",?\s*{re.escape(name)}\s*,?", ",", original_line)
        new_line = re.sub(r",\s*$", "", new_line).strip()
        new_line = re.sub(r"import\s+,", "import ", new_line)

        if new_line != original_line:
            lines[line_idx] = new_line
            return True
        return False
