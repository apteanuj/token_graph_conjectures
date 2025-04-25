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


def get_maximum_matching_at_most_k_edges(G, k, return_edges=False):
    match_weight, max_matching = get_maximum_matching(G, return_edges=True)
    k_prime = len(max_matching)
    if k_prime <= k:
        if return_edges:
            return match_weight, max_matching
        else:
            return match_weight
    else:
        return get_maximum_matching_k_edges(G, k, return_edges=return_edges)


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