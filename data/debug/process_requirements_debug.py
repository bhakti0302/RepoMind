#!/usr/bin/env python3
"""
Modified version of process_requirements.py that saves the RAG context.
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
import importlib.util
import inspect
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point."""
    # Get the path to the original script
    original_script_path = os.path.join("codebase-analyser", "scripts", "process_requirements.py")
    
    # Check if the original script exists
    if not os.path.exists(original_script_path):
        logger.error(f"Original script not found: {original_script_path}")
        return False
    
    # Import the original script
    spec = importlib.util.spec_from_file_location("process_requirements", original_script_path)
    process_requirements = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(process_requirements)
    
    # Get the original main function
    original_main = process_requirements.main
    
    # Get the original RequirementsProcessor class
    from codebase_analyser.requirements.requirements_processor import RequirementsProcessor
    
    # Save the original process_requirement method
    original_process_requirement = RequirementsProcessor.process_requirement
    
    # Define a wrapper for the process_requirement method
    @wraps(original_process_requirement)
    def process_requirement_wrapper(self, *args, **kwargs):
        # Get the RAG context
        logger.info("Getting RAG context...")
        
        # Get the requirement text
        requirement_text = kwargs.get("requirement_text")
        if not requirement_text and args:
            requirement_text = args[0]
        
        # Get the project ID
        project_id = kwargs.get("project_id")
        if not project_id and len(args) > 1:
            project_id = args[1]
        
        # Get the language
        language = kwargs.get("language")
        if not language and "language" in self.__dict__:
            language = self.language
        
        # Get the file type
        file_type = kwargs.get("file_type")
        if not file_type and "file_type" in self.__dict__:
            file_type = self.file_type
        
        # Save the requirement details
        requirement_details = {
            "requirement_text": requirement_text,
            "project_id": project_id,
            "language": language,
            "file_type": file_type
        }
        
        # Save to file
        debug_dir = os.path.join("data", "debug")
        os.makedirs(debug_dir, exist_ok=True)
        
        requirement_file = os.path.join(debug_dir, "requirement_details.json")
        logger.info(f"Saving requirement details to: {requirement_file}")
        with open(requirement_file, 'w') as f:
            json.dump(requirement_details, f, indent=2)
        
        # Get the RAG context
        if hasattr(self, "codebase_service") and self.codebase_service:
            # Get the relevant chunks
            logger.info("Getting relevant chunks...")
            
            # Define a function to get relevant chunks
            def get_relevant_chunks(query, project_id, limit=10):
                try:
                    # Get the chunks
                    chunks = self.codebase_service.search(
                        query=query,
                        project_id=project_id,
                        limit=limit
                    )
                    
                    # Convert to list of dictionaries
                    result = []
                    for chunk in chunks:
                        chunk_dict = chunk.to_dict()
                        
                        # Convert numpy arrays to lists
                        for key, value in chunk_dict.items():
                            if hasattr(value, 'tolist'):
                                chunk_dict[key] = value.tolist()
                        
                        result.append(chunk_dict)
                    
                    return result
                except Exception as e:
                    logger.error(f"Error getting relevant chunks: {e}")
                    return []
            
            # Get the chunks
            chunks = get_relevant_chunks(requirement_text, project_id)
            
            # Save to file
            rag_context_file = os.path.join(debug_dir, "rag_context.json")
            logger.info(f"Saving RAG context to: {rag_context_file}")
            with open(rag_context_file, 'w') as f:
                json.dump(chunks, f, indent=2)
            
            # Print summary
            print(f"RAG context saved to: {rag_context_file}")
            print(f"Found {len(chunks)} relevant chunks")
            
            # Print chunk types
            chunk_types = {}
            for chunk in chunks:
                chunk_type = chunk.get('chunk_type', 'unknown')
                if chunk_type not in chunk_types:
                    chunk_types[chunk_type] = 0
                chunk_types[chunk_type] += 1
            
            print("\nChunk types:")
            for chunk_type, count in chunk_types.items():
                print(f"  - {chunk_type}: {count}")
            
            # Print file paths
            file_paths = set()
            for chunk in chunks:
                file_path = chunk.get('file_path', '')
                if file_path:
                    file_paths.add(file_path)
            
            print("\nFile paths:")
            for file_path in file_paths:
                print(f"  - {file_path}")
        
        # Call the original method
        return original_process_requirement(self, *args, **kwargs)
    
    # Replace the method
    RequirementsProcessor.process_requirement = process_requirement_wrapper
    
    # Call the original main function with the command line arguments
    return original_main()

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
