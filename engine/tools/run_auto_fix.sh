#!/bin/bash
# =============================================================================
# Automated Lint Fixer - Master Script
# =============================================================================
# Runs all 3 phases: Collect -> Analyze -> Execute
#
# Usage:
#   ./tools/run_auto_fix.sh [--dry-run]
# =============================================================================

# Activate venv
source .venv/bin/activate

# Parse arguments
DRY_RUN=""
if [[ "$1" == "--dry-run" ]]; then
    DRY_RUN="--dry-run"
fi

# Run Modular Auto Fixer
echo "🚀 Starting Modular Automated Lint Fixer..."
python -m tools.auto_fixer.main $DRY_RUN

echo "Done."
