#!/usr/bin/env python3
"""
gen_paths_cycles.py

Usage:
    gen_paths_cycles.py OUTPUT_DIR MAX_N

Generates path graphs and cycle graphs for each n up to MAX_N:
  • Path graphs P_n for n = 3..MAX_N (vertices in a line)
  • Cycle graphs C_n for n = 3..MAX_N (vertices in a cycle)

Graphs are unweighted. Produces two JSONL files in OUTPUT_DIR:
  • paths_n_3_to_{MAX_N}.jsonl
  • cycles_n_3_to_{MAX_N}.jsonl

Each line in each file is a node-link JSON for one graph, including metadata: "n" and "type".
"""

import os
import sys
import json
import networkx as nx
from networkx.readwrite import json_graph


def main():
    # Parse arguments
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    outdir = sys.argv[1]
    try:
        max_n = int(sys.argv[2])
    except ValueError:
        print("Error: MAX_N must be an integer.")
        sys.exit(1)

    # Ensure output directory exists
    os.makedirs(outdir, exist_ok=True)

    # Prepare output files
    paths_fname = os.path.join(outdir, f"paths_n_3_to_{max_n}.jsonl")
    cycles_fname = os.path.join(outdir, f"cycles_n_3_to_{max_n}.jsonl")

    with open(paths_fname, 'w') as paths_f, open(cycles_fname, 'w') as cycles_f:
        # Generate path graphs P_n for n from 3 to max_n
        for n in range(3, max_n + 1):
            G = nx.path_graph(n)
            data = json_graph.node_link_data(G, edges="edges")
            data['n'] = n
            data['type'] = 'path'
            paths_f.write(json.dumps(data) + "\n")

        # Generate cycle graphs C_n for n from 3 to max_n
        for n in range(3, max_n + 1):
            G = nx.cycle_graph(n)
            data = json_graph.node_link_data(G, edges="edges")
            data['n'] = n
            data['type'] = 'cycle'
            cycles_f.write(json.dumps(data) + "\n")

    # Summary
    print(f"Wrote {max_n-2} path graphs (n=3..{max_n}) to {paths_fname}")
    if max_n >= 3:
        num_cycles = max_n - 2
        print(f"Wrote {num_cycles} cycle graphs (n=3..{max_n}) to {cycles_fname}")


if __name__ == '__main__':
    main()
