#!/usr/bin/env bash

ENV_DIR="graph-env"
ACTIVATE="$ENV_DIR/bin/activate"
REQ_FILE="requirements.txt"

if [ ! -f "$ACTIVATE" ]; then
  echo "No valid virtualenv found in '$ENV_DIR'. Creating a new one…"
  python3 -m venv "$ENV_DIR"
  echo "→ virtualenv created"

  # now activate and install
  # shellcheck source=/dev/null
  source "$ACTIVATE"
  echo "→ activated: $(which python)"

  pip install --upgrade pip
  if [ -f "$REQ_FILE" ]; then
    echo "→ installing from $REQ_FILE"
    pip install -r "$REQ_FILE"
  fi
else
  echo "Valid virtualenv detected in '$ENV_DIR'. Skipping creation/install."
  # just activate
  # shellcheck source=/dev/null
  source "$ACTIVATE"
  echo "→ activated: $VIRTUAL_ENV"
fi

echo "Done."