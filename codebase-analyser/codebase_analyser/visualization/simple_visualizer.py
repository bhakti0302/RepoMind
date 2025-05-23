"""
Simple visualization utility for code chunk hierarchy and dependency relationships.

This module provides functionality to visualize code chunks and their relationships
using matplotlib, which doesn't require external dependencies.
"""

import os
import json
from typing import Dict, List, Optional, Set, Union, Any, Tuple
from pathlib import Path
import tempfile
import webbrowser

import networkx as nx

# Try to import matplotlib, but don't fail if it's not available
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None


class SimpleVisualizer:
    """Simple visualization utility for code chunks and their relationships."""

    def __init__(self, output_dir: Optional[str] = None):
        """Initialize the visualizer.

        Args:
            output_dir: Directory to save visualization outputs (default: temp directory)
        """
        self.output_dir = output_dir or tempfile.gettempdir()
        os.makedirs(self.output_dir, exist_ok=True)

        # Color schemes for different chunk types
        self.chunk_colors = {
            "file": "#4285F4",  # Google Blue
            "class_declaration": "#EA4335",  # Google Red
            "interface_declaration": "#FBBC05",  # Google Yellow
            "enum_declaration": "#34A853",  # Google Green
            "method_declaration": "#8AB4F8",  # Light Blue
            "constructor_declaration": "#F28B82",  # Light Red
            "field_declaration": "#FDD663",  # Light Yellow
            "package_declaration": "#CEEAD6",  # Light Green
            "import_declaration": "#D2E3FC",  # Very Light Blue
            "orphaned_method_declaration": "#FAD2CF",  # Very Light Red
            "default": "#9AA0A6"  # Gray
        }

        # Edge colors for different dependency types
        self.edge_colors = {
            "CONTAINS": "#4285F4",  # Blue
            "EXTENDS": "#EA4335",  # Red
            "IMPLEMENTS": "#FBBC05",  # Yellow
            "CALLS": "#34A853",  # Green
            "USES": "#8AB4F8",  # Light Blue
            "CREATES": "#F28B82",  # Light Red
            "IMPORTS": "#FDD663",  # Light Yellow
            "OVERRIDES": "#CEEAD6",  # Light Green
            "default": "#9AA0A6"  # Gray
        }

    def _get_chunk_color(self, chunk_type: str) -> str:
        """Get the color for a chunk type."""
        return self.chunk_colors.get(chunk_type, self.chunk_colors["default"])

    def _get_edge_color(self, edge_type: str) -> str:
        """Get the color for an edge type."""
        return self.edge_colors.get(edge_type, self.edge_colors["default"])

    def _create_graph_from_chunks(self, chunks: List['CodeChunk']) -> nx.DiGraph:
        """Create a NetworkX directed graph from code chunks."""
        G = nx.DiGraph()

        # Add nodes for each chunk
        for chunk in chunks:
            # Get all chunks (including descendants)
            all_chunks = [chunk] + chunk.get_descendants()

            for c in all_chunks:
                # Add node with attributes
                G.add_node(
                    c.node_id,
                    name=c.name or "",
                    qualified_name=c.qualified_name or "",
                    chunk_type=c.chunk_type,
                    start_line=c.start_line,
                    end_line=c.end_line,
                    file_path=c.file_path,
                    color=self._get_chunk_color(c.chunk_type)
                )

                # Add parent-child edges
                if c.parent:
                    G.add_edge(
                        c.parent.node_id,
                        c.node_id,
                        type="CONTAINS",
                        color=self._get_edge_color("CONTAINS"),
                        weight=1.0
                    )

        # Add dependency edges
        for chunk in chunks:
            all_chunks = [chunk] + chunk.get_descendants()

            for c in all_chunks:
                # Skip chunks without a dependency graph
                if 'dependency_graph' not in c.metadata:
                    continue

                # Add edges from the dependency graph
                dep_graph = c.metadata['dependency_graph']
                for edge in dep_graph.get('edges', []):
                    # Skip CONTAINS edges (already added above)
                    if edge.get('type') == 'CONTAINS':
                        continue

                    # Add the edge with attributes
                    G.add_edge(
                        edge.get('source_id'),
                        edge.get('target_id'),
                        type=edge.get('type'),
                        color=self._get_edge_color(edge.get('type')),
                        weight=edge.get('strength', 0.5),
                        description=edge.get('description', "")
                    )

        return G

    def visualize_hierarchy(
        self,
        chunks: List['CodeChunk'],
        output_file: Optional[str] = None,
        show: bool = True,
        figsize: Tuple[int, int] = (12, 8),
        include_dependencies: bool = True
    ) -> str:
        """Visualize code chunk hierarchy using matplotlib.

        Args:
            chunks: List of code chunks
            output_file: Path to save the visualization (default: temp file)
            show: Whether to show the visualization
            figsize: Figure size (width, height) in inches
            include_dependencies: Whether to include dependency relationships

        Returns:
            Path to the saved visualization
        """
        if not MATPLOTLIB_AVAILABLE:
            import logging
            logging.warning("Matplotlib is not available. Visualization will be skipped.")
            if output_file is None:
                output_file = os.path.join(self.output_dir, "code_visualization.png")
            return output_file

        G = self._create_graph_from_chunks(chunks)

        # Remove non-CONTAINS edges if dependencies are not included
        if not include_dependencies:
            edges_to_remove = [(u, v) for u, v, d in G.edges(data=True) if d.get('type') != 'CONTAINS']
            G.remove_edges_from(edges_to_remove)

        # Create the figure
        plt.figure(figsize=figsize)

        # Use spring layout (doesn't require external dependencies)
        pos = nx.spring_layout(G, k=0.3, iterations=50)

        # Draw nodes
        node_colors = [G.nodes[n]['color'] for n in G.nodes]
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, alpha=0.8, node_size=500)

        # Draw edges with different colors based on type
        edge_types = set(nx.get_edge_attributes(G, 'type').values())
        for edge_type in edge_types:
            edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('type') == edge_type]
            if edges:
                edge_color = self._get_edge_color(edge_type)
                nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color=edge_color,
                                      width=1.5, alpha=0.7, arrows=True,
                                      label=edge_type)

        # Draw labels
        labels = {n: G.nodes[n].get('name') or n.split(':')[-1] for n in G.nodes}
        nx.draw_networkx_labels(G, pos, labels=labels, font_size=8)

        # Add legend if dependencies are included
        if include_dependencies and edge_types:
            plt.legend(title="Relationship Types")

        # Set title and remove axis
        plt.title("Code Chunk Hierarchy and Dependencies")
        plt.axis('off')

        # Save the figure
        if output_file is None:
            output_file = os.path.join(self.output_dir, "code_visualization.png")

        plt.savefig(output_file, dpi=300, bbox_inches='tight')

        if show:
            plt.show()

        return output_file
