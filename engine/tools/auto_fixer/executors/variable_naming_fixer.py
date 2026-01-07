"""
Variable Naming Fixer Strategy

Handles:
- N806: Variable in function should be lowercase
- E741: Ambiguous variable name

Strategy: Renames variables to follow PEP8 conventions.
"""

import re
from collections import defaultdict
from pathlib import Path
from typing import List

from ..core.types import FixResult, LintError
from .base import BaseStrategy


class VariableNamingFixer(BaseStrategy):
    """Fixes variable naming convention issues."""

    # Common mappings for ambiguous single-letter names
    RENAME_MAP = {
        "l": "layer",
        "O": "opacity",
        "I": "index",
    }

    def fix(self, errors: List[LintError]) -> List[FixResult]:
        results = []

        relevant = [e for e in errors if e.code in ("N806", "E741")]
        if not relevant:
            return results

        files: dict[str, list[LintError]] = defaultdict(list)
        for err in relevant:
            files[err.file].append(err)

        for file_path, file_errors in files.items():
            path = Path(file_path)
            if not path.exists():
                continue

            content = path.read_text()
            modified = False

            for err in file_errors:
                # Extract variable name from error message
                var_name = self._extract_var_name(err.message)
                if var_name:
                    new_name = self._get_new_name(var_name)
                    if new_name and new_name != var_name:
                        # Replace all occurrences in the function scope
                        # Simple approach: just replace in the file
                        content = self._rename_variable(content, var_name, new_name)
                        modified = True

            if modified:
                path.write_text(content)
                results.append(
                    FixResult(
                        file=file_path,
                        fixed=True,
                        strategy="variable_naming",
                        details=f"Renamed {len(file_errors)} variables",
                    )
                )

        return results

    def _extract_var_name(self, message: str) -> str | None:
        """Extract variable name from error message."""
        # N806: Variable `X` in function should be lowercase
        match = re.search(r"Variable `([^`]+)`", message)
        if match:
            return match.group(1)
        # E741: Ambiguous variable name 'l'
        match = re.search(r"variable name '([^']+)'", message)
        if match:
            return match.group(1)
        return None

    def _get_new_name(self, var_name: str) -> str | None:
        """Get new name for variable."""
        # Check direct mapping
        if var_name in self.RENAME_MAP:
            return self.RENAME_MAP[var_name]

        # Convert CamelCase to snake_case for N806
        if var_name[0].isupper():
            return self._to_snake_case(var_name)

        return None

    def _to_snake_case(self, name: str) -> str:
        """Convert CamelCase to snake_case."""
        s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

    def _rename_variable(self, content: str, old_name: str, new_name: str) -> str:
        """Rename variable in content."""
        # Use word boundary to avoid partial replacements
        pattern = rf"\b{re.escape(old_name)}\b"
        return re.sub(pattern, new_name, content)
