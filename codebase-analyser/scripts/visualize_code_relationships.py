#!/usr/bin/env python3
"""
Visualize code relationships for a Java project.

This script analyzes a Java project and generates visualizations of the code relationships.
It can be called from the VS Code extension to provide enhanced visualizations.

Usage:
    python visualize_code_relationships.py --repo-path <path_to_repo> --output-dir <path_to_output_dir> --project-id <project_id>
"""

import os
import sys
import json
import argparse
import logging
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from codebase_analyser import CodebaseAnalyser
from codebase_analyser.parsing.dependency_analyzer import DependencyAnalyzer

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
    "FIELD_TYPE": "#00BCD4",  # Cyan
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

def analyze_project(repo_path):
    """Analyze a Java project and return the code chunks and dependency graph.

    Args:
        repo_path: Path to the Java repository

    Returns:
        Tuple of (chunks, dependency_graph)
    """
    logger.info(f"Analyzing project: {repo_path}")

    # Parse the repository
    analyser = CodebaseAnalyser(repo_path=repo_path)
    chunks = analyser.parse()

    if not chunks:
        logger.error("No chunks found in the repository")
        return None, None

    logger.info(f"Found {len(chunks)} chunks in the repository")

    # Analyze dependencies
    dependency_analyzer = DependencyAnalyzer()
    dependency_graph = dependency_analyzer.analyze_dependencies(chunks)

    return chunks, dependency_graph

def create_sample_data(project_id):
    """Create sample data for visualization when no chunks are found.

    Args:
        project_id: Project ID to use in the sample data

    Returns:
        Tuple of (chunks, dependency_graph)
    """
    logger.info("Creating sample data for visualization")

    # Create a dependency graph
    from codebase_analyser.parsing.dependency_analyzer import DependencyGraph
    from codebase_analyser.parsing.dependency_types import DependencyType, Dependency
    from codebase_analyser.chunking.code_chunk import CodeChunk

    # Create a dependency graph
    dependency_graph = DependencyGraph()

    # Create sample chunks
    chunks = []

    # Entity interface
    entity_chunk = CodeChunk(
        chunk_type="interface_declaration",
        name="Entity",
        content="public interface Entity { String getId(); boolean isValid(); }",
        node_id="interface:Entity",
        qualified_name="com.example.Entity",
        file_path=f"{project_id}/Entity.java",
        start_line=1,
        end_line=3,
        language="java"
    )
    # Add context manually
    entity_chunk.context = {
        "file_path": f"{project_id}/Entity.java",
        "package": "com.example",
        "methods": [
            {"name": "getId", "return_type": "String"},
            {"name": "isValid", "return_type": "boolean"}
        ]
    }
    chunks.append(entity_chunk)

    # AbstractEntity class
    abstract_entity_chunk = CodeChunk(
        chunk_type="class_declaration",
        name="AbstractEntity",
        content="public abstract class AbstractEntity implements Entity { ... }",
        node_id="class:AbstractEntity",
        qualified_name="com.example.AbstractEntity",
        file_path=f"{project_id}/AbstractEntity.java",
        start_line=1,
        end_line=10,
        language="java"
    )
    # Add context manually
    abstract_entity_chunk.context = {
        "file_path": f"{project_id}/AbstractEntity.java",
        "package": "com.example",
        "implements": ["Entity"],
        "methods": [
            {"name": "getId", "return_type": "String"},
            {"name": "isValid", "return_type": "boolean"}
        ],
        "fields": [
            {"name": "id", "type": "String"},
            {"name": "valid", "type": "boolean"}
        ]
    }
    chunks.append(abstract_entity_chunk)

    # User class
    user_chunk = CodeChunk(
        chunk_type="class_declaration",
        name="User",
        content="public class User extends AbstractEntity { ... }",
        node_id="class:User",
        qualified_name="com.example.User",
        file_path=f"{project_id}/User.java",
        start_line=1,
        end_line=15,
        language="java"
    )
    # Add context manually
    user_chunk.context = {
        "file_path": f"{project_id}/User.java",
        "package": "com.example",
        "extends": "AbstractEntity",
        "methods": [
            {"name": "getUsername", "return_type": "String"},
            {"name": "getEmail", "return_type": "String"},
            {"name": "addOrder", "return_type": "void"}
        ],
        "fields": [
            {"name": "username", "type": "String"},
            {"name": "email", "type": "String"},
            {"name": "orders", "type": "List<Order>"},
            {"name": "address", "type": "Address"}
        ]
    }
    chunks.append(user_chunk)

    # Order class
    order_chunk = CodeChunk(
        chunk_type="class_declaration",
        name="Order",
        content="public class Order extends AbstractEntity { ... }",
        node_id="class:Order",
        qualified_name="com.example.Order",
        file_path=f"{project_id}/Order.java",
        start_line=1,
        end_line=15,
        language="java"
    )
    # Add context manually
    order_chunk.context = {
        "file_path": f"{project_id}/Order.java",
        "package": "com.example",
        "extends": "AbstractEntity",
        "methods": [
            {"name": "getOrderNumber", "return_type": "String"},
            {"name": "getOrderDate", "return_type": "Date"},
            {"name": "getTotalAmount", "return_type": "double"},
            {"name": "getUser", "return_type": "User"}
        ],
        "fields": [
            {"name": "orderNumber", "type": "String"},
            {"name": "orderDate", "type": "Date"},
            {"name": "totalAmount", "type": "double"},
            {"name": "user", "type": "User"}
        ]
    }
    chunks.append(order_chunk)

    # Address class
    address_chunk = CodeChunk(
        chunk_type="class_declaration",
        name="Address",
        content="public class Address { ... }",
        node_id="class:Address",
        qualified_name="com.example.Address",
        file_path=f"{project_id}/Address.java",
        start_line=1,
        end_line=15,
        language="java"
    )
    # Add context manually
    address_chunk.context = {
        "file_path": f"{project_id}/Address.java",
        "package": "com.example",
        "methods": [
            {"name": "getStreet", "return_type": "String"},
            {"name": "getCity", "return_type": "String"},
            {"name": "getState", "return_type": "String"},
            {"name": "getZipCode", "return_type": "String"},
            {"name": "getCountry", "return_type": "String"}
        ],
        "fields": [
            {"name": "street", "type": "String"},
            {"name": "city", "type": "String"},
            {"name": "state", "type": "String"},
            {"name": "zipCode", "type": "String"},
            {"name": "country", "type": "String"}
        ]
    }
    chunks.append(address_chunk)

    # Add nodes to the dependency graph
    for chunk in chunks:
        dependency_graph.add_node(
            node_id=chunk.node_id,
            node_type=chunk.chunk_type,
            name=chunk.name,
            qualified_name=chunk.qualified_name
        )

    # Add edges to the dependency graph

    # AbstractEntity implements Entity
    dependency_graph.add_edge(Dependency(
        source_id="class:AbstractEntity",
        target_id="interface:Entity",
        dep_type=DependencyType.IMPLEMENTS,
        strength=0.9,
        is_required=True,
        description="AbstractEntity implements Entity"
    ))

    # User extends AbstractEntity
    dependency_graph.add_edge(Dependency(
        source_id="class:User",
        target_id="class:AbstractEntity",
        dep_type=DependencyType.EXTENDS,
        strength=0.9,
        is_required=True,
        description="User extends AbstractEntity"
    ))

    # Order extends AbstractEntity
    dependency_graph.add_edge(Dependency(
        source_id="class:Order",
        target_id="class:AbstractEntity",
        dep_type=DependencyType.EXTENDS,
        strength=0.9,
        is_required=True,
        description="Order extends AbstractEntity"
    ))

    # User has field of type Order
    dependency_graph.add_edge(Dependency(
        source_id="class:User",
        target_id="class:Order",
        dep_type=DependencyType.USES,
        strength=0.8,
        is_required=True,
        description="User has field of type Order"
    ))

    # User has field of type Address
    dependency_graph.add_edge(Dependency(
        source_id="class:User",
        target_id="class:Address",
        dep_type=DependencyType.USES,
        strength=0.8,
        is_required=True,
        description="User has field of type Address"
    ))

    # Order has field of type User
    dependency_graph.add_edge(Dependency(
        source_id="class:Order",
        target_id="class:User",
        dep_type=DependencyType.USES,
        strength=0.8,
        is_required=True,
        description="Order has field of type User"
    ))

    logger.info(f"Created sample data with {len(chunks)} chunks and {len(dependency_graph.edges)} edges")

    return chunks, dependency_graph

def create_multi_file_graph(chunks, dependency_graph):
    """Create a graph showing multi-file relationships.

    Args:
        chunks: List of code chunks
        dependency_graph: Dependency graph

    Returns:
        NetworkX graph
    """
    # Create a NetworkX graph
    G = nx.DiGraph()

    # Create a map of file paths to file nodes
    file_map = {}
    for chunk in chunks:
        if 'file_path' in chunk.context:
            file_path = chunk.context['file_path']
            file_name = Path(file_path).name
            if file_path not in file_map:
                file_map[file_path] = file_name
                G.add_node(file_name, type="file", name=file_name)

    # Add class and interface nodes
    for chunk in chunks:
        if chunk.chunk_type in ['class_declaration', 'interface_declaration']:
            G.add_node(chunk.node_id, type=chunk.chunk_type, name=chunk.name)

            # Add file contains class relationship
            if 'file_path' in chunk.context:
                file_path = chunk.context['file_path']
                file_name = file_map.get(file_path)
                if file_name:
                    G.add_edge(file_name, chunk.node_id, type="CONTAINS", description=f"File contains {chunk.chunk_type}")

    # Add edges from the dependency graph
    for edge in dependency_graph.edges:
        source_id = edge.source_id
        target_id = edge.target_id
        edge_type = edge.type.name

        # Skip edges between nodes that don't exist in our graph
        if source_id not in G.nodes or target_id not in G.nodes:
            continue

        G.add_edge(source_id, target_id, type=edge_type, description=edge.description)

    # Add import relationships between files
    for chunk in chunks:
        if 'file_path' in chunk.context and 'imports' in chunk.context:
            source_file = file_map.get(chunk.context['file_path'])
            if not source_file:
                continue

            for imp in chunk.context.get('imports', []):
                # Find the target file
                target_file = None
                for path, name in file_map.items():
                    if path.endswith(f"{imp.replace('.', '/')}.java"):
                        target_file = name
                        break

                if target_file and source_file != target_file:
                    G.add_edge(source_file, target_file, type="IMPORTS", description=f"{source_file} imports {target_file}")

    return G

def create_relationship_types_graph(chunks, dependency_graph):
    """Create a graph showing different types of relationships.

    Args:
        chunks: List of code chunks
        dependency_graph: Dependency graph

    Returns:
        NetworkX graph
    """
    # Create a NetworkX graph
    G = nx.DiGraph()

    # Add class and interface nodes
    for chunk in chunks:
        if chunk.chunk_type in ['class_declaration', 'interface_declaration']:
            G.add_node(chunk.node_id, type=chunk.chunk_type, name=chunk.name)

    # Add method nodes
    for chunk in chunks:
        if chunk.chunk_type == 'method_declaration':
            G.add_node(chunk.node_id, type=chunk.chunk_type, name=chunk.name)

            # Add container relationship
            if 'class_id' in chunk.context:
                class_id = chunk.context['class_id']
                if class_id in G.nodes:
                    G.add_edge(class_id, chunk.node_id, type="CONTAINS", description="Class contains method")

    # Add field nodes
    for chunk in chunks:
        if chunk.chunk_type == 'field_declaration':
            G.add_node(chunk.node_id, type=chunk.chunk_type, name=chunk.name)

            # Add container relationship
            if 'class_id' in chunk.context:
                class_id = chunk.context['class_id']
                if class_id in G.nodes:
                    G.add_edge(class_id, chunk.node_id, type="CONTAINS", description="Class contains field")

    # Add edges from the dependency graph
    for edge in dependency_graph.edges:
        source_id = edge.source_id
        target_id = edge.target_id
        edge_type = edge.type.name

        # Skip edges between nodes that don't exist in our graph
        if source_id not in G.nodes or target_id not in G.nodes:
            continue

        G.add_edge(source_id, target_id, type=edge_type, description=edge.description)

    return G

def visualize_graph(G, output_file, title):
    """Visualize the graph with better relationship highlighting.

    Args:
        G: NetworkX graph
        output_file: Path to save the visualization
        title: Title of the visualization
    """
    logger.info(f"Visualizing graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")

    # Create figure
    plt.figure(figsize=(16, 12))
    plt.title(title, fontsize=16)

    # Use a more sophisticated layout
    try:
        pos = nx.kamada_kawai_layout(G)
    except:
        # Fall back to spring layout if kamada_kawai fails
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

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Visualize code relationships")
    parser.add_argument("--repo-path", required=True, help="Path to the Java repository")
    parser.add_argument("--output-dir", default="visualizations", help="Directory to save visualizations")
    parser.add_argument("--project-id", default=None, help="Project ID (defaults to folder name)")
    parser.add_argument("--timestamp", default=None, help="Timestamp to include in the filename")

    args = parser.parse_args()

    # Validate repo path
    repo_path = Path(args.repo_path)
    if not repo_path.exists() or not repo_path.is_dir():
        logger.error(f"Repository path does not exist or is not a directory: {repo_path}")
        sys.exit(1)

    # Set project ID if not provided
    project_id = args.project_id or repo_path.name

    # Get timestamp if provided
    timestamp = args.timestamp

    # Create output directory if it doesn't exist
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get data from the database
    logger.info("Reading data from the database...")

    from codebase_analyser.database.unified_storage import UnifiedStorage
    from codebase_analyser.chunking.code_chunk import CodeChunk
    from codebase_analyser.parsing.dependency_types import DependencyType, Dependency

    # Connect to the database
    try:
        storage = UnifiedStorage(db_path='.lancedb', read_only=True)

        # Get chunks from the database
        db_chunks = []

        # Get all chunks for this project from the database
        table = storage.db_manager.get_code_chunks_table()
        chunks_df = table.search().where(f'project_id = \"{project_id}\"').to_pandas()

        if len(chunks_df) > 0:
            logger.info(f"Found {len(chunks_df)} chunks in the database for project {project_id}")

            # Convert database chunks to CodeChunk objects
            for _, row in chunks_df.iterrows():
                chunk = CodeChunk(
                    chunk_type=row.get('chunk_type', 'unknown'),
                    name=row.get('name', ''),
                    content=row.get('content', ''),
                    node_id=row.get('node_id', ''),
                    qualified_name=row.get('qualified_name', ''),
                    file_path=row.get('file_path', ''),
                    start_line=row.get('start_line', 0),
                    end_line=row.get('end_line', 0),
                    language=row.get('language', 'java')
                )

                # Add context if available
                if 'context' in row and row['context']:
                    chunk.context = row['context']

                # Add metadata if available
                if 'metadata' in row and row['metadata']:
                    try:
                        if isinstance(row['metadata'], str):
                            chunk.metadata = json.loads(row['metadata'])
                        else:
                            chunk.metadata = row['metadata']
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse metadata for chunk {chunk.node_id}")

                db_chunks.append(chunk)

            # Get dependency graph from the database
            db_dependency_graph = storage.get_dependency_graph(project_id)

            # Log the number of edges found
            if db_dependency_graph:
                logger.info(f"Found dependency graph with {len(db_dependency_graph.edges)} edges in the database")
            else:
                logger.warning("No dependency graph found in the database")

            # Use the data from the database
            chunks, dependency_graph = db_chunks, db_dependency_graph
            logger.info("Successfully loaded data from the database")
        else:
            logger.error(f"No chunks found in the database for project {project_id}")
            logger.error("Please sync your codebase first")
            sys.exit(1)

        # Close the database connection
        storage.close()

    except Exception as e:
        logger.error(f"Error reading from database: {e}")
        logger.error("Please make sure the database exists and is properly configured")
        sys.exit(1)

    # Create filenames with timestamp if provided
    if timestamp:
        multi_file_filename = f"{project_id}_multi_file_relationships_{timestamp}.png"
        relationship_types_filename = f"{project_id}_relationship_types_{timestamp}.png"
    else:
        multi_file_filename = f"{project_id}_multi_file_relationships.png"
        relationship_types_filename = f"{project_id}_relationship_types.png"

    # Create and visualize multi-file graph
    G_multi_file = create_multi_file_graph(chunks, dependency_graph)
    visualize_graph(
        G_multi_file,
        output_dir / multi_file_filename,
        f"Multi-File Relationships - {project_id}"
    )

    # Create and visualize relationship types graph
    G_relationship_types = create_relationship_types_graph(chunks, dependency_graph)
    visualize_graph(
        G_relationship_types,
        output_dir / relationship_types_filename,
        f"Different Types of Relationships - {project_id}"
    )

    logger.info("Code relationship visualization completed successfully")

    # Return the paths to the visualizations for the VS Code extension
    result = {
        "multi_file_relationships": str(output_dir / multi_file_filename),
        "relationship_types": str(output_dir / relationship_types_filename)
    }

    print(json.dumps(result))

if __name__ == "__main__":
    main()
