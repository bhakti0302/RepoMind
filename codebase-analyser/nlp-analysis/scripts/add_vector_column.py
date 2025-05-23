#!/usr/bin/env python3

"""
Add Vector Column Script.

This script adds a vector column to the LanceDB database for improved vector search.
It processes existing code chunks, generates embeddings, and adds them to the database.
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Try to import required modules
try:
    import lancedb
    from sentence_transformers import SentenceTransformer
except ImportError as e:
    logger.error(f"Error importing dependencies: {e}")
    logger.error("Make sure LanceDB and sentence-transformers are installed")
    logger.error("Run: pip install lancedb sentence-transformers")
    sys.exit(1)

def load_embedding_model(model_name: str = "all-MiniLM-L6-v2") -> SentenceTransformer:
    """Load the embedding model.
    
    Args:
        model_name: Name of the model to load
        
    Returns:
        Loaded model
    """
    logger.info(f"Loading embedding model: {model_name}")
    try:
        model = SentenceTransformer(model_name)
        logger.info(f"Model loaded successfully: {model_name}")
        return model
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise

def generate_embeddings(texts: List[str], model: SentenceTransformer) -> np.ndarray:
    """Generate embeddings for a list of texts.
    
    Args:
        texts: List of texts to embed
        model: Embedding model
        
    Returns:
        Array of embeddings
    """
    logger.info(f"Generating embeddings for {len(texts)} texts")
    try:
        embeddings = model.encode(texts, show_progress_bar=True)
        logger.info(f"Generated {len(embeddings)} embeddings")
        return embeddings
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        raise

def add_vector_column(
    db_path: str,
    model_name: str = "all-MiniLM-L6-v2",
    batch_size: int = 100,
    vector_column_name: str = "vector"
) -> None:
    """Add a vector column to the database.
    
    Args:
        db_path: Path to the LanceDB database
        model_name: Name of the embedding model to use
        batch_size: Number of chunks to process at once
        vector_column_name: Name of the vector column to add
    """
    try:
        # Connect to the database
        logger.info(f"Connecting to LanceDB at {db_path}")
        db = lancedb.connect(db_path)
        
        # Get the table names
        tables = db.table_names()
        
        # Check if the code_chunks table exists
        if "code_chunks" not in tables:
            logger.error("code_chunks table not found in the database")
            return
        
        # Open the table
        logger.info("Opening code_chunks table")
        table = db.open_table("code_chunks")
        
        # Get the schema
        schema = table.schema
        
        # Check if the vector column already exists
        if vector_column_name in [field.name for field in schema]:
            logger.info(f"Vector column '{vector_column_name}' already exists")
            return
        
        # Load the embedding model
        model = load_embedding_model(model_name)
        
        # Get the embedding dimension
        embedding_dim = model.get_sentence_embedding_dimension()
        logger.info(f"Embedding dimension: {embedding_dim}")
        
        # Get all rows
        logger.info("Loading all rows from the table")
        all_rows = table.to_pandas()
        
        # Check if there are any rows
        if len(all_rows) == 0:
            logger.warning("No rows found in the table")
            return
        
        # Get the content column
        if "content" not in all_rows.columns:
            logger.error("Content column not found in the table")
            return
        
        # Process in batches
        total_batches = (len(all_rows) + batch_size - 1) // batch_size
        logger.info(f"Processing {len(all_rows)} rows in {total_batches} batches")
        
        # Create a new table with the vector column
        new_table_name = "code_chunks_with_vector"
        
        # Process each batch
        for i in range(total_batches):
            start_idx = i * batch_size
            end_idx = min((i + 1) * batch_size, len(all_rows))
            
            logger.info(f"Processing batch {i+1}/{total_batches} (rows {start_idx}-{end_idx})")
            
            # Get the batch
            batch = all_rows.iloc[start_idx:end_idx]
            
            # Get the content
            content = batch["content"].tolist()
            
            # Generate embeddings
            embeddings = generate_embeddings(content, model)
            
            # Add the embeddings to the batch
            batch[vector_column_name] = list(embeddings)
            
            # Add the batch to the new table
            if i == 0:
                # Create the table with the first batch
                logger.info(f"Creating new table: {new_table_name}")
                db.create_table(new_table_name, data=batch)
            else:
                # Add to the existing table
                new_table = db.open_table(new_table_name)
                new_table.add(batch)
        
        # Rename the tables
        logger.info("Renaming tables")
        old_table_name = "code_chunks_backup"
        db.rename_table("code_chunks", old_table_name)
        db.rename_table(new_table_name, "code_chunks")
        
        logger.info("Vector column added successfully")
        
    except Exception as e:
        logger.error(f"Error adding vector column: {e}")
        raise

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Add a vector column to the LanceDB database")
    parser.add_argument("--db-path", default="../.lancedb", help="Path to the LanceDB database")
    parser.add_argument("--model-name", default="all-MiniLM-L6-v2", help="Name of the embedding model to use")
    parser.add_argument("--batch-size", type=int, default=100, help="Number of chunks to process at once")
    parser.add_argument("--vector-column-name", default="vector", help="Name of the vector column to add")
    args = parser.parse_args()
    
    # Add the vector column
    add_vector_column(
        db_path=args.db_path,
        model_name=args.model_name,
        batch_size=args.batch_size,
        vector_column_name=args.vector_column_name
    )

if __name__ == "__main__":
    main()
