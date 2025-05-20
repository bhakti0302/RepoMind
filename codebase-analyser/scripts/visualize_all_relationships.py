#!/usr/bin/env python3
"""
Visualize all types of code relationships for a Java project.

This script combines multiple visualization types into a single script:
1. Multi-file relationships
2. Relationship types
3. Class diagram
4. Package diagram
5. Dependency graph
6. Inheritance hierarchy

Usage:
    python visualize_all_relationships.py --repo-path <path_to_repo> --output-dir <path_to_output_dir> --project-id <project_id> [--timestamp <timestamp>]
"""

import os
import sys
import json
import argparse
import logging
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
import datetime

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from codebase_analyser import CodebaseAnalyser
from codebase_analyser.parsing.dependency_analyzer import DependencyAnalyzer
from codebase_analyser.database.unified_storage import UnifiedStorage
from codebase_analyser.chunking.code_chunk import CodeChunk
from codebase_analyser.parsing.dependency_types import DependencyType, Dependency

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

def get_data_from_database(project_id):
    """Get code chunks and dependency graph from the database.

    Args:
        project_id: Project ID to get data for

    Returns:
        Tuple of (chunks, dependency_graph)
    """
    logger.info("Reading data from the database...")

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

        return chunks, dependency_graph

    except Exception as e:
        logger.error(f"Error reading from database: {e}")
        logger.error("Please make sure the database exists and is properly configured")
        sys.exit(1)

def create_multi_file_graph(chunks, dependency_graph):
    """Create a graph showing multi-file relationships with enhanced labels and relationships."""
    # Create a NetworkX graph
    G = nx.DiGraph()

    # Create a map of file paths to file nodes
    file_map = {}
    package_map = {}  # Track packages for each file

    # First pass: collect all files and their packages
    for chunk in chunks:
        if 'file_path' in chunk.context:
            file_path = chunk.context['file_path']
            file_name = Path(file_path).name

            # Get package if available
            package = None
            if 'package' in chunk.context:
                package = chunk.context['package']
                if package not in package_map:
                    package_map[package] = []
                package_map[package].append(file_path)

            if file_path not in file_map:
                file_map[file_path] = file_name
                # Add package info to the node attributes
                G.add_node(file_name, type="file", name=file_name, package=package, full_path=file_path)

    # Add class and interface nodes with more details
    class_to_file = {}  # Map classes to their files
    for chunk in chunks:
        if chunk.chunk_type in ['class_declaration', 'interface_declaration']:
            # Add more detailed information for the node
            methods = []
            fields = []

            if 'methods' in chunk.context:
                methods = chunk.context['methods']

            if 'fields' in chunk.context:
                fields = chunk.context['fields']

            # Get superclass and interfaces if available
            superclass = chunk.context.get('superclass', None)
            interfaces = chunk.context.get('interfaces', [])

            G.add_node(chunk.node_id,
                      type=chunk.chunk_type,
                      name=chunk.name,
                      methods=methods,
                      fields=fields,
                      superclass=superclass,
                      interfaces=interfaces)

            # Add file contains class relationship with more descriptive label
            if 'file_path' in chunk.context:
                file_path = chunk.context['file_path']
                file_name = file_map.get(file_path)
                if file_name:
                    class_to_file[chunk.node_id] = file_name
                    G.add_edge(file_name, chunk.node_id,
                              type="CONTAINS",
                              description=f"File {file_name} contains {chunk.chunk_type} {chunk.name}")

    # Add edges from the dependency graph with enhanced descriptions
    for edge in dependency_graph.edges:
        source_id = edge.source_id
        target_id = edge.target_id
        edge_type = edge.type.name

        # Skip edges between nodes that don't exist in our graph
        if source_id not in G.nodes or target_id not in G.nodes:
            continue

        # Get source and target names for better description
        source_name = G.nodes[source_id].get('name', source_id)
        target_name = G.nodes[target_id].get('name', target_id)

        # Create a more descriptive edge label
        if edge_type == "EXTENDS":
            description = f"{source_name} extends {target_name}"
        elif edge_type == "IMPLEMENTS":
            description = f"{source_name} implements {target_name}"
        elif edge_type == "IMPORTS":
            description = f"{source_name} imports {target_name}"
        elif edge_type == "CALLS":
            description = f"{source_name} calls {target_name}"
        elif edge_type == "USES":
            description = f"{source_name} uses {target_name}"
        elif edge_type == "FIELD_TYPE":
            description = f"{source_name} has field of type {target_name}"
        else:
            description = edge.description or f"{source_name} {edge_type.lower()} {target_name}"

        G.add_edge(source_id, target_id, type=edge_type, description=description)

    # Add import relationships between files with better descriptions
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
                    # Get the class name from the import
                    class_name = imp.split('.')[-1]
                    G.add_edge(source_file, target_file,
                              type="IMPORTS",
                              description=f"{source_file} imports {class_name} from {target_file}")

    # Add package relationships
    for package, files in package_map.items():
        if len(files) > 1:
            # For files in the same package, add a relationship
            for i, file1 in enumerate(files):
                for file2 in files[i+1:]:
                    file1_name = file_map.get(file1)
                    file2_name = file_map.get(file2)
                    if file1_name and file2_name:
                        # Add bidirectional "SAME_PACKAGE" edges
                        if not G.has_edge(file1_name, file2_name):
                            G.add_edge(file1_name, file2_name,
                                      type="SAME_PACKAGE",
                                      description=f"{file1_name} and {file2_name} are in package {package}")

    return G

def create_relationship_types_graph(chunks, dependency_graph):
    """Create a graph showing different types of relationships."""
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

def create_class_diagram(chunks, dependency_graph):
    """Create a UML-style class diagram with detailed relationships."""
    # Create a NetworkX graph
    G = nx.DiGraph()

    # Add class and interface nodes with detailed information
    for chunk in chunks:
        if chunk.chunk_type in ['class_declaration', 'interface_declaration']:
            # Add more detailed information for the node
            methods = []
            fields = []

            if 'methods' in chunk.context:
                methods = chunk.context['methods']

            if 'fields' in chunk.context:
                fields = chunk.context['fields']

            # Get package information
            package = chunk.context.get('package', '')

            # Get superclass and interfaces if available
            superclass = chunk.context.get('superclass', None)
            interfaces = chunk.context.get('interfaces', [])

            # Create a more descriptive node label
            node_label = f"{chunk.name}"
            if package:
                node_label = f"{package}.{node_label}"

            G.add_node(chunk.node_id,
                      type=chunk.chunk_type,
                      name=chunk.name,
                      label=node_label,
                      package=package,
                      methods=methods,
                      fields=fields,
                      superclass=superclass,
                      interfaces=interfaces)

    # Add all types of relationships between classes
    for edge in dependency_graph.edges:
        source_id = edge.source_id
        target_id = edge.target_id
        edge_type = edge.type.name

        # Skip edges between nodes that don't exist in our graph
        if source_id not in G.nodes or target_id not in G.nodes:
            continue

        # Get source and target names for better description
        source_name = G.nodes[source_id].get('name', source_id)
        target_name = G.nodes[target_id].get('name', target_id)

        # Create a more descriptive edge label
        if edge_type == "EXTENDS":
            description = f"{source_name} extends {target_name}"
        elif edge_type == "IMPLEMENTS":
            description = f"{source_name} implements {target_name}"
        elif edge_type == "IMPORTS":
            description = f"{source_name} imports {target_name}"
        elif edge_type == "CALLS":
            description = f"{source_name} calls {target_name}"
        elif edge_type == "USES":
            description = f"{source_name} uses {target_name}"
        elif edge_type == "FIELD_TYPE":
            description = f"{source_name} has field of type {target_name}"
        else:
            description = edge.description or f"{source_name} {edge_type.lower()} {target_name}"

        G.add_edge(source_id, target_id, type=edge_type, description=description)

    # Add field type relationships
    for chunk in chunks:
        if chunk.chunk_type == 'class_declaration':
            class_id = chunk.node_id

            # Check fields for relationships
            for field in chunk.context.get('fields', []):
                field_type = field.get('type', '')

                # Find target class by name
                for target_chunk in chunks:
                    if target_chunk.chunk_type in ['class_declaration', 'interface_declaration'] and target_chunk.name == field_type:
                        target_id = target_chunk.node_id

                        # Add field type relationship if not already present
                        if not G.has_edge(class_id, target_id):
                            G.add_edge(class_id, target_id,
                                      type="FIELD_TYPE",
                                      description=f"{chunk.name} has field of type {target_chunk.name}")

    # Add method parameter and return type relationships
    for chunk in chunks:
        if chunk.chunk_type == 'class_declaration':
            class_id = chunk.node_id

            # Check methods for relationships
            for method in chunk.context.get('methods', []):
                return_type = method.get('return_type', '')
                parameters = method.get('parameters', [])

                # Find target classes for return type
                for target_chunk in chunks:
                    if target_chunk.chunk_type in ['class_declaration', 'interface_declaration']:
                        # Check return type relationship
                        if target_chunk.name == return_type:
                            target_id = target_chunk.node_id
                            if not G.has_edge(class_id, target_id):
                                G.add_edge(class_id, target_id,
                                          type="USES",
                                          description=f"{chunk.name} uses {target_chunk.name} as return type")

                        # Check parameter type relationships
                        for param in parameters:
                            param_type = param.get('type', '')
                            if target_chunk.name == param_type:
                                target_id = target_chunk.node_id
                                if not G.has_edge(class_id, target_id):
                                    G.add_edge(class_id, target_id,
                                              type="USES",
                                              description=f"{chunk.name} uses {target_chunk.name} as parameter type")

    return G

def create_package_diagram(chunks, dependency_graph):
    """Create a package diagram showing relationships between packages."""
    # Create a NetworkX graph
    G = nx.DiGraph()

    # Create a map of packages
    packages = {}
    package_to_files = {}  # Track files in each package

    # Extract packages from chunks
    for chunk in chunks:
        # Get package from any chunk that has it
        if 'package' in chunk.context:
            package = chunk.context['package']

            # If package is empty or None, use "default" as the package name
            if not package:
                package = "default"

            # Initialize package data structures if needed
            if package not in packages:
                packages[package] = []
                package_to_files[package] = set()

            # Add chunk to package
            if chunk.chunk_type in ['class_declaration', 'interface_declaration']:
                packages[package].append(chunk.node_id)

            # Track file path for this package
            if 'file_path' in chunk.context:
                package_to_files[package].add(chunk.context['file_path'])

    # If no packages were found, create a default package with all classes
    if not packages:
        packages["default"] = []
        package_to_files["default"] = set()

        for chunk in chunks:
            if chunk.chunk_type in ['class_declaration', 'interface_declaration']:
                packages["default"].append(chunk.node_id)
                if 'file_path' in chunk.context:
                    package_to_files["default"].add(chunk.context['file_path'])

    # Add package nodes with more information
    for package, classes in packages.items():
        # Count the number of classes and files in this package
        num_classes = len(classes)
        num_files = len(package_to_files[package])

        # Create a descriptive label
        label = f"{package}\n({num_classes} classes, {num_files} files)"

        G.add_node(package,
                  type="package",
                  name=package,
                  label=label,
                  classes=classes,
                  files=list(package_to_files[package]),
                  num_classes=num_classes,
                  num_files=num_files)

    # Add dependencies between packages based on imports
    for chunk in chunks:
        if 'package' in chunk.context and 'imports' in chunk.context:
            source_package = chunk.context['package'] or "default"

            for imp in chunk.context.get('imports', []):
                # Extract the package from the import
                import_parts = imp.split('.')
                if len(import_parts) > 1:
                    # The package is everything except the last part (class name)
                    target_package = '.'.join(import_parts[:-1])

                    # Add edge between packages if they're different and both exist
                    if (source_package != target_package and
                        source_package in packages and
                        target_package in packages):

                        # Check if the edge already exists
                        if not G.has_edge(source_package, target_package):
                            G.add_edge(source_package, target_package,
                                      type="IMPORTS",
                                      description=f"{source_package} imports from {target_package}",
                                      weight=1)
                        else:
                            # Increment the weight of the existing edge
                            G[source_package][target_package]['weight'] += 1
                            # Update the description to show the count
                            weight = G[source_package][target_package]['weight']
                            G[source_package][target_package]['description'] = f"{source_package} imports from {target_package} ({weight} times)"

    # Add dependencies between packages based on class relationships
    for edge in dependency_graph.edges:
        source_id = edge.source_id
        target_id = edge.target_id
        edge_type = edge.type.name

        # Find the packages for the source and target
        source_package = None
        target_package = None

        for package, classes in packages.items():
            if source_id in classes:
                source_package = package
            if target_id in classes:
                target_package = package

        # Add edge between packages if they're different
        if source_package and target_package and source_package != target_package:
            # Check if the edge already exists
            if not G.has_edge(source_package, target_package):
                G.add_edge(source_package, target_package,
                          type="DEPENDS_ON",
                          description=f"{source_package} depends on {target_package}",
                          weight=1,
                          relationship_types=set([edge_type]))
            else:
                # Increment the weight of the existing edge
                G[source_package][target_package]['weight'] += 1

                # Add this relationship type to the set
                if 'relationship_types' not in G[source_package][target_package]:
                    G[source_package][target_package]['relationship_types'] = set()
                G[source_package][target_package]['relationship_types'].add(edge_type)

                # Update the description to show the count and relationship types
                weight = G[source_package][target_package]['weight']
                rel_types = ', '.join(G[source_package][target_package]['relationship_types'])
                G[source_package][target_package]['description'] = f"{source_package} depends on {target_package} ({weight} dependencies, types: {rel_types})"

    # If the graph is still empty, create a simple structure
    if len(G.nodes) == 0:
        G.add_node("No packages found", type="package", name="No packages found")

    return G

def create_dependency_graph(chunks, dependency_graph):
    """Create a comprehensive dependency graph showing all dependencies between classes."""
    # Create a NetworkX graph
    G = nx.DiGraph()

    # Add class and interface nodes with detailed information
    for chunk in chunks:
        if chunk.chunk_type in ['class_declaration', 'interface_declaration']:
            # Get package information
            package = chunk.context.get('package', '')

            # Create a more descriptive node label
            node_label = f"{chunk.name}"
            if package:
                node_label = f"{package}.{node_label}"

            G.add_node(chunk.node_id,
                      type=chunk.chunk_type,
                      name=chunk.name,
                      label=node_label,
                      package=package)

    # Add all dependency edges with enhanced descriptions
    edge_count = 0
    for edge in dependency_graph.edges:
        source_id = edge.source_id
        target_id = edge.target_id
        edge_type = edge.type.name

        # Skip edges between nodes that don't exist in our graph
        if source_id not in G.nodes or target_id not in G.nodes:
            continue

        # Get source and target names for better description
        source_name = G.nodes[source_id].get('name', source_id)
        target_name = G.nodes[target_id].get('name', target_id)

        # Create a more descriptive edge label
        if edge_type == "EXTENDS":
            description = f"{source_name} extends {target_name}"
        elif edge_type == "IMPLEMENTS":
            description = f"{source_name} implements {target_name}"
        elif edge_type == "IMPORTS":
            description = f"{source_name} imports {target_name}"
        elif edge_type == "CALLS":
            description = f"{source_name} calls {target_name}"
        elif edge_type == "USES":
            description = f"{source_name} uses {target_name}"
        elif edge_type == "FIELD_TYPE":
            description = f"{source_name} has field of type {target_name}"
        else:
            description = edge.description or f"{source_name} {edge_type.lower()} {target_name}"

        G.add_edge(source_id, target_id, type=edge_type, description=description)
        edge_count += 1

    # If no edges were found in the dependency graph, add additional relationships
    if edge_count == 0:
        # Add field type relationships
        for chunk in chunks:
            if chunk.chunk_type == 'class_declaration':
                class_id = chunk.node_id

                # Check fields for relationships
                for field in chunk.context.get('fields', []):
                    field_type = field.get('type', '')

                    # Find target class by name
                    for target_chunk in chunks:
                        if target_chunk.chunk_type in ['class_declaration', 'interface_declaration'] and target_chunk.name == field_type:
                            target_id = target_chunk.node_id

                            # Add field type relationship if not already present
                            if not G.has_edge(class_id, target_id):
                                G.add_edge(class_id, target_id,
                                          type="FIELD_TYPE",
                                          description=f"{chunk.name} has field of type {target_chunk.name}")
                                edge_count += 1

        # Add method parameter and return type relationships
        for chunk in chunks:
            if chunk.chunk_type == 'class_declaration':
                class_id = chunk.node_id

                # Check methods for relationships
                for method in chunk.context.get('methods', []):
                    return_type = method.get('return_type', '')
                    parameters = method.get('parameters', [])

                    # Find target classes for return type
                    for target_chunk in chunks:
                        if target_chunk.chunk_type in ['class_declaration', 'interface_declaration']:
                            # Check return type relationship
                            if target_chunk.name == return_type:
                                target_id = target_chunk.node_id
                                if not G.has_edge(class_id, target_id):
                                    G.add_edge(class_id, target_id,
                                              type="USES",
                                              description=f"{chunk.name} uses {target_chunk.name} as return type")
                                    edge_count += 1

                            # Check parameter type relationships
                            for param in parameters:
                                param_type = param.get('type', '')
                                if target_chunk.name == param_type:
                                    target_id = target_chunk.node_id
                                    if not G.has_edge(class_id, target_id):
                                        G.add_edge(class_id, target_id,
                                                  type="USES",
                                                  description=f"{chunk.name} uses {target_chunk.name} as parameter type")
                                        edge_count += 1

        # Add import relationships
        for chunk in chunks:
            if 'imports' in chunk.context and chunk.chunk_type == 'class_declaration':
                source_id = chunk.node_id

                for imp in chunk.context.get('imports', []):
                    # Extract the class name from the import
                    import_parts = imp.split('.')
                    if import_parts:
                        class_name = import_parts[-1]

                        # Find target class by name
                        for target_chunk in chunks:
                            if target_chunk.chunk_type in ['class_declaration', 'interface_declaration'] and target_chunk.name == class_name:
                                target_id = target_chunk.node_id

                                # Add import relationship if not already present
                                if not G.has_edge(source_id, target_id):
                                    G.add_edge(source_id, target_id,
                                              type="IMPORTS",
                                              description=f"{chunk.name} imports {target_chunk.name}")
                                    edge_count += 1

    # If the graph is still empty, create a simple structure
    if len(G.nodes) == 0:
        G.add_node("No classes found", type="class_declaration", name="No classes found")
    elif edge_count == 0:
        # If we have nodes but no edges, add a dummy node explaining the issue
        G.add_node("No dependencies found", type="info", name="No dependencies found")
        # Connect it to the first real node to make it visible
        if len(G.nodes) > 1:
            first_node = next(iter([n for n in G.nodes if n != "No dependencies found"]))
            G.add_edge("No dependencies found", first_node, type="INFO", description="No dependencies were found between classes")

    return G

def create_inheritance_hierarchy(chunks, dependency_graph):
    """Create a detailed inheritance hierarchy graph."""
    # Create a NetworkX graph
    G = nx.DiGraph()

    # Add class and interface nodes with detailed information
    for chunk in chunks:
        if chunk.chunk_type in ['class_declaration', 'interface_declaration']:
            # Get package information
            package = chunk.context.get('package', '')

            # Get superclass and interfaces if available
            superclass = chunk.context.get('superclass', None)
            interfaces = chunk.context.get('interfaces', [])

            # Create a more descriptive node label
            node_label = f"{chunk.name}"
            if package:
                node_label = f"{package}.{node_label}"

            G.add_node(chunk.node_id,
                      type=chunk.chunk_type,
                      name=chunk.name,
                      label=node_label,
                      package=package,
                      superclass=superclass,
                      interfaces=interfaces)

    # Add inheritance relationships from the dependency graph
    inheritance_count = 0
    for edge in dependency_graph.edges:
        source_id = edge.source_id
        target_id = edge.target_id
        edge_type = edge.type.name

        # Only include inheritance relationships
        if edge_type in ['EXTENDS', 'IMPLEMENTS']:
            # Skip edges between nodes that don't exist in our graph
            if source_id not in G.nodes or target_id not in G.nodes:
                continue

            # Get source and target names for better description
            source_name = G.nodes[source_id].get('name', source_id)
            target_name = G.nodes[target_id].get('name', target_id)

            # Create a more descriptive edge label
            if edge_type == "EXTENDS":
                description = f"{source_name} extends {target_name}"
            elif edge_type == "IMPLEMENTS":
                description = f"{source_name} implements {target_name}"

            G.add_edge(source_id, target_id, type=edge_type, description=description)
            inheritance_count += 1

    # If no inheritance relationships were found in the dependency graph, try to infer them
    if inheritance_count == 0:
        # Try to infer inheritance relationships from class metadata
        for chunk in chunks:
            if chunk.chunk_type == 'class_declaration':
                source_id = chunk.node_id
                source_name = chunk.name

                # Check for superclass
                superclass = chunk.context.get('superclass', None)
                if superclass:
                    # Find the superclass node
                    for target_chunk in chunks:
                        if (target_chunk.chunk_type in ['class_declaration', 'interface_declaration'] and
                            target_chunk.name == superclass):
                            target_id = target_chunk.node_id
                            target_name = target_chunk.name

                            # Add extends relationship
                            G.add_edge(source_id, target_id,
                                      type="EXTENDS",
                                      description=f"{source_name} extends {target_name}")
                            inheritance_count += 1

                # Check for implemented interfaces
                interfaces = chunk.context.get('interfaces', [])
                for interface in interfaces:
                    # Find the interface node
                    for target_chunk in chunks:
                        if (target_chunk.chunk_type == 'interface_declaration' and
                            target_chunk.name == interface):
                            target_id = target_chunk.node_id
                            target_name = target_chunk.name

                            # Add implements relationship
                            G.add_edge(source_id, target_id,
                                      type="IMPLEMENTS",
                                      description=f"{source_name} implements {target_name}")
                            inheritance_count += 1

    # If still no inheritance relationships, create a default hierarchy
    if inheritance_count == 0:
        # Check if we have Object class or any base class
        base_class_id = None
        for chunk in chunks:
            if chunk.chunk_type == 'class_declaration' and chunk.name in ['Object', 'BaseClass', 'Base']:
                base_class_id = chunk.node_id
                break

        # If no base class found, create one
        if not base_class_id and len(G.nodes) > 0:
            base_class_id = "java.lang.Object"
            G.add_node(base_class_id,
                      type="class_declaration",
                      name="Object",
                      label="java.lang.Object",
                      package="java.lang")

            # Connect all classes to Object except interfaces
            for node_id in G.nodes:
                if node_id != base_class_id and G.nodes[node_id].get('type') == 'class_declaration':
                    source_name = G.nodes[node_id].get('name', node_id)
                    G.add_edge(node_id, base_class_id,
                              type="EXTENDS",
                              description=f"{source_name} extends Object")

    # If the graph is still empty, create a simple structure
    if len(G.nodes) == 0:
        G.add_node("No classes found", type="class_declaration", name="No classes found")
    elif inheritance_count == 0 and len(G.nodes) > 0:
        # If we have nodes but no inheritance, add a dummy node explaining the issue
        G.add_node("No inheritance found", type="info", name="No inheritance found")
        # Connect it to the first real node to make it visible
        if len(G.nodes) > 1:
            first_node = next(iter([n for n in G.nodes if n != "No inheritance found"]))
            G.add_edge("No inheritance found", first_node, type="INFO", description="No inheritance relationships were found")

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
        elif node_type == 'package':
            labels[node] = f"Package: {node_name}"
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
    parser = argparse.ArgumentParser(description="Visualize all code relationships")
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

    # Get timestamp if provided or generate one
    timestamp = args.timestamp
    if not timestamp:
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")

    # Create output directory if it doesn't exist
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get data from the database
    chunks, dependency_graph = get_data_from_database(project_id)

    # Create filenames with timestamp
    multi_file_filename = f"{project_id}_multi_file_relationships_{timestamp}.png"
    relationship_types_filename = f"{project_id}_relationship_types_{timestamp}.png"
    class_diagram_filename = f"{project_id}_class_diagram_{timestamp}.png"
    package_diagram_filename = f"{project_id}_package_diagram_{timestamp}.png"
    dependency_graph_filename = f"{project_id}_dependency_graph_{timestamp}.png"
    inheritance_hierarchy_filename = f"{project_id}_inheritance_hierarchy_{timestamp}.png"

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

    # Create and visualize class diagram
    G_class_diagram = create_class_diagram(chunks, dependency_graph)
    visualize_graph(
        G_class_diagram,
        output_dir / class_diagram_filename,
        f"Class Diagram - {project_id}"
    )

    # Create and visualize package diagram
    G_package_diagram = create_package_diagram(chunks, dependency_graph)
    visualize_graph(
        G_package_diagram,
        output_dir / package_diagram_filename,
        f"Package Diagram - {project_id}"
    )

    # Create and visualize dependency graph
    G_dependency_graph = create_dependency_graph(chunks, dependency_graph)
    visualize_graph(
        G_dependency_graph,
        output_dir / dependency_graph_filename,
        f"Dependency Graph - {project_id}"
    )

    # Create and visualize inheritance hierarchy
    G_inheritance_hierarchy = create_inheritance_hierarchy(chunks, dependency_graph)
    visualize_graph(
        G_inheritance_hierarchy,
        output_dir / inheritance_hierarchy_filename,
        f"Inheritance Hierarchy - {project_id}"
    )

    logger.info("All code relationship visualizations completed successfully")

    # Return the paths to the visualizations for the VS Code extension
    result = {
        "multi_file_relationships": str(output_dir / multi_file_filename),
        "relationship_types": str(output_dir / relationship_types_filename),
        "class_diagram": str(output_dir / class_diagram_filename),
        "package_diagram": str(output_dir / package_diagram_filename),
        "dependency_graph": str(output_dir / dependency_graph_filename),
        "inheritance_hierarchy": str(output_dir / inheritance_hierarchy_filename)
    }

    print(json.dumps(result))

if __name__ == "__main__":
    main()
