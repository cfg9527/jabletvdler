#!/bin/bash
# ECC Validation Script — JableTV Downloader
# Runs: tests, lint, typecheck
# Exit 0 = all pass, Exit 1 = failure (triggers auto-fix loop)

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "  ECC Validation — JableTV Downloader"
echo "========================================"
echo ""

FAILED=0

# ── 1. Unit Tests ──
echo "── 1. Running pytest..."
if python3 -m pytest tests/ -v --tb=short 2>&1; then
    echo "   [PASS] All tests pass"
else
    echo "   [FAIL] Tests failed"
    FAILED=1
fi
echo ""

# ── 2. Lint (ruff) ──
echo "── 2. Running ruff lint..."
if python3 -m ruff check jabletv/ tests/ 2>&1; then
    echo "   [PASS] No lint errors"
else
    echo "   [FAIL] Lint errors found"
    FAILED=1
fi
echo ""

# ── 3. Typecheck (mypy) ──
echo "── 3. Running mypy typecheck..."
if python3 -m mypy jabletv/ --ignore-missing-imports 2>&1; then
    echo "   [PASS] Typecheck passes"
else
    echo "   [FAIL] Type errors found"
    FAILED=1
fi
echo ""

# ── Summary ──
echo "========================================"
if [ "$FAILED" -eq 0 ]; then
    echo "  ALL CHECKS PASSED — production-ready"
    echo "========================================"
    exit 0
else
    echo "  VALIDATION FAILED — fix and re-run"
    echo "========================================"
    exit 1
fi
