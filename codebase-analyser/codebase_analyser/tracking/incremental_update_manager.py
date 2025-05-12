"""
Incremental update manager for efficient database updates.

This module provides functionality to update the database incrementally
when files change, avoiding the need to reprocess the entire codebase.
"""

import os
import time
import logging
import multiprocessing
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Set, Optional, Any, Tuple, Callable

from ..database.unified_storage import UnifiedStorage
from ..parsing.java_parser_adapter import JavaParserAdapter
from ..embeddings.embedding_generator import EmbeddingGenerator
from .file_change_tracker import FileChangeTracker

logger = logging.getLogger(__name__)

class IncrementalUpdateManager:
    """Manages incremental updates to the database when files change."""

    def __init__(
        self,
        repo_path: str,
        project_id: str,
        db_path: str = ".lancedb",
        data_dir: str = "../data",
        use_minimal_schema: bool = False,
        mock_embeddings: bool = False,
        embedding_model: str = "BAAI/bge-small-en-v1.5",
        embedding_cache_dir: str = ".cache",
        embedding_batch_size: int = 8,
        max_workers: int = None,
        chunk_size: int = 100,
        batch_insert: bool = True,
        file_extensions: List[str] = None,
        skip_patterns: List[str] = None,
        enable_parallel: bool = True
    ):
        """Initialize the incremental update manager.

        Args:
            repo_path: Path to the repository
            project_id: Project ID
            db_path: Path to the LanceDB database
            data_dir: Path to the data directory
            use_minimal_schema: Whether to use a minimal schema
            mock_embeddings: Whether to use mock embeddings
            embedding_model: Model to use for embeddings
            embedding_cache_dir: Directory to cache embedding models
            embedding_batch_size: Batch size for embedding generation
            max_workers: Maximum number of worker threads (None = auto)
            chunk_size: Number of chunks to process in a batch
            batch_insert: Whether to insert chunks in batches
            file_extensions: List of file extensions to process
            skip_patterns: List of patterns to skip
            enable_parallel: Whether to enable parallel processing
        """
        self.repo_path = Path(repo_path)
        self.project_id = project_id
        self.db_path = db_path
        self.data_dir = data_dir
        self.use_minimal_schema = use_minimal_schema
        self.mock_embeddings = mock_embeddings
        self.embedding_model = embedding_model
        self.embedding_cache_dir = embedding_cache_dir
        self.embedding_batch_size = embedding_batch_size

        # Performance optimization parameters
        self.max_workers = max_workers if max_workers is not None else min(32, multiprocessing.cpu_count() + 4)
        self.chunk_size = chunk_size
        self.batch_insert = batch_insert
        self.file_extensions = file_extensions if file_extensions is not None else ['.java']
        self.skip_patterns = skip_patterns if skip_patterns is not None else [
            'node_modules', 'build', 'dist', 'target', 'bin', 'obj',
            '.git', '.svn', '.hg', '.idea', '.vscode', '__pycache__'
        ]
        self.enable_parallel = enable_parallel

        # Initialize file change tracker
        self.change_tracker = FileChangeTracker(data_dir, project_id)

        # Initialize storage manager
        self.storage = UnifiedStorage(
            db_path=db_path,
            data_dir=data_dir,
            use_minimal_schema=use_minimal_schema,
            create_if_not_exists=True,
            read_only=False
        )

        # Initialize embedding generator if needed
        self.embedding_generator = None
        if not mock_embeddings:
            self.embedding_generator = EmbeddingGenerator(
                model_name=embedding_model,
                cache_dir=embedding_cache_dir,
                batch_size=embedding_batch_size
            )

    def detect_changes(self) -> Tuple[List[Path], List[Path], List[Path]]:
        """Detect changes in the repository.

        Returns:
            Tuple of (added_files, modified_files, deleted_files)
        """
        return self.change_tracker.detect_changes(
            self.repo_path,
            file_extensions=self.file_extensions
        )

    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if a file should be skipped based on patterns.

        Args:
            file_path: Path to the file

        Returns:
            True if the file should be skipped, False otherwise
        """
        # Check if file has the right extension
        if not any(str(file_path).lower().endswith(ext) for ext in self.file_extensions):
            return True

        # Check if file matches any skip patterns
        rel_path = str(file_path.relative_to(self.repo_path))
        for pattern in self.skip_patterns:
            if pattern in rel_path:
                return True

        return False

    def _process_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Process a single file and return its chunks.

        Args:
            file_path: Path to the file

        Returns:
            List of chunks generated from the file
        """
        try:
            logger.info(f"Processing file: {file_path}")
            result = JavaParserAdapter.parse_file(file_path)
            if result:
                logger.info(f"Generated {len(result['chunks'])} chunks for {file_path}")

                # Add project_id to chunks
                for chunk in result['chunks']:
                    chunk["project_id"] = self.project_id

                # Generate embeddings
                if self.mock_embeddings:
                    self._add_mock_embeddings(result['chunks'])
                else:
                    self._add_real_embeddings(result['chunks'])

                return result['chunks']
            else:
                logger.warning(f"Failed to parse {file_path}")
                return []
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            return []

    def _process_files_parallel(self, files: List[Path]) -> List[Dict[str, Any]]:
        """Process multiple files in parallel and return all chunks.

        Args:
            files: List of files to process

        Returns:
            List of all chunks generated from the files
        """
        all_chunks = []

        # Filter files that should be skipped
        files_to_process = [f for f in files if not self._should_skip_file(f)]

        if not files_to_process:
            return all_chunks

        logger.info(f"Processing {len(files_to_process)} files in parallel with {self.max_workers} workers")

        # Process files in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {executor.submit(self._process_file, file_path): file_path for file_path in files_to_process}

            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    chunks = future.result()
                    all_chunks.extend(chunks)
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {e}")

        return all_chunks

    def update_database(self) -> Dict[str, Any]:
        """Update the database incrementally based on file changes.

        Returns:
            Dictionary with update statistics
        """
        start_time = time.time()

        # Detect changes
        added_files, modified_files, deleted_files = self.detect_changes()

        # Combine added and modified files for processing
        files_to_process = added_files + modified_files

        # Skip if no changes
        if not files_to_process and not deleted_files:
            logger.info("No changes detected. Skipping update.")
            return {
                "added_files": 0,
                "modified_files": 0,
                "deleted_files": 0,
                "processed_chunks": 0,
                "deleted_chunks": 0,
                "elapsed_time": 0
            }

        logger.info(f"Detected {len(added_files)} added files, {len(modified_files)} modified files, and {len(deleted_files)} deleted files")

        # Process files (parallel or sequential)
        if self.enable_parallel and len(files_to_process) > 1:
            all_chunks = self._process_files_parallel(files_to_process)
        else:
            all_chunks = []
            for file_path in files_to_process:
                chunks = self._process_file(file_path)
                all_chunks.extend(chunks)

        # Delete chunks for deleted files
        deleted_chunks_count = 0
        if deleted_files:
            try:
                # Get all chunks for deleted files
                deleted_file_paths = [str(f) for f in deleted_files]
                deleted_chunks = self.storage.get_chunks_by_file_paths(deleted_file_paths, self.project_id)

                if deleted_chunks:
                    # Delete chunks from the database
                    self.storage.delete_chunks([chunk["node_id"] for chunk in deleted_chunks])
                    deleted_chunks_count = len(deleted_chunks)
                    logger.info(f"Deleted {deleted_chunks_count} chunks for {len(deleted_files)} files")
            except Exception as e:
                logger.error(f"Error deleting chunks for deleted files: {e}")

        # Add chunks to the database in batches if needed
        if all_chunks:
            try:
                if self.batch_insert and len(all_chunks) > self.chunk_size:
                    # Process chunks in batches
                    total_chunks = len(all_chunks)
                    for i in range(0, total_chunks, self.chunk_size):
                        batch = all_chunks[i:i+self.chunk_size]
                        self.storage.add_code_chunks_with_graph_metadata(batch)
                        logger.info(f"Added batch {i//self.chunk_size + 1}/{(total_chunks + self.chunk_size - 1)//self.chunk_size} ({len(batch)} chunks)")
                else:
                    # Add all chunks at once
                    self.storage.add_code_chunks_with_graph_metadata(all_chunks)
                    logger.info(f"Added {len(all_chunks)} chunks to the database")
            except Exception as e:
                logger.error(f"Error adding chunks to the database: {e}")

        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        logger.info(f"Update completed in {elapsed_time:.2f} seconds")

        # Close resources
        if self.embedding_generator:
            self.embedding_generator.close()

        return {
            "added_files": len(added_files),
            "modified_files": len(modified_files),
            "deleted_files": len(deleted_files),
            "processed_chunks": len(all_chunks),
            "deleted_chunks": deleted_chunks_count,
            "elapsed_time": elapsed_time
        }

    def _add_mock_embeddings(self, chunks: List[Dict[str, Any]]) -> None:
        """Add mock embeddings to chunks.

        Args:
            chunks: List of chunks to add embeddings to
        """
        import numpy as np

        # Generate mock embeddings (768-dimensional random vectors)
        embedding_dim = 768
        for chunk in chunks:
            # Generate a random embedding
            embedding = np.random.randn(embedding_dim).astype(np.float32)
            # Normalize the embedding
            embedding = embedding / np.linalg.norm(embedding)
            # Add the embedding to the chunk
            chunk["embedding"] = embedding.tolist()

    def _add_real_embeddings(self, chunks: List[Dict[str, Any]]) -> None:
        """Add real embeddings to chunks.

        Args:
            chunks: List of chunks to add embeddings to
        """
        if not self.embedding_generator:
            logger.error("Embedding generator not initialized")
            return

        try:
            # Process chunks in batches
            batch_size = self.embedding_batch_size
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i+batch_size]

                # Extract content and language for each chunk
                contents = [chunk["content"] for chunk in batch]
                languages = [chunk["language"] for chunk in batch]

                # Generate embeddings
                embeddings = self.embedding_generator.generate_embeddings_batch(contents, languages)

                # Add embeddings to chunks
                for j, embedding in enumerate(embeddings):
                    batch[j]["embedding"] = embedding.tolist()

                logger.info(f"Generated embeddings for batch {i//batch_size + 1}/{(len(chunks) + batch_size - 1)//batch_size}")
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")

    def close(self) -> None:
        """Close resources."""
        if self.storage:
            self.storage.close()
        if self.embedding_generator:
            self.embedding_generator.close()
