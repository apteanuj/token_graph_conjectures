#!/usr/bin/env python3
"""
gen_er_graphs_uniform.py

Usage:
    gen_er_graphs_uniform.py OUTPUT_DIR K

Generates exactly K Erdos–Renyi graphs for each n=3..10, with
  • p ~ Uniform(0,1)
  • edge weights w ~ Uniform(0,1)
Stores them newline-delimited in:
    OUTPUT_DIR/ER_n_3_to_10_{K}_per_n.jsonl
Each line is a node-link JSON for one graph, with fields "n" and "p".
"""

import os, sys, json, random
import networkx as nx
from networkx.readwrite import json_graph

def main():
    if len(sys.argv) != 3:
        print(__doc__); sys.exit(1)
    outdir = sys.argv[1]
    K      = int(sys.argv[2])
    os.makedirs(outdir, exist_ok=True)

    fname = f"ER_n_3_to_10_{K}_per_n.jsonl"
    path  = os.path.join(outdir, fname)

    with open(path, "w") as fout:
        for n in range(3, 11):
            for _ in range(K):
                # generate until connected
                while True:
                    p = random.random()
                    G = nx.erdos_renyi_graph(n, p)
                    if nx.is_connected(G):
                        break
                # assign random weights
                for u, v in G.edges():
                    G[u][v]["weight"] = random.random()
                # serialize
                data = json_graph.node_link_data(G)
                # data["n"] = n # optional meta-data
                # data["p"] = p # optional meta-data 
                fout.write(json.dumps(data) + "\n")

    print(f"Wrote uniform ER graphs to {path}")

if __name__ == "__main__":
    main()
