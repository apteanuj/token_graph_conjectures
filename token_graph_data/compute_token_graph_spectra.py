from itertools import combinations
import networkx as nx
import numpy as np
from scipy.linalg import eigh


def get_token_graph(G, k):
    vertices = list(G.nodes)
    Gk = nx.Graph()
    token_nodes = list(combinations(vertices, k))
    Gk.add_nodes_from(token_nodes)
    for subset_1, subset_2 in combinations(token_nodes, 2):
        diff_1 = set(subset_1) - set(subset_2)
        diff_2 = set(subset_2) - set(subset_1)
        if len(diff_1) == 1 and len(diff_2) == 1:
            u, = diff_1
            v, = diff_2
            if G.has_edge(u, v):
                weight = G.get_edge_data(u, v, default={}).get('weight', 1)
                Gk.add_edge(subset_1, subset_2, weight=weight)
    return Gk


def get_graph_matrices(G, nodelist=None):
    A = nx.adjacency_matrix(G, nodelist=nodelist).toarray()
    degrees = np.array([G.degree(n) for n in (nodelist or G.nodes())])
    D = np.diag(degrees)
    L = D - A
    Q = D + A
    return A, L, Q


# bug in scipy for computing only largest eigval https://github.com/scipy/scipy/issues/13220
# resolution: subset_by_index=(0, 0) for min, (H.shape[0]-1, H.shape[0]-1) for max
def get_maximum_eigval(H):
    return eigh(H, eigvals_only=True, subset_by_index=(H.shape[0]-1, H.shape[0]-1))[0] 

def get_minimum_eigval(H):
    return eigh(H, eigvals_only=True, subset_by_index=(0, 0))[0]

