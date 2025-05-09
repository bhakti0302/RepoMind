#!/usr/bin/env python3
"""
Simple visualization script for Java code chunks.
"""

import os
import sys
import json
import argparse
import matplotlib.pyplot as plt
import networkx as nx
from pathlib import Path


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Visualize Java code chunks")
    parser.add_argument("db_path", help="Path to the LanceDB database")
    parser.add_argument("--output-file", help="Path to the output file", default="samples/java_dependency_graph.png")
    return parser.parse_args()


def load_chunks_from_db(db_path):
    """Load chunks from the database."""
    import lancedb
    
    db = lancedb.connect(db_path)
    table = db.open_table("code_chunks")
    
    # Query all Java chunks
    df = table.to_pandas()
    java_chunks = df[df['language'] == 'java']
    
    return java_chunks


def build_graph(chunks):
    """Build a graph from the chunks."""
    G = nx.DiGraph()
    
    # Add nodes
    for _, chunk in chunks.iterrows():
        G.add_node(
            chunk['node_id'],
            name=chunk['name'],
            chunk_type=chunk['chunk_type'],
            qualified_name=chunk.get('qualified_name', chunk['name'])
        )
    
    # Add parent-child edges
    for _, chunk in chunks.iterrows():
        if 'parent_id' in chunk and chunk['parent_id']:
            G.add_edge(
                chunk['parent_id'],
                chunk['node_id'],
                type='CONTAINS',
                weight=1.0
            )
    
    return G


def visualize_graph(G, output_file):
    """Visualize the graph."""
    plt.figure(figsize=(16, 12))
    
    # Define node colors based on chunk type
    node_colors = []
    for node in G.nodes():
        chunk_type = G.nodes[node].get('chunk_type', 'unknown')
        if chunk_type == 'file':
            node_colors.append('lightblue')
        elif chunk_type == 'class_declaration':
            node_colors.append('lightgreen')
        elif chunk_type == 'method_declaration':
            node_colors.append('orange')
        elif chunk_type == 'field_declaration':
            node_colors.append('pink')
        elif chunk_type == 'package_declaration':
            node_colors.append('yellow')
        elif chunk_type == 'import_declaration':
            node_colors.append('lightgray')
        else:
            node_colors.append('gray')
    
    # Define node labels
    node_labels = {node: G.nodes[node].get('name', node) for node in G.nodes()}
    
    # Define layout
    pos = nx.spring_layout(G, k=0.5, iterations=50)
    
    # Draw the graph
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=500, alpha=0.8)
    nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5, arrows=True)
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=8)
    
    # Add legend
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightblue', markersize=10, label='File'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightgreen', markersize=10, label='Class'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='orange', markersize=10, label='Method'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='pink', markersize=10, label='Field'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='yellow', markersize=10, label='Package'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightgray', markersize=10, label='Import')
    ]
    plt.legend(handles=legend_elements, loc='upper right')
    
    # Save the figure
    plt.title("Java Code Structure")
    plt.axis('off')
    plt.tight_layout()
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    plt.savefig(output_file, dpi=300)
    print(f"Saved visualization to {output_file}")


def main():
    """Main entry point."""
    args = parse_args()
    
    # Load chunks from the database
    chunks = load_chunks_from_db(args.db_path)
    print(f"Loaded {len(chunks)} Java chunks from the database")
    
    # Build the graph
    G = build_graph(chunks)
    print(f"Built graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    
    # Visualize the graph
    visualize_graph(G, args.output_file)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
