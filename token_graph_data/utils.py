import networkx as nx


def read_graph_from_g6(g6):
    """
    TODO: test
    Read a graph from a G6 string.
    """
    return nx.from_graph6_bytes(g6.encode('utf-8'))


def convert_graph6_to_networkx(graph6):
    # is this better?
    G = nx.from_graph6_bytes(graph6)
    return G


def read_graph_from_json(json):
    """
    TODO: test
    Read a graph from a JSON string.
    """
    return nx.readwrite.json_graph.node_link_graph(json)

def save_graph_data_to_json(G, filename):
    """
    TODO
    """
    return 