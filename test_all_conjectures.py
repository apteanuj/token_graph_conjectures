import os
import numpy as np
import jsonpickle
import tarfile
import re
import shutil

def stream_results_in_batches(filename, batch_size):
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
    Conjectures:
    lambda_{max}(L(F_k(G))) <=(W+C)/2 + M_k
    lambda_{max}(Q(F_k(G))) <= W + M_k
    lambda_{max}(-A(F_k(G))) <= C/2 + M_k/2
    lambda_{max}(A(F_k(G))) <= W/2 + M_k/2
    """
    W, C, M = data['graph_invariants']['W'], data['graph_invariants']['C'], data['graph_invariants']['M']
    n = len(data['graph']['nodes'])
    prev_Lk_max, prev_Qk_max, prev_Ak_max, prev_nAk_max = -np.inf, -np.inf, -np.inf, -np.inf

    for k in range(1, n // 2 + 1):
        Ak_max = data['k_data'][str(k)]['spec']['A']['max']
        nAk_max = -data['k_data'][str(k)]['spec']['A']['min']
        Lk_max = data['k_data'][str(k)]['spec']['L']['max']
        Qk_max = data['k_data'][str(k)]['spec']['Q']['max']
        Mk = data['k_data'][str(k)]['M_le_k']


        if not (Lk_max <= (W + C) / 2 + Mk): print(f"{data}, Lk <= (W+C)/2+Mk failed at k={k}")
        if not (Qk_max <= W + Mk): print(f"{data}, Qk <= W+Mk failed at k={k}")
        if not (nAk_max <= C / 2 + Mk / 2):print(f"{data}, -Ak <= C/2+Mk/2 failed at k={k}")
        if not (Ak_max <= W / 2 + Mk / 2):print(f"{data}, Ak <= W/2+Mk/2 failed at k={k}")
        if not (Lk_max >= prev_Lk_max):print(f"{data}, Lk monotonicity failed at k={k}")
        if not (Qk_max >= prev_Qk_max):print(f"{data}, Qk monotonicity failed at k={k}")
        if not (Ak_max >= prev_Ak_max):print(f"{data}, Ak monotonicity failed at k={k}")

        prev_Lk_max, prev_Qk_max, prev_Ak_max, prev_nAk_max = Lk_max, Qk_max, Ak_max, nAk_max


def safe_tarinfo_filter(tarinfo, path):
    """
    A secure tar filter that prevents extraction of absolute paths
    or paths with '..' to avoid path traversal vulnerabilities.
    """
    if tarinfo.name.startswith('/') or '..' in tarinfo.name.split('/'):
        print(f"Skipping unsafe file in tar: {tarinfo.name}")
        return None  # Exclude this file
    return tarinfo

def untar_file(tar_path, extract_to):
    """
    Extracts a tar file safely and returns a list of extracted .jsonl files.
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
            #print(f'Adding {part} to {output_path}')
            with open(part, 'rb') as infile:
                shutil.copyfileobj(infile, outfile)
    #print(f'Concatenated into: {output_path}')


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
    extracted_jsonl_files = set()  # Keep track of extracted .jsonl files to delete later

    for dirpath, dirnames, filenames in os.walk(root):
        filenames = sorted(filenames)

        # Match split archives like .tar.gz.part00.part
        part_pattern = re.compile(r'(.*\.tar\.gz)\.part\d+\.part')
        grouped_parts = {}

        # Group split parts by base name
        for filename in filenames:
            match = part_pattern.match(filename)
            if match:
                base = match.group(1)
                grouped_parts.setdefault(base, []).append(os.path.join(dirpath, filename))

        # Concatenate and extract each group of split parts
        for base, parts in grouped_parts.items():
            combined_path = os.path.join(dirpath, os.path.basename(base))
            concatenate_split_parts(parts, combined_path)
            extracted = untar_file(combined_path, dirpath)
            extracted_jsonl_files.update(extracted)

        # Extract any regular (non-split) .tar.gz files
        for filename in filenames:
            if filename.endswith('.tar.gz') and not part_pattern.match(filename):
                tar_path = os.path.join(dirpath, filename)
                extracted = untar_file(tar_path, dirpath)
                extracted_jsonl_files.update(extracted)

        # Run test_conjectures on all .jsonl files in the directory
        for filename in os.listdir(dirpath):
            if filename.endswith('.jsonl'):
                filepath = os.path.join(dirpath, filename)
                print(f'testing {filepath}')
                try:
                    for batch in stream_results_in_batches(filepath, batch_size):
                        for data in batch:
                            test_conjectures(data)
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")

    # Cleanup: delete extracted .jsonl files after processing
    for jsonl_path in extracted_jsonl_files:
        if os.path.exists(jsonl_path):
            print(f"Deleting extracted file: {jsonl_path}")
            os.remove(jsonl_path)

if __name__ == '__main__':
    run_all_conjecture_tests()
    print("Success!")