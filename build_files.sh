#!/usr/bin/env bash
set -euo pipefail

# Create and use an isolated virtual environment to avoid modifying system Python
VENV_DIR=".vercel_venv"
VENV_PY="$VENV_DIR/bin/python"

python -m venv "$VENV_DIR"
"$VENV_PY" -m pip install --upgrade pip
"$VENV_PY" -m pip install -r requirements.txt

# Run collectstatic with the venv Python
"$VENV_PY" manage.py collectstatic --noinput