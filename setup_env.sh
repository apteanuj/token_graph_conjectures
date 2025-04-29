#!/usr/bin/env bash

ENV_DIR="graph-env"
REQ_FILE="requirements.txt"

if [ ! -d "$ENV_DIR" ]; then
  echo "Virtual environment not found at '$ENV_DIR'. Creating..."
  python3 -m venv "$ENV_DIR"
  echo "Created venv in '$ENV_DIR'."

  # Activate and install on first creation
  # shellcheck source=/dev/null
  source "$ENV_DIR/bin/activate"
  echo "Activated venv: $(which python)"

  pip install --upgrade pip

  if [ -f "$REQ_FILE" ]; then
    echo "Installing dependencies from '$REQ_FILE'..."
    pip install -r "$REQ_FILE"
    echo "Dependencies installed."
  else
    echo "No '$REQ_FILE' found; skipping pip install."
  fi
else
  echo "Virtual environment already exists at '$ENV_DIR'; skipping install steps."

  # Just activate
  # shellcheck source=/dev/null
  source "$ENV_DIR/bin/activate"
  echo "Activated venv: $(which python)"
fi

echo "Environment setup complete."