#!/usr/bin/env bash
set -euo pipefail

ENV_DIR="graph-env"
REQ_FILE="requirements.txt"

# 1) Create venv if it doesn't exist
if [ ! -d "$ENV_DIR" ]; then
  echo "Virtual environment not found at '$ENV_DIR'. Creating..."
  python3 -m venv "$ENV_DIR"
  echo "Created venv in '$ENV_DIR'."
else
  echo "Virtual environment already exists at '$ENV_DIR'."
fi

# 2) Activate it
# shellcheck source=/dev/null
source "$ENV_DIR/bin/activate"
echo "Activated venv: $(which python)"

# 3) Upgrade pip
pip install --upgrade pip

# 4) Install dependencies if requirements.txt is present
if [ -f "$REQ_FILE" ]; then
  echo "Installing dependencies from '$REQ_FILE'..."
  pip install -r "$REQ_FILE"
  echo "Dependencies installed."
else
  echo "No '$REQ_FILE' found; skipping pip install."
fi

echo "Environment setup complete."
