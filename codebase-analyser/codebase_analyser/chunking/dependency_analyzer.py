"""
Dependency analyzer for code chunks.
"""

import re
from typing import Dict, List, Set, Optional, Any, Tuple
from pathlib import Path

from tree_sitter import Node, Tree

from .dependency_types import DependencyType, Dependency, DependencyLocation
from ..utils.ast_utils import find_nodes_by_type, get_node_text, get_node_location


class DependencyGraph:
    """Represents a graph of dependencies between code chunks."""

    def __init__(self):
        """Initialize an empty dependency graph."""
        self.nodes = {}  # Dict[node_id, node_metadata]
        self.edges = []  # List of dependencies
        self.metrics = {
            "coupling_score": 0.0,
            "cohesion_score": 0.0,
            "dependency_depth": 0,
            "cyclic_dependencies": []
        }

    def add_node(self, node_id: str, node_type: str, name: str, qualified_name: Optional[str] = None) -> None:
        """Add a node to the graph.

        Args:
            node_id: Unique identifier for the node
            node_type: Type of the node (class, method, etc.)
            name: Name of the node
            qualified_name: Fully qualified name of the node
        """
        self.nodes[node_id] = {
            "id": node_id,
            "type": node_type,
            "name": name,
            "qualified_name": qualified_name or name
        }

    def add_edge(self, dependency: Dependency) -> None:
        """Add an edge (dependency) to the graph.

        Args:
            dependency: The dependency to add
        """
        self.edges.append(dependency)

    def calculate_metrics(self) -> None:
        """Calculate graph-level metrics."""
        if not self.nodes or not self.edges:
            return

        # Calculate coupling score (ratio of actual dependencies to possible dependencies)
        n = len(self.nodes)
        max_dependencies = n * (n - 1)  # Maximum possible directed dependencies
        actual_dependencies = len(self.edges)
        self.metrics["coupling_score"] = actual_dependencies / max_dependencies if max_dependencies > 0 else 0

        # Calculate dependency depth (longest path in the dependency graph)
        self.metrics["dependency_depth"] = self._calculate_dependency_depth()

        # Find cyclic dependencies
        self.metrics["cyclic_dependencies"] = self._find_cycles()

        # Calculate cohesion score (inverse of the number of connected components)
        connected_components = self._find_connected_components()
        self.metrics["cohesion_score"] = 1.0 / len(connected_components) if connected_components else 0

    def _calculate_dependency_depth(self) -> int:
        """Calculate the maximum dependency depth (longest path)."""
        # Build adjacency list
        adj_list = {node_id: [] for node_id in self.nodes}
        for edge in self.edges:
            adj_list[edge.source_id].append(edge.target_id)

        # Find longest path using DFS
        visited = set()
        memo = {}

        def dfs(node_id):
            if node_id in memo:
                return memo[node_id]

            if node_id in visited:
                return 0  # Cycle detected, return 0 to avoid infinite recursion

            visited.add(node_id)
            max_depth = 0

            for neighbor in adj_list[node_id]:
                max_depth = max(max_depth, 1 + dfs(neighbor))

            visited.remove(node_id)
            memo[node_id] = max_depth
            return max_depth

        max_depth = 0
        for node_id in self.nodes:
            max_depth = max(max_depth, dfs(node_id))

        return max_depth

    def _find_cycles(self) -> List[List[str]]:
        """Find cycles in the dependency graph."""
        cycles = []

        # Build adjacency list
        adj_list = {node_id: [] for node_id in self.nodes}
        for edge in self.edges:
            adj_list[edge.source_id].append(edge.target_id)

        # DFS to find cycles
        def find_cycle(node_id, path, visited):
            if node_id in path:
                cycle_start = path.index(node_id)
                cycles.append(path[cycle_start:] + [node_id])
                return

            if node_id in visited:
                return

            visited.add(node_id)
            path.append(node_id)

            for neighbor in adj_list[node_id]:
                find_cycle(neighbor, path.copy(), visited)

            path.pop()

        visited = set()
        for node_id in self.nodes:
            if node_id not in visited:
                find_cycle(node_id, [], visited)

        return cycles

    def _find_connected_components(self) -> List[Set[str]]:
        """Find connected components in the undirected version of the graph."""
        # Build undirected adjacency list
        adj_list = {node_id: set() for node_id in self.nodes}
        for edge in self.edges:
            adj_list[edge.source_id].add(edge.target_id)
            adj_list[edge.target_id].add(edge.source_id)

        # Find connected components using DFS
        visited = set()
        components = []

        def dfs(node_id, component):
            visited.add(node_id)
            component.add(node_id)

            for neighbor in adj_list[node_id]:
                if neighbor not in visited:
                    dfs(neighbor, component)

        for node_id in self.nodes:
            if node_id not in visited:
                component = set()
                dfs(node_id, component)
                components.append(component)

        return components

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "nodes": list(self.nodes.values()),
            "edges": [edge.to_dict() for edge in self.edges],
            "metrics": self.metrics
        }


class DependencyAnalyzer:
    """Analyzes dependencies between code chunks."""

    def __init__(self):
        """Initialize the dependency analyzer."""
        self.dependency_graph = DependencyGraph()
        self.chunk_metrics = {}  # Dict[chunk_id, metrics]

    def analyze_dependencies(self, chunks: List['CodeChunk']) -> DependencyGraph:
        """Analyze dependencies between chunks.

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

        # Calculate graph-level metrics
        self.dependency_graph.calculate_metrics()

        # Calculate chunk-level metrics
        self._calculate_chunk_metrics(chunks)

        return self.dependency_graph

    def _analyze_inheritance_dependencies(self, chunks: List['CodeChunk']) -> None:
        """Analyze inheritance dependencies (extends, implements).

        Args:
            chunks: List of code chunks to analyze
        """
        for chunk in chunks:
            # Skip non-class chunks
            if chunk.chunk_type not in ['class_declaration', 'interface_declaration', 'enum_declaration']:
                continue

            # Check for extends relationship
            if 'extends' in chunk.context:
                extends_name = chunk.context['extends']
                if extends_name:
                    # Find the target chunk
                    for target in chunks:
                        if (target.chunk_type in ['class_declaration', 'interface_declaration'] and
                            target.name and target.name in extends_name):
                            # Create an EXTENDS dependency
                            dependency = Dependency(
                                source_id=chunk.node_id,
                                target_id=target.node_id,
                                dep_type=DependencyType.EXTENDS,
                                strength=1.0,
                                is_required=True,
                                description=f"{chunk.name} extends {target.name}"
                            )
                            self.dependency_graph.add_edge(dependency)

            # Check for implements relationship
            if 'implements' in chunk.context:
                implements_name = chunk.context['implements']
                if implements_name:
                    # Find the target chunks
                    for target in chunks:
                        if (target.chunk_type == 'interface_declaration' and
                            target.name and target.name in implements_name):
                            # Create an IMPLEMENTS dependency
                            dependency = Dependency(
                                source_id=chunk.node_id,
                                target_id=target.node_id,
                                dep_type=DependencyType.IMPLEMENTS,
                                strength=1.0,
                                is_required=True,
                                description=f"{chunk.name} implements {target.name}"
                            )
                            self.dependency_graph.add_edge(dependency)

    def _analyze_method_call_dependencies(self, chunks: List['CodeChunk']) -> None:
        """Analyze method call dependencies.

        Args:
            chunks: List of code chunks to analyze
        """
        # Get all method chunks
        method_chunks = [c for c in chunks if c.chunk_type in ['method_declaration', 'constructor_declaration']]

        for chunk in method_chunks:
            # Skip chunks without content
            if not chunk.content:
                continue

            # For each method chunk, check if it calls other methods
            for target in method_chunks:
                # Skip self-references
                if target == chunk:
                    continue

                # Skip targets without names
                if not target.name:
                    continue

                # Check if the method name appears in the content
                if target.name in chunk.content:
                    # Simple heuristic: check if the name is used as a method call
                    pattern = r'\b' + re.escape(target.name) + r'\s*\('
                    matches = re.finditer(pattern, chunk.content)

                    for match in matches:
                        # Create a CALLS dependency
                        dependency = Dependency(
                            source_id=chunk.node_id,
                            target_id=target.node_id,
                            dep_type=DependencyType.CALLS,
                            strength=0.8,  # Method calls are strong but not as strong as inheritance
                            is_required=True,
                            description=f"{chunk.name} calls {target.name}"
                        )

                        # Add the location of the call
                        line_number = chunk.start_line
                        for i, line in enumerate(chunk.content.split('\n')):
                            if match.group(0) in line:
                                line_number = chunk.start_line + i
                                break

                        dependency.add_location(
                            line=line_number,
                            column=match.start(),
                            snippet=match.group(0)
                        )

                        self.dependency_graph.add_edge(dependency)

    def _analyze_field_usage_dependencies(self, chunks: List['CodeChunk']) -> None:
        """Analyze field usage dependencies.

        Args:
            chunks: List of code chunks to analyze
        """
        # This is a simplified implementation that could be enhanced with more sophisticated analysis
        # For now, we'll just check for field names in method bodies

        # Get all class chunks
        class_chunks = [c for c in chunks if c.chunk_type in ['class_declaration', 'interface_declaration']]

        # Get all method chunks
        method_chunks = [c for c in chunks if c.chunk_type in ['method_declaration', 'constructor_declaration']]

        # For each method, check if it uses fields from classes
        for method in method_chunks:
            # Skip methods without content
            if not method.content:
                continue

            # Get the parent class of this method
            parent_class = method.parent

            # Skip methods without a parent class
            if not parent_class or parent_class.chunk_type not in ['class_declaration', 'interface_declaration']:
                continue

            # For each class, check if the method uses its fields
            for cls in class_chunks:
                # Skip the parent class (we're looking for usage of fields from other classes)
                if cls == parent_class:
                    continue

                # Skip classes without a name
                if not cls.name:
                    continue

                # Check if the class name appears in the method content
                if cls.name in method.content:
                    # Create a USES dependency
                    dependency = Dependency(
                        source_id=method.node_id,
                        target_id=cls.node_id,
                        dep_type=DependencyType.USES,
                        strength=0.6,  # Field usage is moderately strong
                        is_required=True,
                        description=f"{method.name} uses fields from {cls.name}"
                    )

                    # Add a generic location (could be improved with more detailed analysis)
                    dependency.add_location(
                        line=method.start_line,
                        snippet=f"Usage of {cls.name} in {method.name}"
                    )

                    self.dependency_graph.add_edge(dependency)

    def _analyze_container_dependencies(self, chunks: List['CodeChunk']) -> None:
        """Analyze container dependencies (class contains method).

        Args:
            chunks: List of code chunks to analyze
        """
        for chunk in chunks:
            # Skip chunks without a parent
            if not chunk.parent:
                continue

            # Create a CONTAINS dependency from parent to child
            dependency = Dependency(
                source_id=chunk.parent.node_id,
                target_id=chunk.node_id,
                dep_type=DependencyType.CONTAINS,
                strength=1.0,  # Container relationship is very strong
                is_required=True,
                description=f"{chunk.parent.name or 'Parent'} contains {chunk.name or 'Child'}"
            )

            self.dependency_graph.add_edge(dependency)

    def _analyze_import_dependencies(self, chunks: List['CodeChunk']) -> None:
        """Analyze import dependencies.

        Args:
            chunks: List of code chunks to analyze
        """
        # Get all file-level chunks
        file_chunks = [c for c in chunks if c.chunk_type == 'file']

        for file_chunk in file_chunks:
            # Skip chunks without imports
            if 'imports' not in file_chunk.context or not file_chunk.context['imports']:
                continue

            imports = file_chunk.context['imports']

            # For each import, check if it matches any other chunk's qualified name
            for imp in imports:
                for target in chunks:
                    # Skip chunks without a qualified name
                    if not target.qualified_name:
                        continue

                    # Check if the import matches the target's qualified name
                    if imp == target.qualified_name or imp.endswith('.' + target.qualified_name):
                        # Create an IMPORTS dependency
                        dependency = Dependency(
                            source_id=file_chunk.node_id,
                            target_id=target.node_id,
                            dep_type=DependencyType.IMPORTS,
                            strength=0.7,  # Import relationship is moderately strong
                            is_required=True,
                            description=f"{file_chunk.name} imports {target.qualified_name}"
                        )

                        self.dependency_graph.add_edge(dependency)

    def _calculate_chunk_metrics(self, chunks: List['CodeChunk']) -> None:
        """Calculate metrics for each chunk.

        Args:
            chunks: List of code chunks to analyze
        """
        # For each chunk, calculate metrics based on its dependencies
        for chunk in chunks:
            # Get incoming and outgoing dependencies
            incoming = [e for e in self.dependency_graph.edges if e.target_id == chunk.node_id]
            outgoing = [e for e in self.dependency_graph.edges if e.source_id == chunk.node_id]

            # Calculate fan-in and fan-out
            fan_in = len(incoming)
            fan_out = len(outgoing)

            # Calculate instability (I = fan-out / (fan-in + fan-out))
            instability = fan_out / (fan_in + fan_out) if (fan_in + fan_out) > 0 else 0

            # Calculate abstractness (simplified: 1.0 for interfaces, 0.0 for concrete classes)
            abstractness = 1.0 if chunk.chunk_type == 'interface_declaration' else 0.0

            # Calculate distance from main sequence (|A + I - 1|)
            distance = abs(abstractness + instability - 1.0)

            # Store metrics for this chunk
            self.chunk_metrics[chunk.node_id] = {
                "fan_in": fan_in,
                "fan_out": fan_out,
                "instability": instability,
                "abstractness": abstractness,
                "distance_from_main_sequence": distance,
                "incoming_dependencies": [
                    {
                        "chunk_id": e.source_id,
                        "type": e.type.name,
                        "strength": e.strength
                    } for e in incoming
                ],
                "outgoing_dependencies": [
                    {
                        "chunk_id": e.target_id,
                        "type": e.type.name,
                        "strength": e.strength
                    } for e in outgoing
                ]
            }

            # Add metrics to the chunk's metadata
            chunk.metadata["dependency_metrics"] = self.chunk_metrics[chunk.node_id]
