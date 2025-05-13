"""
Dependency graph builder module.

This module provides functionality to build dependency graphs from code chunks
and store them in the database.
"""

import os
import logging
import json
from typing import Dict, List, Set, Optional, Any, Tuple
from pathlib import Path

from ..chunking.dependency_analyzer import DependencyAnalyzer, DependencyGraph
from ..chunking.dependency_types import DependencyType, Dependency
from ..database.lancedb_manager import LanceDBManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DependencyGraphBuilder:
    """Builder for dependency graphs from code chunks."""

    def __init__(
        self,
        db_manager: Optional[LanceDBManager] = None,
        db_path: Optional[str] = None,
        use_minimal_schema: bool = True
    ):
        """Initialize the dependency graph builder.

        Args:
            db_manager: LanceDB manager instance (optional)
            db_path: Path to the LanceDB database (optional)
            use_minimal_schema: Whether to use the minimal schema
        """
        self.db_manager = db_manager
        self.db_path = db_path
        self.use_minimal_schema = use_minimal_schema
        self.dependency_analyzer = DependencyAnalyzer()

        # Connect to the database if not provided
        if self.db_manager is None and self.db_path is not None:
            self.db_manager = LanceDBManager(
                db_path=self.db_path,
                use_minimal_schema=self.use_minimal_schema
            )
            self.should_close_db = True
        else:
            self.should_close_db = False

    def build_dependency_graph(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build a dependency graph from code chunks.

        Args:
            chunks: List of code chunk dictionaries

        Returns:
            Dependency graph as a dictionary
        """
        logger.info(f"Building dependency graph from {len(chunks)} chunks...")

        # Convert chunks to the format expected by the dependency analyzer
        from ..chunking.code_chunk import CodeChunk
        code_chunks = []

        for chunk_dict in chunks:
            # Create a minimal CodeChunk object
            chunk = CodeChunk(
                node_id=chunk_dict.get("node_id", ""),
                chunk_type=chunk_dict.get("chunk_type", ""),
                content=chunk_dict.get("content", ""),
                file_path=chunk_dict.get("file_path", ""),
                start_line=chunk_dict.get("start_line", 0),
                end_line=chunk_dict.get("end_line", 0),
                language=chunk_dict.get("language", ""),
                name=chunk_dict.get("name", ""),
                qualified_name=chunk_dict.get("qualified_name", "")
            )

            # Add context if available
            if "context" in chunk_dict:
                if isinstance(chunk_dict["context"], str):
                    try:
                        chunk.context = json.loads(chunk_dict["context"])
                    except json.JSONDecodeError:
                        chunk.context = {}
                else:
                    chunk.context = chunk_dict["context"]

            # Add parent reference if available
            if "parent_id" in chunk_dict:
                # Find the parent chunk
                for parent_dict in chunks:
                    if parent_dict.get("node_id") == chunk_dict["parent_id"]:
                        parent = CodeChunk(
                            node_id=parent_dict.get("node_id", ""),
                            chunk_type=parent_dict.get("chunk_type", ""),
                            content=parent_dict.get("content", ""),
                            file_path=parent_dict.get("file_path", ""),
                            start_line=parent_dict.get("start_line", 0),
                            end_line=parent_dict.get("end_line", 0),
                            language=parent_dict.get("language", ""),
                            name=parent_dict.get("name", ""),
                            qualified_name=parent_dict.get("qualified_name", "")
                        )
                        chunk.parent = parent
                        break

            code_chunks.append(chunk)

        # Create a dependency graph
        dependency_graph = DependencyGraph()

        # Add all chunks as nodes
        for chunk in code_chunks:
            dependency_graph.add_node(
                node_id=chunk.node_id,
                node_type=chunk.chunk_type,
                name=chunk.name or "",
                qualified_name=chunk.qualified_name
            )

        # Extract dependencies from metadata
        for chunk_dict in chunks:
            if "metadata" in chunk_dict and isinstance(chunk_dict["metadata"], dict):
                if "dependencies" in chunk_dict["metadata"]:
                    deps = chunk_dict["metadata"]["dependencies"]
                    if isinstance(deps, list):
                        for dep_dict in deps:
                            # Create a dependency object
                            from ..chunking.dependency_types import DependencyType, Dependency

                            # Get the dependency type
                            dep_type_str = dep_dict.get("type", "UNKNOWN")
                            try:
                                dep_type = DependencyType[dep_type_str]
                            except (KeyError, ValueError):
                                dep_type = DependencyType.UNKNOWN

                            # Create the dependency
                            dependency = Dependency(
                                source_id=dep_dict.get("source_id", ""),
                                target_id=dep_dict.get("target_id", ""),
                                dep_type=dep_type,
                                strength=dep_dict.get("strength", 1.0),
                                is_direct=dep_dict.get("is_direct", True),
                                is_required=dep_dict.get("is_required", True),
                                description=dep_dict.get("description", "")
                            )

                            # Add the dependency to the graph
                            dependency_graph.add_edge(dependency)

        # Calculate metrics
        dependency_graph.calculate_metrics()

        # Convert to dictionary
        graph_dict = dependency_graph.to_dict()

        logger.info(f"Built dependency graph with {len(graph_dict['nodes'])} nodes and {len(graph_dict['edges'])} edges")

        return graph_dict

    def store_dependencies(self, dependency_graph: Dict[str, Any]) -> None:
        """Store dependencies from a dependency graph in the database.

        Args:
            dependency_graph: Dependency graph as a dictionary
        """
        if self.db_manager is None:
            logger.warning("No database manager provided, cannot store dependencies")
            return

        logger.info(f"Storing {len(dependency_graph['edges'])} dependencies in the database...")

        # Convert edges to the format expected by the database
        dependencies = []

        for edge in dependency_graph['edges']:
            # Create a dependency dictionary
            dependency = {
                "source_id": edge["source_id"],
                "target_id": edge["target_id"],
                "type": edge["type"],
                "strength": edge["strength"],
                "is_direct": edge["is_direct"],
                "is_required": edge["is_required"],
                "description": edge["description"]
            }

            # Add locations if available
            if "locations" in edge and edge["locations"]:
                dependency["locations"] = json.dumps(edge["locations"])

            dependencies.append(dependency)

        # Store in the database
        self.db_manager.add_dependencies(dependencies)

        logger.info(f"Stored {len(dependencies)} dependencies in the database")

    def get_dependencies_for_chunk(self, chunk_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """Get dependencies for a specific chunk.

        Args:
            chunk_id: ID of the chunk

        Returns:
            Dictionary with incoming and outgoing dependencies
        """
        if self.db_manager is None:
            logger.warning("No database manager provided, cannot get dependencies")
            return {"incoming": [], "outgoing": []}

        logger.info(f"Getting dependencies for chunk {chunk_id}...")

        # Get incoming dependencies (where this chunk is the target)
        incoming = self.db_manager.get_dependencies(target_id=chunk_id)

        # Get outgoing dependencies (where this chunk is the source)
        outgoing = self.db_manager.get_dependencies(source_id=chunk_id)

        logger.info(f"Found {len(incoming)} incoming and {len(outgoing)} outgoing dependencies")

        return {
            "incoming": incoming,
            "outgoing": outgoing
        }

    def close(self) -> None:
        """Close the database connection if it was opened by this builder."""
        if self.should_close_db and self.db_manager is not None:
            self.db_manager.close()
            self.db_manager = None
            logger.info("Closed database connection")


def build_and_store_dependency_graph(
    chunks: List[Dict[str, Any]],
    db_path: Optional[str] = None,
    use_minimal_schema: bool = True,
    store_in_db: bool = False
) -> Dict[str, Any]:
    """Build a dependency graph from code chunks and optionally store it in the database.

    Args:
        chunks: List of code chunk dictionaries
        db_path: Path to the LanceDB database
        use_minimal_schema: Whether to use the minimal schema
        store_in_db: Whether to store dependencies in the database

    Returns:
        Dependency graph as a dictionary
    """
    # Create a builder
    builder = DependencyGraphBuilder(
        db_path=db_path if store_in_db else None,
        use_minimal_schema=use_minimal_schema
    )

    try:
        # Build the dependency graph
        graph = builder.build_dependency_graph(chunks)

        # Store the dependencies if requested
        if store_in_db:
            builder.store_dependencies(graph)

        return graph

    finally:
        # Close the builder
        builder.close()
