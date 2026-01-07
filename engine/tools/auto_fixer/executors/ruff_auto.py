import subprocess
from typing import List

from ..core.config import EXCLUDES, ROOT_DIR, RUFF_FIX_CMD
from ..core.types import FixResult, LintError
from .base import BaseStrategy


class RuffAutoStrategy(BaseStrategy):
    def fix(self, errors: List[LintError]) -> List[FixResult]:
        print("Running Ruff auto-fix...")
        try:
            result = subprocess.run(
                RUFF_FIX_CMD + ["--exclude"] + EXCLUDES,
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT_DIR,
            )
            # Rough estimation of fixed files from stdout
            fixed_count = len(
                [line for line in result.stdout.splitlines() if "fixed" in line.lower()]
            )
            return [
                FixResult(
                    file="various",
                    fixed=True,
                    strategy="ruff_auto",
                    details=f"Applied {fixed_count} fixes",
                )
            ]
        except Exception as e:
            print(f"Ruff fix failed: {e}")
            return [FixResult(file="various", fixed=False, strategy="ruff_auto", details=str(e))]
