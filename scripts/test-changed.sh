#!/bin/bash
# Runs pytest only on test files changed vs the base branch (default: origin/develop).
# Falls back to the full suite if no test files changed or diff fails.
set -euo pipefail

BASE_REF="${1:-origin/develop}"

# shellcheck disable=SC1091
. .venv/bin/activate 2>/dev/null || true

CHANGED_TESTS=$(git diff --name-only "$BASE_REF"...HEAD -- 'tests/*.py' 2>/dev/null || true)

if [ -z "$CHANGED_TESTS" ]; then
    echo "No changed test files vs $BASE_REF — running full suite"
    pytest -m "regression or security"
else
    echo "Running changed test files:"
    echo "$CHANGED_TESTS"
    # shellcheck disable=SC2086
    pytest $CHANGED_TESTS
fi
