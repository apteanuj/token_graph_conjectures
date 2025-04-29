import json
import networkx as nx
from networkx.readwrite.json_graph import node_link_data, node_link_graph
from typing import Dict, Union
from compute_graph_invariants import *
from compute_token_graph_spectra import *


def read_graph_from_g6_line(line: Union[str, bytes]) -> nx.Graph:
    """
    Parse a single Graph6 line into a NetworkX Graph, handling both str and bytes.
    """
    if isinstance(line, str):
        raw = line.strip().encode('ascii')
    else:
        raw = line.strip()
    return nx.from_graph6_bytes(raw)

def read_graph_from_json(json_str: str) -> nx.Graph:
    """
    Read a graph from a JSON string in node-link format.
    """
    data = json.loads(json_str)
    return node_link_graph(data)


def save_graph_data_to_json(G: nx.Graph, filename: str) -> None:
    """
    Save graph G to a JSON file in node-link format.
    """
    data = node_link_data(G)
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)


def graph_invariant_data(G: nx.Graph) -> Dict:
    """
    Compute basic invariants for a graph G:

    - W: Total sum of all edge weights
    - C: Maximum cut value
    - M: Maximum matching weight

    Parameters
    ----------
    G : networkx.Graph
        The input graph (possibly weighted).

    Returns
    -------
    dict
        {
            "W": float,  # total weight
            "C": float,  # max cut
            "M": float   # max matching
        }
    """
    W = get_weight_sum(G)
    C = get_maximum_cut(G)
    M = get_maximum_matching(G)

    return {"W": W, "C": C, "M": M}


def graph_k_invariants(G: nx.Graph, k: int) -> Dict[str, float]:
    """
    Compute two k-constrained invariants on G:
      - M_le_k : maximum matching weight using ≤ k edges
      - C_k    : maximum k-cut (partition size = k)

    Parameters
    ----------
    G : networkx.Graph
    k : int

    Returns
    -------
    dict
      {
        "M_le_k": float,  # max matching weight with ≤ k edges
        "C_k":    float   # max cut value when one side has size k
      }
    """
    M_le_k = get_maximum_matching_at_most_k_edges(G, k)
    C_k    = get_maximum_k_cut(G, k)
    return {
        "M_le_k": M_le_k,
        "C_k":    C_k
    }

def token_graph_spectrum(G: nx.Graph, k: int) -> Dict:
    """
    For the k-token graph of G, compute the min/max eigenvalues of:
      - A (adjacency)
      - L (graph Laplacian)
      - Q (signless Laplacian)

    Returns
    -------
    {
      "A": {"min": float, "max": float},
      "L": {"min": float, "max": float},
      "Q": {"min": float, "max": float}
    }
    """
    kth_token_graph = get_token_graph(G, k)
    A, L, Q = get_graph_matrices(kth_token_graph)
    
    # Extract scalar values from NumPy arrays
    min_A = float(get_minimum_eigval(A))
    min_A = round(min_A, 6)
    max_A = float(get_maximum_eigval(A))
    max_A = round(max_A, 6)
    min_L = float(get_minimum_eigval(L))
    min_L = round(min_L, 6)
    max_L = float(get_maximum_eigval(L))
    max_L = round(max_L, 6)
    min_Q = float(get_minimum_eigval(Q))
    min_Q = round(min_Q, 6)
    max_Q = float(get_maximum_eigval(Q))
    max_Q = round(max_Q, 6)
    
    return {
        "A": {"min": min_A, "max": max_A},
        "L": {"min": min_L, "max": max_L},
        "Q": {"min": min_Q, "max": max_Q},
    }
    
def graph_data_all_k(G) -> Dict:
    """
    Combine everything in one structure 

        • basic_graph_data(G)
        • graph_k_invariants(G, k)
        • token_graph_spectrum(G, k)

    The output has three top-level keys:
      - "graph"   : NetworkX node-link JSON for G
      - "basic_data" : {"W", "C", "M"} from basic_graph_data
      - "k_data"  : mapping k ↦ {M_le_k, C_k, spec}

    Here  k  runs from 1 up to ⌊(n)/2⌋.
    """
    # ensure every edge carries a numeric weight
    if "weight" not in next(iter(G.edges(data=True)))[2]:
        nx.set_edge_attributes(G, 1.0, name="weight")
    
    n        = G.number_of_nodes()
    max_k    = (n) // 2

    # graph-level metrics
    summary  = {
        "graph":   node_link_data(G),          # topology + weights
        "graph_invariants": graph_invariant_data(G),        # W, C, M
        "k_data":  {}
    }

    # per-k data
    for k in range(1, max_k + 1):
        k_dict = graph_k_invariants(G, k)      # M_le_k, C_k
        k_dict["spec"] = token_graph_spectrum(G, k)   # eigenvalue mins/maxs
        summary["k_data"][k] = k_dict

    return summary

# G = nx.star_graph(8)
# nx.set_edge_attributes(G, 1.0, "weight")      # unit weights
# result = graph_data_all_k(G)
# print(result)