#!/bin/bash
# Mirrors the Jenkins pipeline locally: venv, install, lint, full test suite.
set -euo pipefail

python3 -m venv .venv
# shellcheck disable=SC1091
. .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
pip install pytest-xdist pytest-cov ruff

ruff check --select=E9,F .
pytest -m "regression or security" -n auto --cov=. --cov-report=xml:coverage.xml --junitxml=results.xml
