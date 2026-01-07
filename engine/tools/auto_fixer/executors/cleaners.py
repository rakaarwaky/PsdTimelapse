import re
from collections import defaultdict
from pathlib import Path
from typing import List

from ..core.types import FixResult, LintError
from .base import BaseStrategy


class CleanerStrategy(BaseStrategy):
    def fix(self, errors: List[LintError]) -> List[FixResult]:
        results = []
        files = defaultdict(list)
        for e in errors:
            files[e.file].append(e)

        for file_path, file_errors in files.items():
            path = Path(file_path)
            if not path.exists():
                continue

            content = path.read_text()
            original = content

            # unused-ignore
            unused_ignores = [e.line for e in file_errors if e.code == "unused-ignore"]
            if unused_ignores:
                lines = content.splitlines()
                for ln in sorted(unused_ignores, reverse=True):
                    idx = ln - 1
                    if 0 <= idx < len(lines):
                        lines[idx] = re.sub(r"\s*#\s*type:\s*ignore.*$", "", lines[idx])
                content = "\n".join(lines) + "\n"

            # bare-except
            if any(e.code == "E722" for e in file_errors):
                content = re.sub(r"\bexcept\s*:", "except Exception:", content)

            # newline-eof
            if any(e.code == "W292" for e in file_errors):
                if not content.endswith("\n"):
                    content += "\n"

            if content != original:
                path.write_text(content)
                results.append(
                    FixResult(
                        file=file_path, fixed=True, strategy="cleaner", details="Cleaned code"
                    )
                )

        return results
