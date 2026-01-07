from typing import List

from ..core.types import FixResult, LintError


class BaseStrategy:
    def fix(self, errors: List[LintError]) -> List[FixResult]:
        raise NotImplementedError
