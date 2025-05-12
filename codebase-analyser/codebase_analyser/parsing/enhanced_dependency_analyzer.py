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
