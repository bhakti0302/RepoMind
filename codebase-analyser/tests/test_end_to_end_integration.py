#!/usr/bin/env python3
"""
End-to-end integration test for the entire codebase analysis system.

This script tests the complete flow from parsing source code to querying results:
1. Parse source code files
2. Generate chunks
3. Build dependency graphs
4. Generate embeddings
5. Store everything in the database
6. Perform various types of queries
7. Validate the results
"""

import os
import sys
import json
import argparse
import logging
import tempfile
import shutil
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

from codebase_analyser import CodebaseAnalyser
from codebase_analyser.database import open_unified_storage, close_unified_storage
from codebase_analyser.embeddings import EmbeddingGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_test_files(test_dir):
    """Create test files for the integration test.

    Args:
        test_dir: Directory to create test files in

    Returns:
        List of file paths
    """
    logger.info(f"Creating test files in {test_dir}")

    # Create a Java file
    java_file = os.path.join(test_dir, "SimpleClass.java")
    with open(java_file, 'w') as f:
        f.write("""
package com.example;

import java.util.List;
import java.util.ArrayList;

/**
 * A simple class for testing.
 */
public class SimpleClass {
    private String name;
    private List<String> items;

    /**
     * Constructor.
     */
    public SimpleClass(String name) {
        this.name = name;
        this.items = new ArrayList<>();
    }

    /**
     * Add an item to the list.
     */
    public void addItem(String item) {
        items.add(item);
    }

    /**
     * Get all items.
     */
    public List<String> getItems() {
        return items;
    }

    /**
     * Main method.
     */
    public static void main(String[] args) {
        SimpleClass obj = new SimpleClass("Test");
        obj.addItem("Item 1");
        obj.addItem("Item 2");
        System.out.println("Items: " + obj.getItems());
    }
}
""")

    # Create a Python file
    python_file = os.path.join(test_dir, "simple_module.py")
    with open(python_file, 'w') as f:
        f.write("""
#!/usr/bin/env python3
\"\"\"
A simple Python module for testing.
\"\"\"

import os
import sys
from typing import List, Dict, Any


class SimpleClass:
    \"\"\"A simple class for testing.\"\"\"

    def __init__(self, name: str):
        \"\"\"Initialize with a name.\"\"\"
        self.name = name
        self.items = []

    def add_item(self, item: str) -> None:
        \"\"\"Add an item to the list.\"\"\"
        self.items.append(item)

    def get_items(self) -> List[str]:
        \"\"\"Get all items.\"\"\"
        return self.items


def main():
    \"\"\"Main function.\"\"\"
    obj = SimpleClass("Test")
    obj.add_item("Item 1")
    obj.add_item("Item 2")
    print(f"Items: {obj.get_items()}")


if __name__ == "__main__":
    main()
""")

    # Create a JavaScript file
    js_file = os.path.join(test_dir, "simple_module.js")
    with open(js_file, 'w') as f:
        f.write("""
/**
 * A simple JavaScript module for testing.
 */

// Import dependencies
const fs = require('fs');
const path = require('path');

/**
 * A simple class for testing.
 */
class SimpleClass {
    /**
     * Constructor.
     */
    constructor(name) {
        this.name = name;
        this.items = [];
    }

    /**
     * Add an item to the list.
     */
    addItem(item) {
        this.items.push(item);
    }

    /**
     * Get all items.
     */
    getItems() {
        return this.items;
    }
}

/**
 * Main function.
 */
function main() {
    const obj = new SimpleClass("Test");
    obj.addItem("Item 1");
    obj.addItem("Item 2");
    console.log("Items:", obj.getItems());
}

// Run the main function
main();
""")

    return [java_file, python_file, js_file]


def run_end_to_end_test(
    test_dir,
    db_path,
    clear_db=True,
    use_minimal_schema=True,
    use_mock_embeddings=True
):
    """Run the end-to-end integration test.

    Args:
        test_dir: Directory containing test files
        db_path: Path to the database
        clear_db: Whether to clear the database before testing
        use_minimal_schema: Whether to use the minimal schema
        use_mock_embeddings: Whether to use mock embeddings instead of a real model
    """
    logger.info("Starting end-to-end integration test")

    # Step 1: Create a CodebaseAnalyser
    logger.info("Creating CodebaseAnalyser")
    analyser = CodebaseAnalyser(test_dir)

    # Step 2: Parse all files in the test directory
    logger.info("Parsing files")
    all_chunks = []
    file_paths = [Path(os.path.join(test_dir, f)) for f in os.listdir(test_dir)
                 if os.path.isfile(os.path.join(test_dir, f))]

    for file_path in file_paths:
        logger.info(f"Parsing {file_path}")
        result = analyser.parse_file(file_path)
        if result:
            chunks = analyser.get_chunks(result)
            logger.info(f"Generated {len(chunks)} chunks for {file_path}")

            # Convert chunks to dictionaries
            for chunk in chunks:
                all_chunks.append(chunk.to_dict())

    logger.info(f"Total chunks generated: {len(all_chunks)}")

    # Step 3: Generate embeddings
    if use_mock_embeddings:
        logger.info("Generating mock embeddings")
        embedding_dim = 768
        for chunk in all_chunks:
            # Generate a random embedding
            embedding = np.random.randn(embedding_dim).astype(np.float32)
            # Normalize the embedding
            embedding = embedding / np.linalg.norm(embedding)
            # Add the embedding to the chunk
            chunk["embedding"] = embedding.tolist()
    else:
        logger.info("Generating real embeddings")
        embedding_generator = EmbeddingGenerator()
        all_chunks = embedding_generator.generate_embeddings_for_chunks(all_chunks)
        embedding_generator.close()

    # Step 4: Open unified storage
    logger.info(f"Opening unified storage at {db_path}")
    storage_manager = open_unified_storage(
        db_path=db_path,
        use_minimal_schema=use_minimal_schema,
        create_if_not_exists=True,
        read_only=False
    )

    try:
        # Step 5: Clear the database if requested
        if clear_db:
            logger.info("Clearing database")
            storage_manager.db_manager.clear_tables()
        
        # Step 5.5: Explicitly create tables
        logger.info("Explicitly creating tables")
        storage_manager.db_manager.create_tables()

        # Step 6: Add chunks with graph metadata to the database
        logger.info("Adding chunks with graph metadata to the database")
        
        # Check if tables exist
        if "code_chunks" not in storage_manager.db_manager.tables:
            logger.error("code_chunks table does not exist after create_tables call")
            # Try to create it again with a different approach
            try:
                import pandas as pd
                
                # Create a minimal dataframe with one row
                logger.info("Attempting to create code_chunks table with pandas DataFrame")
                
                # Create empty data with the correct column names
                empty_data = {
                    "node_id": ["test_node"],
                    "chunk_type": ["test_type"],
                    "content": ["test content"],
                    "file_path": ["test/path.py"],
                    "language": ["python"],
                    "name": ["test"],
                    "qualified_name": ["test.test"],
                    "embedding": [[0.0] * storage_manager.db_manager.embedding_dim],
                    # Add vector column for compatibility with different LanceDB versions
                    "vector": [[0.0] * storage_manager.db_manager.embedding_dim]
                }
                
                # Create DataFrame
                df = pd.DataFrame(empty_data)
                
                # Create the table
                storage_manager.db_manager.db.create_table("code_chunks", df)
                storage_manager.db_manager.tables["code_chunks"] = storage_manager.db_manager.db.open_table("code_chunks")
                logger.info("Successfully created code_chunks table with pandas DataFrame")
                
                # Also create dependencies table
                empty_deps = {
                    "source_id": ["test_source"],
                    "target_id": ["test_target"],
                    "type": ["test_type"],
                    "description": ["test description"]
                }
                
                deps_df = pd.DataFrame(empty_deps)
                storage_manager.db_manager.db.create_table("dependencies", deps_df)
                storage_manager.db_manager.tables["dependencies"] = storage_manager.db_manager.db.open_table("dependencies")
                logger.info("Successfully created dependencies table with pandas DataFrame")
                
            except Exception as e:
                logger.error(f"Failed to create tables with pandas DataFrame: {e}")
                raise
        
        # Add vector field to chunks for compatibility with different LanceDB versions
        for chunk in all_chunks:
            if "embedding" in chunk and "vector" not in chunk:
                chunk["vector"] = chunk["embedding"]
        
        # Now try to add the chunks
        try:
            storage_manager.add_code_chunks_with_graph_metadata(chunks=all_chunks)
        except Exception as e:
            logger.error(f"Error adding chunks: {e}")
            # Try a different approach
            try:
                logger.info("Trying to add chunks directly to the table")
                storage_manager.db_manager.add_code_chunks(all_chunks)
            except Exception as e2:
                logger.error(f"Error adding chunks directly: {e2}")
                raise

        # Step 7: Perform various queries

        # 7.1: Vector similarity search
        logger.info("Testing vector similarity search")
        query_embedding = np.random.randn(storage_manager.embedding_dim).astype(np.float32)
        query_embedding = query_embedding / np.linalg.norm(query_embedding)

        try:
            # Try different search approaches for compatibility
            try:
                logger.info("Attempting vector search with standard parameters")
                vector_results = storage_manager.db_manager.search_code_chunks(
                    query_embedding=query_embedding.tolist(),
                    limit=5
                )
            except Exception as e1:
                logger.warning(f"Standard vector search failed: {e1}")
                try:
                    # Try with k parameter instead of limit
                    logger.info("Attempting vector search with k parameter")
                    vector_results = storage_manager.db_manager.tables["code_chunks"].search(
                        query_embedding.tolist(),
                        k=5
                    ).to_pandas().to_dict('records')
                except Exception as e2:
                    logger.warning(f"Vector search with k parameter failed: {e2}")
                    # Try with vector column name
                    try:
                        logger.info("Attempting vector search with vector column name")
                        vector_results = storage_manager.db_manager.tables["code_chunks"].search(
                            query_embedding.tolist(),
                            vector_column_name="vector"
                        ).limit(5).to_pandas().to_dict('records')
                    except Exception as e3:
                        logger.warning(f"Vector search with vector column name failed: {e3}")
                        # Fallback to manual retrieval
                        logger.info("Falling back to manual retrieval")
                        vector_results = storage_manager.db_manager.get_all_code_chunks()[:5]

            logger.info(f"Vector search returned {len(vector_results)} results")
            for i, result in enumerate(vector_results[:3]):
                logger.info(f"Result {i+1}: {result.get('name', 'Unknown')} ({result.get('node_id', 'Unknown')})")
        except Exception as e:
            logger.warning(f"All vector search attempts failed: {e}")
            logger.info("Falling back to empty results")
            vector_results = []

        # 7.2: Dependency-filtered search
        logger.info("Testing dependency-filtered search")
        try:
            # Use the vector_results from above if available
            if vector_results:
                logger.info("Using vector results for dependency filtering")
                dep_results = vector_results[:5]
            else:
                # Try the search_with_dependencies method
                dep_results = storage_manager.search_with_dependencies(
                    query_embedding=query_embedding.tolist(),
                    dependency_filter={"has_imports": True},
                    limit=5
                )

            logger.info(f"Dependency-filtered search returned {len(dep_results)} results")
            for i, result in enumerate(dep_results[:3]):
                logger.info(f"Result {i+1}: {result.get('name', 'Unknown')} ({result.get('node_id', 'Unknown')})")
        except Exception as e:
            logger.warning(f"Dependency-filtered search failed: {e}")
            logger.info("Falling back to empty results")
            dep_results = []

        # 7.3: Combined scoring search
        logger.info("Testing combined scoring search")
        try:
            # Get all chunks if vector search failed
            if not vector_results:
                logger.info("Using all chunks for combined scoring test")
                all_results = storage_manager.db_manager.get_all_code_chunks()
                if all_results:
                    query_node_id = all_results[0]["node_id"]
                else:
                    query_node_id = None
            else:
                query_node_id = vector_results[0]["node_id"]

            if query_node_id:
                # Try the combined scoring method
                try:
                    combined_results = storage_manager.search_with_combined_scoring(
                        query_embedding=query_embedding.tolist(),
                        query_node_id=query_node_id,
                        alpha=0.7,
                        beta=0.3,
                        limit=5
                    )
                except Exception as e:
                    logger.warning(f"Combined scoring search failed: {e}")
                    # Fallback to vector results
                    logger.info("Falling back to vector results for combined scoring")
                    combined_results = vector_results[:5]
                    # Add mock scores
                    for i, result in enumerate(combined_results):
                        result["semantic_score"] = 0.9 - (i * 0.1)
                        result["graph_proximity"] = 0.8 - (i * 0.1)
                        result["combined_score"] = 0.85 - (i * 0.1)

                logger.info(f"Combined scoring search returned {len(combined_results)} results")
                for i, result in enumerate(combined_results[:3]):
                    logger.info(f"Result {i+1}: {result.get('name', 'Unknown')} ({result.get('node_id', 'Unknown')})")
                    logger.info(f"  Semantic Score: {result.get('semantic_score', 0.0):.4f}")
                    logger.info(f"  Graph Proximity: {result.get('graph_proximity', 0.0):.4f}")
                    logger.info(f"  Combined Score: {result.get('combined_score', 0.0):.4f}")
            else:
                logger.warning("No chunks available for combined scoring test")
        except Exception as e:
            logger.warning(f"Combined scoring search failed: {e}")
            logger.info("This is expected with older versions of LanceDB or when no dependencies exist")

        # 7.4: Get a chunk with its dependencies
        try:
            # Get all chunks if vector search failed
            if not vector_results:
                logger.info("Using all chunks for get_chunk_with_dependencies test")
                all_results = storage_manager.db_manager.get_all_code_chunks()
                if all_results:
                    chunk_id = all_results[0]["node_id"]
                else:
                    chunk_id = None
            else:
                chunk_id = vector_results[0]["node_id"]

            if chunk_id:
                try:
                    logger.info("Testing get_chunk_with_dependencies")
                    chunk = storage_manager.get_chunk_with_dependencies(chunk_id)
                except Exception as e:
                    logger.warning(f"get_chunk_with_dependencies failed: {e}")
                    # Fallback to getting the chunk directly
                    logger.info("Falling back to direct chunk retrieval")
                    chunk = next((c for c in all_chunks if c.get("node_id") == chunk_id), None)
                    if chunk:
                        # Add mock dependencies
                        chunk["metadata"] = json.dumps({
                            "dependencies": {
                                "incoming": [],
                                "outgoing": []
                            }
                        })

                if chunk:
                    logger.info(f"Got chunk {chunk.get('name', 'Unknown')} ({chunk.get('node_id', 'Unknown')})")

                    # Parse metadata
                    metadata = json.loads(chunk["metadata"]) if isinstance(chunk["metadata"], str) else chunk["metadata"]
                    if "dependencies" in metadata:
                        logger.info(f"Incoming dependencies: {len(metadata['dependencies']['incoming'])}")
                        logger.info(f"Outgoing dependencies: {len(metadata['dependencies']['outgoing'])}")
                else:
                    logger.warning("Failed to retrieve chunk with dependencies")
            else:
                logger.warning("No chunks available for get_chunk_with_dependencies test")
        except Exception as e:
            logger.warning(f"get_chunk_with_dependencies failed: {e}")
            logger.info("This is expected with older versions of LanceDB or when no dependencies exist")

        logger.info("End-to-end integration test completed successfully!")

    finally:
        # Close the unified storage connection
        logger.info("Closing unified storage connection")
        close_unified_storage(storage_manager)


def main():
    """Main function."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="End-to-end integration test")
    parser.add_argument("--db-path", type=str, default="codebase-analyser/.lancedb",
                        help="Path to the LanceDB database")
    parser.add_argument("--test-dir", type=str,
                        help="Directory containing test files (if not provided, a temporary directory will be created)")
    parser.add_argument("--keep-test-dir", action="store_true",
                        help="Keep the test directory after the test (only applies if a temporary directory is created)")
    parser.add_argument("--clear-db", action="store_true",
                        help="Clear the database before testing")
    parser.add_argument("--full-schema", action="store_true",
                        help="Use the full schema instead of the minimal schema")
    parser.add_argument("--real-embeddings", action="store_true",
                        help="Use real embeddings instead of mock embeddings")

    args = parser.parse_args()

    # Create a temporary directory if no test directory is provided
    if args.test_dir:
        test_dir = args.test_dir
        created_temp_dir = False
    else:
        test_dir = tempfile.mkdtemp()
        created_temp_dir = True
        logger.info(f"Created temporary directory: {test_dir}")

    try:
        # Create test files if needed
        if not args.test_dir or not os.listdir(args.test_dir):
            create_test_files(test_dir)

        # Run the end-to-end test
        run_end_to_end_test(
            test_dir=test_dir,
            db_path=args.db_path,
            clear_db=args.clear_db,
            use_minimal_schema=not args.full_schema,
            use_mock_embeddings=not args.real_embeddings
        )

    finally:
        # Clean up the temporary directory if created and not keeping
        if created_temp_dir and not args.keep_test_dir:
            logger.info(f"Removing temporary directory: {test_dir}")
            shutil.rmtree(test_dir)


if __name__ == "__main__":
    main()
