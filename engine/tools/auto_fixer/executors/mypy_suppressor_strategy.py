import re
from collections import defaultdict
from pathlib import Path
from typing import List

from ..core.types import FixResult, LintError
from .base import BaseStrategy


class MyPySuppressorStrategy(BaseStrategy):
    """
    Last-resort strategy: Suppresses persistent MyPy errors with specific codes.
    Ensures 'Zero Errors' state by making technical debt explicit.
    """

    def fix(self, errors: List[LintError]) -> List[FixResult]:
        results = []
        
        # Filter for MyPy errors only
        mypy_errors = [e for e in errors if e.source == "mypy"]
        if not mypy_errors:
            return results

        # Group by file
        files = defaultdict(list)
        for e in mypy_errors:
            files[e.file].append(e)

        for file_path, file_errors in files.items():
            path = Path(file_path)
            if not path.exists():
                continue

            try:
                content = path.read_text()
                lines = content.splitlines()
                modified = False
                suppressed_count = 0

                # Sort errors descending by line to avoid offset issues
                # Logic: We append '# type: ignore[code]' to the line
                
                # We need to map errors to lines, but watch out for multiple errors on one line
                line_errors = defaultdict(set)
                for err in file_errors:
                    line_errors[err.line].add(err.code)

                # Process lines from bottom up
                sorted_lines = sorted(line_errors.keys(), reverse=True)
                
                for line_num in sorted_lines:
                    # 1-based index
                    idx = line_num - 1
                    if idx < 0 or idx >= len(lines):
                        continue

                    current_line = lines[idx]
                    codes_to_ignore = line_errors[line_num]
                    
                    # Check if line already has ignore
                    if "# type: ignore" in current_line:
                        # Existing ignore. 
                        # If strict: augment it.
                        # For now, simplistic approach: if it has a global ignore, skip.
                        if "# type: ignore" in current_line and "[" not in current_line:
                            continue # Global ignore exists
                            
                        # If specific ignores exist, parse them?
                        # This is complex. For MVP, we only append if NO ignore exists.
                        # Or if we want to be smarter, we append to the existing list.
                        # Let's try to append safely.
                         pass
                    else:
                        # No ignore exists. Add one.
                        # Construct ignore string: "# type: ignore[code1,code2]"
                        codes_str = ",".join(sorted(codes_to_ignore))
                        new_line = f"{current_line}  # type: ignore[{codes_str}]"
                        lines[idx] = new_line
                        modified = True
                        suppressed_count += 1

                if modified:
                    path.write_text("\n".join(lines) + "\n")
                    results.append(
                        FixResult(
                            file=file_path,
                            fixed=True,
                            strategy="mypy_suppressor",
                            details=f"Suppressed {suppressed_count} errors",
                        )
                    )

            except Exception as e:
                results.append(
                    FixResult(
                        file=file_path,
                        fixed=False,
                        strategy="mypy_suppressor",
                        details=f"Error: {e}",
                    )
                )

        return results
