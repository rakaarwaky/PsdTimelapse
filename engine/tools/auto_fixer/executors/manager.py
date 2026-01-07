from typing import Dict, List

from ..core.types import FixResult, LintError
from .base import BaseStrategy
from .cleaners import CleanerStrategy
from .import_order_fixer import ImportOrderFixer
from .line_length_fixer import LineLengthFixer
from .return_type_fixer import ReturnTypeFixer
from .ruff_auto import RuffAutoStrategy
from .type_fixing import TypeFixingStrategy
from .variable_naming_fixer import VariableNamingFixer


class ExecutorManager:
    def __init__(self) -> None:
        self.strategies: Dict[str, BaseStrategy] = {
            "ruff_auto": RuffAutoStrategy(),
            "import_order": ImportOrderFixer(),
            "return_type": ReturnTypeFixer(),
            "type_fixing": TypeFixingStrategy(),
            "variable_naming": VariableNamingFixer(),
            "line_length": LineLengthFixer(),
            "cleaner": CleanerStrategy(),
        }

    def execute(self, errors: List[LintError], dry_run: bool = False) -> List[FixResult]:
        results: List[FixResult] = []

        # Priority order: most impactful first
        strategy_order = [
            "ruff_auto",  # Generic Ruff fixes first
            # "import_order",  # DISABLED: Too risky, breaks try-block imports
            "return_type",  # no-untyped-def (84 errors)
            "type_fixing",  # type-arg, implicit-optional
            "variable_naming",  # N806, E741 (10 errors)
            "line_length",  # E501 (16 errors)
            "cleaner",  # bare-except, unused-ignore
        ]

        for name in strategy_order:
            if name not in self.strategies:
                continue

            strategy = self.strategies[name]
            if dry_run:
                print(f"[DRY RUN] Would execute strategy: {name}")
                continue

            print(f"🔧 Executing strategy: {name}...")
            try:
                strategy_results = strategy.fix(errors)
                results.extend(strategy_results)
                fixed = sum(1 for r in strategy_results if r.fixed)
                print(f"   ✓ Fixed {fixed} items")
            except Exception as e:
                print(f"   ✗ Error: {e}")

        return results
