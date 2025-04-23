#!/usr/bin/env bash
#
# usage: ./generate-2vc-odd.sh /path/to/output/dir

OUTDIR="$1"
if [[ -z "$OUTDIR" ]]; then
  echo "Usage: $0 /path/to/output/dir"
  exit 1
fi

# ensure the directory exists
mkdir -p "$OUTDIR"

# loop over odd n = 3,5,7,9
for n in {3..9..2}; do
  echo "Generating 2-vertex-connected graphs on $n vertices…"
  ./nauty2_8_9/geng -C "$n" > "$OUTDIR/2vc_n_${n}.g6"
done

echo "Done. Files in $OUTDIR:"
ls -1 "$OUTDIR"/2vc_n_*.g6
