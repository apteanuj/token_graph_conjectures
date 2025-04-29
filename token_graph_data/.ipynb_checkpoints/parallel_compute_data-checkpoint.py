import json
import networkx as nx
from tqdm import tqdm
from typing import Dict, Union, List, Generator
import argparse
import multiprocessing as mp
from pathlib import Path
import jsonpickle
from utils import * 

def process_single_graph(data: Union[str, bytes], is_g6: bool) -> dict:
    """Process a single graph from either G6 or JSON format."""
    try:
        if is_g6:
            G = read_graph_from_g6_line(data)
        else:
            G = read_graph_from_json(data)
        
        # Compute all graph invariants
        result = graph_data_all_k(G)
        return result
    except Exception as e:
        print(f"Error processing graph: {e}")
        return None


def batch_reader(file_path: str, batch_size: int = 1000) -> Generator[List[str], None, None]:
    """Simple batch reader without counting lines."""
    batch = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line:  # Skip empty lines
                batch.append(line)
                if len(batch) >= batch_size:
                    yield batch
                    batch = []
        
        # Don't forget the last batch
        if batch:
            yield batch

def process_batch(batch: List[str], is_g6: bool, worker_id: int) -> List[dict]:
    """Process a batch of graphs."""
    results = []
    for data in batch:
        try:
            result = process_single_graph(data, is_g6)
            if result is not None:
                results.append(result)
        except Exception as e:
            print(f"Worker {worker_id}: Error processing graph: {e}")
    return results

def process_file_batched(input_file: str, output_file: str, num_workers: int, batch_size: int = 1000):
    """Process graphs from input file in batches with multiple workers."""
    # Determine file format based on extension
    is_g6 = not input_file.endswith('.jsonl')
    
    # Create output file (or truncate if it exists)
    with open(output_file, 'w') as f:
        pass
    
    total_processed = 0
    total_batches = 0
    
    # Count total lines once
    print("Counting total graphs in file...")
    with open(input_file, 'r') as f:
        total_lines = sum(1 for _ in f)
    estimated_batches = (total_lines + batch_size - 1) // batch_size
    print(f"Found {total_lines} total graphs, will process in approximately {estimated_batches} batches")
    
    # Create the progress bar after showing count message
    batch_pbar = tqdm(
        desc=f"Processing {estimated_batches} batches", 
        unit="batch", 
        total=estimated_batches
    )
    
    # Process file in batches
    for batch_num, batch in enumerate(batch_reader(input_file, batch_size)):
        total_batches += 1
        batch_size_actual = len(batch)
        
        # Split the batch into smaller chunks for workers
        chunk_size = max(1, batch_size_actual // num_workers)
        chunks = [batch[i:i+chunk_size] for i in range(0, batch_size_actual, chunk_size)]
        
        # Process chunks in parallel
        with mp.Pool(num_workers) as pool:
            results = pool.starmap(
                process_batch,
                [(chunk, is_g6, i) for i, chunk in enumerate(chunks)]
            )
        
        # Flatten results from all workers
        flat_results = [r for worker_results in results for r in worker_results]
        batch_processed = len(flat_results)
        
        # Append results to output file
        with open(output_file, 'a') as f:
            for result in flat_results:
                # Consistently use jsonpickle
                json_str = jsonpickle.encode(result, unpicklable=False)
                f.write(json_str + '\n')
        
        total_processed += batch_processed
        
        # Update progress bar description with current stats
        batch_pbar.set_description(
            f"Batch {batch_num+1}/{estimated_batches}: {batch_processed}/{batch_size_actual} graphs, total: {total_processed}/{total_lines}"
        )
        
        # Update progress bar
        batch_pbar.update(1)
    
    # Close progress bar
    batch_pbar.close()
    
    print(f"All done! Processed {total_processed} graphs across {total_batches} batches.")
    print(f"Results written to {output_file}")

def process_graphs_cli():
    """Command-line interface for processing graph files."""
    parser = argparse.ArgumentParser(description='Process graph files and compute invariants')
    parser.add_argument('input_file', help='Input file path (JSONL or G6 format)')
    parser.add_argument('--output_dir', '-o', default=None, help='Output directory (default: same as input)')
    parser.add_argument('--workers', '-w', type=int, default=mp.cpu_count(), 
                        help=f'Number of worker processes (default: {mp.cpu_count()})')
    parser.add_argument('--batch_size', '-b', type=int, default=1000,
                        help='Number of graphs to process in each batch (default: 1000)')
    
    args = parser.parse_args()
    
    # Set up output directory and file
    input_path = Path(args.input_file)
    
    if args.output_dir:
        output_dir = Path(args.output_dir)
        output_dir.mkdir(exist_ok=True, parents=True)
    else:
        output_dir = input_path.parent
    
    output_file = output_dir / f"{input_path.stem}_data.jsonl"
    
    # Process the file
    process_file_batched(args.input_file, output_file, args.workers, args.batch_size)

if __name__ == "__main__":
    process_graphs_cli()