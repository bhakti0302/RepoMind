#!/usr/bin/env python3
"""
Visualize the testshreya project with enhanced visualization.

This script analyzes the testshreya project and generates an enhanced visualization
of the code relationships.
"""

import os
import sys
import json
import logging
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path

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

def run_analysis():
    """Run the analysis on the testshreya project."""
    # Import the necessary modules
    from codebase_analyser import CodebaseAnalyser
    from codebase_analyser.parsing.dependency_analyzer import DependencyAnalyzer

    # Parse the repository
    logger.info("Parsing repository...")
    repo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'testshreya')
    analyser = CodebaseAnalyser(repo_path=repo_path)
    chunks = analyser.parse()

    logger.info(f"Found {len(chunks)} chunks in the repository")

    # Print information about the chunks
    class_chunks = [c for c in chunks if c.chunk_type == 'class_declaration']
    interface_chunks = [c for c in chunks if c.chunk_type == 'interface_declaration']
    method_chunks = [c for c in chunks if c.chunk_type == 'method_declaration']

    logger.info(f"Found {len(class_chunks)} classes, {len(interface_chunks)} interfaces, {len(method_chunks)} methods")

    # Print information about the classes
    logger.info("\nClasses:")
    for chunk in class_chunks:
        logger.info(f"  - {chunk.name} ({chunk.node_id})")

        # Print parent class if available
        if 'extends' in chunk.context:
            logger.info(f"    Extends: {chunk.context['extends']}")

        # Print implemented interfaces if available
        if 'implements' in chunk.context:
            logger.info(f"    Implements: {', '.join(chunk.context['implements'])}")

        # Print fields if available
        if 'fields' in chunk.context:
            logger.info(f"    Fields:")
            for field in chunk.context['fields']:
                logger.info(f"      - {field.get('name', 'unknown')} ({field.get('type', 'unknown')})")

    # Print information about the interfaces
    logger.info("\nInterfaces:")
    for chunk in interface_chunks:
        logger.info(f"  - {chunk.name} ({chunk.node_id})")

    # Analyze dependencies
    logger.info("\nAnalyzing dependencies...")
    dependency_analyzer = DependencyAnalyzer()
    dependency_graph = dependency_analyzer.analyze_dependencies(chunks)

    # Add additional edges for inheritance and field type relationships
    add_inheritance_edges(chunks, dependency_graph)
    add_field_type_edges(chunks, dependency_graph)

    # Print information about the dependencies
    logger.info("\nDependencies:")
    edges = dependency_graph.edges

    # Group edges by type
    edge_types = {}
    for edge in edges:
        edge_type = edge.type.name
        if edge_type not in edge_types:
            edge_types[edge_type] = []
        edge_types[edge_type].append(edge)

    # Print edges by type
    for edge_type, edges in edge_types.items():
        logger.info(f"\n  {edge_type} ({len(edges)}):")
        for edge in edges:
            source_id = edge.source_id
            target_id = edge.target_id

            # Find the source and target chunks
            source_chunk = next((c for c in chunks if c.node_id == source_id), None)
            target_chunk = next((c for c in chunks if c.node_id == target_id), None)

            source_name = source_chunk.name if source_chunk else source_id
            target_name = target_chunk.name if target_chunk else target_id

            logger.info(f"    - {source_name} -> {target_name} ({edge.description})")

    # Convert to dictionary and save
    graph_dict = dependency_graph.to_dict()
    with open('samples/testshreya_enhanced_dependency_graph.json', 'w') as f:
        json.dump(graph_dict, f, indent=2)

    logger.info(f"\nGenerated dependency graph with {len(graph_dict['nodes'])} nodes and {len(graph_dict['edges'])} edges")
    logger.info(f"Saved to samples/testshreya_enhanced_dependency_graph.json")

    # Visualize the graph
    visualize_enhanced_graph(graph_dict, 'samples/testshreya_enhanced_graph.png')

def add_inheritance_edges(chunks, dependency_graph):
    """Add inheritance edges to the dependency graph."""
    from codebase_analyser.parsing.dependency_types import DependencyType, Dependency

    # Create a map of class/interface names to chunks for quick lookup
    class_map = {}
    for chunk in chunks:
        if chunk.chunk_type in ['class_declaration', 'interface_declaration']:
            class_map[chunk.name] = chunk
            # Also map by qualified name if available
            if chunk.qualified_name:
                class_map[chunk.qualified_name] = chunk

    # Look for inheritance relationships
    for chunk in chunks:
        # Skip non-class chunks
        if chunk.chunk_type != 'class_declaration':
            continue

        # Check for extends in the context
        if 'extends' in chunk.context:
            parent_class = chunk.context['extends']

            # Find the parent class
            if parent_class in class_map:
                parent_chunk = class_map[parent_class]

                # Create an EXTENDS dependency
                dependency = Dependency(
                    source_id=chunk.node_id,
                    target_id=parent_chunk.node_id,
                    dep_type=DependencyType.EXTENDS,
                    strength=0.9,
                    is_required=True,
                    description=f"{chunk.name} extends {parent_chunk.name}"
                )

                dependency_graph.add_edge(dependency)

        # Check for implements in the context
        if 'implements' in chunk.context:
            implements_list = chunk.context['implements']

            for interface_name in implements_list:
                # Find the target interface
                if interface_name in class_map:
                    interface_chunk = class_map[interface_name]

                    # Create an IMPLEMENTS dependency
                    dependency = Dependency(
                        source_id=chunk.node_id,
                        target_id=interface_chunk.node_id,
                        dep_type=DependencyType.IMPLEMENTS,
                        strength=0.9,
                        is_required=True,
                        description=f"{chunk.name} implements {interface_chunk.name}"
                    )

                    dependency_graph.add_edge(dependency)

def add_field_type_edges(chunks, dependency_graph):
    """Add field type edges to the dependency graph."""
    from codebase_analyser.parsing.dependency_types import DependencyType, Dependency

    # Create a map of class names to chunks for quick lookup
    class_map = {}
    for chunk in chunks:
        if chunk.chunk_type in ['class_declaration', 'interface_declaration', 'enum_declaration']:
            class_map[chunk.name] = chunk
            # Also map by qualified name if available
            if chunk.qualified_name:
                class_map[chunk.qualified_name] = chunk

    # Look for field declarations with types that match our classes
    for chunk in chunks:
        # Skip non-class chunks
        if chunk.chunk_type not in ['class_declaration', 'interface_declaration', 'enum_declaration']:
            continue

        # Check for fields in the context
        if 'fields' not in chunk.context:
            continue

        for field in chunk.context.get('fields', []):
            field_type = field.get('type', '')

            # Remove generic type parameters if present
            import re
            base_type = re.sub(r'<.*>', '', field_type).strip()

            # Check if the field type matches one of our classes
            if base_type in class_map:
                target_chunk = class_map[base_type]

                # Create a FIELD_TYPE dependency (using USES as a fallback)
                dependency = Dependency(
                    source_id=chunk.node_id,
                    target_id=target_chunk.node_id,
                    dep_type=DependencyType.USES,
                    strength=0.8,
                    is_required=True,
                    description=f"{chunk.name} has field of type {target_chunk.name}"
                )

                dependency_graph.add_edge(dependency)

def visualize_enhanced_graph(graph_dict, output_file):
    """Visualize the enhanced graph with better relationship highlighting."""
    logger.info(f"Visualizing enhanced graph with {len(graph_dict['nodes'])} nodes and {len(graph_dict['edges'])} edges")

    # Create a NetworkX graph
    G = nx.DiGraph()

    # Add nodes
    for node in graph_dict.get('nodes', []):
        node_id = node.get('id', '')
        node_type = node.get('type', 'DEFAULT')
        node_name = node.get('name', node_id)

        G.add_node(
            node_id,
            type=node_type,
            name=node_name,
            qualified_name=node.get('qualified_name', node_name),
            color=NODE_COLORS.get(node_type, NODE_COLORS['DEFAULT'])
        )

    # Add edges
    for edge in graph_dict.get('edges', []):
        source_id = edge.get('source_id', '')
        target_id = edge.get('target_id', '')
        edge_type = edge.get('type', 'DEFAULT')

        # Skip if source or target doesn't exist
        if source_id not in G.nodes or target_id not in G.nodes:
            continue

        G.add_edge(
            source_id,
            target_id,
            type=edge_type,
            strength=edge.get('strength', 0.5),
            is_direct=edge.get('is_direct', True),
            is_required=edge.get('is_required', False),
            description=edge.get('description', ''),
            color=RELATIONSHIP_COLORS.get(edge_type, RELATIONSHIP_COLORS['DEFAULT'])
        )

    # Create figure
    plt.figure(figsize=(16, 12))
    plt.title("Enhanced Code Relationships - testshreya", fontsize=16)

    # Use a more sophisticated layout
    try:
        pos = nx.kamada_kawai_layout(G)
    except:
        # Fall back to spring layout if kamada_kawai fails
        pos = nx.spring_layout(G, k=0.3, iterations=50, seed=42)

    # Draw nodes with different colors based on type
    node_colors = [G.nodes[n].get('color', NODE_COLORS['DEFAULT']) for n in G.nodes]
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
        else:
            labels[node] = node_name

    nx.draw_networkx_labels(G, pos, labels=labels, font_size=10, font_weight='bold')

    # Add legend for relationship types
    legend_elements = []
    import matplotlib.patches as mpatches
    import matplotlib.lines as mlines

    # Node type legend
    for node_type, color in NODE_COLORS.items():
        if node_type != 'DEFAULT':
            legend_elements.append(
                mpatches.Patch(color=color, alpha=0.8, label=f"{node_type.replace('_declaration', '').capitalize()}")
            )

    # Edge type legend
    for edge_type, color in RELATIONSHIP_COLORS.items():
        if edge_type != 'DEFAULT':
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

if __name__ == "__main__":
    run_analysis()
