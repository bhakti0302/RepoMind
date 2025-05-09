"""
LanceDB Manager for code embeddings and dependency graph storage.

This module provides functionality to initialize, configure, and interact with LanceDB
for storing code embeddings and dependency graph information.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from datetime import datetime

import lancedb
import pyarrow as pa
import numpy as np
from tqdm import tqdm

from .schema import SchemaDefinitions
from .schema_manager import SchemaManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LanceDBManager:
    """Manager for LanceDB operations."""

    def __init__(
        self,
        db_path: Optional[str] = None,
        create_if_not_exists: bool = True,
        read_only: bool = False,
        embedding_dim: int = 384,
        use_minimal_schema: bool = True
    ):
        """Initialize the LanceDB manager.

        Args:
            db_path: Path to the LanceDB database (default: .lancedb in current directory)
            create_if_not_exists: Whether to create the database if it doesn't exist
            read_only: Whether to open the database in read-only mode
            embedding_dim: Dimension of the embedding vectors
            use_minimal_schema: Whether to use the minimal schema (fewer fields)
        """
        self.db_path = db_path or os.path.join(os.getcwd(), '.lancedb')
        self.create_if_not_exists = create_if_not_exists
        self.read_only = read_only
        self.embedding_dim = embedding_dim
        self.use_minimal_schema = use_minimal_schema
        self.db = None
        self.tables = {}

        # Create a schema manager for consistent schema handling
        self.schema_manager = SchemaManager(
            embedding_dim=embedding_dim,
            use_minimal_schema=use_minimal_schema
        )

        # Get canonical schemas from the schema manager
        self.schemas = {
            table_name: schema
            for table_name, schema in self.schema_manager.canonical_schemas.items()
        }

        # Connect to the database
        self._connect()

    def _connect(self) -> None:
        """Connect to the LanceDB database."""
        try:
            # Create the database directory if it doesn't exist
            if self.create_if_not_exists:
                os.makedirs(self.db_path, exist_ok=True)

            # Connect to the database
            # Note: Different versions of LanceDB have different APIs
            try:
                # Try newer version API
                self.db = lancedb.connect(self.db_path, read_only=self.read_only)
            except TypeError:
                # Fall back to older version API
                self.db = lancedb.connect(self.db_path)
                logger.info("Connected using legacy LanceDB API")

            logger.info(f"Connected to LanceDB at {self.db_path}")

            # Get existing tables
            try:
                existing_tables = self.db.table_names()
            except AttributeError:
                # Older versions might not have table_names method
                existing_tables = []
                logger.info("Could not retrieve table names (older LanceDB version)")

            logger.info(f"Found {len(existing_tables)} existing tables: {existing_tables}")

        except Exception as e:
            logger.error(f"Error connecting to LanceDB: {e}")
            raise

    def create_tables(self) -> None:
        """Create tables if they don't exist."""
        try:
            # Check if tables exist
            try:
                existing_tables = self.db.table_names()
            except AttributeError:
                # Older versions might not have table_names method
                # Assume tables don't exist
                existing_tables = []

            # Create code_chunks table if it doesn't exist
            if "code_chunks" not in existing_tables:
                logger.info("Creating code_chunks table")
                schema = pa.schema([
                    pa.field(name, dtype) for name, dtype in self.schemas["code_chunks"].items()
                ])

                # Create empty data for initial table creation
                empty_data = {
                    name: [] for name in self.schemas["code_chunks"].keys()
                }
                empty_data["embedding"] = [[0.0] * self.embedding_dim]  # Add one empty embedding

                # Add timestamps if they exist in the schema
                if "created_at" in self.schemas["code_chunks"]:
                    empty_data["created_at"] = [datetime.now()]
                if "updated_at" in self.schemas["code_chunks"]:
                    empty_data["updated_at"] = [datetime.now()]

                try:
                    # Try newer version API
                    self.db.create_table("code_chunks", schema=schema)
                except (TypeError, AttributeError):
                    # Fall back to older version API - create with data
                    self.db.create_table("code_chunks", data=empty_data)

                logger.info("Created code_chunks table")

            # Create dependencies table if it doesn't exist
            if "dependencies" not in existing_tables:
                logger.info("Creating dependencies table")
                schema = pa.schema([
                    pa.field(name, dtype) for name, dtype in self.schemas["dependencies"].items()
                ])

                # Create empty data for initial table creation
                empty_data = {
                    name: [] for name in self.schemas["dependencies"].keys()
                }
                # Add one empty row
                for name in self.schemas["dependencies"].keys():
                    if name in ["source_id", "target_id", "type", "description", "locations"]:
                        empty_data[name] = [""]
                    elif name in ["strength", "impact"]:
                        empty_data[name] = [0.0]
                    elif name in ["is_direct", "is_required"]:
                        empty_data[name] = [False]
                    elif name in ["frequency"]:
                        empty_data[name] = [0]
                    elif name in ["created_at", "updated_at"]:
                        empty_data[name] = [datetime.now()]

                try:
                    # Try newer version API
                    self.db.create_table("dependencies", schema=schema)
                except (TypeError, AttributeError):
                    # Fall back to older version API - create with data
                    self.db.create_table("dependencies", data=empty_data)

                logger.info("Created dependencies table")

            # Create embedding_metadata table if it doesn't exist and we're using the full schema
            if not self.use_minimal_schema and "embedding_metadata" in self.schemas and "embedding_metadata" not in existing_tables:
                logger.info("Creating embedding_metadata table")
                schema = pa.schema([
                    pa.field(name, dtype) for name, dtype in self.schemas["embedding_metadata"].items()
                ])

                # Create empty data for initial table creation
                empty_data = {
                    name: [] for name in self.schemas["embedding_metadata"].keys()
                }
                # Add one empty row
                for name in self.schemas["embedding_metadata"].keys():
                    if name in ["embedding_id", "chunk_id", "model_name", "model_version", "embedding_type"]:
                        empty_data[name] = [""]
                    elif name in ["embedding_dim"]:
                        empty_data[name] = [self.embedding_dim]
                    elif name in ["quality_score", "confidence"]:
                        empty_data[name] = [0.0]
                    elif name in ["created_at", "updated_at"]:
                        empty_data[name] = [datetime.now()]

                try:
                    # Try newer version API
                    self.db.create_table("embedding_metadata", schema=schema)
                except (TypeError, AttributeError):
                    # Fall back to older version API - create with data
                    self.db.create_table("embedding_metadata", data=empty_data)

                logger.info("Created embedding_metadata table")

            # Open the tables
            try:
                self.tables["code_chunks"] = self.db.open_table("code_chunks")
                self.tables["dependencies"] = self.db.open_table("dependencies")

                # Open embedding_metadata table if it exists and we're using the full schema
                if not self.use_minimal_schema and "embedding_metadata" in self.schemas and "embedding_metadata" in existing_tables:
                    self.tables["embedding_metadata"] = self.db.open_table("embedding_metadata")
            except AttributeError:
                # Older versions might use a different API
                self.tables["code_chunks"] = self.db["code_chunks"]
                self.tables["dependencies"] = self.db["dependencies"]

                # Open embedding_metadata table if it exists and we're using the full schema
                if not self.use_minimal_schema and "embedding_metadata" in self.schemas:
                    try:
                        self.tables["embedding_metadata"] = self.db["embedding_metadata"]
                    except KeyError:
                        # Table might not exist
                        pass

            logger.info("Tables created and opened successfully")

        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise

    def add_code_chunks(self, chunks: List[Dict[str, Any]]) -> None:
        """Add code chunks to the database.

        Args:
            chunks: List of code chunk dictionaries with embeddings
        """
        try:
            if not chunks:
                logger.warning("No chunks to add")
                return

            # Open the code_chunks table if not already open
            if "code_chunks" not in self.tables:
                try:
                    self.tables["code_chunks"] = self.db.open_table("code_chunks")
                except AttributeError:
                    # Older versions might use a different API
                    self.tables["code_chunks"] = self.db["code_chunks"]

            # Use the schema manager to filter chunks according to the canonical schema
            filtered_chunks = self.schema_manager.filter_batch_for_schema("code_chunks", chunks)
            schema_fields = self.schema_manager.get_canonical_field_names("code_chunks")

            # Process each chunk for special fields
            now_timestamp = int(datetime.now().timestamp() * 1000)

            for filtered_chunk in filtered_chunks:
                # Convert metadata and context to JSON strings
                if "metadata" in filtered_chunk and isinstance(filtered_chunk["metadata"], dict):
                    filtered_chunk["metadata"] = json.dumps(filtered_chunk["metadata"])
                if "context" in filtered_chunk and isinstance(filtered_chunk["context"], dict):
                    filtered_chunk["context"] = json.dumps(filtered_chunk["context"])

                # Add timestamps if they exist in the schema
                if "created_at" in schema_fields and "created_at" not in filtered_chunk:
                    filtered_chunk["created_at"] = now_timestamp
                if "updated_at" in schema_fields and "updated_at" not in filtered_chunk:
                    filtered_chunk["updated_at"] = now_timestamp

                # Add default values for optional fields if they exist in the schema
                if "token_count" in schema_fields and "token_count" not in filtered_chunk:
                    # Rough estimate of token count based on content length
                    filtered_chunk["token_count"] = len(filtered_chunk.get("content", "").split())
                if "complexity" in schema_fields and "complexity" not in filtered_chunk:
                    filtered_chunk["complexity"] = 0.0
                if "importance" in schema_fields and "importance" not in filtered_chunk:
                    filtered_chunk["importance"] = 0.5  # Default to medium importance
                if "tags" in schema_fields and "tags" not in filtered_chunk:
                    filtered_chunk["tags"] = []
                if "categories" in schema_fields and "categories" not in filtered_chunk:
                    filtered_chunk["categories"] = []

            # Replace the original chunks with the filtered ones
            chunks = filtered_chunks

            # Add the chunks to the table
            try:
                # Get the actual schema from the table
                table_schema = self.tables["code_chunks"].schema
                schema_names = set(field.name for field in table_schema)

                # Log the actual schema fields
                logger.info(f"Actual schema fields in code_chunks table: {sorted(schema_names)}")

                # Final filtering to ensure only fields in the actual table schema are included
                final_chunks = []
                for chunk in chunks:
                    final_chunk = {k: v for k, v in chunk.items() if k in schema_names}

                    # Ensure all required fields are present
                    for field_name in schema_names:
                        if field_name not in final_chunk:
                            # Add default values for missing fields
                            if field_name == "embedding":
                                final_chunk[field_name] = [0.0] * self.embedding_dim
                            elif field_name in ["node_id", "chunk_type", "content", "file_path",
                                              "language", "name", "qualified_name", "metadata",
                                              "context", "parent_id", "root_id"]:
                                final_chunk[field_name] = ""
                            elif field_name in ["start_line", "end_line", "depth", "token_count"]:
                                final_chunk[field_name] = 0
                            elif field_name in ["complexity", "importance"]:
                                final_chunk[field_name] = 0.0
                            elif field_name in ["created_at", "updated_at"]:
                                # Use integer timestamp to avoid precision issues
                                final_chunk[field_name] = int(datetime.now().timestamp() * 1000)
                            elif field_name in ["tags", "categories"]:
                                final_chunk[field_name] = []

                    final_chunks.append(final_chunk)

                self.tables["code_chunks"].add(final_chunks)
            except AttributeError:
                # Older versions might use a different API
                for chunk in chunks:
                    # Get only the fields that are in the schema
                    schema_fields = set(self.schemas["code_chunks"].keys())
                    filtered_chunk = {k: v for k, v in chunk.items() if k in schema_fields}
                    self.tables["code_chunks"].add_data([filtered_chunk])

            logger.info(f"Added {len(chunks)} code chunks to the database")

        except Exception as e:
            logger.error(f"Error adding code chunks: {e}")
            raise

    def add_dependencies(self, dependencies: List[Dict[str, Any]]) -> None:
        """Add dependencies to the database.

        Args:
            dependencies: List of dependency dictionaries
        """
        try:
            if not dependencies:
                logger.warning("No dependencies to add")
                return

            # Open the dependencies table if not already open
            if "dependencies" not in self.tables:
                try:
                    self.tables["dependencies"] = self.db.open_table("dependencies")
                except AttributeError:
                    # Older versions might use a different API
                    self.tables["dependencies"] = self.db["dependencies"]

            # Use the schema manager to filter dependencies according to the canonical schema
            filtered_deps = self.schema_manager.filter_batch_for_schema("dependencies", dependencies)
            schema_fields = self.schema_manager.get_canonical_field_names("dependencies")

            # Process each dependency for special fields
            now_timestamp = int(datetime.now().timestamp() * 1000)

            for filtered_dep in filtered_deps:
                # Add timestamps if they exist in the schema
                if "created_at" in schema_fields and "created_at" not in filtered_dep:
                    filtered_dep["created_at"] = now_timestamp
                if "updated_at" in schema_fields and "updated_at" not in filtered_dep:
                    filtered_dep["updated_at"] = now_timestamp

            # Replace the original dependencies with the filtered ones
            dependencies = filtered_deps

            # Add the dependencies to the table
            try:
                # Get the actual schema from the table
                table_schema = self.tables["dependencies"].schema
                schema_names = set(field.name for field in table_schema)

                # Log the actual schema fields
                logger.info(f"Actual schema fields in dependencies table: {sorted(schema_names)}")

                # Final filtering to ensure only fields in the actual table schema are included
                final_deps = []
                for dep in dependencies:
                    final_dep = {k: v for k, v in dep.items() if k in schema_names}

                    # Ensure all required fields are present
                    for field_name in schema_names:
                        if field_name not in final_dep:
                            # Add default values for missing fields
                            if field_name in ["source_id", "target_id", "type", "description", "locations"]:
                                final_dep[field_name] = ""
                            elif field_name in ["strength", "impact"]:
                                final_dep[field_name] = 0.0
                            elif field_name in ["is_direct", "is_required"]:
                                final_dep[field_name] = False
                            elif field_name in ["frequency"]:
                                final_dep[field_name] = 0
                            elif field_name in ["created_at", "updated_at"]:
                                # Use integer timestamp to avoid precision issues
                                final_dep[field_name] = int(datetime.now().timestamp() * 1000)

                    final_deps.append(final_dep)

                self.tables["dependencies"].add(final_deps)
            except AttributeError:
                # Older versions might use a different API
                for dep in dependencies:
                    # Get only the fields that are in the schema
                    schema_fields = set(self.schemas["dependencies"].keys())
                    filtered_dep = {k: v for k, v in dep.items() if k in schema_fields}
                    self.tables["dependencies"].add_data([filtered_dep])

            logger.info(f"Added {len(dependencies)} dependencies to the database")

        except Exception as e:
            logger.error(f"Error adding dependencies: {e}")
            raise

    def add_embedding_metadata(self, metadata_entries: List[Dict[str, Any]]) -> None:
        """Add embedding metadata to the database.

        Args:
            metadata_entries: List of embedding metadata dictionaries
        """
        try:
            if not metadata_entries:
                logger.warning("No embedding metadata to add")
                return

            # Skip if using minimal schema
            if self.use_minimal_schema or "embedding_metadata" not in self.schemas:
                logger.warning("Embedding metadata table not available in minimal schema")
                return

            # Open the embedding_metadata table if not already open
            if "embedding_metadata" not in self.tables:
                try:
                    self.tables["embedding_metadata"] = self.db.open_table("embedding_metadata")
                except (AttributeError, KeyError):
                    # Table might not exist or older API
                    try:
                        self.tables["embedding_metadata"] = self.db["embedding_metadata"]
                    except KeyError:
                        # Create the table if it doesn't exist
                        self.create_tables()
                        try:
                            self.tables["embedding_metadata"] = self.db.open_table("embedding_metadata")
                        except AttributeError:
                            self.tables["embedding_metadata"] = self.db["embedding_metadata"]

            # Use the schema manager to filter metadata entries according to the canonical schema
            filtered_entries = self.schema_manager.filter_batch_for_schema("embedding_metadata", metadata_entries)
            schema_fields = self.schema_manager.get_canonical_field_names("embedding_metadata")

            # Process each metadata entry for special fields
            now_timestamp = int(datetime.now().timestamp() * 1000)

            for filtered_entry in filtered_entries:
                # Add timestamps if they exist in the schema
                if "created_at" in schema_fields and "created_at" not in filtered_entry:
                    filtered_entry["created_at"] = now_timestamp
                if "updated_at" in schema_fields and "updated_at" not in filtered_entry:
                    filtered_entry["updated_at"] = now_timestamp

            # Replace the original entries with the filtered ones
            metadata_entries = filtered_entries

            # Add the metadata to the table
            try:
                # Get the actual schema from the table
                table_schema = self.tables["embedding_metadata"].schema
                schema_names = set(field.name for field in table_schema)

                # Log the actual schema fields
                logger.info(f"Actual schema fields in embedding_metadata table: {sorted(schema_names)}")

                # Final filtering to ensure only fields in the actual table schema are included
                final_entries = []
                for entry in metadata_entries:
                    final_entry = {k: v for k, v in entry.items() if k in schema_names}

                    # Ensure all required fields are present
                    for field_name in schema_names:
                        if field_name not in final_entry:
                            # Add default values for missing fields
                            if field_name in ["embedding_id", "chunk_id", "model_name", "model_version", "embedding_type"]:
                                final_entry[field_name] = ""
                            elif field_name in ["embedding_dim"]:
                                final_entry[field_name] = self.embedding_dim
                            elif field_name in ["quality_score", "confidence"]:
                                final_entry[field_name] = 0.0
                            elif field_name in ["created_at", "updated_at"]:
                                # Use integer timestamp to avoid precision issues
                                final_entry[field_name] = int(datetime.now().timestamp() * 1000)

                    final_entries.append(final_entry)

                self.tables["embedding_metadata"].add(final_entries)
            except AttributeError:
                # Older versions might use a different API
                for entry in metadata_entries:
                    # Get only the fields that are in the schema
                    schema_fields = set(self.schemas["embedding_metadata"].keys())
                    filtered_entry = {k: v for k, v in entry.items() if k in schema_fields}
                    self.tables["embedding_metadata"].add_data([filtered_entry])

            logger.info(f"Added {len(metadata_entries)} embedding metadata entries to the database")

        except Exception as e:
            logger.error(f"Error adding embedding metadata: {e}")
            raise

    def search_code_chunks(
        self,
        query_embedding: List[float],
        limit: int = 10,
        where: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search for code chunks by embedding similarity.

        Args:
            query_embedding: The embedding vector to search for
            limit: Maximum number of results to return
            where: Optional filter condition

        Returns:
            List of matching code chunks
        """
        try:
            # Open the code_chunks table if not already open
            if "code_chunks" not in self.tables:
                try:
                    self.tables["code_chunks"] = self.db.open_table("code_chunks")
                except AttributeError:
                    # Older versions might use a different API
                    self.tables["code_chunks"] = self.db["code_chunks"]

            # Try multiple approaches for compatibility with different LanceDB versions
            results = None
            errors = []

            # Approach 1: Try with standard parameters
            try:
                # Try with default vector column name
                query = self.tables["code_chunks"].search(query_embedding)
                
                # Add filter if provided
                if where:
                    query = query.where(where)
                
                # Try with limit method
                try:
                    results = query.limit(limit).to_pandas()
                except (AttributeError, TypeError) as e:
                    errors.append(f"Standard limit approach failed: {e}")
                    # Try with different parameter
                    try:
                        results = query.to_pandas(limit=limit)
                    except Exception as e2:
                        errors.append(f"to_pandas with limit parameter failed: {e2}")
                        # Just get all results and limit in Python
                        all_results = query.to_pandas()
                        results = all_results.head(limit)
            except KeyError as e:
                if "vector does not exist" in str(e):
                    errors.append(f"Default vector column failed: {e}")
                    # Try with "embedding" as the vector column name
                    try:
                        query = self.tables["code_chunks"].search(query_embedding, vector_column_name="embedding")
                        if where:
                            query = query.where(where)
                        try:
                            results = query.limit(limit).to_pandas()
                        except (AttributeError, TypeError):
                            try:
                                results = query.to_pandas(limit=limit)
                            except Exception:
                                all_results = query.to_pandas()
                                results = all_results.head(limit)
                    except Exception as e2:
                        errors.append(f"Embedding column approach failed: {e2}")
                else:
                    errors.append(f"Unexpected KeyError: {e}")
            except (AttributeError, TypeError) as e:
                errors.append(f"Standard search approach failed: {e}")

            # Approach 2: Try with k parameter (older versions)
            if results is None:
                try:
                    results = self.tables["code_chunks"].search(
                        query_embedding,
                        k=limit
                    ).to_pandas()
                except Exception as e:
                    errors.append(f"k parameter approach failed: {e}")

            # Approach 3: Try with different parameter name
            if results is None:
                try:
                    results = self.tables["code_chunks"].search(
                        query_embedding,
                        limit=limit
                    ).to_pandas()
                except Exception as e:
                    errors.append(f"limit parameter approach failed: {e}")

            # Approach 4: Try with vector column name
            if results is None:
                try:
                    results = self.tables["code_chunks"].search(
                        query_embedding,
                        vector_column_name="vector"
                    ).to_pandas().head(limit)
                except Exception as e:
                    errors.append(f"vector column name approach failed: {e}")

            # Approach 5: Try with embedding column name
            if results is None:
                try:
                    results = self.tables["code_chunks"].search(
                        query_embedding,
                        vector_column_name="embedding"
                    ).to_pandas().head(limit)
                except Exception as e:
                    errors.append(f"embedding column name approach failed: {e}")

            # Fallback: Get all chunks and return the first few
            if results is None:
                logger.warning(f"All search attempts failed: {'; '.join(errors)}")
                logger.info("Falling back to retrieving all chunks")
                try:
                    all_results = self.tables["code_chunks"].to_pandas()
                    results = all_results.head(limit)
                except Exception as e:
                    logger.error(f"Fallback retrieval failed: {e}")
                    # Return empty results as last resort
                    import pandas as pd
                    results = pd.DataFrame()

            # Convert results to dictionaries
            result_dicts = results.to_dict('records')

            # Parse JSON strings back to dictionaries
            for result in result_dicts:
                if "metadata" in result and isinstance(result["metadata"], str):
                    try:
                        result["metadata"] = json.loads(result["metadata"])
                    except json.JSONDecodeError:
                        result["metadata"] = {}

                if "context" in result and isinstance(result["context"], str):
                    try:
                        result["context"] = json.loads(result["context"])
                    except json.JSONDecodeError:
                        result["context"] = {}

            return result_dicts

        except Exception as e:
            logger.error(f"Error searching code chunks: {e}")
            return []



    def get_all_code_chunks(self) -> List[Dict[str, Any]]:
        """Get all code chunks from the database.

        Returns:
            List of all code chunks
        """
        try:
            # Open the code_chunks table if not already open
            if "code_chunks" not in self.tables:
                try:
                    self.tables["code_chunks"] = self.db.open_table("code_chunks")
                except AttributeError:
                    # Older versions might use a different API
                    self.tables["code_chunks"] = self.db["code_chunks"]

            # Get all chunks
            results = self.tables["code_chunks"].to_pandas()

            # Convert results to dictionaries
            return results.to_dict('records')

        except Exception as e:
            logger.error(f"Error getting all code chunks: {e}")
            return []

    def get_code_chunk(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get a code chunk by its node ID.

        Args:
            node_id: The node ID of the chunk to retrieve

        Returns:
            The code chunk dictionary, or None if not found
        """
        try:
            # Open the code_chunks table if not already open
            if "code_chunks" not in self.tables:
                try:
                    self.tables["code_chunks"] = self.db.open_table("code_chunks")
                except AttributeError:
                    # Older versions might use a different API
                    self.tables["code_chunks"] = self.db["code_chunks"]

            try:
                # Build the where clause
                where_clause = f"node_id = '{node_id}'"

                # Execute the query
                results = self.tables["code_chunks"].to_pandas(filter=where_clause)
            except (AttributeError, TypeError):
                # Older versions might not support filtering
                logger.warning("Using legacy API for code chunks (filtering in memory)")

                # Get all chunks
                results = self.tables["code_chunks"].to_pandas()

                # Filter in memory
                results = results[results["node_id"] == node_id]

            # Convert results to dictionary
            if len(results) > 0:
                return results.iloc[0].to_dict()
            else:
                return None

        except Exception as e:
            logger.error(f"Error getting code chunk: {e}")
            return None

    def get_dependencies(
        self,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        dep_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get dependencies from the database.

        Args:
            source_id: Optional source node ID to filter by
            target_id: Optional target node ID to filter by
            dep_type: Optional dependency type to filter by

        Returns:
            List of matching dependencies
        """
        try:
            # Open the dependencies table if not already open
            if "dependencies" not in self.tables:
                try:
                    self.tables["dependencies"] = self.db.open_table("dependencies")
                except AttributeError:
                    # Older versions might use a different API
                    self.tables["dependencies"] = self.db["dependencies"]

            try:
                # Build the where clause
                where_clauses = []
                if source_id:
                    where_clauses.append(f"source_id = '{source_id}'")
                if target_id:
                    where_clauses.append(f"target_id = '{target_id}'")
                if dep_type:
                    where_clauses.append(f"type = '{dep_type}'")

                where_clause = " AND ".join(where_clauses) if where_clauses else None

                # Execute the query
                if where_clause:
                    results = self.tables["dependencies"].to_pandas(filter=where_clause)
                else:
                    results = self.tables["dependencies"].to_pandas()
            except (AttributeError, TypeError):
                # Older versions might not support filtering
                logger.warning("Using legacy API for dependencies (filtering in memory)")

                # Get all dependencies
                results = self.tables["dependencies"].to_pandas()

                # Filter in memory
                if source_id:
                    results = results[results["source_id"] == source_id]
                if target_id:
                    results = results[results["target_id"] == target_id]
                if dep_type:
                    results = results[results["type"] == dep_type]

            # Convert results to dictionaries
            return results.to_dict('records')

        except Exception as e:
            logger.error(f"Error getting dependencies: {e}")
            raise

    def clear_tables(self) -> None:
        """Clear all tables in the database."""
        try:
            # Get existing tables
            try:
                existing_tables = self.db.table_names()
            except AttributeError:
                # Older versions might not have table_names method
                # Just try to drop the tables we know about
                existing_tables = ["code_chunks", "dependencies"]
                logger.info("Using hardcoded table list for clearing")

            # Delete each table
            for table_name in existing_tables:
                try:
                    self.db.drop_table(table_name)
                    logger.info(f"Dropped table {table_name}")
                except (AttributeError, KeyError):
                    # Table might not exist or drop_table might not be available
                    logger.warning(f"Could not drop table {table_name} (might not exist)")

            # Recreate the tables
            self.create_tables()
            logger.info("Tables cleared and recreated")

        except Exception as e:
            logger.error(f"Error clearing tables: {e}")
            raise

    def close(self) -> None:
        """Close the database connection."""
        try:
            # Close the tables
            self.tables = {}

            # Close the database
            try:
                # Some versions might have a close method
                if hasattr(self.db, 'close'):
                    self.db.close()
            except Exception as e:
                logger.warning(f"Could not explicitly close database: {e}")

            # Set to None to release reference
            self.db = None
            logger.info("Database connection closed")

        except Exception as e:
            logger.error(f"Error closing database: {e}")
            raise
