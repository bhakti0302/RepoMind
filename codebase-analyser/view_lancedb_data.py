#!/usr/bin/env python3
"""
Script to view all data in LanceDB database.
This script helps you explore the contents of your LanceDB database,
including all tables, schemas, and sample data.
"""

import lancedb
import pandas as pd
import os
import json
import argparse
import sys
import datetime
from typing import Dict, List, Optional, Any, TextIO

# Try to import tabulate, but provide a fallback if not available
try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False
    print("Note: 'tabulate' package not found. Install with 'pip install tabulate' for better table formatting.")
    print("Using basic table formatting instead.\n")

# Global file handle for output
output_file = None

def log(message: str):
    """Log a message to both console and file if output_file is set."""
    print(message)
    if output_file:
        output_file.write(message + "\n")

def connect_to_db(db_path: str = ".lancedb"):
    """Connect to the LanceDB database."""
    log(f"Connecting to LanceDB at: {db_path}")
    try:
        db = lancedb.connect(db_path)
        log("✅ Connection successful")
        return db
    except Exception as e:
        log(f"❌ Connection failed: {e}")
        return None

def list_tables(db):
    """List all tables in the database."""
    if not db:
        return []

    try:
        tables = db.table_names()
        log(f"\n📊 Found {len(tables)} tables in the database:")
        for i, table_name in enumerate(tables, 1):
            log(f"  {i}. {table_name}")
        return tables
    except Exception as e:
        log(f"❌ Error listing tables: {e}")
        return []

def get_table_info(db, table_name: str):
    """Get information about a specific table."""
    if not db:
        return None

    try:
        table = db.open_table(table_name)
        log(f"\n📋 Table: {table_name}")

        # Get schema
        schema = table.schema
        log("\nSchema:")
        for field in schema:
            log(f"  - {field.name}: {field.type}")

        # Get row count
        df = table.to_arrow().to_pandas()
        row_count = len(df)
        log(f"\nRow count: {row_count}")

        return {
            "table": table,
            "schema": schema,
            "row_count": row_count,
            "dataframe": df
        }
    except Exception as e:
        log(f"❌ Error getting table info for {table_name}: {e}")
        return None

def display_sample_data(table_info, num_samples: int = 5):
    """Display sample data from the table."""
    if not table_info:
        return

    df = table_info["dataframe"]
    if len(df) == 0:
        log("Table is empty")
        return

    # Limit samples to available rows
    num_samples = min(num_samples, len(df))

    log(f"\nSample data ({num_samples} rows):")

    # Handle embedding columns specially
    sample_df = df.head(num_samples).copy()
    for col in sample_df.columns:
        # Check if column contains embeddings (lists of floats)
        if col == 'embedding' or (
            sample_df[col].dtype == 'object' and
            len(sample_df) > 0 and
            isinstance(sample_df[col].iloc[0], list) and
            len(sample_df[col].iloc[0]) > 10
        ):
            # Replace embedding values with their dimensions
            sample_df[col] = sample_df[col].apply(
                lambda x: f"[{len(x)} dims]" if isinstance(x, list) else x
            )

    # Display the sample data
    if HAS_TABULATE:
        table_str = tabulate(sample_df, headers='keys', tablefmt='pretty', showindex=False)
        log(table_str)
    else:
        # Basic formatting fallback
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        log(str(sample_df))

def analyze_code_chunks_table(table_info):
    """Analyze the code_chunks table to provide useful statistics."""
    if not table_info or table_info["row_count"] == 0:
        return

    df = table_info["dataframe"]

    # Check if this is likely the code_chunks table
    required_columns = ['chunk_type', 'language', 'project_id']
    if not all(col in df.columns for col in required_columns):
        print("This doesn't appear to be the code_chunks table. Skipping detailed analysis.")
        return

    print("\n📊 Code Chunks Analysis:")

    # Count by project_id
    if 'project_id' in df.columns:
        print("\nChunks by Project:")
        project_counts = df['project_id'].value_counts()
        for project, count in project_counts.items():
            print(f"  - {project}: {count} chunks")

    # Count by chunk_type
    if 'chunk_type' in df.columns:
        print("\nChunks by Type:")
        type_counts = df['chunk_type'].value_counts()
        for chunk_type, count in type_counts.items():
            print(f"  - {chunk_type}: {count} chunks")

    # Count by language
    if 'language' in df.columns:
        print("\nChunks by Language:")
        language_counts = df['language'].value_counts()
        for language, count in language_counts.items():
            print(f"  - {language}: {count} chunks")

def analyze_embeddings_table(table_info):
    """Analyze the embeddings table to provide useful statistics."""
    if not table_info or table_info["row_count"] == 0:
        return

    df = table_info["dataframe"]

    # Check if this is likely an embeddings table
    if 'embedding' not in df.columns:
        print("This doesn't appear to be an embeddings table. Skipping detailed analysis.")
        return

    print("\n📊 Embeddings Analysis:")

    # Get embedding dimensions
    if len(df) > 0 and isinstance(df['embedding'].iloc[0], list):
        embedding_dim = len(df['embedding'].iloc[0])
        print(f"\nEmbedding dimension: {embedding_dim}")

    # Count by model if available
    if 'model_name' in df.columns:
        print("\nEmbeddings by Model:")
        model_counts = df['model_name'].value_counts()
        for model, count in model_counts.items():
            print(f"  - {model}: {count} embeddings")

    # Count by type if available
    if 'embedding_type' in df.columns:
        print("\nEmbeddings by Type:")
        type_counts = df['embedding_type'].value_counts()
        for emb_type, count in type_counts.items():
            print(f"  - {emb_type}: {count} embeddings")

def main():
    parser = argparse.ArgumentParser(description="View data in LanceDB database")
    parser.add_argument("--db-path", default=".lancedb", help="Path to LanceDB database")
    parser.add_argument("--samples", type=int, default=5, help="Number of sample rows to display")
    parser.add_argument("--table", help="Specific table to analyze (optional)")
    parser.add_argument("--output", help="Output file to save results (optional)")
    args = parser.parse_args()

    global output_file

    # Open output file if specified
    if args.output:
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            output_file = open(args.output, 'w')
            log(f"LanceDB Data Analysis - {timestamp}")
            log(f"Database path: {args.db_path}")
            log("=" * 80)
        except Exception as e:
            print(f"Error opening output file: {e}")
            return

    try:
        # Connect to the database
        db = connect_to_db(args.db_path)
        if not db:
            return

        # List all tables
        tables = list_tables(db)
        if not tables:
            log("No tables found in the database.")
            return

        # If a specific table is requested, only analyze that one
        if args.table and args.table in tables:
            tables = [args.table]

        # Analyze each table
        for table_name in tables:
            table_info = get_table_info(db, table_name)
            if table_info:
                display_sample_data(table_info, args.samples)

                # Run specialized analysis based on table type
                if table_name == "code_chunks":
                    analyze_code_chunks_table(table_info)
                elif "embedding" in table_name:
                    analyze_embeddings_table(table_info)

    finally:
        # Close output file if it was opened
        if output_file:
            output_file.close()
            print(f"Results saved to {args.output}")
            output_file = None

if __name__ == "__main__":
    main()
