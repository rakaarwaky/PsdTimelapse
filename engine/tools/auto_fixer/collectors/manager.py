import json
import re
import subprocess
from pathlib import Path
from typing import List

from ..core.config import EXCLUDES, MYPY_CMD, ROOT_DIR, RUFF_CMD
from ..core.types import LintError


class CollectorManager:
    def collect(self) -> List[LintError]:
        """Run all collectors and return unique errors."""
        mypy_errors = self._run_mypy()
        ruff_errors = self._run_ruff()

        all_errors = mypy_errors + ruff_errors
        return self._deduplicate(all_errors)

    def _run_mypy(self) -> List[LintError]:
        print("Running Mypy...")
        try:
            result = subprocess.run(
                [*MYPY_CMD, "--exclude", *EXCLUDES],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT_DIR,
            )
            return self._parse_mypy(result.stdout)
        except Exception as e:
            print(f"Mypy execution failed: {e}")
            return []

    def _run_ruff(self) -> List[LintError]:
        print("Running Ruff...")
        try:
            result = subprocess.run(
                [*RUFF_CMD, "--exclude", *EXCLUDES],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT_DIR,
            )
            return self._parse_ruff(result.stdout)
        except Exception as e:
            print(f"Ruff execution failed: {e}")
            return []

    def _parse_mypy(self, output: str) -> List[LintError]:
        errors = []
        # Pattern: path:line:col: severity: message [code]
        pattern = re.compile(r"^([^:]+):(\d+):(\d+):\s+(\w+):\s+(.*)\s+\[(.*)\]$")

        for line in output.splitlines():
            match = pattern.match(line)
            if match:
                file_path, line_no, col_no, severity, msg, code = match.groups()

                # Check excludes
                if any(ex in file_path for ex in EXCLUDES):
                    continue

                errors.append(
                    LintError(
                        file=str(Path(ROOT_DIR) / file_path),
                        line=int(line_no),
                        column=int(col_no),
                        code=code.strip(),
                        message=msg.strip(),
                        source="mypy",
                        severity=severity,
                    )
                )
        return errors

    def _parse_ruff(self, output: str) -> List[LintError]:
        try:
            data = json.loads(output)
            errors = []
            for item in data:
                file_path = item.get("filename", "")

                # Check excludes
                if any(ex in file_path for ex in EXCLUDES):
                    continue

                # Map Ruff code if needed
                code = item.get("code", "UNKNOWN")

                errors.append(
                    LintError(
                        file=file_path,
                        line=item.get("location", {}).get("row", 0),
                        column=item.get("location", {}).get("column", 0),
                        code=code,
                        message=item.get("message", ""),
                        source="ruff",
                        severity="error",
                    )
                )
            return errors
        except json.JSONDecodeError:
            print("Failed to parse Ruff JSON output")
            return []

    def _deduplicate(self, errors: List[LintError]) -> List[LintError]:
        unique = {}
        for err in errors:
            key = (err.file, err.line, err.code, err.message)
            unique[key] = err

        return list(unique.values())
