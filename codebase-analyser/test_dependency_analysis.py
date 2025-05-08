#!/usr/bin/env python3
"""
Test script to verify dependency analysis between code chunks.
"""

import sys
import json
from pathlib import Path
from codebase_analyser import CodebaseAnalyser

def print_dependency_graph(graph):
    """Print a dependency graph in a readable format."""
    print("\n=== Dependency Graph ===")
    
    # Print nodes
    print(f"\nNodes ({len(graph['nodes'])}):")
    for node in graph['nodes']:
        print(f"  {node['id']} - {node['name']} ({node['type']})")
    
    # Print edges
    print(f"\nEdges ({len(graph['edges'])}):")
    for edge in graph['edges']:
        print(f"  {edge['source_id']} -> {edge['target_id']} ({edge['type']})")
        print(f"    Strength: {edge['strength']:.2f}")
        print(f"    Description: {edge['description']}")
        if edge['locations']:
            print(f"    Locations: {len(edge['locations'])}")
            for loc in edge['locations'][:2]:  # Show at most 2 locations
                snippet = loc.get('snippet', 'N/A')
                print(f"      Line {loc['line']}: {snippet}")
            if len(edge['locations']) > 2:
                print(f"      ... and {len(edge['locations']) - 2} more locations")
    
    # Print metrics
    print("\nMetrics:")
    for key, value in graph['metrics'].items():
        if key == 'cyclic_dependencies' and value:
            print(f"  {key}: {len(value)} cycles found")
            for i, cycle in enumerate(value[:3]):  # Show at most 3 cycles
                print(f"    Cycle {i+1}: {' -> '.join(cycle)}")
            if len(value) > 3:
                print(f"    ... and {len(value) - 3} more cycles")
        else:
            print(f"  {key}: {value}")

def print_chunk_metrics(chunk):
    """Print dependency metrics for a chunk."""
    if 'dependency_metrics' not in chunk.metadata:
        print(f"No dependency metrics for {chunk.chunk_type} {chunk.name}")
        return
    
    metrics = chunk.metadata['dependency_metrics']
    print(f"\nDependency Metrics for {chunk.chunk_type} {chunk.name}:")
    print(f"  Fan-in: {metrics['fan_in']}")
    print(f"  Fan-out: {metrics['fan_out']}")
    print(f"  Instability: {metrics['instability']:.2f}")
    print(f"  Abstractness: {metrics['abstractness']:.2f}")
    print(f"  Distance from Main Sequence: {metrics['distance_from_main_sequence']:.2f}")
    
    # Print incoming dependencies
    if metrics['incoming_dependencies']:
        print(f"  Incoming Dependencies ({len(metrics['incoming_dependencies'])}):")
        for dep in metrics['incoming_dependencies']:
            print(f"    From {dep['chunk_id']} - Type: {dep['type']}, Strength: {dep['strength']:.2f}")
    
    # Print outgoing dependencies
    if metrics['outgoing_dependencies']:
        print(f"  Outgoing Dependencies ({len(metrics['outgoing_dependencies'])}):")
        for dep in metrics['outgoing_dependencies']:
            print(f"    To {dep['chunk_id']} - Type: {dep['type']}, Strength: {dep['strength']:.2f}")

def test_dependency_analysis(file_path):
    """Test dependency analysis on a file."""
    print(f"Testing dependency analysis on {file_path}")
    
    # Create analyser with the parent directory as the repo path
    analyser = CodebaseAnalyser(file_path.parent)
    
    # Parse the file
    result = analyser.parse_file(file_path)
    
    if not result:
        print(f"Failed to parse {file_path}")
        return
    
    print(f"Successfully parsed {file_path}")
    print(f"Language: {result['language']}")
    
    # Get chunks for the file
    chunks = analyser.get_chunks(result)
    
    print(f"\nCreated {len(chunks)} top-level chunks")
    
    # Get all chunks including descendants
    all_chunks = []
    for chunk in chunks:
        all_chunks.append(chunk)
        all_chunks.extend(chunk.get_descendants())
    
    print(f"Total chunks (including children): {len(all_chunks)}")
    
    # Print dependency graph
    if 'dependency_graph' in chunks[0].metadata:
        print_dependency_graph(chunks[0].metadata['dependency_graph'])
    else:
        print("No dependency graph found in file chunk metadata")
    
    # Print metrics for each chunk
    print("\n=== Chunk Dependency Metrics ===")
    for chunk in all_chunks:
        if chunk.chunk_type in ['class_declaration', 'interface_declaration', 'method_declaration', 'constructor_declaration']:
            print_chunk_metrics(chunk)
    
    # Save detailed results to a JSON file
    output_file = file_path.with_suffix('.dependencies.json')
    
    # Create a serializable representation of the chunk hierarchy with dependencies
    def chunk_to_dict(chunk):
        chunk_dict = chunk.to_dict()
        chunk_dict['children'] = [chunk_to_dict(child) for child in chunk.children]
        return chunk_dict
    
    with open(output_file, 'w') as f:
        json.dump([chunk_to_dict(chunk) for chunk in chunks], f, indent=2)
    
    print(f"\nDetailed results saved to {output_file}")
    print("Dependency analysis test completed successfully")

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_dependency_analysis.py <path_to_file>")
        return
    
    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return
    
    test_dependency_analysis(file_path)

if __name__ == "__main__":
    main()
