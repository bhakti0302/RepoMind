"""
Utility module for embedding code chunks and storing them in the database.
"""

import os
import logging
import json
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
from tqdm import tqdm

from ..database import UnifiedStorage, open_unified_storage as open_db_connection, close_unified_storage as close_db_connection
from .embedding_generator import EmbeddingGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def embed_and_store_chunks(
    chunks: List[Dict[str, Any]],
    db_path: Optional[str] = None,
    model_name: Optional[str] = None,
    cache_dir: Optional[str] = None,
    batch_size: int = 8,
    use_minimal_schema: bool = True
) -> None:
    """Embed code chunks and store them in the database.

    Args:
        chunks: List of code chunk dictionaries
        db_path: Path to the LanceDB database
        model_name: Name of the pre-trained model to use
        cache_dir: Directory to cache the model and tokenizer
        batch_size: Batch size for inference
        use_minimal_schema: Whether to use the minimal schema
    """
    if not chunks:
        logger.warning("No chunks to embed")
        return

    logger.info(f"Embedding {len(chunks)} code chunks...")

    # Create an embedding generator
    generator = EmbeddingGenerator(
        model_name=model_name,
        cache_dir=cache_dir,
        batch_size=batch_size
    )

    try:
        # Generate embeddings for the chunks
        chunks_with_embeddings = generator.generate_embeddings_for_chunks(chunks)

        # Open a database connection
        db_manager = open_db_connection(
            db_path=db_path,
            use_minimal_schema=use_minimal_schema,
            embedding_dim=768  # Use 768-dimensional embeddings for CodeBERT
        )

        try:
            # Store the chunks in the database
            db_manager.add_code_chunks(chunks_with_embeddings)
            logger.info(f"Stored {len(chunks_with_embeddings)} chunks in the database")

            # Extract dependencies if available
            dependencies = []
            for chunk in chunks_with_embeddings:
                if "metadata" in chunk and isinstance(chunk["metadata"], dict):
                    if "dependencies" in chunk["metadata"]:
                        chunk_deps = chunk["metadata"]["dependencies"]
                        if isinstance(chunk_deps, list):
                            dependencies.extend(chunk_deps)

            # Store dependencies in the database if available
            if dependencies:
                db_manager.add_dependencies(dependencies)
                logger.info(f"Stored {len(dependencies)} dependencies in the database")

            # Create embedding metadata if using full schema
            if not use_minimal_schema:
                embedding_metadata = []
                for chunk in chunks_with_embeddings:
                    if "embedding" in chunk and "node_id" in chunk:
                        metadata = {
                            "embedding_id": f"emb:{chunk['node_id']}",
                            "chunk_id": chunk["node_id"],
                            "model_name": generator.model_name,
                            "model_version": "1.0.0",  # TODO: Get actual model version
                            "embedding_type": "code",
                            "embedding_dim": len(chunk["embedding"]),
                            "quality_score": 1.0,  # TODO: Implement quality scoring
                            "confidence": 1.0  # TODO: Implement confidence scoring
                        }
                        embedding_metadata.append(metadata)

                if embedding_metadata:
                    db_manager.add_embedding_metadata(embedding_metadata)
                    logger.info(f"Stored {len(embedding_metadata)} embedding metadata entries in the database")

        finally:
            # Close the database connection
            close_db_connection(db_manager)

    finally:
        # Close the embedding generator
        generator.close()


def embed_chunks_from_file(
    file_path: str,
    db_path: Optional[str] = None,
    model_name: Optional[str] = None,
    cache_dir: Optional[str] = None,
    batch_size: int = 8,
    use_minimal_schema: bool = True
) -> None:
    """Embed code chunks from a JSON file and store them in the database.

    Args:
        file_path: Path to the JSON file containing code chunks
        db_path: Path to the LanceDB database
        model_name: Name of the pre-trained model to use
        cache_dir: Directory to cache the model and tokenizer
        batch_size: Batch size for inference
        use_minimal_schema: Whether to use the minimal schema
    """
    logger.info(f"Loading chunks from {file_path}...")

    try:
        with open(file_path, 'r') as f:
            chunks = json.load(f)

        if not isinstance(chunks, list):
            logger.error(f"Expected a list of chunks, got {type(chunks)}")
            return

        logger.info(f"Loaded {len(chunks)} chunks from {file_path}")

        # Embed and store the chunks
        embed_and_store_chunks(
            chunks=chunks,
            db_path=db_path,
            model_name=model_name,
            cache_dir=cache_dir,
            batch_size=batch_size,
            use_minimal_schema=use_minimal_schema
        )

    except Exception as e:
        logger.error(f"Error loading chunks from {file_path}: {e}")


def main():
    """Command-line interface for embedding code chunks."""
    import argparse

    parser = argparse.ArgumentParser(description="Embed code chunks and store them in the database")
    parser.add_argument("file_path", help="Path to the JSON file containing code chunks")
    parser.add_argument("--db-path", help="Path to the LanceDB database")
    parser.add_argument("--model", help="Name of the pre-trained model to use")
    parser.add_argument("--cache-dir", help="Directory to cache the model and tokenizer")
    parser.add_argument("--batch-size", type=int, default=8, help="Batch size for inference")
    parser.add_argument("--full-schema", action="store_true", help="Use the full schema")

    args = parser.parse_args()

    embed_chunks_from_file(
        file_path=args.file_path,
        db_path=args.db_path,
        model_name=args.model,
        cache_dir=args.cache_dir,
        batch_size=args.batch_size,
        use_minimal_schema=not args.full_schema
    )


if __name__ == "__main__":
    main()
