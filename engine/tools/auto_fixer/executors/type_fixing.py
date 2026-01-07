import re
from collections import defaultdict
from pathlib import Path
from typing import List

from ..core.types import FixResult, LintError
from .base import BaseStrategy


class TypeFixingStrategy(BaseStrategy):
    def fix(self, errors: List[LintError]) -> List[FixResult]:
        results = []

        # Group by file
        files = defaultdict(list)
        for e in errors:
            files[e.file].append(e)

        for file_path, file_errors in files.items():
            path = Path(file_path)
            if not path.exists():
                continue

            content = path.read_text()
            original = content

            # Apply fixes
            content = self._fix_implicit_optional(content, file_errors)
            content = self._fix_type_args(content, file_errors)
            content = self._fix_no_untyped_def(content, file_errors)

            if content != original:
                path.write_text(content)
                results.append(
                    FixResult(
                        file=file_path,
                        fixed=True,
                        strategy="type_fixing",
                        details="Fixed type issues",
                    )
                )

        return results

    def _fix_implicit_optional(self, content: str, errors: List[LintError]) -> str:
        # Check if we have implicit optional errors
        relevant = [
            e
            for e in errors
            if "implicit Optional" in e.message
            or (e.code == "assignment" and 'default has type "None"' in e.message)
        ]

        if not relevant:
            return content

        # Pattern: param: Type = None -> param: Type | None = None
        content = re.sub(
            r"(\w+):\s*([A-Z]\w+(?:\[[^\]]+\])?)\s*=\s*None\b(?!\s*\|)",
            r"\1: \2 | None = None",
            content,
        )
        content = re.sub(
            r"(\w+):\s*(Callable\[[^\]]+\])\s*=\s*None\b(?!\s*\|)", r"\1: \2 | None = None", content
        )
        return content

    def _fix_type_args(self, content: str, errors: List[LintError]) -> str:
        relevant = [e for e in errors if e.code == "type-arg"]
        if not relevant:
            return content

        lines = content.splitlines()
        modified = False

        for err in sorted(relevant, key=lambda e: e.line, reverse=True):
            idx = err.line - 1
            if 0 <= idx < len(lines):
                line = lines[idx]
                if '"dict"' in err.message:
                    line = re.sub(r"\bdict\b(?!\[)", "dict[str, Any]", line)
                elif '"list"' in err.message:
                    line = re.sub(r"\blist\b(?!\[)", "list[Any]", line)
                elif '"tuple"' in err.message:
                    line = re.sub(r"\btuple\b(?!\[)", "tuple[Any, ...]", line)
                elif '"set"' in err.message:
                    line = re.sub(r"\bset\b(?!\[)", "set[Any]", line)
                elif '"Callable"' in err.message:
                    line = re.sub(r"\bCallable\b(?!\[)", "Callable[..., Any]", line)

                if lines[idx] != line:
                    lines[idx] = line
                    modified = True

        if modified:
            new_content = "\n".join(lines) + "\n"
            # Add Any import if needed
            if "Any" in new_content and "from typing import" in new_content:
                match = re.search(r"from typing import ([^\n]+)", new_content)
                if match and "Any" not in match.group(1):
                    new_content = re.sub(
                        r"(from typing import )([^\n]+)", r"\1Any, \2", new_content, count=1
                    )
            elif "Any" in new_content and "from typing import" not in new_content:
                new_content = "from typing import Any\n" + new_content
            return new_content

        return content

    def _fix_no_untyped_def(self, content: str, errors: List[LintError]) -> str:
        relevant = [e for e in errors if e.code == "no-untyped-def"]
        if not relevant:
            return content

        lines = content.splitlines()
        modified = False

        for err in sorted(relevant, key=lambda e: e.line, reverse=True):
            idx = err.line - 1
            if 0 <= idx < len(lines):
                line = lines[idx]

                # Strategy 1: Always fix __init__ -> None
                if "def __init__" in line and "->" not in line:
                    # check if we can safely append -> None
                    if line.rstrip().endswith(":"):
                        lines[idx] = re.sub(r"\)\s*:", ") -> None:", line)
                        modified = True

        if modified:
            return "\n".join(lines) + "\n"

        return content
