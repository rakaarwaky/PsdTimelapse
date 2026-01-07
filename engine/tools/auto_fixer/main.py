import argparse
import json
import sys
from pathlib import Path

# Add project root to path so we can import modules
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from tools.auto_fixer.analysis.analyzer import Analyzer
from tools.auto_fixer.collectors.manager import CollectorManager
from tools.auto_fixer.core.config import ERRORS_FILE
from tools.auto_fixer.executors.manager import ExecutorManager


def main():
    parser = argparse.ArgumentParser(description="Automated Lint Fixer (Modular)")
    parser.add_argument(
        "--dry-run", action="store_true", help="Simulate fixes without applying them"
    )
    parser.add_argument(
        "--skip-collect",
        action="store_true",
        help="Skip error collection (use existing errors.json)",
    )
    args = parser.parse_args()

    print("==============================================")
    print("   AUTOMATED LINT FIXER (Modular)")
    print("==============================================")

    # 1. Collect
    if not args.skip_collect:
        print("\n📥 Phase 1: Collecting errors...")
        collector = CollectorManager()
        errors = collector.collect()

        # Save errors
        with open(ERRORS_FILE, "w") as f:
            json.dump({"errors": [e.__dict__ for e in errors]}, f, indent=2)
        print(f"Total unique errors: {len(errors)}")
    else:
        print("\n📥 Phase 1: Loading existing errors...")
        from tools.auto_fixer.core.types import LintError

        with open(ERRORS_FILE) as f:
            data = json.load(f)
            errors = [LintError(**e) for e in data.get("errors", [])]
        print(f"Loaded {len(errors)} errors")

    # 2. Analyze
    print("\n🔬 Phase 2: Analyzing patterns...")
    analyzer = Analyzer()
    analysis = analyzer.analyze(errors)

    total_patterns = len(analysis["groups"])
    print(f"Analysis complete. Total patterns: {total_patterns}")

    # 3. Execute
    print("\n🔧 Phase 3: Executing fixes...")
    executor = ExecutorManager()
    results = executor.execute(errors, dry_run=args.dry_run)

    fixed_count = sum(1 for r in results if r.fixed)
    print(f"\nExecution complete. Fixed: {fixed_count} items")


if __name__ == "__main__":
    main()
