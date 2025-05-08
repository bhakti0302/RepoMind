"""
Unified storage for vectors and graph metadata.

This module provides a unified storage system that integrates code embeddings with
dependency graph metadata, allowing for more efficient querying and better integration
between vector search and graph-based filtering.
"""

import os
import json
import logging
import numpy as np
from typing import Dict, List, Set, Optional, Any, Tuple, Union

from .lancedb_manager import LanceDBManager
from ..graph.dependency_graph_builder import DependencyGraphBuilder, build_and_store_dependency_graph

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UnifiedStorage:
    """Unified storage for vectors and graph metadata."""

    def __init__(
        self,
        db_path: Optional[str] = None,
        embedding_dim: int = 768,
        use_minimal_schema: bool = True,
        create_if_not_exists: bool = True,
        read_only: bool = False
    ):
        """Initialize the unified storage.

        Args:
            db_path: Path to the LanceDB database
            embedding_dim: Dimension of the embedding vectors
            use_minimal_schema: Whether to use the minimal schema
            create_if_not_exists: Whether to create the database if it doesn't exist
            read_only: Whether to open the database in read-only mode
        """
        self.db_path = db_path
        self.embedding_dim = embedding_dim
        self.use_minimal_schema = use_minimal_schema
        self.create_if_not_exists = create_if_not_exists
        self.read_only = read_only

        # Connect to the database
        self.db_manager = LanceDBManager(
            db_path=self.db_path,
            embedding_dim=self.embedding_dim,
            use_minimal_schema=self.use_minimal_schema,
            create_if_not_exists=self.create_if_not_exists,
            read_only=self.read_only
        )

        # Create a dependency graph builder
        self.graph_builder = DependencyGraphBuilder(
            db_manager=self.db_manager,
            use_minimal_schema=self.use_minimal_schema
        )

    def close(self) -> None:
        """Close the database connection."""
        if self.db_manager:
            self.db_manager.close()
            self.db_manager = None
            logger.info("Closed database connection")

    def add_code_chunks_with_graph_metadata(
        self,
        chunks: List[Dict[str, Any]],
        dependencies: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """Add code chunks with graph metadata to the database.

        Args:
            chunks: List of code chunk dictionaries
            dependencies: List of dependency dictionaries (optional)
        """
        if not chunks:
            logger.warning("No chunks provided, skipping")
            return

        logger.info(f"Adding {len(chunks)} code chunks with graph metadata")

        # Build the dependency graph
        graph = self.graph_builder.build_dependency_graph(chunks)

        # Extract dependencies from the graph if not provided
        if dependencies is None:
            dependencies = []
            for edge in graph["edges"]:
                dependency = {
                    "source_id": edge["source_id"],
                    "target_id": edge["target_id"],
                    "type": edge["type"],
                    "strength": edge["strength"],
                    "is_direct": edge["is_direct"],
                    "is_required": edge["is_required"],
                    "description": edge["description"]
                }
                if "locations" in edge and edge["locations"]:
                    dependency["locations"] = json.dumps(edge["locations"])
                dependencies.append(dependency)

        # Calculate graph metrics for each chunk
        self._calculate_graph_metrics(chunks, graph)

        # Add the chunks to the database using the existing flow
        self.db_manager.add_code_chunks(chunks)

        # Add the dependencies to the database using the existing flow
        self.db_manager.add_dependencies(dependencies)

        logger.info(f"Added {len(chunks)} code chunks with graph metadata")

    def _calculate_graph_metrics(self, chunks: List[Dict[str, Any]], graph: Dict[str, Any]) -> None:
        """Calculate graph metrics for each chunk.

        Args:
            chunks: List of code chunk dictionaries
            graph: Dependency graph dictionary
        """
        # For each chunk, calculate graph-related metrics
        for chunk in chunks:
            # Initialize metadata if not present
            if "metadata" not in chunk:
                chunk["metadata"] = {}
            elif isinstance(chunk["metadata"], str):
                try:
                    chunk["metadata"] = json.loads(chunk["metadata"])
                except json.JSONDecodeError:
                    chunk["metadata"] = {}

            # Get incoming and outgoing dependencies
            incoming = [e for e in graph["edges"] if e["target_id"] == chunk["node_id"]]
            outgoing = [e for e in graph["edges"] if e["source_id"] == chunk["node_id"]]

            # Calculate metrics
            incoming_count = len(incoming)
            outgoing_count = len(outgoing)
            dependency_count = incoming_count + outgoing_count
            in_cycle = any(cycle for cycle in graph["metrics"]["cyclic_dependencies"] if chunk["node_id"] in cycle)

            # Determine graph position
            if incoming_count == 0 and outgoing_count > 0:
                graph_position = "root"
            elif incoming_count > 0 and outgoing_count == 0:
                graph_position = "leaf"
            else:
                graph_position = "intermediate"

            # Calculate instability
            instability = outgoing_count / dependency_count if dependency_count > 0 else 0.0

            # Add graph metadata to the chunk
            chunk["metadata"]["graph_metadata"] = {
                "dependency_count": dependency_count,
                "incoming_count": incoming_count,
                "outgoing_count": outgoing_count,
                "in_cycle": in_cycle,
                "graph_position": graph_position,
                "instability": instability,
                "incoming_dependencies": [e["source_id"] for e in incoming],
                "outgoing_dependencies": [e["target_id"] for e in outgoing]
            }

            # Add dependency type flags
            chunk["metadata"]["graph_metadata"]["has_imports"] = any(e["type"] == "IMPORTS" for e in incoming + outgoing)
            chunk["metadata"]["graph_metadata"]["has_extends"] = any(e["type"] == "EXTENDS" for e in incoming + outgoing)
            chunk["metadata"]["graph_metadata"]["has_implements"] = any(e["type"] == "IMPLEMENTS" for e in incoming + outgoing)
            chunk["metadata"]["graph_metadata"]["has_calls"] = any(e["type"] == "CALLS" for e in incoming + outgoing)
            chunk["metadata"]["graph_metadata"]["has_uses"] = any(e["type"] == "USES" for e in incoming + outgoing)

            # Convert metadata back to string if needed
            if isinstance(chunk["metadata"], dict):
                chunk["metadata"] = json.dumps(chunk["metadata"])

    def search_with_dependencies(
        self,
        query_embedding: List[float],
        dependency_filter: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """Search for code chunks by vector similarity and dependency filters.

        Args:
            query_embedding: Query embedding vector
            dependency_filter: Dictionary of dependency filters
            limit: Maximum number of results to return
            include_metadata: Whether to include metadata in the results

        Returns:
            List of matching code chunks
        """
        # First, search by vector similarity
        results = self.db_manager.search_code_chunks(
            query_embedding=query_embedding,
            limit=limit * 2  # Get more results than needed to allow for filtering
        )

        # If no dependency filter, return the results directly
        if not dependency_filter:
            return results[:limit]

        # Filter results by dependency criteria
        filtered_results = []
        for result in results:
            # Parse metadata
            metadata = {}
            if "metadata" in result and result["metadata"]:
                try:
                    metadata = json.loads(result["metadata"])
                except json.JSONDecodeError:
                    metadata = {}

            # Check if graph metadata exists
            if "graph_metadata" not in metadata:
                continue

            graph_metadata = metadata["graph_metadata"]

            # Apply filters
            matches_filter = True
            for key, value in dependency_filter.items():
                if key not in graph_metadata:
                    matches_filter = False
                    break

                if graph_metadata[key] != value:
                    matches_filter = False
                    break

            if matches_filter:
                filtered_results.append(result)
                if len(filtered_results) >= limit:
                    break

        return filtered_results

    def get_chunk_with_dependencies(self, node_id: str) -> Dict[str, Any]:
        """Get a code chunk with its dependencies.

        Args:
            node_id: ID of the chunk

        Returns:
            Code chunk with dependencies
        """
        # Get the chunk
        chunk = self.db_manager.get_code_chunk(node_id)
        if not chunk:
            return {}

        # Get dependencies
        dependencies = self.graph_builder.get_dependencies_for_chunk(node_id)

        # Add dependencies to the chunk
        if "metadata" in chunk and chunk["metadata"]:
            try:
                metadata = json.loads(chunk["metadata"])
            except json.JSONDecodeError:
                metadata = {}
        else:
            metadata = {}

        metadata["dependencies"] = dependencies
        chunk["metadata"] = json.dumps(metadata)

        return chunk
