import networkx as nx
from itertools import combinations
import numpy as np


def get_weight_sum(G):
    return G.size(weight="weight")


def get_maximum_matching(G, return_edges=False):
    M_list = nx.max_weight_matching(G, weight='weight')
    if return_edges: return sum([G[u][v]['weight'] for u,v in M_list]), M_list
    else: return sum([G[u][v]['weight'] for u,v in M_list])


def is_valid_matching(edge_set):
    seen = set()
    for u, v in edge_set:
        if u in seen or v in seen:
            return False
        seen.add(u)
        seen.add(v)
    return True


def get_maximum_matching_k_edges(G, k, return_edges=False):
    best_matching = set()
    best_weight = float('-inf')
    # brute force all subsets of k edges
    for edge_combo in combinations(G.edges, k):
        if is_valid_matching(edge_combo):
            weight = sum(G[u][v].get("weight", 1) for u, v in edge_combo)
            if weight > best_weight:
                best_matching = set(edge_combo)
                best_weight = weight
    if not best_matching:
        raise ValueError(f"No matching of exactly {k} edges exists.")
    if return_edges:
        return best_weight, best_matching
    else:
        return best_weight

# Confused here why don't we have to iterate over all k less than given k value ? 

from typing import Set, Tuple, List
import networkx as nx
import numpy as np

def max_weight_matching_at_most_k(G: nx.Graph, k: int,
                                  return_edges: bool = False):
    """Exact max-weight matching using ≤k edges via branch-and-bound."""
    edges_sorted: List[Tuple[int,int]] = sorted(
        G.edges(), key=lambda e: G[e[0]][e[1]].get("weight", 1.0), reverse=True)

    best_w, best_set = -np.inf, set()
    prefix_sums = np.cumsum([G[u][v].get("weight", 1.0) for u, v in edges_sorted])

    def dfs(idx: int, chosen: Set[Tuple[int,int]], used: Set[int], cur_w: float):
        nonlocal best_w, best_set
        # prune by cardinality
        if len(chosen) == k or idx == len(edges_sorted):
            if cur_w > best_w:
                best_w, best_set = cur_w, set(chosen)
            return
        # optimistic bound with remaining largest weights
        rem = k - len(chosen)
        opt_bound = cur_w + (prefix_sums[idx + rem - 1] - (prefix_sums[idx - 1] if idx else 0))
        if opt_bound <= best_w:
            return

        u, v = edges_sorted[idx]
        w_uv = G[u][v].get("weight", 1.0)

        # 1) choose this edge if feasible
        if u not in used and v not in used:
            dfs(idx + 1, chosen | {(u, v)}, used | {u, v}, cur_w + w_uv)
        # 2) skip this edge
        dfs(idx + 1, chosen, used, cur_w)

    dfs(0, set(), set(), 0.0)
    return (best_w, best_set) if return_edges else best_w

def get_maximum_matching_at_most_k_edges(G, k, return_edges=False):
    """
    Exact solution but orders-of-magnitude faster than the old brute force.
    Falls back to the trivial case if the unrestricted matching
    already has ≤k edges.
    """
    total, full = get_maximum_matching(G, return_edges=True)
    if len(full) <= k:
        return (total, full) if return_edges else total
    # otherwise use branch-and-bound
    return max_weight_matching_at_most_k(G, k, return_edges)


def calculate_cut_value(G, partition):
    cut_value = 0
    for edge in G.edges(data=True):
        u, v, weight = edge[0], edge[1], edge[2].get('weight', 1)
        if (u in partition and v not in partition) or (u not in partition and v in partition):
            cut_value += weight
    return cut_value


def get_maximum_cut(G, return_partitions=False):
    nodes = G.nodes
    n = len(nodes)
    weights = range(1, n // 2 + 1)
    max_cut_at_weight = {weight: 0 for weight in weights}
    # Iterate over all possible partitions
    for weight in weights:
        for subset in combinations(nodes, weight):
            cut_value = calculate_cut_value(G, set(subset))
            if cut_value > max_cut_at_weight[weight]:
                max_cut_at_weight[weight] = cut_value
    max_cut = max(max_cut_at_weight.values())
    if return_partitions:
        return max_cut, [k for k,v in max_cut_at_weight.items() if np.abs(v-max_cut)<TOL]
    else:
        return max_cut
    
    
def get_maximum_k_cut(G, k):
    nodes = G.nodes
    n = len(nodes)
    max_cut = -np.inf
    # Iterate over all possible partitions
    for subset in combinations(nodes, k):
        cut_value = calculate_cut_value(G, set(subset))
        if cut_value > max_cut: 
            max_cut  = cut_value
    return max_cut