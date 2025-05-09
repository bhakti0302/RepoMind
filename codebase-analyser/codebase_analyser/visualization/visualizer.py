"""
Visualization utility for code chunk hierarchy and dependency relationships.

This module provides functionality to visualize code chunks and their relationships
using various visualization libraries.
"""

import os
import json
from typing import Dict, List, Optional, Set, Union, Any, Tuple
from pathlib import Path
import tempfile
import webbrowser

import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

try:
    import graphviz
    GRAPHVIZ_AVAILABLE = True
except ImportError:
    GRAPHVIZ_AVAILABLE = False

try:
    import pydot
    PYDOT_AVAILABLE = True
except ImportError:
    PYDOT_AVAILABLE = False


class ChunkVisualizer:
    """Visualization utility for code chunks and their relationships."""

    def __init__(self, output_dir: Optional[str] = None):
        """Initialize the chunk visualizer.

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
        """Get the color for a chunk type.

        Args:
            chunk_type: The type of chunk

        Returns:
            Hex color code
        """
        return self.chunk_colors.get(chunk_type, self.chunk_colors["default"])

    def _get_edge_color(self, edge_type: str) -> str:
        """Get the color for an edge type.

        Args:
            edge_type: The type of edge/dependency

        Returns:
            Hex color code
        """
        return self.edge_colors.get(edge_type, self.edge_colors["default"])

    def _create_graph_from_chunks(self, chunks: List['CodeChunk']) -> nx.DiGraph:
        """Create a NetworkX directed graph from code chunks.

        Args:
            chunks: List of code chunks

        Returns:
            NetworkX directed graph
        """
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

    def visualize_hierarchy_matplotlib(
        self,
        chunks: List['CodeChunk'],
        output_file: Optional[str] = None,
        show: bool = True,
        figsize: Tuple[int, int] = (12, 8)
    ) -> str:
        """Visualize chunk hierarchy using matplotlib.

        Args:
            chunks: List of code chunks
            output_file: Path to save the visualization (default: temp file)
            show: Whether to show the visualization
            figsize: Figure size (width, height) in inches

        Returns:
            Path to the saved visualization
        """
        G = self._create_graph_from_chunks(chunks)

        # Create the figure
        plt.figure(figsize=figsize)

        # Use hierarchical layout
        pos = nx.nx_agraph.graphviz_layout(G, prog='dot') if PYDOT_AVAILABLE else nx.spring_layout(G)

        # Draw nodes
        node_colors = [G.nodes[n]['color'] for n in G.nodes]
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, alpha=0.8, node_size=500)

        # Draw edges
        edge_colors = [G.edges[e]['color'] for e in G.edges]
        nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=1.5, alpha=0.7, arrows=True)

        # Draw labels
        labels = {n: G.nodes[n].get('name') or n.split(':')[-1] for n in G.nodes}
        nx.draw_networkx_labels(G, pos, labels=labels, font_size=8)

        # Set title and remove axis
        plt.title("Code Chunk Hierarchy")
        plt.axis('off')

        # Save the figure
        if output_file is None:
            output_file = os.path.join(self.output_dir, "chunk_hierarchy.png")

        plt.savefig(output_file, dpi=300, bbox_inches='tight')

        if show:
            plt.show()

        return output_file

    def visualize_hierarchy_graphviz(
        self,
        chunks: List['CodeChunk'],
        output_file: Optional[str] = None,
        show: bool = True,
        format: str = "png"
    ) -> str:
        """Visualize chunk hierarchy using Graphviz.

        Args:
            chunks: List of code chunks
            output_file: Path to save the visualization (default: temp file)
            show: Whether to show the visualization
            format: Output format (png, svg, pdf)

        Returns:
            Path to the saved visualization
        """
        if not GRAPHVIZ_AVAILABLE:
            raise ImportError("Graphviz is not available. Please install it with 'pip install graphviz'.")

        # Create a Graphviz Digraph
        dot = graphviz.Digraph(
            comment="Code Chunk Hierarchy",
            format=format,
            engine="dot",
            graph_attr={'rankdir': 'TB', 'splines': 'ortho'}
        )

        # Add nodes and edges for each chunk
        for chunk in chunks:
            # Get all chunks (including descendants)
            all_chunks = [chunk] + chunk.get_descendants()

            # Add nodes
            for c in all_chunks:
                node_id = c.node_id
                label = f"{c.name or c.chunk_type}\n({c.start_line}-{c.end_line})"
                color = self._get_chunk_color(c.chunk_type)

                dot.node(
                    node_id,
                    label=label,
                    style="filled",
                    fillcolor=color,
                    fontcolor="white" if c.chunk_type in ["file", "class_declaration"] else "black"
                )

                # Add parent-child edges
                if c.parent:
                    dot.edge(
                        c.parent.node_id,
                        node_id,
                        color=self._get_edge_color("CONTAINS"),
                        style="solid"
                    )

        # Save the visualization
        if output_file is None:
            output_file = os.path.join(self.output_dir, f"chunk_hierarchy.{format}")

        # Remove extension from output_file for Graphviz
        output_base = os.path.splitext(output_file)[0]
        dot.render(output_base, cleanup=True)

        # The actual output file has the format extension
        actual_output = f"{output_base}.{format}"

        if show:
            # Open the file in the default viewer
            if os.path.exists(actual_output):
                webbrowser.open(f"file://{os.path.abspath(actual_output)}")

        return actual_output

    def visualize_dependencies_plotly(
        self,
        chunks: List['CodeChunk'],
        output_file: Optional[str] = None,
        show: bool = True,
        include_contains: bool = False
    ) -> str:
        """Visualize dependency relationships using Plotly.

        Args:
            chunks: List of code chunks
            output_file: Path to save the visualization (default: temp file)
            show: Whether to show the visualization
            include_contains: Whether to include CONTAINS relationships

        Returns:
            Path to the saved visualization
        """
        G = self._create_graph_from_chunks(chunks)

        # Remove CONTAINS edges if not included
        if not include_contains:
            edges_to_remove = [(u, v) for u, v, d in G.edges(data=True) if d.get('type') == 'CONTAINS']
            G.remove_edges_from(edges_to_remove)

        # Use hierarchical layout
        pos = nx.nx_agraph.graphviz_layout(G, prog='dot') if PYDOT_AVAILABLE else nx.spring_layout(G)

        # Create edge traces by dependency type
        edge_traces = {}
        for u, v, data in G.edges(data=True):
            edge_type = data.get('type', 'default')
            x0, y0 = pos[u]
            x1, y1 = pos[v]

            if edge_type not in edge_traces:
                edge_traces[edge_type] = go.Scatter(
                    x=[],
                    y=[],
                    line=dict(width=1.5, color=self._get_edge_color(edge_type)),
                    hoverinfo='text',
                    mode='lines',
                    name=edge_type,
                    text=[]
                )

            edge_traces[edge_type].x += [x0, x1, None]
            edge_traces[edge_type].y += [y0, y1, None]
            edge_traces[edge_type].text.append(data.get('description', f"{edge_type} relationship"))

        # Create node trace
        node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode='markers+text',
            textposition='top center',
            hoverinfo='text',
            marker=dict(
                showscale=False,
                color=[],
                size=15,
                line=dict(width=2, color='white')
            )
        )

        # Add node positions and attributes
        for node in G.nodes():
            x, y = pos[node]
            node_trace.x += [x]
            node_trace.y += [y]

            node_data = G.nodes[node]
            node_name = node_data.get('name') or node.split(':')[-1]
            node_type = node_data.get('chunk_type', 'unknown')

            # Add node text and hover info
            node_trace.text += [node_name]
            node_trace.marker.color += [self._get_chunk_color(node_type)]

            # Add hover text
            hover_text = f"Name: {node_name}<br>"
            hover_text += f"Type: {node_type}<br>"
            hover_text += f"Lines: {node_data.get('start_line')}-{node_data.get('end_line')}<br>"
            hover_text += f"File: {node_data.get('file_path', '').split('/')[-1]}"

            if hasattr(node_trace, 'hovertext'):
                node_trace.hovertext += [hover_text]
            else:
                node_trace.hovertext = [hover_text]

        # Create figure
        fig = go.Figure(
            data=[node_trace] + list(edge_traces.values()),
            layout=go.Layout(
                title='Code Dependency Graph',
                showlegend=True,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                height=800,
                legend=dict(
                    title='Dependency Types',
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01
                )
            )
        )

        # Save the figure
        if output_file is None:
            output_file = os.path.join(self.output_dir, "dependency_graph.html")

        fig.write_html(output_file)

        if show:
            # Open the file in the default browser
            webbrowser.open(f"file://{os.path.abspath(output_file)}")

        return output_file

    def generate_html_report(
        self,
        chunks: List['CodeChunk'],
        output_file: Optional[str] = None,
        show: bool = True
    ) -> str:
        """Generate a comprehensive HTML report of the code structure.

        Args:
            chunks: List of code chunks
            output_file: Path to save the report (default: temp file)
            show: Whether to show the report

        Returns:
            Path to the saved report
        """
        if output_file is None:
            output_file = os.path.join(self.output_dir, "code_structure_report.html")

        # Generate visualizations
        try:
            hierarchy_img = self.visualize_hierarchy_graphviz(
                chunks,
                os.path.join(self.output_dir, "hierarchy.svg"),
                show=False,
                format="svg"
            )
            has_hierarchy = True
        except (ImportError, FileNotFoundError):
            # Graphviz not available
            hierarchy_img = None
            has_hierarchy = False

        dependency_html = self.visualize_dependencies_plotly(
            chunks,
            os.path.join(self.output_dir, "dependencies.html"),
            show=False
        )

        # Extract dependency graph metrics
        metrics = {}
        for chunk in chunks:
            if chunk.chunk_type == 'file' and 'dependency_graph' in chunk.metadata:
                metrics = chunk.metadata['dependency_graph'].get('metrics', {})
                break

        # Generate HTML content
        total_chunks = sum(1 + len(chunk.get_descendants()) for chunk in chunks)
        coupling_score = metrics.get('coupling_score', 0)
        cohesion_score = metrics.get('cohesion_score', 0)
        dependency_depth = metrics.get('dependency_depth', 0)

        # Build HTML content in parts to avoid complex f-strings
        html_head = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Code Structure Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
                h1, h2, h3 { color: #4285F4; }
                .container { max-width: 1200px; margin: 0 auto; }
                .section { margin-bottom: 30px; }
                .metrics { display: flex; flex-wrap: wrap; }
                .metric-card {
                    background-color: #f5f5f5;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 10px;
                    flex: 1 1 200px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }
                .metric-value {
                    font-size: 24px;
                    font-weight: bold;
                    color: #EA4335;
                }
                .chunk-list {
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    overflow: hidden;
                }
                .chunk-list table {
                    width: 100%;
                    border-collapse: collapse;
                }
                .chunk-list th {
                    background-color: #4285F4;
                    color: white;
                    text-align: left;
                    padding: 12px;
                }
                .chunk-list td {
                    padding: 10px;
                    border-top: 1px solid #ddd;
                }
                .chunk-list tr:nth-child(even) {
                    background-color: #f9f9f9;
                }
                .visualization {
                    margin: 20px 0;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    overflow: hidden;
                }
                iframe {
                    width: 100%;
                    height: 600px;
                    border: none;
                }
                .tabs {
                    display: flex;
                    border-bottom: 1px solid #ddd;
                }
                .tab {
                    padding: 10px 20px;
                    cursor: pointer;
                    background-color: #f1f1f1;
                }
                .tab.active {
                    background-color: white;
                    border-bottom: 3px solid #4285F4;
                }
                .tab-content {
                    display: none;
                    padding: 20px;
                }
                .tab-content.active {
                    display: block;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Code Structure Report</h1>
        """

        # Overview section
        overview_section = f"""
                <div class="section">
                    <h2>Overview</h2>
                    <div class="metrics">
                        <div class="metric-card">
                            <h3>Total Chunks</h3>
                            <div class="metric-value">{total_chunks}</div>
                        </div>
                        <div class="metric-card">
                            <h3>Coupling Score</h3>
                            <div class="metric-value">{coupling_score:.2f}</div>
                        </div>
                        <div class="metric-card">
                            <h3>Cohesion Score</h3>
                            <div class="metric-value">{cohesion_score:.2f}</div>
                        </div>
                        <div class="metric-card">
                            <h3>Dependency Depth</h3>
                            <div class="metric-value">{dependency_depth}</div>
                        </div>
                    </div>
                </div>
        """

        # Visualization section
        vis_section_start = """
                <div class="section">
                    <h2>Visualizations</h2>
                    <div class="tabs">
        """

        # Add tabs based on available visualizations
        vis_tabs = ""
        if has_hierarchy:
            vis_tabs += '<div class="tab active" onclick="openTab(event, \'hierarchy\')">Hierarchy</div>'

        vis_tabs += f'<div class="tab{" active" if not has_hierarchy else ""}" onclick="openTab(event, \'dependencies\')">Dependencies</div>'

        vis_section_middle = """
                    </div>
        """

        # Add visualization content
        vis_content = ""
        if has_hierarchy:
            vis_content += f"""
                    <div id="hierarchy" class="tab-content active">
                        <div class="visualization">
                            <img src="{os.path.basename(hierarchy_img)}" alt="Hierarchy Visualization" style="width:100%;">
                        </div>
                    </div>
            """

        vis_content += f"""
                    <div id="dependencies" class="tab-content{' active' if not has_hierarchy else ''}">
                        <div class="visualization">
                            <iframe src="{os.path.basename(dependency_html)}"></iframe>
                        </div>
                    </div>
                </div>
        """

        # Chunk list section start
        chunk_list_start = """
                <div class="section">
                    <h2>Chunk List</h2>
                    <div class="chunk-list">
                        <table>
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Type</th>
                                    <th>Lines</th>
                                    <th>Fan-In</th>
                                    <th>Fan-Out</th>
                                </tr>
                            </thead>
                            <tbody>
        """

        # Combine all parts
        html_content = html_head + overview_section + vis_section_start + vis_tabs + vis_section_middle + vis_content + chunk_list_start

        # Add rows for each chunk
        for chunk in chunks:
            all_chunks = [chunk] + chunk.get_descendants()
            for c in all_chunks:
                metrics = c.metadata.get('dependency_metrics', {})
                fan_in = metrics.get('fan_in', 0)
                fan_out = metrics.get('fan_out', 0)

                html_content += f"""
                <tr>
                    <td>{c.name or c.chunk_type}</td>
                    <td>{c.chunk_type}</td>
                    <td>{c.start_line}-{c.end_line}</td>
                    <td>{fan_in}</td>
                    <td>{fan_out}</td>
                </tr>
                """

        html_content += """
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <script>
                function openTab(evt, tabName) {
                    var i, tabcontent, tablinks;

                    // Hide all tab content
                    tabcontent = document.getElementsByClassName("tab-content");
                    for (i = 0; i < tabcontent.length; i++) {
                        tabcontent[i].className = tabcontent[i].className.replace(" active", "");
                    }

                    // Remove active class from all tabs
                    tablinks = document.getElementsByClassName("tab");
                    for (i = 0; i < tablinks.length; i++) {
                        tablinks[i].className = tablinks[i].className.replace(" active", "");
                    }

                    // Show the current tab and add active class
                    document.getElementById(tabName).className += " active";
                    evt.currentTarget.className += " active";
                }
            </script>
        </body>
        </html>
        """

        # Write the HTML file
        with open(output_file, 'w') as f:
            f.write(html_content)

        if show:
            # Open the file in the default browser
            webbrowser.open(f"file://{os.path.abspath(output_file)}")

        return output_file
