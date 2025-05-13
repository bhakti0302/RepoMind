#!/usr/bin/env python3
"""
Script to index a single file in LanceDB.
"""

import os
import sys
import argparse
import logging
from pathlib import Path
import importlib

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def index_file(file_path, db_path, project_id):
    """Index a single file in LanceDB.
    
    Args:
        file_path: Path to the file to index
        db_path: Path to the LanceDB database
        project_id: Project ID to associate with the file
    """
    logger.info(f"Indexing file: {file_path}")
    file_path = Path(file_path)
    
    # Dynamically import the necessary modules
    try:
        # Try different possible module paths
        try:
            from codebase_analyser.parsing.analyser import CodebaseAnalyser
            logger.info("Imported CodebaseAnalyser from codebase_analyser.parsing.analyser")
        except ImportError:
            try:
                from codebase_analyser.analyser import CodebaseAnalyser
                logger.info("Imported CodebaseAnalyser from codebase_analyser.analyser")
            except ImportError:
                # Last resort - try to find the module dynamically
                logger.info("Searching for CodebaseAnalyser module...")
                for root, dirs, files in os.walk("codebase-analyser/codebase_analyser"):
                    for file in files:
                        if file == "analyser.py":
                            module_path = os.path.join(root, file)
                            logger.info(f"Found analyser.py at {module_path}")
                            # Try to import from this path
                            module_name = module_path.replace("/", ".").replace(".py", "")
                            CodebaseAnalyser = importlib.import_module(module_name).CodebaseAnalyser
                            break
        
        from codebase_analyser.database.lancedb_manager import LanceDBManager
        from codebase_analyser.embeddings import EmbeddingGenerator
        
        # Create a CodebaseAnalyser instance
        analyser = CodebaseAnalyser(repo_path=os.path.dirname(file_path))
        
        # Parse the file
        logger.info("Parsing file...")
        parsed_file = analyser.parse_file(file_path)
        
        if not parsed_file:
            logger.error(f"Failed to parse file: {file_path}")
            return
        
        # Get the chunks
        logger.info("Generating chunks...")
        try:
            # Try different methods to get chunks
            if hasattr(analyser, 'chunker') and hasattr(analyser.chunker, 'chunk_file'):
                chunks = analyser.chunker.chunk_file(parsed_file)
            elif hasattr(analyser, 'get_chunks'):
                chunks = analyser.get_chunks(parsed_file)
            else:
                logger.error("Could not find a method to generate chunks")
                return
                
            logger.info(f"Generated {len(chunks)} chunks")
        except Exception as e:
            logger.error(f"Error generating chunks: {e}")
            return
        
        # Generate embeddings
        logger.info("Generating embeddings...")
        generator = EmbeddingGenerator()
        for chunk in chunks:
            chunk.embedding = generator.generate_embedding(chunk.content, chunk.language)
            # Add project ID to the chunk
            chunk.project_id = project_id
        
        # Store in database
        logger.info(f"Storing chunks in database: {db_path}")
        db_manager = LanceDBManager(db_path=db_path)
        
        # Create tables if they don't exist
        db_manager.create_tables()
        
        # Add the chunks to the database
        chunk_dicts = [chunk.to_dict() for chunk in chunks]
        db_manager.add_code_chunks(chunk_dicts)
        
        # Get dependencies between chunks if available
        try:
            if hasattr(analyser, 'get_dependencies'):
                dependencies = analyser.get_dependencies(parsed_file)
                
                # Add dependencies to the database if there are any
                if dependencies:
                    logger.info(f"Storing {len(dependencies)} dependencies in database")
                    dependency_dicts = [dep.to_dict() for dep in dependencies]
                    db_manager.add_dependencies(dependency_dicts)
        except Exception as e:
            logger.warning(f"Could not extract dependencies: {e}")
        
        logger.info("Indexing complete")
        
    except Exception as e:
        logger.error(f"Error indexing file: {e}")
        raise

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Index a single file in LanceDB")
    parser.add_argument("--file-path", required=True, help="Path to the file to index")
    parser.add_argument("--db-path", default="codebase-analyser/.lancedb", help="Path to the LanceDB database")
    parser.add_argument("--project-id", default="default", help="Project ID to associate with the file")
    
    args = parser.parse_args()
    
    # Convert file path to absolute path
    file_path = os.path.abspath(args.file_path)
    
    # Index the file
    index_file(file_path, args.db_path, args.project_id)

if __name__ == "__main__":
    main()
