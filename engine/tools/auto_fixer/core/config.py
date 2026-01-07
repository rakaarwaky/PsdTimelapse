from pathlib import Path

# Project paths
ROOT_DIR = Path(__file__).parent.parent.parent.parent
SRC_DIR = ROOT_DIR / "src"
EXCLUDES = [
    "src/domain/modules/pipeline_manager/scenario",
]

# Lint tool paths
MYPY_CMD = [
    ".venv/bin/mypy",
    "src",
    "--ignore-missing-imports",
    "--show-error-codes",
    "--no-error-summary",
]
RUFF_CMD = [".venv/bin/ruff", "check", "src", "--output-format=json"]
RUFF_FIX_CMD = [".venv/bin/ruff", "check", "src", "--fix", "--unsafe-fixes"]

# Data files
ERRORS_FILE = ROOT_DIR / "errors.json"
PATTERNS_FILE = Path(__file__).parent.parent.parent / "llm_patterns.json"
