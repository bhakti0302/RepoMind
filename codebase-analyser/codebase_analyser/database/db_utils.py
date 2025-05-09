"""
Database utility functions for managing LanceDB connections.

This module provides utility functions for opening and closing LanceDB connections,
as well as a command-line interface for database management.

Note on Schema Consistency:
- It's important to maintain schema consistency when accessing tables
- Different versions of LanceDB have different APIs for search and table creation
- If upgrading LanceDB, clear and recreate tables to ensure schema consistency
- Pin the LanceDB version in your requirements.txt for API stability
"""

import os
import argparse
import logging
from typing import Optional

from .lancedb_manager import LanceDBManager
from .schema_manager import SchemaManager, get_schema_manager
from .unified_storage import UnifiedStorage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def open_db_connection(
    db_path: Optional[str] = None,
    use_minimal_schema: bool = True,
    embedding_dim: int = 384,
    create_if_not_exists: bool = True,
    read_only: bool = False
) -> LanceDBManager:
    """Open a connection to the LanceDB database.

    Args:
        db_path: Path to the LanceDB database (default: .lancedb in current directory)
        use_minimal_schema: Whether to use the minimal schema
        embedding_dim: Dimension of the embedding vectors
        create_if_not_exists: Whether to create the database if it doesn't exist
        read_only: Whether to open the database in read-only mode

    Returns:
        LanceDBManager instance with an open connection
    """
    logger.info(f"Opening connection to LanceDB at {db_path or '.lancedb'}")

    # Create the LanceDBManager instance
    db_manager = LanceDBManager(
        db_path=db_path,
        use_minimal_schema=use_minimal_schema,
        embedding_dim=embedding_dim,
        create_if_not_exists=create_if_not_exists,
        read_only=read_only
    )

    # Create tables if they don't exist
    db_manager.create_tables()

    return db_manager


def close_db_connection(db_manager: LanceDBManager) -> None:
    """Close a connection to the LanceDB database.

    Args:
        db_manager: LanceDBManager instance to close
    """
    if db_manager:
        logger.info("Closing connection to LanceDB")
        db_manager.close()


def open_unified_storage(
    db_path: Optional[str] = None,
    embedding_dim: int = 768,
    use_minimal_schema: bool = True,
    create_if_not_exists: bool = True,
    read_only: bool = False
) -> UnifiedStorage:
    """Open a unified storage connection.

    Args:
        db_path: Path to the LanceDB database
        embedding_dim: Dimension of the embedding vectors
        use_minimal_schema: Whether to use the minimal schema
        create_if_not_exists: Whether to create the database if it doesn't exist
        read_only: Whether to open the database in read-only mode

    Returns:
        UnifiedStorage instance
    """
    logger.info(f"Opening unified storage connection to {db_path or '.lancedb'}")

    # Create a unified storage manager
    storage = UnifiedStorage(
        db_path=db_path,
        embedding_dim=embedding_dim,
        use_minimal_schema=use_minimal_schema,
        create_if_not_exists=create_if_not_exists,
        read_only=read_only
    )

    logger.info("Opened unified storage connection")

    return storage


def close_unified_storage(storage: UnifiedStorage) -> None:
    """Close a unified storage connection.

    Args:
        storage: UnifiedStorage instance
    """
    if storage:
        logger.info("Closing unified storage connection")
        storage.close()


def check_schema_consistency(db_path=None, use_minimal_schema=True, embedding_dim=768):
    """Check schema consistency between the database and the code.

    Args:
        db_path: Path to the LanceDB database
        use_minimal_schema: Whether to use the minimal schema
        embedding_dim: Dimension of the embedding vectors

    Returns:
        True if the schema is consistent, False otherwise
    """
    logger.info("Checking schema consistency...")

    # Create a schema manager
    schema_manager = get_schema_manager(
        embedding_dim=embedding_dim,
        use_minimal_schema=use_minimal_schema
    )

    # Open a database connection
    db_manager = open_db_connection(
        db_path=db_path,
        use_minimal_schema=use_minimal_schema,
        embedding_dim=embedding_dim
    )

    try:
        # Check each table
        all_consistent = True
        for table_name in db_manager.tables:
            table = db_manager.tables[table_name]
            schema = table.schema

            logger.info(f"Checking schema for table {table_name}...")
            is_consistent = schema_manager.validate_schema(table_name, schema)

            if is_consistent:
                logger.info(f"Schema for table {table_name} is consistent")
            else:
                logger.warning(f"Schema for table {table_name} is inconsistent")
                all_consistent = False

        return all_consistent

    finally:
        close_db_connection(db_manager)


def view_metadata(node_id=None, db_path=None, use_minimal_schema=True, embedding_dim=768):
    """View metadata for a specific node or all nodes.

    Args:
        node_id: ID of the node to view metadata for (None for all nodes)
        db_path: Path to the LanceDB database
        use_minimal_schema: Whether to use the minimal schema
        embedding_dim: Dimension of the embedding vectors
    """
    import json

    logger.info(f"Viewing metadata for {'all nodes' if node_id is None else node_id}...")

    # Open a database connection
    db_manager = open_db_connection(
        db_path=db_path,
        use_minimal_schema=use_minimal_schema,
        embedding_dim=embedding_dim
    )

    try:
        # Get the code chunks table
        if "code_chunks" not in db_manager.tables:
            logger.error("Code chunks table not found")
            return

        # Query the table
        table = db_manager.tables["code_chunks"]
        if node_id:
            # Filter by node_id
            try:
                df = table.to_pandas(filter=f"node_id = '{node_id}'")
            except Exception as e:
                logger.warning(f"Error filtering by node_id: {e}")
                # Fallback to in-memory filtering
                df = table.to_pandas()
                df = df[df["node_id"] == node_id]
        else:
            # Get all chunks
            df = table.to_pandas()

        # Print the results
        if len(df) == 0:
            logger.info("No matching nodes found")
            return

        # Print metadata for each node
        for i, row in df.iterrows():
            print(f"\nNode: {row['node_id']} ({row['chunk_type']})")
            print(f"Name: {row['name']}")
            print(f"Language: {row['language']}")
            print(f"File: {row['file_path']} (lines {row['start_line']}-{row['end_line']})")

            # Parse and print metadata
            if "metadata" in row and row["metadata"]:
                try:
                    metadata = json.loads(row["metadata"])
                    print("\nMetadata:")
                    for key, value in metadata.items():
                        if isinstance(value, (dict, list)) and len(str(value)) > 100:
                            print(f"  {key}: <complex value>")
                        else:
                            print(f"  {key}: {value}")
                except json.JSONDecodeError:
                    print(f"Metadata: {row['metadata']}")

            # Parse and print context
            if "context" in row and row["context"]:
                try:
                    context = json.loads(row["context"])
                    print("\nContext:")
                    for key, value in context.items():
                        if isinstance(value, (dict, list)) and len(str(value)) > 100:
                            print(f"  {key}: <complex value>")
                        else:
                            print(f"  {key}: {value}")
                except json.JSONDecodeError:
                    print(f"Context: {row['context']}")

            # Print a separator between nodes
            if i < len(df) - 1:
                print("\n" + "-" * 50)

    finally:
        # Close the database connection
        close_db_connection(db_manager)


def main():
    """Command-line interface for database utilities."""
    parser = argparse.ArgumentParser(description="Database utilities for LanceDB")
    parser.add_argument("--db-path", help="Path to the LanceDB database")
    parser.add_argument("--clear", action="store_true", help="Clear existing tables")
    parser.add_argument("--full", action="store_true", help="Use full schema instead of minimal")
    parser.add_argument("--info", action="store_true", help="Print database information")
    parser.add_argument("--check-schema", action="store_true", help="Check schema consistency")
    parser.add_argument("--view-metadata", action="store_true", help="View metadata for nodes")
    parser.add_argument("--node-id", help="Node ID to view metadata for")
    parser.add_argument("--embedding-dim", type=int, default=768,
                        help="Dimension of the embedding vectors (default: 768)")

    args = parser.parse_args()

    # Check if we need to check schema consistency
    if args.check_schema:
        is_consistent = check_schema_consistency(
            db_path=args.db_path,
            use_minimal_schema=not args.full,
            embedding_dim=args.embedding_dim
        )

        if is_consistent:
            logger.info("All schemas are consistent")
        else:
            logger.warning("Some schemas are inconsistent")
        return

    # Check if we need to view metadata
    if args.view_metadata:
        view_metadata(
            node_id=args.node_id,
            db_path=args.db_path,
            use_minimal_schema=not args.full,
            embedding_dim=args.embedding_dim
        )
        return

    # Open the database connection
    db_manager = open_db_connection(
        db_path=args.db_path,
        use_minimal_schema=not args.full,
        embedding_dim=args.embedding_dim
    )

    try:
        # Clear tables if requested
        if args.clear:
            logger.info("Clearing existing tables...")
            db_manager.clear_tables()

        # Print database information if requested
        if args.info:
            try:
                # Get table names
                table_names = db_manager.db.table_names()
                logger.info(f"Tables in database: {table_names}")

                # Print schema for each table
                for table_name in table_names:
                    table = db_manager.db.open_table(table_name)
                    logger.info(f"Schema for table {table_name}:")
                    for field in table.schema:
                        logger.info(f"  - {field.name}: {field.type}")

                    # Print row count
                    try:
                        row_count = len(table.to_pandas())
                        logger.info(f"  - Row count: {row_count}")
                    except Exception as e:
                        logger.warning(f"  - Could not get row count: {e}")
            except Exception as e:
                logger.error(f"Error getting database information: {e}")

    finally:
        # Close the database connection
        close_db_connection(db_manager)


if __name__ == "__main__":
    main()
