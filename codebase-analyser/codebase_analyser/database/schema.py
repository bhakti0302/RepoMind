"""
Schema definitions for code embeddings and dependency relationships.

This module provides schema definitions for storing code chunks and their relationships
in the vector database.
"""

import pyarrow as pa
from typing import Dict, List, Optional, Any


class SchemaDefinitions:
    """Schema definitions for code embeddings and dependency relationships."""

    @staticmethod
    def get_code_chunks_schema(embedding_dim: int = 768) -> Dict[str, pa.DataType]:
        """Get the schema for code chunks.

        Args:
            embedding_dim: Dimension of the embedding vectors (default: 768 for CodeBERT)

        Returns:
            Dictionary mapping field names to PyArrow data types
        """
        return {
            # Vector embedding (required for similarity search)
            "embedding": pa.list_(pa.float32(), embedding_dim),

            # Core identification fields
            "node_id": pa.string(),  # Unique identifier for the chunk
            "chunk_type": pa.string(),  # Type of chunk (file, class, method, etc.)

            # Content and location
            "content": pa.string(),  # The actual code content
            "file_path": pa.string(),  # Path to the source file
            "start_line": pa.int32(),  # Starting line number (1-based)
            "end_line": pa.int32(),  # Ending line number (1-based)
            "language": pa.string(),  # Programming language

            # Naming and identification
            "name": pa.string(),  # Name of the chunk (class name, method name, etc.)
            "qualified_name": pa.string(),  # Fully qualified name

            # Metadata and context (stored as JSON strings)
            "metadata": pa.string(),  # Additional metadata as JSON
            "context": pa.string(),  # Context information as JSON

            # Optional fields for advanced queries
            "parent_id": pa.string(),  # ID of the parent chunk
            "root_id": pa.string(),  # ID of the root chunk (usually file)
            "depth": pa.int32(),  # Depth in the chunk hierarchy

            # Metrics and statistics
            "token_count": pa.int32(),  # Number of tokens in the chunk
            "complexity": pa.float32(),  # Complexity score (e.g., cyclomatic complexity)
            "importance": pa.float32(),  # Importance score (0.0 to 1.0)

            # Timestamps (using int64 to avoid precision issues)
            "created_at": pa.int64(),  # Creation timestamp in milliseconds
            "updated_at": pa.int64(),  # Last update timestamp in milliseconds

            # Tags and categories
            "tags": pa.list_(pa.string()),  # List of tags
            "categories": pa.list_(pa.string()),  # List of categories


        }

    @staticmethod
    def get_dependencies_schema() -> Dict[str, pa.DataType]:
        """Get the schema for dependency relationships.

        Returns:
            Dictionary mapping field names to PyArrow data types
        """
        return {
            # Core relationship fields
            "source_id": pa.string(),  # ID of the source chunk
            "target_id": pa.string(),  # ID of the target chunk
            "type": pa.string(),  # Type of dependency (IMPORTS, EXTENDS, CALLS, etc.)

            # Relationship properties
            "strength": pa.float32(),  # Strength of the dependency (0.0 to 1.0)
            "is_direct": pa.bool_(),  # Whether this is a direct dependency
            "is_required": pa.bool_(),  # Whether this dependency is required for compilation
            "description": pa.string(),  # Human-readable description

            # Locations of the dependency in the source code
            "locations": pa.string(),  # JSON array of locations

            # Metrics and statistics
            "frequency": pa.int32(),  # Number of times this dependency occurs
            "impact": pa.float32(),  # Impact score (0.0 to 1.0)

            # Timestamps (using int64 to avoid precision issues)
            "created_at": pa.int64(),  # Creation timestamp in milliseconds
            "updated_at": pa.int64(),  # Last update timestamp in milliseconds
        }

    @staticmethod
    def get_embedding_metadata_schema() -> Dict[str, pa.DataType]:
        """Get the schema for embedding metadata.

        Returns:
            Dictionary mapping field names to PyArrow data types
        """
        return {
            # Core identification fields
            "embedding_id": pa.string(),  # Unique identifier for the embedding
            "chunk_id": pa.string(),  # ID of the associated chunk

            # Embedding properties
            "model_name": pa.string(),  # Name of the model used to generate the embedding
            "model_version": pa.string(),  # Version of the model
            "embedding_type": pa.string(),  # Type of embedding (code, comment, etc.)
            "embedding_dim": pa.int32(),  # Dimension of the embedding

            # Quality metrics
            "quality_score": pa.float32(),  # Quality score (0.0 to 1.0)
            "confidence": pa.float32(),  # Confidence score (0.0 to 1.0)

            # Timestamps (using int64 to avoid precision issues)
            "created_at": pa.int64(),  # Creation timestamp in milliseconds
            "updated_at": pa.int64(),  # Last update timestamp in milliseconds
        }

    @staticmethod
    def get_minimal_code_chunks_schema(embedding_dim: int = 768) -> Dict[str, pa.DataType]:
        """Get a minimal schema for code chunks with only essential fields.

        Args:
            embedding_dim: Dimension of the embedding vectors (default: 768 for CodeBERT)

        Returns:
            Dictionary mapping field names to PyArrow data types
        """
        return {
            "embedding": pa.list_(pa.float32(), embedding_dim),
            "node_id": pa.string(),
            "chunk_type": pa.string(),
            "content": pa.string(),
            "file_path": pa.string(),
            "start_line": pa.int32(),
            "end_line": pa.int32(),
            "language": pa.string(),
            "name": pa.string(),
            "qualified_name": pa.string(),
            "metadata": pa.string(),
            "context": pa.string(),

        }

    @staticmethod
    def get_minimal_dependencies_schema() -> Dict[str, pa.DataType]:
        """Get a minimal schema for dependency relationships with only essential fields.

        Returns:
            Dictionary mapping field names to PyArrow data types
        """
        return {
            "source_id": pa.string(),
            "target_id": pa.string(),
            "type": pa.string(),
            "strength": pa.float32(),
            "is_direct": pa.bool_(),
            "is_required": pa.bool_(),
            "description": pa.string(),

        }
