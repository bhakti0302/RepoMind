
"""
Main processor for requirements-based code generation.

This module provides the main processor that orchestrates the entire
requirements-to-code generation pipeline.
"""

import logging
import os
import uuid
from typing import Dict, List, Set, Optional, Any, Tuple, Union
from pathlib import Path

from .nlp.entity_extractor import CodeEntityExtractor
from .nlp.requirements_parser import RequirementsParser
from .rag.context_retriever import ContextRetriever
from .rag.relevance_scorer import RelevanceScorer
from .synthesis.code_generator import CodeGenerator
from .synthesis.output_formatter import OutputFormatter
from .utils.file_utils import (
    save_requirement_file,
    load_requirement_file,
    ensure_dir_exists,
    read_text_file
)

logger = logging.getLogger(__name__)

class RequirementsProcessor:
    """Main processor for requirements-based code generation."""
    
    def __init__(
        self,
        db_path: str = ".lancedb",
        output_dir: str = "output",
        model: str = "deepseek/deepseek-prover-v2:free",
        api_key: Optional[str] = None
    ):
        """Initialize the requirements processor.
        
        Args:
            db_path: Path to the LanceDB database
            output_dir: Directory to save output files
            model: Name of the model to use for code generation
            api_key: OpenRouter API key (defaults to environment variable)
        """
        # Initialize components
        self.entity_extractor = CodeEntityExtractor()
        self.requirements_parser = RequirementsParser()
        self.context_retriever = ContextRetriever(db_path=db_path)
        self.relevance_scorer = RelevanceScorer()
        self.code_generator = CodeGenerator(model=model, api_key=api_key)
        self.output_formatter = OutputFormatter(output_dir=output_dir)
        
        logger.info(f"Initialized RequirementsProcessor with database at {db_path}")
    
    def process_requirement(
        self,
        requirement_text: str,
        project_id: str,
        requirement_id: Optional[str] = None,
        language: str = "java",
        file_type: str = "class",
        save_results: bool = True
    ) -> Dict[str, Any]:
        """Process a requirement and generate code.
        
        Args:
            requirement_text: Text of the requirement
            project_id: Project ID
            requirement_id: Requirement ID (generated if not provided)
            language: Target programming language
            file_type: Type of file to generate
            save_results: Whether to save results to files
            
        Returns:
            Dictionary with processing results
        """
        # Generate requirement ID if not provided
        if requirement_id is None:
            requirement_id = str(uuid.uuid4())
        
        logger.info(f"Processing requirement {requirement_id} for project {project_id}")
        
        # Save requirement text if requested
        if save_results:
            save_requirement_file(project_id, requirement_id, requirement_text)
        
        # Step 1: Parse the requirement
        logger.info("Step 1: Parsing requirement")
        parsed_requirement = self.requirements_parser.parse_text(requirement_text)
        
        # Step 2: Extract entities
        logger.info("Step 2: Extracting entities")
        entities = self.entity_extractor.extract_entities(requirement_text)
        parsed_requirement["entities"] = entities
        
        # Step 3: Extract search terms
        logger.info("Step 3: Extracting search terms")
        try:
            search_terms = self.entity_extractor.extract_search_terms(requirement_text)
            # Ensure all search terms are strings
            search_terms = [str(term) for term in search_terms if term is not None]
            parsed_requirement["search_terms"] = search_terms
            logger.info(f"Extracted search terms: {search_terms}")
        except Exception as e:
            logger.error(f"Error extracting search terms: {e}")
            search_terms = []
            parsed_requirement["search_terms"] = search_terms

        # Step 4: Retrieve relevant context
        logger.info("Step 4: Retrieving context")
        try:
            context_chunks = self.context_retriever.retrieve_combined(
                text=requirement_text,
                keywords=search_terms,
                project_id=project_id,
                limit=20,
                language=language
            )
            
            if not context_chunks:
                logger.warning("No context chunks found. Proceeding without context.")
                context_chunks = []
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            context_chunks = []

        # Step 5: Score and filter context
        logger.info("Step 5: Scoring and filtering context")
        logger.info(f"context_chunks: {len(context_chunks)} chunks retrieved")

        if context_chunks:
            # Log the first few chunks for debugging
            for i, chunk in enumerate(context_chunks[:3]):
                logger.info(f"Sample chunk {i+1}: {chunk.get('file_path', 'unknown')}, {chunk.get('chunk_type', 'unknown')}")
            
            try:
                # Ensure entities is a dictionary of lists of strings
                sanitized_entities = {}
                for key, value in entities.items():
                    if isinstance(value, list):
                        sanitized_entities[key] = [str(item) for item in value if item is not None]
                    else:
                        sanitized_entities[key] = [str(value)] if value is not None else []
            
                scored_chunks = self.relevance_scorer.score_chunks(
                    chunks=context_chunks,
                    keywords=search_terms,
                    entities=sanitized_entities
                )
            
                # Log the scores of the top chunks
                for i, chunk in enumerate(scored_chunks[:5]):
                    logger.info(f"Top scored chunk {i+1}: score={chunk.get('relevance_score', 0)}, file={chunk.get('file_path', 'unknown')}")
            
                filtered_chunks = self.relevance_scorer.filter_by_threshold(
                    chunks=scored_chunks,
                    threshold=0.3
                )
            
                # If no chunks passed the filter, take the top 5 scored chunks
                if not filtered_chunks and scored_chunks:
                    logger.warning("No chunks passed the threshold filter. Taking top 5 scored chunks.")
                    filtered_chunks = scored_chunks[:5]
            
                logger.info(f"After filtering: {len(filtered_chunks)} chunks")
            except Exception as e:
                logger.error(f"Error scoring and filtering chunks: {e}")
                # Use the first 5 chunks as a fallback
                filtered_chunks = context_chunks[:5]
                logger.warning(f"Using first {len(filtered_chunks)} chunks as fallback due to error")
        else:
            filtered_chunks = []
            logger.warning("No context chunks to filter")

        # Step 6: Generate code
        logger.info("Step 6: Generating code")
        logger.info("parsed_requirement"+str(parsed_requirement))
        logger.info("filtered_chunks"+str(filtered_chunks))
        generation_result = self.code_generator.generate_code(
            requirements=parsed_requirement,
            context_chunks=filtered_chunks,
            language=language,
            file_type=file_type
        )
        
        # Step 7: Format and save output
        logger.info("Step 7: Formatting and saving output")
        formatted_output = self.output_formatter.format_for_display(generation_result)
        
        if save_results:
            saved_files = self.output_formatter.save_to_data_dir(
                result=generation_result,
                project_id=project_id,
                requirement_id=requirement_id
            )
            generation_result["saved_files"] = saved_files
        
        # Prepare final result
        result = {
            "requirement_id": requirement_id,
            "project_id": project_id,
            "parsed_requirement": parsed_requirement,
            "context_chunks": filtered_chunks,
            "generation_result": generation_result,
            "formatted_output": formatted_output
        }
        
        logger.info(f"Completed processing requirement {requirement_id}")
        
        return result
    
    def process_requirement_file(
        self,
        file_path: str,
        project_id: str,
        language: str = "java",
        file_type: str = "class",
        save_results: bool = True
    ) -> Dict[str, Any]:
        """Process a requirement file and generate code.
        
        Args:
            file_path: Path to the requirement file
            project_id: Project ID
            language: Target programming language
            file_type: Type of file to generate
            save_results: Whether to save results to files
            
        Returns:
            Dictionary with processing results
        """
        logger.info(f"Processing requirement file: {file_path}")
        
        # Read the requirement file
        requirement_text = read_text_file(file_path)
        
        # Generate requirement ID from filename
        requirement_id = Path(file_path).stem
        
        # Process the requirement
        return self.process_requirement(
            requirement_text=requirement_text,
            project_id=project_id,
            requirement_id=requirement_id,
            language=language,
            file_type=file_type,
            save_results=save_results
        )
    
    def process_project_requirements(
        self,
        project_id: str,
        requirements_dir: str,
        language: str = "java",
        file_type: str = "class",
        save_results: bool = True
    ) -> Dict[str, Dict[str, Any]]:
        """Process all requirements in a directory.
        
        Args:
            project_id: Project ID
            requirements_dir: Directory containing requirement files
            language: Target programming language
            file_type: Type of file to generate
            save_results: Whether to save results to files
            
        Returns:
            Dictionary mapping requirement IDs to processing results
        """
        logger.info(f"Processing requirements in directory: {requirements_dir}")
        
        # Get all text files in the directory
        requirements_path = Path(requirements_dir)
        requirement_files = list(requirements_path.glob("*.txt"))
        
        if not requirement_files:
            logger.warning(f"No requirement files found in {requirements_dir}")
            return {}
        
        # Process each requirement file
        results = {}
        for file_path in requirement_files:
            try:
                result = self.process_requirement_file(
                    file_path=str(file_path),
                    project_id=project_id,
                    language=language,
                    file_type=file_type,
                    save_results=save_results
                )
                results[result["requirement_id"]] = result
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                results[file_path.stem] = {"error": str(e)}
        
        return results
    
    def close(self):
        """Close the processor and release resources."""
        # Close the context retriever
        if hasattr(self.context_retriever, 'close'):
            self.context_retriever.close()
        
        logger.info("Closed RequirementsProcessor")



