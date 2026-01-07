"""
Unused Import Fixer Strategy
============================
Fixes F401 (unused import) errors by removing or commenting out unused imports.
Handles special cases like try-blocks and __all__ exports.
"""

import re
from typing import List

from ..core.types import FixResult, LintError
from .base import BaseStrategy


class UnusedImportFixer(BaseStrategy):
    """
    Fixes F401 unused import errors.

    Strategy:
    1. Parse the unused import name from error message
    2. Check if it's in a try-block (skip if so - likely optional)
    3. Check if it's exported via __all__ (skip if so)
    4. Remove the import line
    """

    def fix(self, errors: List[LintError]) -> List[FixResult]:
        results: List[FixResult] = []

        # Filter for F401 errors
        f401_errors = [e for e in errors if e.code == "F401"]

        # Group by file
        errors_by_file: dict[str, list[LintError]] = {}
        for err in f401_errors:
            if err.file not in errors_by_file:
                errors_by_file[err.file] = []
            errors_by_file[err.file].append(err)

        for file_path, file_errors in errors_by_file.items():
            try:
                with open(file_path, "r") as f:
                    content = f.read()
                    lines = content.split("\n")

                modified = False
                lines_to_remove: set[int] = set()

                for err in file_errors:
                    line_idx = err.line - 1  # 0-indexed
                    if line_idx < 0 or line_idx >= len(lines):
                        continue

                    line = lines[line_idx]

                    # Extract import name from message
                    # Pattern: "`XXX` imported but unused"
                    match = re.search(r"`([^`]+)` imported but unused", err.message)
                    if not match:
                        continue

                    unused_name = match.group(1)

                    # Check if inside try-block (skip - likely optional import)
                    # Look at indentation and previous lines
                    is_in_try_block = False
                    for i in range(max(0, line_idx - 5), line_idx):
                        check_line = lines[i].strip()
                        if check_line.startswith("try:"):
                            is_in_try_block = True
                            break

                    if is_in_try_block:
                        continue  # Skip - optional import

                    # Check if exported in __all__ (skip)
                    if f'"{unused_name}"' in content or f"'{unused_name}'" in content:
                        # Might be in __all__, check more carefully
                        if re.search(
                            r'__all__\s*=.*["\']' + re.escape(unused_name) + r'["\']', content
                        ):
                            continue

                    # Handle different import styles
                    # Case 1: Single import on line
                    # import foo or from bar import foo
                    if f"import {unused_name}" in line and "," not in line:
                        lines_to_remove.add(line_idx)
                        modified = True
                    # Case 2: Multiple imports, need to remove just one
                    elif "," in line:
                        # Remove just this name from the import
                        new_line = re.sub(rf",?\s*{re.escape(unused_name)}\s*,?", ",", line)
                        new_line = re.sub(r",\s*$", "", new_line)  # Cleanup trailing comma
                        new_line = re.sub(
                            r"import\s+,", "import ", new_line
                        )  # Cleanup leading comma
                        if new_line != line:
                            lines[line_idx] = new_line
                            modified = True

                # Remove marked lines
                if lines_to_remove:
                    lines = [line for i, line in enumerate(lines) if i not in lines_to_remove]
                    modified = True

                if modified:
                    with open(file_path, "w") as f:
                        f.write("\n".join(lines))

                    results.append(
                        FixResult(
                            file=file_path,
                            fixed=True,
                            strategy="unused_import",
                            message="Removed unused imports",
                        )
                    )

            except Exception as e:
                results.append(
                    FixResult(
                        file=file_path, fixed=False, strategy="unused_import", message=f"Error: {e}"
                    )
                )

        return results
