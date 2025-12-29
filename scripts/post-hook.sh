#!/usr/bin/env bash
set -euo pipefail

echo "Running post-hook checks..."

echo "Running ruff..."
uvx ruff check app tests

echo "Running ruff format check..."
uvx ruff format --check app tests

echo "Running ty (type checker)..."
uvx ty check app

echo "All checks passed!"

