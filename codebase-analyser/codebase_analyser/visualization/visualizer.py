"""
Visualizer for code chunks and dependency graphs.
"""

import os
import logging
import networkx as nx
import matplotlib.pyplot as plt
from typing import List, Optional, Any, Union, Dict

logger = logging.getLogger(__name__)


class ChunkVisualizer:
    """Visualizer for code chunks and dependency graphs."""
    
    def __init__(self, output_dir: str = "samples"):
        """Initialize the visualizer.
        
        Args:
            output_dir: Directory to save visualization files
        """
        self.output_dir = output_dir
        
        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
    
    def visualize_hierarchy_matplotlib(
        self,
        chunks: List[Any],
        output_file: str,
        show: bool = False,
        figsize: tuple = (12, 8)
    ) -> None:
        """Visualize the chunk hierarchy using matplotlib.
        
        Args:
            chunks: List of CodeChunk objects
            output_file: Path to save the visualization
            show: Whether to show the visualization
            figsize: Figure size
        """
        # Create a directed graph
        graph = nx.DiGraph()
        
        # Add nodes to the graph
        for chunk in chunks:
            graph.add_node(
                chunk.node_id,
                type=chunk.chunk_type,
                name=chunk.name
            )
        
        # Add edges based on parent-child relationships
        for chunk in chunks:
            for child in chunk.children:
                graph.add_edge(
                    chunk.node_id,
                    child.node_id,
                    type='CONTAINS'
                )
        
        # Add edges based on references
        for chunk in chunks:
            for ref in chunk.references:
                graph.add_edge(
                    chunk.node_id,
                    ref.node_id,
                    type='REFERENCES'
                )
        
        # Create the figure
        plt.figure(figsize=figsize)
        
        # Create a layout for the graph
        pos = nx.spring_layout(graph, seed=42)
        
        # Draw the nodes
        nx.draw_networkx_nodes(
            graph,
            pos,
            node_size=1000,
            node_color='lightblue',
            alpha=0.8
        )
        
        # Draw the edges
        nx.draw_networkx_edges(
            graph,
            pos,
            width=1.0,
            alpha=0.5,
            edge_color='gray',
            arrows=True
        )
        
        # Draw the labels
        nx.draw_networkx_labels(
            graph,
            pos,
            labels={node: graph.nodes[node]['name'] for node in graph.nodes},
            font_size=8,
            font_family='sans-serif'
        )
        
        # Save the figure
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        
        # Show the figure if requested
        if show:
            plt.show()
        else:
            plt.close()
