#!/usr/bin/env python3
"""
Script to incrementally update the database when files change.

This script detects changes in the repository and updates the database
incrementally, avoiding the need to reprocess the entire codebase.
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path

from codebase_analyser.tracking.incremental_update_manager import IncrementalUpdateManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Incrementally update the database when files change")
    parser.add_argument("repo_path", help="Path to the repository or directory to analyze")
    parser.add_argument("--db-path", help="Path to the LanceDB database", default="./.lancedb")
    parser.add_argument("--data-dir", help="Path to the data directory", default="../data")
    parser.add_argument("--mock-embeddings", action="store_true", help="Use mock embeddings instead of generating real ones")
    parser.add_argument("--project-id", help="Project ID for the chunks")
    parser.add_argument("--embedding-model", help="Model to use for embeddings", default="BAAI/bge-small-en-v1.5")
    parser.add_argument("--embedding-cache-dir", help="Directory to cache embedding models", default=".cache")
    parser.add_argument("--embedding-batch-size", type=int, help="Batch size for embedding generation", default=8)
    parser.add_argument("--minimal-schema", action="store_true", help="Use minimal schema for the database")
    parser.add_argument("--force-full-update", action="store_true", help="Force a full update instead of incremental")

    # Performance optimization options
    parser.add_argument("--max-workers", type=int, help="Maximum number of worker threads (default: auto)")
    parser.add_argument("--chunk-size", type=int, help="Number of chunks to process in a batch", default=100)
    parser.add_argument("--no-batch-insert", action="store_true", help="Disable batch insertion of chunks")
    parser.add_argument("--file-extensions", help="Comma-separated list of file extensions to process (default: .java)")
    parser.add_argument("--skip-patterns", help="Comma-separated list of patterns to skip")
    parser.add_argument("--no-parallel", action="store_true", help="Disable parallel processing")

    return parser.parse_args()


def update_codebase(args):
    """Update the codebase incrementally based on file changes."""
    import time
    start_time = time.time()

    repo_path = Path(args.repo_path)
    if not repo_path.exists():
        logger.error(f"Repository path does not exist: {repo_path}")
        return False

    # Determine project ID if not provided
    project_id = args.project_id
    if not project_id:
        project_id = repo_path.name
        logger.info(f"Using directory name as project ID: {project_id}")

    # Parse file extensions
    file_extensions = None
    if args.file_extensions:
        file_extensions = [ext.strip() for ext in args.file_extensions.split(',')]
        logger.info(f"Using file extensions: {file_extensions}")

    # Parse skip patterns
    skip_patterns = None
    if args.skip_patterns:
        skip_patterns = [pattern.strip() for pattern in args.skip_patterns.split(',')]
        logger.info(f"Using skip patterns: {skip_patterns}")

    logger.info(f"Starting incremental update for repository: {repo_path}")

    # Initialize incremental update manager
    update_manager = IncrementalUpdateManager(
        repo_path=repo_path,
        project_id=project_id,
        db_path=args.db_path,
        data_dir=args.data_dir,
        use_minimal_schema=args.minimal_schema,
        mock_embeddings=args.mock_embeddings,
        embedding_model=args.embedding_model,
        embedding_cache_dir=args.embedding_cache_dir,
        embedding_batch_size=args.embedding_batch_size,
        max_workers=args.max_workers,
        chunk_size=args.chunk_size,
        batch_insert=not args.no_batch_insert,
        file_extensions=file_extensions,
        skip_patterns=skip_patterns,
        enable_parallel=not args.no_parallel
    )

    try:
        # Force full update if requested
        if args.force_full_update:
            logger.info("Forcing full update")
            # Clear tracking data to force full update
            update_manager.change_tracker.clear_tracking_data()

        # Update the database
        stats = update_manager.update_database()

        # Update the last sync time
        from codebase_analyser.database.unified_storage import UnifiedStorage
        storage = UnifiedStorage(
            db_path=args.db_path,
            data_dir=args.data_dir,
            use_minimal_schema=args.minimal_schema
        )
        try:
            timestamp = storage.update_last_sync_time(project_id)
            logger.info(f"Updated last sync time for project {project_id}: {timestamp}")
        finally:
            storage.close()

        # Print statistics
        logger.info(f"Update statistics:")
        logger.info(f"  Added files: {stats['added_files']}")
        logger.info(f"  Modified files: {stats['modified_files']}")
        logger.info(f"  Deleted files: {stats['deleted_files']}")
        logger.info(f"  Processed chunks: {stats['processed_chunks']}")
        logger.info(f"  Deleted chunks: {stats['deleted_chunks']}")
        logger.info(f"  Processing time: {stats.get('elapsed_time', 0):.2f} seconds")

        elapsed_time = time.time() - start_time
        logger.info(f"Total update completed in {elapsed_time:.2f} seconds")
        return True
    finally:
        # Close resources
        update_manager.close()


def main():
    """Main entry point."""
    args = parse_args()
    success = update_codebase(args)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
