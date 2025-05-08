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


def main():
    """Command-line interface for database utilities."""
    parser = argparse.ArgumentParser(description="Database utilities for LanceDB")
    parser.add_argument("--db-path", help="Path to the LanceDB database")
    parser.add_argument("--clear", action="store_true", help="Clear existing tables")
    parser.add_argument("--full", action="store_true", help="Use full schema instead of minimal")
    parser.add_argument("--info", action="store_true", help="Print database information")
    parser.add_argument("--check-schema", action="store_true", help="Check schema consistency")
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
