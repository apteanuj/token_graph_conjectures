#!/usr/bin/env python3
"""
filter_factor_critical.py

Usage:
    ./filter_factor_critical.py /path/to/g6_dir

For each file X.g6 in the directory, produces fc_X.jsonl containing
all factor-critical graphs (in node-link JSON, one per line), and prints counts.
"""

import os
import sys
import glob
import json
import networkx as nx
from networkx.readwrite import json_graph


def is_factor_critical(G: nx.Graph) -> bool:
    """
    A graph G is factor-critical if:
      1) G has an odd number of vertices,
      2) for every vertex v, the graph G - v has a perfect matching.
    """
    n = G.number_of_nodes()
    # (1) must be odd
    if n % 2 == 0:
        return False

    # (2) check removal of each vertex leaves a perfect matching
    for v in G.nodes():
        H = G.copy()
        H.remove_node(v)
        m = nx.algorithms.matching.max_weight_matching(H, maxcardinality=True)
        if len(m) * 2 != n - 1:
            return False
    return True


def process_file(g6_path: str):
    base = os.path.basename(g6_path)
    stem = os.path.splitext(base)[0]
    out_name = f"fc_{stem}.jsonl"
    out_path = os.path.join(os.path.dirname(g6_path), out_name)

    total = 0
    fc_count = 0

    with open(g6_path, 'rt') as fin, open(out_path, 'wt') as fout:
        for line in fin:
            s = line.strip()
            if not s or s.startswith('#'):
                continue
            total += 1
            G = nx.from_graph6_bytes(s.encode('ascii'))
            if is_factor_critical(G):
                fc_count += 1
                data = json_graph.node_link_data(G)
                fout.write(json.dumps(data) + "\n")

    print(f"{base}: {total} graphs read, {fc_count} factor-critical written to {out_name}")


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    directory = sys.argv[1]
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a directory")
        sys.exit(1)

    # glob is used here to find all .g6 files in the given directory
    for g6_file in glob.glob(os.path.join(directory, '*.g6')):
        print(f"Processing {g6_file} …")
        process_file(g6_file)

if __name__ == "__main__":
    main()
