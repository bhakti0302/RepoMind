"""
Enhanced dependency analyzer for code chunks.

This module extends the existing dependency analyzer with improved relationship detection,
focusing on import, inheritance, and field type relationships.
"""

import re
import logging
from typing import Dict, List, Optional, Set, Union, Any, Tuple

from .dependency_analyzer import DependencyAnalyzer, DependencyGraph
from .dependency_types import DependencyType, Dependency

logger = logging.getLogger(__name__)

class EnhancedDependencyAnalyzer(DependencyAnalyzer):
    """Enhanced analyzer for dependencies between code chunks."""

    def __init__(self):
        """Initialize the enhanced dependency analyzer."""
        super().__init__()

        # Add FIELD_TYPE to dependency types if not already present
        if not hasattr(DependencyType, 'FIELD_TYPE'):
            # Add dynamically if not in the enum
            try:
                DependencyType.FIELD_TYPE = DependencyType('FIELD_TYPE')
            except:
                # If we can't add it dynamically, we'll use USES instead
                logger.warning("Could not add FIELD_TYPE to DependencyType enum, using USES instead")

    def analyze_dependencies(self, chunks: List['CodeChunk']) -> DependencyGraph:
        """Analyze dependencies between chunks with enhanced detection.

        Args:
            chunks: List of code chunks to analyze

        Returns:
            Dependency graph
        """
        # Reset the dependency graph
        self.dependency_graph = DependencyGraph()
        self.chunk_metrics = {}

        # Add all chunks as nodes in the graph
        for chunk in chunks:
            self.dependency_graph.add_node(
                node_id=chunk.node_id,
                node_type=chunk.chunk_type,
                name=chunk.name or "",
                qualified_name=chunk.qualified_name
            )

        # Analyze different types of dependencies
        self._analyze_inheritance_dependencies(chunks)
        self._analyze_method_call_dependencies(chunks)
        self._analyze_field_usage_dependencies(chunks)
        self._analyze_container_dependencies(chunks)
        self._analyze_import_dependencies(chunks)

        # Add enhanced dependency analysis
        self._analyze_field_type_dependencies(chunks)
        self._enhance_import_dependencies(chunks)
        self._enhance_inheritance_dependencies(chunks)

        # Add new enhanced relationship analysis
        self._detect_bidirectional_relationships()
        self._detect_transitive_relationships()
        self._calculate_relationship_frequencies()
        self._assign_group_ids(chunks)
        self._infer_relationships(chunks)

        # Calculate graph-level metrics
        self.dependency_graph.calculate_metrics()

        # Calculate chunk-level metrics
        self._calculate_chunk_metrics(chunks)

        return self.dependency_graph

    def _analyze_field_type_dependencies(self, chunks: List['CodeChunk']) -> None:
        """Analyze field type dependencies (field has type of another class).

        Args:
            chunks: List of code chunks to analyze
        """
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
                base_type = re.sub(r'<.*>', '', field_type).strip()

                # Check if the field type matches one of our classes
                if base_type in class_map:
                    target_chunk = class_map[base_type]

                    # Create a FIELD_TYPE dependency
                    try:
                        dep_type = DependencyType.FIELD_TYPE
                    except:
                        # Fall back to USES if FIELD_TYPE is not available
                        dep_type = DependencyType.USES

                    dependency = Dependency(
                        source_id=chunk.node_id,
                        target_id=target_chunk.node_id,
                        dep_type=dep_type,
                        strength=0.8,  # Field type relationships are strong
                        is_required=True,
                        description=f"{chunk.name} has field of type {target_chunk.name}"
                    )

                    self.dependency_graph.add_edge(dependency)

    def _enhance_import_dependencies(self, chunks: List['CodeChunk']) -> None:
        """Enhance import dependency detection with better package handling.

        Args:
            chunks: List of code chunks to analyze
        """
        # Create a map of qualified names to chunks for quick lookup
        qualified_name_map = {}
        for chunk in chunks:
            if chunk.qualified_name:
                qualified_name_map[chunk.qualified_name] = chunk

        # Look for import statements and match with qualified names
        for chunk in chunks:
            # Skip chunks without imports
            if 'imports' not in chunk.context:
                continue

            imports = chunk.context.get('imports', [])

            for imp in imports:
                # Handle wildcard imports (e.g., import java.util.*)
                if imp.endswith('.*'):
                    package_prefix = imp[:-2]  # Remove the '.*'

                    # Find all chunks that belong to this package
                    for qualified_name, target_chunk in qualified_name_map.items():
                        if qualified_name.startswith(package_prefix):
                            # Create an IMPORTS dependency
                            dependency = Dependency(
                                source_id=chunk.node_id,
                                target_id=target_chunk.node_id,
                                dep_type=DependencyType.IMPORTS,
                                strength=0.6,  # Wildcard imports are slightly weaker
                                is_required=True,
                                description=f"{chunk.name} imports {target_chunk.qualified_name} via wildcard"
                            )

                            self.dependency_graph.add_edge(dependency)

    def _enhance_inheritance_dependencies(self, chunks: List['CodeChunk']) -> None:
        """Enhance inheritance dependency detection with interface implementation.

        Args:
            chunks: List of code chunks to analyze
        """
        # Create a map of class/interface names to chunks for quick lookup
        class_map = {}
        for chunk in chunks:
            if chunk.chunk_type in ['class_declaration', 'interface_declaration']:
                class_map[chunk.name] = chunk
                # Also map by qualified name if available
                if chunk.qualified_name:
                    class_map[chunk.qualified_name] = chunk

        # Look for interface implementations
        for chunk in chunks:
            # Skip non-class chunks
            if chunk.chunk_type != 'class_declaration':
                continue

            # Check for implements in the context
            if 'implements' not in chunk.context:
                continue

            implements_list = chunk.context.get('implements', [])

            for interface_name in implements_list:
                # Find the target interface
                if interface_name in class_map:
                    target_chunk = class_map[interface_name]

                    # Create an IMPLEMENTS dependency
                    dependency = Dependency(
                        source_id=chunk.node_id,
                        target_id=target_chunk.node_id,
                        dep_type=DependencyType.IMPLEMENTS,
                        strength=0.9,  # Interface implementation is strong
                        is_required=True,
                        description=f"{chunk.name} implements {target_chunk.name}"
                    )

                    self.dependency_graph.add_edge(dependency)

    def _detect_bidirectional_relationships(self) -> None:
        """Detect bidirectional relationships between nodes.

        A bidirectional relationship exists when there are edges in both directions
        between two nodes.
        """
        # Get all edges from the graph
        edges = self.dependency_graph.edges

        # Create a dictionary to track bidirectional relationships
        bidirectional_pairs = {}

        # Find all pairs of nodes with edges in both directions
        for edge in edges:
            source_id = edge.source_id
            target_id = edge.target_id

            # Check if the reverse edge exists
            reverse_key = (target_id, source_id)
            if reverse_key in bidirectional_pairs:
                # We found a bidirectional relationship
                # Mark both edges as bidirectional
                edge.is_bidirectional = True
                bidirectional_pairs[reverse_key].is_bidirectional = True
            else:
                # Store this edge for potential future matching
                bidirectional_pairs[(source_id, target_id)] = edge

    def _detect_transitive_relationships(self) -> None:
        """Detect transitive relationships in the dependency graph.

        A transitive relationship exists when there is a path from A to C through B,
        but also a direct edge from A to C.
        """
        # Build a NetworkX graph for path analysis
        import networkx as nx
        G = nx.DiGraph()

        # Add all edges to the NetworkX graph
        for edge in self.dependency_graph.edges:
            G.add_edge(edge.source_id, edge.target_id)

        # Check each edge to see if it's part of a transitive relationship
        for edge in self.dependency_graph.edges:
            source_id = edge.source_id
            target_id = edge.target_id

            # Remove the direct edge temporarily
            if G.has_edge(source_id, target_id):
                G.remove_edge(source_id, target_id)

                # Check if there's still a path from source to target
                try:
                    path = nx.shortest_path(G, source=source_id, target=target_id)
                    if len(path) > 2:  # Path exists with intermediate nodes
                        # This is a transitive relationship
                        edge.is_transitive = True
                        edge.transitive_path_length = len(path) - 1  # Number of edges in the path
                except nx.NetworkXNoPath:
                    # No path exists, so this is not a transitive relationship
                    pass

                # Restore the edge
                G.add_edge(source_id, target_id)

    def _calculate_relationship_frequencies(self) -> None:
        """Calculate the frequency of each relationship type between nodes.

        This method counts how many times the same relationship occurs between
        the same pair of nodes.
        """
        # Create a dictionary to track frequencies
        relationship_counts = {}

        # Count occurrences of each relationship
        for edge in self.dependency_graph.edges:
            key = (edge.source_id, edge.target_id, edge.type.name)
            if key in relationship_counts:
                relationship_counts[key] += 1
            else:
                relationship_counts[key] = 1

        # Update frequency for each edge
        for edge in self.dependency_graph.edges:
            key = (edge.source_id, edge.target_id, edge.type.name)
            edge.frequency = relationship_counts[key]

    def _assign_group_ids(self, chunks: List['CodeChunk']) -> None:
        """Assign group IDs to relationships based on package/module membership.

        Args:
            chunks: List of code chunks to analyze
        """
        # Create a map of node IDs to package/module names
        node_to_package = {}

        # Extract package information from chunks
        for chunk in chunks:
            if chunk.qualified_name:
                # Extract package from qualified name (everything before the last dot)
                parts = chunk.qualified_name.split('.')
                if len(parts) > 1:
                    package = '.'.join(parts[:-1])
                    node_to_package[chunk.node_id] = package

        # Assign group IDs to edges based on package membership
        for edge in self.dependency_graph.edges:
            source_package = node_to_package.get(edge.source_id)
            target_package = node_to_package.get(edge.target_id)

            if source_package and target_package:
                if source_package == target_package:
                    # Intra-package relationship
                    edge.group_id = source_package
                else:
                    # Inter-package relationship
                    edge.group_id = f"{source_package}→{target_package}"

    def _infer_relationships(self, chunks: List['CodeChunk']) -> None:
        """Infer additional relationships based on patterns in the code.

        This method looks for patterns that suggest relationships that aren't
        explicitly stated in the code.

        Args:
            chunks: List of code chunks to analyze
        """
        # Create a map of class names to chunks for quick lookup
        class_map = {}
        for chunk in chunks:
            if chunk.chunk_type in ['class_declaration', 'interface_declaration', 'enum_declaration']:
                class_map[chunk.name] = chunk
                # Also map by qualified name if available
                if chunk.qualified_name:
                    class_map[chunk.qualified_name] = chunk

        # Look for naming patterns that suggest relationships
        for chunk in chunks:
            if chunk.chunk_type == 'class_declaration':
                # Look for classes with similar names (e.g., UserService and UserRepository)
                base_name = self._extract_base_name(chunk.name)
                if base_name:
                    for other_name, other_chunk in class_map.items():
                        if chunk.node_id != other_chunk.node_id:
                            other_base = self._extract_base_name(other_name)
                            if base_name == other_base:
                                # These classes likely have a relationship
                                dependency = Dependency(
                                    source_id=chunk.node_id,
                                    target_id=other_chunk.node_id,
                                    dep_type=DependencyType.USES,
                                    strength=0.5,  # Moderate strength for inferred relationships
                                    is_direct=False,
                                    is_required=False,
                                    description=f"Inferred relationship between {chunk.name} and {other_chunk.name} based on naming pattern",
                                    is_inferred=True,
                                    inference_confidence=0.7  # Moderate confidence
                                )
                                self.dependency_graph.add_edge(dependency)

    def _extract_base_name(self, class_name: str) -> Optional[str]:
        """Extract the base name from a class name.

        For example, UserService, UserRepository, UserController all have the base name "User".

        Args:
            class_name: Name of the class

        Returns:
            Base name or None if no pattern is found
        """
        # Common suffixes that indicate a pattern
        common_suffixes = [
            'Service', 'Repository', 'Controller', 'Manager', 'Handler', 'Provider',
            'Factory', 'Builder', 'Adapter', 'Impl', 'Interface', 'Abstract', 'Base'
        ]

        for suffix in common_suffixes:
            if class_name.endswith(suffix) and len(class_name) > len(suffix):
                return class_name[:-len(suffix)]

        return None