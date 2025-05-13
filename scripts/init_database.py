#!/usr/bin/env python3
"""
Initialize the LanceDB database for the codebase analyser.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add the parent directory to the path so we can import the modules
sys.path.append(str(Path(__file__).parent.parent))

from codebase_analyser.database import LanceDBManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_database(db_path=None, clear=False, use_minimal_schema=True):
    """Initialize the LanceDB database.

    Args:
        db_path: Path to the LanceDB database
        clear: Whether to clear existing tables
        use_minimal_schema: Whether to use the minimal schema
    """
    # Use the default path if not specified
    if db_path is None:
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".lancedb")
    
    logger.info(f"Initializing database at {db_path}")
    
    # Create a LanceDBManager instance
    db_manager = LanceDBManager(
        db_path=db_path,
        use_minimal_schema=use_minimal_schema,
        embedding_dim=384
    )
    
    # Clear tables if requested
    if clear:
        logger.info("Clearing existing tables...")
        db_manager.clear_tables()
    
    # Create tables
    logger.info("Creating tables...")
    db_manager.create_tables()
    
    logger.info("Database initialization complete.")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Initialize the LanceDB database")
    parser.add_argument("--db-path", help="Path to the LanceDB database")
    parser.add_argument("--clear", action="store_true", help="Clear existing tables")
    parser.add_argument("--full-schema", action="store_true", help="Use full schema instead of minimal")
    
    args = parser.parse_args()
    
    # Initialize the database
    init_database(
        db_path=args.db_path,
        clear=args.clear,
        use_minimal_schema=not args.full_schema
    )
    
    return 0

if __name__ == "__main__":
    sys.exit(main())