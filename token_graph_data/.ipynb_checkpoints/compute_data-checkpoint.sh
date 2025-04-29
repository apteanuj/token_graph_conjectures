#!/usr/bin/env bash

WORKERS=64
BATCH_SIZE=4096

# Current script directory (token_graph_conjectures/token_graph_data)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Repository root (token_graph_conjectures)
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
# Python script path
PY_SCRIPT="$SCRIPT_DIR/parallel_compute_data.py"

for TYPE in weighted unweighted; do
  INPUT_DIR="$REPO_ROOT/graph_generation/graphs/$TYPE"
  OUTPUT_DIR="$SCRIPT_DIR/data/$TYPE"

  mkdir -p "$OUTPUT_DIR"

  for graph_file in "$INPUT_DIR"/*; do
    [ -f "$graph_file" ] || continue  # Skip non-files safely
    echo "Processing [$TYPE] $(basename "$graph_file")..."
    python3 "$PY_SCRIPT" \
      "$graph_file" \
      --output_dir "$OUTPUT_DIR" \
      --workers "$WORKERS" \
      --batch_size "$BATCH_SIZE"
  done
done

echo "All jobs complete."