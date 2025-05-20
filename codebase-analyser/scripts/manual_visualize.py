#!/usr/bin/env python3
"""
Manual visualization script for generating code relationship visualizations.
This script is called by the VS Code extension to generate visualizations.
"""

import os
import sys
import argparse
import json
import time
import logging
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import networkx as nx
import matplotlib.pyplot as plt

# Add the parent directory to the path so we can import the codebase_analyser package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from codebase_analyser.database.unified_storage import UnifiedStorage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Define colors for different relationship types
RELATIONSHIP_COLORS = {
    "IMPORTS": "#4CAF50",     # Green
    "EXTENDS": "#F44336",     # Red
    "IMPLEMENTS": "#9C27B0",  # Purple
    "CALLS": "#FF9800",       # Orange
    "USES": "#2196F3",        # Blue
    "CONTAINS": "#607D8B",    # Gray
    "HAS_FIELD": "#00BCD4",   # Cyan
    "DEFAULT": "#9E9E9E"      # Light Gray
}

# Define node colors based on type
NODE_COLORS = {
    "class_declaration": "#FFC107",      # Amber
    "interface_declaration": "#3F51B5",  # Indigo
    "method_declaration": "#8BC34A",     # Light Green
    "field_declaration": "#00BCD4",      # Cyan
    "import_declaration": "#9E9E9E",     # Gray
    "file": "#795548",                   # Brown
    "DEFAULT": "#9E9E9E"                 # Light Gray
}

def hierarchical_layout(G, root=None, width=1.0, height=1.0, iterations=50):
    """Create a hierarchical layout for a directed graph."""
    # If the graph is empty, return an empty layout
    if len(G) == 0:
        return {}

    # Convert to directed graph if it's not already
    if not isinstance(G, nx.DiGraph):
        G = nx.DiGraph(G)

    # Find root nodes (nodes with no incoming edges or with only self-loops)
    if root is None:
        roots = [n for n in G.nodes() if G.in_degree(n) == 0 or
                 (G.in_degree(n) == 1 and n in G.predecessors(n))]

        # If no root nodes found, use nodes with the lowest in-degree
        if not roots:
            min_in_degree = min(G.in_degree(n) for n in G.nodes())
            roots = [n for n in G.nodes() if G.in_degree(n) == min_in_degree]

        # If still no roots, just use the first node
        if not roots:
            roots = [list(G.nodes())[0]]
    else:
        roots = [root]

    # Create a tree from the graph
    tree = nx.bfs_tree(G.to_undirected(), roots[0])

    # Get the depth of each node
    depths = nx.single_source_shortest_path_length(tree, roots[0])

    # Group nodes by depth
    nodes_by_depth = {}
    for node, depth in depths.items():
        if depth not in nodes_by_depth:
            nodes_by_depth[depth] = []
        nodes_by_depth[depth].append(node)

    # Calculate positions
    max_depth = max(depths.values())
    pos = {}

    for depth, nodes in nodes_by_depth.items():
        # Calculate y-coordinate based on depth
        y = height * (1 - depth / (max_depth + 1))

        # Calculate x-coordinates to spread nodes evenly
        n_nodes = len(nodes)
        for i, node in enumerate(nodes):
            if n_nodes == 1:
                x = width / 2
            else:
                x = width * i / (n_nodes - 1) if n_nodes > 1 else width / 2
            pos[node] = (x, y)

    # Add any remaining nodes not reached by BFS
    remaining_nodes = set(G.nodes()) - set(pos.keys())
    if remaining_nodes:
        # Place them at the bottom
        y = 0
        n_nodes = len(remaining_nodes)
        for i, node in enumerate(remaining_nodes):
            x = width * i / (n_nodes - 1) if n_nodes > 1 else width / 2
            pos[node] = (x, y)

    # Refine the layout with iterations of spring layout
    if iterations > 0:
        # Use the calculated positions as initial positions for spring layout
        pos = nx.spring_layout(G, pos=pos, fixed=roots, iterations=iterations, k=0.2)

    return pos

def visualize_graph(G, output_file, title):
    """Visualize the graph with better relationship highlighting."""
    logger.info(f"Visualizing graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")

    # Create figure
    plt.figure(figsize=(16, 12))
    plt.title(title, fontsize=16)

    # Use a hierarchical layout for better visualization
    try:
        # Try to use graphviz for a hierarchical layout
        try:
            import pygraphviz
            pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
        except ImportError:
            # If pygraphviz is not available, try using pydot
            try:
                import pydot
                pos = nx.nx_pydot.graphviz_layout(G, prog='dot')
            except ImportError:
                # If both fail, use a custom hierarchical layout
                pos = hierarchical_layout(G)
    except Exception as e:
        logger.warning(f"Failed to use hierarchical layout: {e}")
        # Fall back to spring layout if hierarchical layout fails
        pos = nx.spring_layout(G, k=0.3, iterations=50, seed=42)

    # Draw nodes with different colors based on type
    node_colors = [NODE_COLORS.get(G.nodes[n].get('type', 'DEFAULT'), NODE_COLORS['DEFAULT']) for n in G.nodes]
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, alpha=0.8, node_size=700)

    # Draw edges with different colors based on type
    edge_types = set(nx.get_edge_attributes(G, 'type').values())

    for edge_type in edge_types:
        edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('type') == edge_type]
        if edges:
            edge_color = RELATIONSHIP_COLORS.get(edge_type, RELATIONSHIP_COLORS['DEFAULT'])
            edge_width = 2.0 if edge_type in ['EXTENDS', 'IMPLEMENTS', 'IMPORTS'] else 1.5
            edge_style = '-' if edge_type != 'IMPLEMENTS' else '--'

            nx.draw_networkx_edges(
                G, pos,
                edgelist=edges,
                edge_color=edge_color,
                width=edge_width,
                alpha=0.7,
                arrows=True,
                arrowstyle='-|>',
                connectionstyle='arc3,rad=0.1',
                style=edge_style
            )

    # Draw labels with better formatting
    labels = {}
    for node in G.nodes:
        node_type = G.nodes[node].get('type', '')
        node_name = G.nodes[node].get('name', node)

        # Format label based on node type
        if node_type == 'class_declaration':
            labels[node] = f"Class: {node_name}"
        elif node_type == 'interface_declaration':
            labels[node] = f"Interface: {node_name}"
        elif node_type == 'method_declaration':
            labels[node] = f"Method: {node_name}"
        elif node_type == 'field_declaration':
            labels[node] = f"Field: {node_name}"
        elif node_type == 'file':
            labels[node] = f"File: {node_name}"
        else:
            labels[node] = node_name

    nx.draw_networkx_labels(G, pos, labels=labels, font_size=10, font_weight='bold')

    # Add legend for relationship types
    legend_elements = []
    import matplotlib.patches as mpatches
    import matplotlib.lines as mlines

    # Node type legend
    for node_type, color in NODE_COLORS.items():
        if node_type != 'DEFAULT' and any(G.nodes[n].get('type') == node_type for n in G.nodes):
            legend_elements.append(
                mpatches.Patch(color=color, alpha=0.8, label=f"{node_type.replace('_declaration', '').capitalize()}")
            )

    # Edge type legend
    for edge_type, color in RELATIONSHIP_COLORS.items():
        if edge_type != 'DEFAULT' and edge_type in edge_types:
            style = '--' if edge_type == 'IMPLEMENTS' else '-'
            legend_elements.append(
                mlines.Line2D([0], [0], color=color, lw=2, label=edge_type.capitalize(), linestyle=style)
            )

    plt.legend(handles=legend_elements, loc='upper right', title="Legend")

    # Remove axis
    plt.axis('off')

    # Save the figure
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    logger.info(f"Saved visualization to {output_file}")

    # Return the path to the visualization
    return output_file

def generate_visualizations(output_dir, project_id, db_path=".lancedb"):
    """
    Generate all visualizations for a project and save them to the output directory.

    Args:
        output_dir (str): Directory to save visualizations
        project_id (str): Project ID to generate visualizations for
        db_path (str): Path to the database

    Returns:
        dict: Dictionary with paths to generated visualizations
    """
    # Import the generic diagrams generator
    from generate_generic_diagrams import generate_class_diagram
    # Create output directory if it doesn't exist
    try:
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Output directory created/verified: {output_dir}")
    except Exception as e:
        logger.error(f"Error creating output directory: {e}")
        return {"error": f"Error creating output directory: {str(e)}"}

    # Check if database exists
    if not os.path.exists(db_path):
        logger.error(f"Database path does not exist: {db_path}")
        return {"error": f"Database path does not exist: {db_path}"}

    # Initialize the database
    try:
        storage = UnifiedStorage(db_path=db_path)
        logger.info(f"Database initialized: {db_path}")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return {"error": f"Error initializing database: {str(e)}"}

    # Check if the project exists in the database by checking if there are any chunks for this project
    try:
        # Get all chunks from the database
        table = storage.db_manager.get_code_chunks_table()
        chunks_df = table.to_pandas()
        project_chunks = chunks_df[chunks_df['project_id'] == project_id]

        logger.info(f"Found {len(project_chunks)} chunks for project {project_id}")

        # Check if there are any chunks for this project
        if len(project_chunks) == 0:
            logger.error(f"No chunks found for project: {project_id}")
            return {"error": f"No chunks found for project: {project_id}. Please sync the codebase first."}
    except Exception as e:
        logger.error(f"Error checking if project exists: {e}")
        return {"error": f"Error checking if project exists: {str(e)}"}

    # Generate timestamp for unique filenames
    timestamp = time.strftime("%Y%m%d%H%M%S")
    logger.info(f"Using timestamp: {timestamp}")

    # Dictionary to store paths to generated visualizations
    visualization_paths = {}

    try:
        # Build the graph from the database
        logger.info(f"Building graph for project: {project_id}")
        graph = storage._build_graph_from_dependencies()

        # Suppress stdout during graph building to avoid contaminating JSON output
        sys.stdout = open(os.devnull, 'w')

        # Get all chunks from the database
        table = storage.db_manager.get_code_chunks_table()
        chunks_df = table.to_pandas()
        project_chunks = chunks_df[chunks_df['project_id'] == project_id]

        logger.info(f"Found {len(project_chunks)} chunks for project {project_id}")

        # Get node IDs from the project chunks
        project_nodes = project_chunks['node_id'].tolist()
        logger.info(f"Found {len(project_nodes)} nodes for project {project_id}")

        # Add nodes that might be missing from the graph
        for _, chunk in project_chunks.iterrows():
            if chunk['node_id'] not in graph:
                graph.add_node(
                    chunk['node_id'],
                    type=chunk['chunk_type'],
                    name=chunk['name'],
                    qualified_name=chunk['qualified_name'],
                    project_id=chunk['project_id']
                )

        # Create a subgraph with only the project nodes
        project_graph = graph.subgraph(project_nodes)

        # Generate multi-file relationships visualization
        try:
            multi_file_path = os.path.join(output_dir, f"{project_id}_multi_file_relationships_{timestamp}.png")
            visualize_graph(
                project_graph,
                multi_file_path,
                f"Multi-File Relationships - {project_id}"
            )
            visualization_paths['multi_file_relationships'] = multi_file_path
            logger.info(f"Generated multi-file relationships visualization: {multi_file_path}")
        except Exception as e:
            logger.error(f"Error generating multi-file relationships visualization: {e}")

        # Create a relationship types graph
        relationship_types_graph = nx.DiGraph()

        # Add nodes and edges from the project graph
        for node, attrs in project_graph.nodes(data=True):
            # Skip file nodes
            if attrs.get('type') != 'file':
                relationship_types_graph.add_node(node, **attrs)

        # Add edges
        for u, v, attrs in project_graph.edges(data=True):
            # Skip edges involving file nodes
            if (project_graph.nodes[u].get('type') != 'file' and
                project_graph.nodes[v].get('type') != 'file'):
                relationship_types_graph.add_edge(u, v, **attrs)

        # Generate relationship types visualization
        try:
            relationship_types_path = os.path.join(output_dir, f"{project_id}_relationship_types_{timestamp}.png")
            visualize_graph(
                relationship_types_graph,
                relationship_types_path,
                f"Different Types of Relationships - {project_id}"
            )
            visualization_paths['relationship_types'] = relationship_types_path
            logger.info(f"Generated relationship types visualization: {relationship_types_path}")
        except Exception as e:
            logger.error(f"Error generating relationship types visualization: {e}")

        # Generate class diagram using the generic diagram generator
        try:
            class_diagram_path = os.path.join(output_dir, f"{project_id}_class_diagram_{timestamp}.png")
            # Create a class diagram graph (only class and interface nodes)
            class_diagram_graph = nx.DiGraph()

            # Add class and interface nodes
            for node, attrs in project_graph.nodes(data=True):
                if attrs.get('type') in ['class_declaration', 'interface_declaration']:
                    class_diagram_graph.add_node(node, **attrs)

            # Add edges between classes and interfaces
            for u, v, attrs in project_graph.edges(data=True):
                if (project_graph.nodes[u].get('type') in ['class_declaration', 'interface_declaration'] and
                    project_graph.nodes[v].get('type') in ['class_declaration', 'interface_declaration']):
                    class_diagram_graph.add_edge(u, v, **attrs)

            # Use the generic class diagram generator
            generate_class_diagram(
                class_diagram_graph,
                class_diagram_path,
                project_id
            )
            visualization_paths['class_diagram'] = class_diagram_path
            logger.info(f"Generated generic class diagram: {class_diagram_path}")
        except Exception as e:
            logger.error(f"Error generating class diagram: {e}")

        # Generate package diagram
        try:
            package_diagram_path = os.path.join(output_dir, f"{project_id}_package_diagram_{timestamp}.png")
            # Create a package diagram graph (file nodes and their relationships)
            package_diagram_graph = nx.DiGraph()

            # Add file nodes
            for node, attrs in project_graph.nodes(data=True):
                if attrs.get('type') == 'file':
                    package_diagram_graph.add_node(node, **attrs)

            # Add edges between files
            for u, v, attrs in project_graph.edges(data=True):
                if (project_graph.nodes[u].get('type') == 'file' and
                    project_graph.nodes[v].get('type') == 'file'):
                    package_diagram_graph.add_edge(u, v, **attrs)

            visualize_graph(
                package_diagram_graph,
                package_diagram_path,
                f"Package Diagram - {project_id}"
            )
            visualization_paths['package_diagram'] = package_diagram_path
            logger.info(f"Generated package diagram: {package_diagram_path}")
        except Exception as e:
            logger.error(f"Error generating package diagram: {e}")

        # Generate dependency graph
        try:
            dependency_graph_path = os.path.join(output_dir, f"{project_id}_dependency_graph_{timestamp}.png")
            # Create a dependency graph (all nodes with import relationships)
            dependency_graph = nx.DiGraph()

            # Add all nodes
            for node, attrs in project_graph.nodes(data=True):
                dependency_graph.add_node(node, **attrs)

            # Add import edges
            for u, v, attrs in project_graph.edges(data=True):
                if attrs.get('type') == 'IMPORTS':
                    dependency_graph.add_edge(u, v, **attrs)

            visualize_graph(
                dependency_graph,
                dependency_graph_path,
                f"Dependency Graph - {project_id}"
            )
            visualization_paths['dependency_graph'] = dependency_graph_path
            logger.info(f"Generated dependency graph: {dependency_graph_path}")
        except Exception as e:
            logger.error(f"Error generating dependency graph: {e}")

        # Generate inheritance hierarchy
        try:
            inheritance_hierarchy_path = os.path.join(output_dir, f"{project_id}_inheritance_hierarchy_{timestamp}.png")
            # Create an inheritance hierarchy graph (class nodes with extends/implements relationships)
            inheritance_graph = nx.DiGraph()

            # Add class and interface nodes
            for node, attrs in project_graph.nodes(data=True):
                if attrs.get('type') in ['class_declaration', 'interface_declaration']:
                    inheritance_graph.add_node(node, **attrs)

            # Add extends and implements edges
            for u, v, attrs in project_graph.edges(data=True):
                if (project_graph.nodes[u].get('type') in ['class_declaration', 'interface_declaration'] and
                    project_graph.nodes[v].get('type') in ['class_declaration', 'interface_declaration'] and
                    attrs.get('type') in ['EXTENDS', 'IMPLEMENTS']):
                    inheritance_graph.add_edge(u, v, **attrs)

            visualize_graph(
                inheritance_graph,
                inheritance_hierarchy_path,
                f"Inheritance Hierarchy - {project_id}"
            )
            visualization_paths['inheritance_hierarchy'] = inheritance_hierarchy_path
            logger.info(f"Generated inheritance hierarchy: {inheritance_hierarchy_path}")
        except Exception as e:
            logger.error(f"Error generating inheritance hierarchy: {e}")

    except Exception as e:
        logger.error(f"Error generating visualizations: {e}")

    finally:
        # Close the database connection
        storage.close()

        # Restore stdout
        sys.stdout = sys.__stdout__

    return visualization_paths

def test_visualizations(output_dir, project_id):
    """
    Test function to verify that visualizations can be generated.

    Args:
        output_dir (str): Directory to save test visualizations
        project_id (str): Project ID to test with

    Returns:
        bool: True if test passed, False otherwise
    """
    logger.info(f"Testing visualization generation for project: {project_id}")

    try:
        # Generate visualizations
        visualization_paths = generate_visualizations(output_dir, project_id)

        # Check if any visualizations were generated
        if not visualization_paths:
            logger.error("No visualizations were generated")
            return False

        # Check if the visualization files exist
        for viz_type, path in visualization_paths.items():
            if not os.path.exists(path):
                logger.error(f"{viz_type} visualization file does not exist: {path}")
                return False

            # Check if the file is a valid image
            if os.path.getsize(path) == 0:
                logger.error(f"{viz_type} visualization file is empty: {path}")
                return False

        logger.info("Visualization test passed successfully")
        return True

    except Exception as e:
        logger.error(f"Error testing visualizations: {e}")
        return False

def main():
    """Main function to parse arguments and generate visualizations."""
    parser = argparse.ArgumentParser(description='Generate code relationship visualizations')
    parser.add_argument('--output-dir', required=True, help='Directory to save visualizations')
    parser.add_argument('--project-id', required=True, help='Project ID to generate visualizations for')
    parser.add_argument('--db-path', default='.lancedb', help='Path to the database')
    parser.add_argument('--test', action='store_true', help='Run test mode')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')

    args = parser.parse_args()

    # Set logging level based on debug flag
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")

        # Log all arguments
        logger.debug(f"Arguments: {args}")
        logger.debug(f"Output directory: {args.output_dir}")
        logger.debug(f"Project ID: {args.project_id}")
        logger.debug(f"Database path: {args.db_path}")
        logger.debug(f"Test mode: {args.test}")

    if args.test:
        # Run test mode
        success = test_visualizations(args.output_dir, args.project_id)
        if success:
            result = {"status": "success", "message": "Test passed successfully"}
            print(json.dumps(result))
            logger.info(f"Test result: {result}")
        else:
            result = {"status": "error", "message": "Test failed"}
            print(json.dumps(result))
            logger.error(f"Test result: {result}")
    else:
        # Generate visualizations
        logger.info(f"Generating visualizations for project {args.project_id} in directory {args.output_dir}")
        visualization_paths = generate_visualizations(args.output_dir, args.project_id, args.db_path)

        # Log the visualization paths
        logger.info(f"Generated visualizations: {visualization_paths}")

        # Print the visualization paths as JSON
        result = json.dumps(visualization_paths, indent=2)
        print(result)
        logger.debug(f"JSON output: {result}")

if __name__ == '__main__':
    main()
