import subprocess
from typing import List

from ..core.config import EXCLUDES, ROOT_DIR, RUFF_FIX_CMD
from ..core.types import FixResult, LintError
from .base import BaseStrategy


class RuffAutoStrategy(BaseStrategy):
    def fix(self, errors: List[LintError]) -> List[FixResult]:
        print("Running Ruff auto-fix (Safe + Unsafe)...")
        results = []

        # 1. Run safe fixes
        safe_res = self._run_ruff(["--fix"])
        results.append(safe_res)

        # 2. Run unsafe fixes (aggressive)
        print("Running Ruff aggressive fixes...")
        unsafe_res = self._run_ruff(["--fix", "--unsafe-fixes"])
        results.append(unsafe_res)

        # 3. Run formatter
        print("Running Ruff formatter...")
        fmt_res = self._run_format()
        results.append(fmt_res)

        return results

    def _run_ruff(self, args: List[str]) -> FixResult:
        try:
            cmd = [*RUFF_FIX_CMD, *args, "--exclude", *EXCLUDES]
            result = subprocess.run(
                cmd,
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT_DIR,
            )
            # Rough estimation of fixed files from stdout
            fixed_count = len(
                [line for line in result.stdout.splitlines() if "fixed" in line.lower()]
            )
            return FixResult(
                file="various",
                fixed=fixed_count > 0,
                strategy="ruff_auto",
                details=f"Ruff {' '.join(args)}: {fixed_count} fixes applied",
            )
        except Exception as e:
            return FixResult(
                file="various", fixed=False, strategy="ruff_auto", details=f"Ruff error: {e}"
            )

    def _run_format(self) -> FixResult:
        try:
            # Assumes 'ruff' in path or same executable as command
            base_cmd = RUFF_FIX_CMD[0] if RUFF_FIX_CMD else "ruff"
            # If RUFF_FIX_CMD is ["python", "-m", "ruff", ...], handle that
            if "python" in base_cmd:
                cmd_list = [
                    *RUFF_FIX_CMD[:-1],
                    "format",
                ]  # Replace 'check' with 'format' if present
                # Fallback if command structure is simple
                if "check" in cmd_list:
                    cmd_list.remove("check")
            else:
                # Standard 'ruff check' -> 'ruff format'
                cmd_list = [base_cmd, "format"]

            cmd = [*cmd_list, "--exclude", *EXCLUDES]

            result = subprocess.run(
                cmd,
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT_DIR,
            )
            reformatted = len(
                [line for line in result.stdout.splitlines() if "reformatted" in line.lower()]
            )
            return FixResult(
                file="various",
                fixed=reformatted > 0,
                strategy="ruff_format",
                details=f"Formatted {reformatted} files",
            )
        except Exception as e:
            return FixResult(
                file="various", fixed=False, strategy="ruff_format", details=f"Format error: {e}"
            )
