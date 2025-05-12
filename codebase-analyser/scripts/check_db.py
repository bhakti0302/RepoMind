#!/usr/bin/env python3
"""
Check the LanceDB database for code chunks and dependencies.
"""

import lancedb
import json

def main():
    """Main entry point."""
    # Connect to the database
    print("Connecting to the database...")
    db = lancedb.connect("./.lancedb")

    # Check if the code_chunks table exists
    if "code_chunks" in db.table_names():
        print("Code chunks table exists")
        table = db.open_table("code_chunks")

        # Get the schema
        print(f"Schema: {table.schema}")

        # Count the number of chunks
        df = table.to_pandas()
        print(f"Found {len(df)} chunks in the database")

        # Count chunks by project
        project_counts = df.groupby("project_id").size()
        print("Chunks by project:")
        for project_id, count in project_counts.items():
            print(f"  - {project_id}: {count}")

        # Count chunks by type
        type_counts = df.groupby("chunk_type").size()
        print("Chunks by type:")
        for chunk_type, count in type_counts.items():
            print(f"  - {chunk_type}: {count}")

        # Check for testshreya chunks
        testshreya_chunks = df[df["project_id"] == "testshreya"]
        print(f"Found {len(testshreya_chunks)} chunks for project 'testshreya'")

        # Count testshreya chunks by type
        testshreya_type_counts = testshreya_chunks.groupby("chunk_type").size()
        print("Testshreya chunks by type:")
        for chunk_type, count in testshreya_type_counts.items():
            print(f"  - {chunk_type}: {count}")

        # Check for references
        reference_counts = 0
        for _, chunk in testshreya_chunks.iterrows():
            if "reference_ids" in chunk and chunk["reference_ids"]:
                reference_counts += len(chunk["reference_ids"])

        print(f"Found {reference_counts} references in testshreya chunks")

        # Check for parent-child relationships
        parent_child_counts = 0
        for _, chunk in testshreya_chunks.iterrows():
            if "parent_id" in chunk and chunk["parent_id"]:
                parent_child_counts += 1

        print(f"Found {parent_child_counts} parent-child relationships in testshreya chunks")

        # Check for metadata
        metadata_counts = 0
        for _, chunk in testshreya_chunks.iterrows():
            if "metadata" in chunk and chunk["metadata"]:
                metadata_counts += 1

        print(f"Found {metadata_counts} chunks with metadata in testshreya chunks")

        # Check for context
        context_counts = 0
        for _, chunk in testshreya_chunks.iterrows():
            if "context" in chunk and chunk["context"]:
                context_counts += 1

        print(f"Found {context_counts} chunks with context in testshreya chunks")

        # Check for embeddings
        embedding_counts = 0
        for _, chunk in testshreya_chunks.iterrows():
            if "embedding" in chunk and chunk["embedding"] is not None:
                embedding_counts += 1

        print(f"Found {embedding_counts} chunks with embeddings in testshreya chunks")
    else:
        print("Code chunks table does not exist")

if __name__ == "__main__":
    main()
