# Token Graph Conjectures

This repository contains code and data related to graphs and associated properties of 2-local Hamiltonians and their token graphs.

---

## 📁 Structure

### `graph_generation/`

Contains code to generate graphs and a subdirectory to store them.

- **`graphs/`** — Generated graphs and their data:
  - **`unweighted/`**: 
    - Non-isomorphic unweighted graphs up to order *n = 10*.
    - Unweighted paths and cycles up to order *n = 13*.
    - Stored in `.g6` or `.jsonl` format.
  - **`weighted/`**: 
    - Weighted graphs up to order *n = 10*.
    - Stored in `.jsonl` format.

- **`nauty2_8_9/`** — Contains an installation of Nauty 2.8.9.

- **Graph Generation Scripts**:
  - `filter_factor_critical.py`: Filters graphs that are not factor-critical.
  - `gen_complete_graphs.py`: Generates complete graphs with random weights (uniform/exponential).
  - `gen_er_graphs_uniform.py`: Generates Erdős–Rényi graphs with random weights.
  - `gen_paths_cycles.py`: Generates unweighted paths and cycles.
  - `generate-2v-odd.sh`: Uses Nauty to generate odd-order biconnected graphs.
  - `generate-connected.sh`: Uses Nauty to generate connected unweighted graphs.
  - `instructions_graph_generation.txt`: Instructions for using Nauty.
  - `nauty2_8_9.tar.gz`: Tarball of Nauty 2.8.9.

---

### `token_graph_data/`

Contains code to compute graph invariants and eigenspectra of token graphs, along with output data.

- **`data/`** — Stores token graph data and properties as nested dictionaries:
  - **Graph Info**: Nodes, edges, weights.
  - **Maximum Matchings**: Including matchings with ≤ *k* edges.
  - **Maximum Cuts**: Including cuts with ≤ *k* edges.
  - **Eigenvalues**: Adjacency ($A$), Laplacian ($L$), and signless Laplacian ($Q$).

- **Subdirectories**:
  - `unweighted/`: Token graphs up to order 10 and paths/cycles up to 13.
  - `weighted/`: Weighted token graphs up to order 10.

- **Computation Scripts**:
  - `compute_graph_invariants.py`: Computes graph invariants and eigenvalues.
  - `compute_token_graphs.py`: Computes eigenvalues of token graphs.
  - `instructions_token_graph_data.txt`: Guide for generating token graph data.

---

## 🧪 Testing and Output

- `failing_conjecture_graphs.jsonl`: Counterexamples to the tested conjectures.
- `inspect_failing_graphs.ipynb`: Jupyter notebook to explore failing cases.
- `test_all_conjectures.py`: Tests all conjectures and outputs:
  - `failing_conjecture_graphs.jsonl`
  - `worst_case_approx.json`
- `worst_case_approx.json`: Approximation ratio stats for conjectures.

---

## ⚙️ Environment Setup

```bash
chmod +x setup_env.sh
source setup_env.sh


