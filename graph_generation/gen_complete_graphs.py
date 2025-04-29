#!/usr/bin/env python3
"""
gen_complete_graphs.py

Usage:
    gen_complete_graphs.py OUTPUT_DIR K

Generates exactly K complete graphs (K_n) for each n = 3..10, with edge weights drawn from three distributions:
  • uniform(0,1)
  • exponential with λ=1
  • exponential with λ=10

Produces three JSONL files in OUTPUT_DIR:
  • complete_n_3_to_10_{K}_uniform.jsonl
  • complete_n_3_to_10_{K}_exp1.jsonl
  • complete_n_3_to_10_{K}_exp10.jsonl

Each line in each file is a node-link JSON for one graph, including metadata:"n" and "dist".
"""

import os
import sys
import json
import random
import networkx as nx
from networkx.readwrite import json_graph


def assign_weights(G: nx.Graph, dist: str) -> None:
    """
    Assign edge weights in-place on G based on distribution:
      - 'uniform': Uniform(0,1)
      - 'exp1':   Exponential(rate=1)
      - 'exp10':  Exponential(rate=10)
    """
    for u, v in G.edges():
        if dist == 'uniform':
            w = random.random()
        elif dist == 'exp1':
            w = random.expovariate(1.0)
        elif dist == 'exp10':
            w = random.expovariate(10.0)
        else:
            raise ValueError(f"Unknown distribution '{dist}'")
        G[u][v]['weight'] = w


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    outdir = sys.argv[1]
    try:
        K = int(sys.argv[2])
    except ValueError:
        print("Error: K must be an integer.")
        sys.exit(1)

    os.makedirs(outdir, exist_ok=True)
    dists = ['uniform', 'exp1', 'exp10']
    writers = {}

    # Open one file per distribution
    for dist in dists:
        fname = f"complete_n_3_to_10_{K}_{dist}.jsonl"
        path = os.path.join(outdir, fname)
        writers[dist] = open(path, 'w')

    # Generate K graphs for each n and each distribution
    for n in range(3, 11):
        for _ in range(K):
            G = nx.complete_graph(n)
            for dist in dists:
                assign_weights(G, dist)
                data = json_graph.node_link_data(G, edges="edges")
                data['n'] = n
                data['dist'] = dist
                writers[dist].write(json.dumps(data) + "\n")

    # Close files and report
    for dist, f in writers.items():
        f.close()
        fname = f"complete_n_3_to_10_{K}_{dist}.jsonl"
        print(f"Wrote {K*8} graphs (n=3..10) to {fname}")


if __name__ == '__main__':
    main()
