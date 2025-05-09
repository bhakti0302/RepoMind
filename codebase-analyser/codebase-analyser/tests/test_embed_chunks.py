#!/usr/bin/env python3
"""
Test script for embedding code chunks and storing them in the database.
"""

import os
import sys
import argparse
import json
from pathlib import Path

from codebase_analyser.embeddings import embed_chunks_from_file
from codebase_analyser.database import open_db_connection, close_db_connection


def test_embed_chunks(
    input_file,
    db_path=None,
    model_name=None,
    cache_dir=None,
    batch_size=4,
    use_minimal_schema=True,
    clear_db=False
):
    """Test embedding code chunks and storing them in the database.

    Args:
        input_file: Path to the JSON file containing code chunks
        db_path: Path to the LanceDB database
        model_name: Name of the pre-trained model to use
        cache_dir: Directory to cache the model and tokenizer
        batch_size: Batch size for inference
        use_minimal_schema: Whether to use the minimal schema
        clear_db: Whether to clear the database before embedding
    """
    print(f"Testing embedding code chunks from {input_file}...")

    # Clear the database if requested
    if clear_db:
        print("Clearing the database...")
        db_manager = open_db_connection(
            db_path=db_path,
            use_minimal_schema=use_minimal_schema,
            embedding_dim=768  # Use 768-dimensional embeddings for CodeBERT
        )
        db_manager.clear_tables()
        close_db_connection(db_manager)

    # Embed the chunks and store them in the database
    embed_chunks_from_file(
        file_path=input_file,
        db_path=db_path,
        model_name=model_name,
        cache_dir=cache_dir,
        batch_size=batch_size,
        use_minimal_schema=use_minimal_schema
    )

    # Verify that the chunks were stored in the database
    print("\nVerifying that the chunks were stored in the database...")
    db_manager = open_db_connection(
        db_path=db_path,
        use_minimal_schema=use_minimal_schema,
        embedding_dim=768  # Use 768-dimensional embeddings for CodeBERT
    )

    try:
        # Get the number of chunks in the database
        code_chunks_table = db_manager.tables["code_chunks"]
        num_chunks = len(code_chunks_table.to_pandas())
        print(f"Found {num_chunks} chunks in the database")

        # Get the number of dependencies in the database
        dependencies_table = db_manager.tables["dependencies"]
        num_dependencies = len(dependencies_table.to_pandas())
        print(f"Found {num_dependencies} dependencies in the database")

        # Get the number of embedding metadata entries in the database
        if not use_minimal_schema and "embedding_metadata" in db_manager.tables:
            embedding_metadata_table = db_manager.tables["embedding_metadata"]
            num_embedding_metadata = len(embedding_metadata_table.to_pandas())
            print(f"Found {num_embedding_metadata} embedding metadata entries in the database")

        # Test searching for similar chunks
        print("\nTesting search functionality...")

        # Load the chunks from the input file
        with open(input_file, 'r') as f:
            chunks = json.load(f)

        # Search for chunks similar to the first chunk
        if chunks:
            first_chunk = chunks[0]
            print(f"Searching for chunks similar to {first_chunk['node_id']}...")

            # Get the embedding for the first chunk from the database
            first_chunk_db = code_chunks_table.to_pandas()
            first_chunk_db = first_chunk_db[first_chunk_db["node_id"] == first_chunk["node_id"]]

            if not first_chunk_db.empty:
                first_chunk_embedding = first_chunk_db.iloc[0]["embedding"]

                # Search for similar chunks
                similar_chunks = db_manager.search_code_chunks(
                    query_embedding=first_chunk_embedding,
                    limit=3
                )

                print(f"Found {len(similar_chunks)} similar chunks:")
                for i, chunk in enumerate(similar_chunks):
                    print(f"  {i+1}. {chunk['node_id']} ({chunk['chunk_type']}, {chunk['language']})")
            else:
                print(f"Could not find {first_chunk['node_id']} in the database")

    finally:
        # Close the database connection
        close_db_connection(db_manager)

    print("\nEmbedding test completed successfully!")


def main():
    parser = argparse.ArgumentParser(description="Test embedding code chunks and storing them in the database")
    parser.add_argument("--input", default="samples/sample_chunks.json", help="Path to the JSON file containing code chunks")
    parser.add_argument("--db-path", help="Path to the LanceDB database")
    parser.add_argument("--model", help="Name of the pre-trained model to use")
    parser.add_argument("--cache-dir", help="Directory to cache the model and tokenizer")
    parser.add_argument("--batch-size", type=int, default=4, help="Batch size for inference")
    parser.add_argument("--full-schema", action="store_true", help="Use the full schema")
    parser.add_argument("--clear-db", action="store_true", help="Clear the database before embedding")

    args = parser.parse_args()

    test_embed_chunks(
        input_file=args.input,
        db_path=args.db_path,
        model_name=args.model,
        cache_dir=args.cache_dir,
        batch_size=args.batch_size,
        use_minimal_schema=not args.full_schema,
        clear_db=args.clear_db
    )


if __name__ == "__main__":
    main()
