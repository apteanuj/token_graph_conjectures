#!/usr/bin/env bash
#
# usage: ./generate-connected.sh /path/to/output/dir

OUTDIR="$1"
if [[ -z "$OUTDIR" ]]; then
  echo "Usage: $0 /path/to/output/dir"
  exit 1
fi

# ensure the directory exists
mkdir -p "$OUTDIR"

# loop over odd n = 3,...,10
for n in {3..10..1}; do
  echo "Generating connected graphs on $n vertices…"
  ./nauty2_8_9/geng -c "$n" > "$OUTDIR/connected_n_${n}.g6"
done

echo "Done. Files in $OUTDIR:"
ls -1 "$OUTDIR"/connected_n_*.g6
