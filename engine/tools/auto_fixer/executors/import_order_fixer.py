"""
Import Order Fixer Strategy

Handles:
- E402: Module level import not at top of file
- F404: `from __future__` imports must occur at the beginning

Strategy: Reorganizes imports to proper order:
1. __future__ imports
2. Standard library
3. Third-party
4. Local imports
"""

from collections import defaultdict
from pathlib import Path
from typing import List

from ..core.types import FixResult, LintError
from .base import BaseStrategy


class ImportOrderFixer(BaseStrategy):
    """Fixes import ordering issues by moving imports to top."""

    def fix(self, errors: List[LintError]) -> List[FixResult]:
        results = []

        # Filter relevant errors
        relevant = [e for e in errors if e.code in ("E402", "F404")]
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
            new_content = self._fix_import_order(content)

            if new_content != content:
                path.write_text(new_content)
                results.append(
                    FixResult(
                        file=file_path,
                        fixed=True,
                        strategy="import_order",
                        details="Reordered imports",
                    )
                )

        return results

    def _fix_import_order(self, content: str) -> str:
        """Reorganize imports to proper order."""
        lines = content.splitlines()

        # Collect different types of content
        docstring_lines: list[str] = []
        future_imports: list[str] = []
        regular_imports: list[str] = []
        other_lines: list[str] = []

        in_docstring = False
        docstring_done = False

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Handle docstrings at the start
            if not docstring_done:
                if stripped.startswith('"""') or stripped.startswith("'''"):
                    in_docstring = (
                        not in_docstring or stripped.count('"""') >= 2 or stripped.count("'''") >= 2
                    )
                    docstring_lines.append(line)
                    if not in_docstring:
                        docstring_done = True
                    continue
                elif in_docstring:
                    docstring_lines.append(line)
                    continue
                elif stripped == "":
                    docstring_lines.append(line)
                    continue
                else:
                    docstring_done = True

            # Categorize imports
            if stripped.startswith("from __future__ import"):
                future_imports.append(line)
            elif stripped.startswith("import ") or stripped.startswith("from "):
                regular_imports.append(line)
            else:
                other_lines.append(line)

        # Rebuild file
        result_lines = docstring_lines

        if future_imports:
            result_lines.extend(future_imports)
            result_lines.append("")

        if regular_imports:
            result_lines.extend(regular_imports)
            result_lines.append("")

        result_lines.extend(other_lines)

        return "\n".join(result_lines)
