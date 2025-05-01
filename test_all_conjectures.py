import os
import numpy as np
import jsonpickle
import tarfile
import re
import shutil
from tqdm.auto import tqdm

TOL = 1e-8

def stream_results_in_batches(filename, batch_size):
    """
    Generate batches of results from a file.

    Parameters:
    - filename: str - the name of the file to read from
    - batch_size: int - the number of results in each batch

    Yields:
    - List of results as decoded from jsonpickle
    """
    batch = []
    with open(filename, 'r') as f:
        for line in f:
            result = jsonpickle.decode(line.strip())
            batch.append(result)
            if len(batch) == batch_size:
                yield batch
                batch = []
        if batch:
            yield batch

def test_conjectures(data):
    """
    Test conjectures for token graphs. Print failures and store failing graphs with reasons.
    """
    W, C, M = data['graph_invariants']['W'], data['graph_invariants']['C'], data['graph_invariants']['M']
    n = len(data['graph']['nodes'])
    prev_Lk_max, prev_Qk_max, prev_Ak_max, prev_nAk_max = -np.inf, -np.inf, -np.inf, -np.inf
    L_max, A_max, nA_max = -np.inf, -np.inf, -np.inf
    failing_conjectures = []

    for k in range(1, n // 2 + 1):
        Ak_max = data['k_data'][str(k)]['spec']['A']['max']
        nAk_max = -data['k_data'][str(k)]['spec']['A']['min']
        Lk_max = data['k_data'][str(k)]['spec']['L']['max']
        Qk_max = data['k_data'][str(k)]['spec']['Q']['max']
        Mk = data['k_data'][str(k)]['M_le_k'] 

        conditions = [
            (Lk_max <= (W + C) / 2 + Mk + TOL, f"Lk <= (W+C)/2+Mk failed at k={k}."),
            (Qk_max <= W + Mk + TOL, f"Qk <= W+Mk failed at k={k}."),
            (nAk_max <= C / 2 + Mk / 2 + TOL, f" -Ak <= C/2+Mk/2 failed at k={k}."),
            (Ak_max <= W / 2 + Mk / 2 + TOL, f"Ak <= W/2+Mk/2 failed at k={k}."),
            (Lk_max >= prev_Lk_max - TOL, f"Lk monotonicity failed at k={k}."),
            (Qk_max >= prev_Qk_max - TOL, f"Qk monotonicity failed at k={k}."),
            (Ak_max >= prev_Ak_max - TOL, f"Ak monotonicity failed at k={k}."),
        ]
        for condition, message in conditions:
            if not condition:
                print(message)
                failing_conjectures.append(message)

        L_max, A_max, nA_max = max(L_max, Lk_max), max(A_max, Ak_max), max(nA_max, nAk_max)
        prev_Lk_max, prev_Qk_max, prev_Ak_max, prev_nAk_max = Lk_max, Qk_max, Ak_max, nAk_max

    # Graph-level checks
    match_energy_qmc = (3 * M + W) / 2
    match_energy_xy = M
    cut_energy_qmc = C
    cut_energy_xy = C - W / 2
    xy_max, xy_min = nA_max, -A_max

    conditions = [
        (max(match_energy_qmc, cut_energy_qmc) / L_max >= 3 / 4 - TOL, "QMC ALG/OPT>=3/4 failed"),
        ((max(match_energy_xy, cut_energy_xy) - xy_min) / (xy_max - xy_min) >= 3 / 4 - TOL, "XY ALG/OPT>=3/4 failed"),
    ]

    for condition, message in conditions:
        if not condition:
            print(message)
            failing_conjectures.append(message)

    # Save failing data if any conjectures failed
    if failing_conjectures:
        data['failing_conjectures'] = failing_conjectures
        with open('failing_graphs.jsonl', 'a') as f:
            f.write(jsonpickle.encode(data) + "\n")

def safe_tarinfo_filter(tarinfo, path):
    """
    A secure tar filter that prevents extraction of absolute paths
    or paths with '..' to avoid path traversal vulnerabilities.

    Parameters:
    - tarinfo: TarInfo - Tarfile metadata
    - path: str - Path to extract to

    Returns:
    - Modified TarInfo object or None if unsafe
    """
    if tarinfo.name.startswith('/') or '..' in tarinfo.name.split('/'):
        print(f"Skipping unsafe file in tar: {tarinfo.name}")
        return None
    return tarinfo

def untar_file(tar_path, extract_to):
    """
    Extracts a tar file safely and returns a list of extracted .jsonl files.

    Parameters:
    - tar_path: str - Path to the tar file
    - extract_to: str - Directory to extract to

    Returns:
    - List of extracted .jsonl file paths
    """
    extracted_jsonls = []
    try:
        with tarfile.open(tar_path, 'r:*') as tar:
            members = tar.getmembers()
            tar.extractall(path=extract_to, filter=safe_tarinfo_filter)
            print(f'Untarred: {tar_path}')
            for member in members:
                if member.name.endswith('.jsonl'):
                    extracted_jsonls.append(os.path.join(extract_to, member.name))
    except tarfile.ReadError:
        print(f'Failed to untar: {tar_path}')
    return extracted_jsonls

def concatenate_split_parts(part_files, output_path):
    """
    Concatenates multiple part files into a single .tar.gz file.

    Parameters:
    - part_files: list of str - paths to split .part files
    - output_path: str - path where the combined file will be written
    """
    with open(output_path, 'wb') as outfile:
        for part in sorted(part_files):
            with open(part, 'rb') as infile:
                shutil.copyfileobj(infile, outfile)


def run_all_conjecture_tests(root='token_graph_data/data', batch_size=100):
    """
    Recursively runs test_conjectures on all .jsonl files found under the root directory.
    - Handles both regular and nested subdirectories.
    - Automatically untars .tar.gz files.
    - Reconstructs and untars split archives like .tar.gz.part00.part, .part01.part, etc.
    - Tracks and deletes all .jsonl files that were originally extracted from tarballs.

    Parameters:
    - root: str - root directory to start searching
    - batch_size: int - batch size to use with stream_results_in_batches
    """
    # keep track of extracted jsonl files and combined tar files to delete later (maintains directory size for github)
    extracted_jsonl_files = set()
    combined_tar_files = set()

    for dirpath, dirnames, filenames in os.walk(root):
        filenames = sorted(filenames)
        part_pattern = re.compile(r'(.*\.tar\.gz)\.part\d+\.part')
        grouped_parts = {}

        for filename in filenames:
            match = part_pattern.match(filename)
            if match:
                base = match.group(1)
                grouped_parts.setdefault(base, []).append(os.path.join(dirpath, filename))

        for base, parts in grouped_parts.items():
            combined_path = os.path.join(dirpath, os.path.basename(base))
            concatenate_split_parts(parts, combined_path)
            combined_tar_files.add(combined_path)
            extracted = untar_file(combined_path, dirpath)
            extracted_jsonl_files.update(extracted)

        for filename in filenames:
            if filename.endswith('.tar.gz') and not part_pattern.match(filename):
                tar_path = os.path.join(dirpath, filename)
                extracted = untar_file(tar_path, dirpath)
                extracted_jsonl_files.update(extracted)

        for filename in os.listdir(dirpath):
            if filename.endswith('.jsonl'):
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, 'r') as f:
                        total_lines = sum(1 for _ in f)

                    for batch in tqdm(stream_results_in_batches(filepath, batch_size),
                                      total=total_lines // batch_size,
                                      desc=f"Processing {filepath}"):
                        for data in batch:
                            test_conjectures(data)

                except Exception as e:
                    print(f"Error processing {filepath}: {e}")

    for jsonl_path in extracted_jsonl_files:
        if os.path.exists(jsonl_path):
            print(f"Deleting extracted file: {jsonl_path}")
            os.remove(jsonl_path)
    for tar_path in combined_tar_files:
        if os.path.exists(tar_path):
            print(f"Deleting combined tar file: {tar_path}")
            os.remove(tar_path)

if __name__ == '__main__':
    run_all_conjecture_tests()
    print("Success!")