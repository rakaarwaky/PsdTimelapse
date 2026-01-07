#!/bin/bash
set -e

# Activate virtual environment
source .venv/bin/activate

echo "Running Ruff..."
ruff check .

echo "Running Mypy..."
mypy .
