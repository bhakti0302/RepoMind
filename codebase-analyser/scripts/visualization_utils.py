#!/usr/bin/env python3
"""
Visualization Utilities for the Codebase Analyzer

This module provides utility functions for:
1. Copying visualizations to a target directory
2. Enhancing existing graph visualizations
3. Other common visualization tasks

Usage:
    python visualization_utils.py --copy-visualizations --source-dir SOURCE --target-dir TARGET
    python visualization_utils.py --enhance-graph --input-file INPUT --output-file OUTPUT
"""

import os
import sys
import json
import argparse
import logging
import shutil
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Color mapping for different relationship types
RELATIONSHIP_COLORS = {
    "IMPORTS": "#9E9E9E",        # Gray
    "EXTENDS": "#4CAF50",        # Green
    "IMPLEMENTS": "#2196F3",     # Blue
    "USES": "#FF9800",           # Orange
    "CONTAINS": "#9C27B0",       # Purple
    "CALLS": "#F44336",          # Red
    "REFERENCES": "#795548",     # Brown
    "FIELD_TYPE": "#607D8B"      # Blue Gray
}

def copy_visualizations(source_dir: str, target_dir: str, file_pattern: str = "*.png") -> None:
    """
    Copy visualization files from source directory to target directory.
    
    Args:
        source_dir: Source directory containing visualization files
        target_dir: Target directory to copy files to
        file_pattern: File pattern to match (default: "*.png")
    """
    source_path = Path(source_dir)
    target_path = Path(target_dir)
    
    # Create target directory if it doesn't exist
    target_path.mkdir(parents=True, exist_ok=True)
    
    # Find all visualization files
    visualization_files = list(source_path.glob(file_pattern))
    
    if not visualization_files:
        logger.warning(f"No visualization files found in {source_dir}")
        return
    
    # Copy files
    for file_path in visualization_files:
        target_file = target_path / file_path.name
        shutil.copy2(file_path, target_file)
        logger.info(f"Copied {file_path} to {target_file}")
    
    logger.info(f"Copied {len(visualization_files)} visualization files to {target_dir}")

def enhance_graph_visualization(input_file: str, output_file: str, 
                               title: str = None, 
                               node_size: int = 1500, 
                               font_size: int = 10,
                               figsize: Tuple[int, int] = (12, 10)) -> None:
    """
    Enhance an existing graph visualization by adding colors, adjusting layout, etc.
    
    Args:
        input_file: Input graph file (JSON format)
        output_file: Output visualization file
        title: Graph title
        node_size: Size of nodes
        font_size: Font size for labels
        figsize: Figure size (width, height)
    """
    # Load graph from JSON
    try:
        with open(input_file, 'r') as f:
            graph_data = json.load(f)
    except Exception as e:
        logger.error(f"Error loading graph data: {e}")
        return
    
    # Create graph
    G = nx.DiGraph()
    
    # Add nodes
    for node in graph_data.get('nodes', []):
        G.add_node(node['id'], label=node.get('label', node['id']), type=node.get('type', 'default'))
    
    # Add edges
    for edge in graph_data.get('edges', []):
        G.add_edge(edge['source'], edge['target'], 
                  type=edge.get('type', 'default'),
                  label=edge.get('label', ''))
    
    # Create visualization
    plt.figure(figsize=figsize)
    
    if title:
        plt.title(title, fontsize=16)
    
    # Use spring layout for better visualization
    pos = nx.spring_layout(G, k=0.3, iterations=50)
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=node_size, 
                          node_color='lightblue', alpha=0.8)
    
    # Draw edges with colors based on relationship type
    for edge_type, color in RELATIONSHIP_COLORS.items():
        edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('type') == edge_type]
        if edges:
            nx.draw_networkx_edges(G, pos, edgelist=edges, width=2, 
                                  edge_color=color, arrows=True)
    
    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=font_size, font_family='sans-serif')
    
    # Draw edge labels
    edge_labels = {(u, v): d.get('label', '') for u, v, d in G.edges(data=True) if d.get('label')}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
    
    # Add legend
    legend_elements = [plt.Line2D([0], [0], color=color, lw=4, label=rel_type) 
                      for rel_type, color in RELATIONSHIP_COLORS.items()]
    plt.legend(handles=legend_elements, loc='upper right')
    
    plt.axis('off')
    plt.tight_layout()
    
    # Save figure
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    logger.info(f"Enhanced graph visualization saved to {output_file}")
    plt.close()

def main():
    """Main function to parse arguments and execute commands."""
    parser = argparse.ArgumentParser(description='Visualization utilities for codebase analysis')
    
    # Add arguments
    parser.add_argument('--copy-visualizations', action='store_true', 
                        help='Copy visualization files from source to target directory')
    parser.add_argument('--source-dir', type=str, help='Source directory for visualizations')
    parser.add_argument('--target-dir', type=str, help='Target directory for visualizations')
    parser.add_argument('--file-pattern', type=str, default='*.png', 
                        help='File pattern to match (default: *.png)')
    
    parser.add_argument('--enhance-graph', action='store_true', 
                        help='Enhance an existing graph visualization')
    parser.add_argument('--input-file', type=str, help='Input graph file (JSON format)')
    parser.add_argument('--output-file', type=str, help='Output visualization file')
    parser.add_argument('--title', type=str, help='Graph title')
    parser.add_argument('--node-size', type=int, default=1500, help='Size of nodes')
    parser.add_argument('--font-size', type=int, default=10, help='Font size for labels')
    
    args = parser.parse_args()
    
    # Execute commands
    if args.copy_visualizations:
        if not args.source_dir or not args.target_dir:
            logger.error("Source and target directories are required for copy-visualizations")
            parser.print_help()
            return
        
        copy_visualizations(args.source_dir, args.target_dir, args.file_pattern)
    
    elif args.enhance_graph:
        if not args.input_file or not args.output_file:
            logger.error("Input and output files are required for enhance-graph")
            parser.print_help()
            return
        
        enhance_graph_visualization(args.input_file, args.output_file, 
                                   args.title, args.node_size, args.font_size)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
