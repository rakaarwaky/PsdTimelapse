"""
Line Length Fixer Strategy

Handles:
- E501: Line too long (> 100 characters)

Strategy: Intelligently breaks long lines at appropriate points.
"""

import re
from collections import defaultdict
from pathlib import Path
from typing import List

from ..core.types import FixResult, LintError
from .base import BaseStrategy


class LineLengthFixer(BaseStrategy):
    """Fixes lines exceeding maximum length by breaking them."""

    MAX_LENGTH = 100

    def fix(self, errors: List[LintError]) -> List[FixResult]:
        results = []

        relevant = [e for e in errors if e.code == "E501"]
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
            lines = content.splitlines()
            modified = False

            for err in sorted(file_errors, key=lambda e: e.line, reverse=True):
                idx = err.line - 1
                if 0 <= idx < len(lines):
                    line = lines[idx]
                    if len(line) > self.MAX_LENGTH:
                        new_lines = self._break_line(line)
                        if new_lines:
                            lines[idx : idx + 1] = new_lines
                            modified = True

            if modified:
                path.write_text("\n".join(lines) + "\n")
                results.append(
                    FixResult(
                        file=file_path,
                        fixed=True,
                        strategy="line_length",
                        details=f"Fixed {len(file_errors)} long lines",
                    )
                )

        return results

    def _break_line(self, line: str) -> list[str] | None:
        """Break a long line into multiple lines."""
        # Get indentation
        indent = len(line) - len(line.lstrip())
        base_indent = " " * indent
        cont_indent = base_indent + "    "  # 4 more spaces for continuation

        # Try different break strategies

        # 1. Break at comma in function args/params
        if "(" in line and ")" in line:
            # Check if it's a function call or definition with args
            match = re.match(r"^(\s*)(.*?\()(.+)(\).*)$", line)
            if match:
                prefix = match.group(1) + match.group(2)
                args = match.group(3)
                suffix = match.group(4)

                # Split args
                arg_list = self._split_args(args)
                if arg_list and len(arg_list) > 1:
                    result = [prefix]
                    for i, arg in enumerate(arg_list):
                        if i < len(arg_list) - 1:
                            result.append(cont_indent + arg.strip() + ",")
                        else:
                            result.append(cont_indent + arg.strip())
                    result[-1] += suffix
                    return result

        # 2. Break at string concatenation
        if '" + "' in line or "' + '" in line:
            return self._break_string_concat(line, cont_indent)

        # 3. Add backslash continuation for other cases
        # (Not safe for all cases, skip)

        return None

    def _split_args(self, args_str: str) -> list[str]:
        """Split argument string respecting nested brackets."""
        result = []
        current = ""
        depth = 0

        for char in args_str:
            if char in "([{":
                depth += 1
            elif char in ")]}":
                depth -= 1
            elif char == "," and depth == 0:
                result.append(current)
                current = ""
                continue
            current += char

        if current.strip():
            result.append(current)

        return result

    def _break_string_concat(self, line: str, cont_indent: str) -> list[str] | None:
        """Break string concatenation lines."""
        # Simple case: break at ' + ' or " + "
        parts = re.split(r"(\s*\+\s*)", line)
        if len(parts) > 1:
            result = []
            current = ""
            for part in parts:
                if len(current + part) > self.MAX_LENGTH - 4:
                    result.append(current.rstrip())
                    current = cont_indent + part.lstrip()
                else:
                    current += part
            if current.strip():
                result.append(current)
            return result if len(result) > 1 else None
        return None
