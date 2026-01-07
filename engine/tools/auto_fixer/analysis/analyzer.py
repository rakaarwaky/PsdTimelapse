import json
from typing import Any, Dict, List, Optional

from ..core.config import PATTERNS_FILE
from ..core.types import LintError, Pattern


class Analyzer:
    def __init__(self):
        self.patterns = self._load_patterns()

    def _load_patterns(self) -> List[Pattern]:
        if not PATTERNS_FILE.exists():
            return []

        try:
            with open(PATTERNS_FILE) as f:
                data = json.load(f)
                patterns_data = data.get("patterns", [])

                patterns = []
                for p in patterns_data:
                    patterns.append(
                        Pattern(
                            code=p["code"],
                            count=p.get("count", 0),
                            source=p["source"],
                            category=p.get("category", "UNKNOWN"),
                            auto_fixable=p.get("auto_fixable", False),
                            severity=p.get("severity", "medium"),
                            description=p.get("description", ""),
                            fix_strategy=p.get("fix_strategy", "manual"),
                            fix_details=p.get("fix_details", {}),
                        )
                    )
                return patterns
        except Exception as e:
            print(f"Failed to load patterns: {e}")
            return []

    def analyze(self, errors: List[LintError]) -> Dict[str, Any]:
        """Group errors by pattern/code and attach fix strategies."""

        analysis_result = {
            "summary": {"total": len(errors)},
            "groups": {},  # keyed by error code
        }

        # Index patterns by code for fast lookup
        pattern_map = {p.code: p for p in self.patterns}

        for error in errors:
            code = error.code
            pattern = pattern_map.get(code)

            if code not in analysis_result["groups"]:
                analysis_result["groups"][code] = {
                    "pattern": pattern,  # Might be None
                    "errors": [],
                    "count": 0,
                }

            analysis_result["groups"][code]["errors"].append(error)
            analysis_result["groups"][code]["count"] += 1

        return analysis_result

    def get_errors_by_strategy(
        self, analysis_result: Dict[str, Any], strategy: str
    ) -> List[LintError]:
        """Filter errors by a specific fix strategy."""
        matching_errors = []
        for code, group in analysis_result["groups"].items():
            pattern: Optional[Pattern] = group["pattern"]
            if pattern and pattern.fix_strategy == strategy:
                matching_errors.extend(group["errors"])
        return matching_errors
