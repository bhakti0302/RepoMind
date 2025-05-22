"""
Business Requirements Processor.

This module processes business requirements using NER and multi-hop RAG.
"""

import os
import sys
import logging
import json
import shutil
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import required modules
try:
    import spacy
    from src.vector_search import VectorSearch
    from src.multi_hop_rag import MultiHopRAG
    from src.requirements_parser import RequirementsParser
    from src.entity_extractor import EntityExtractor
    from src.component_analyzer import ComponentAnalyzer
    from src.text_processor import TextProcessor
    from src.code_synthesis_workflow import CodeSynthesisWorkflow
except ImportError as e:
    logger.error(f"Error importing modules: {e}")
    logger.error("Make sure all required modules are installed")
    sys.exit(1)

class BusinessRequirementsProcessor:
    """Business requirements processor."""

    def __init__(
        self,
        db_path: str = "../.lancedb",
        output_dir: str = "../output",
        data_dir: str = "../../data",
        spacy_model: str = "en_core_web_sm"
    ):
        """Initialize the business requirements processor.

        Args:
            db_path: Path to the LanceDB database
            output_dir: Path to the output directory
            data_dir: Path to the data directory
            spacy_model: Name of the spaCy model to use
        """
        self.db_path = db_path
        self.output_dir = output_dir
        self.data_dir = data_dir
        self.spacy_model = spacy_model

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Load spaCy model
        try:
            self.nlp = spacy.load(spacy_model)
            logger.info(f"Loaded spaCy model: {spacy_model}")
        except Exception as e:
            logger.error(f"Error loading spaCy model: {e}")
            logger.info("Creating a blank English model as fallback")
            self.nlp = spacy.blank("en")
            logger.info("Created blank English model")

        # Initialize components
        self.requirements_parser = RequirementsParser(model_name=spacy_model)
        self.entity_extractor = EntityExtractor(nlp=self.nlp)
        self.component_analyzer = ComponentAnalyzer(nlp=self.nlp)
        self.text_processor = TextProcessor(nlp=self.nlp)

        # Initialize RAG components
        try:
            self.vector_search = VectorSearch(db_path=db_path)
            self.multi_hop_rag = MultiHopRAG(db_path=db_path, output_dir=output_dir)
            logger.info(f"Initialized RAG components with database at {db_path}")
        except Exception as e:
            logger.error(f"Error initializing RAG components: {e}")
            raise

    def process_requirements_file(
        self,
        file_path: str,
        project_id: Optional[str] = None,
        save_to_data_dir: bool = True
    ) -> Dict[str, Any]:
        """Process a business requirements file.

        Args:
            file_path: Path to the business requirements file
            project_id: Project ID (derived from file name if not provided)
            save_to_data_dir: Whether to save the processed requirements to the data directory

        Returns:
            Dictionary containing processed requirements
        """
        try:
            logger.info(f"Processing business requirements file: {file_path}")

            # Get project ID from file name if not provided
            if not project_id:
                project_id = Path(file_path).stem.split("_")[0].lower()
                logger.info(f"Using project ID derived from file name: {project_id}")

            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()

            # Preprocess the text
            preprocessed_text = self.text_processor.preprocess_text(text)

            # Parse the requirements
            parsed_data = self.requirements_parser.parse(preprocessed_text)

            # Extract entities
            entities = self.entity_extractor.extract_entities(preprocessed_text)

            # Analyze components
            components = self.component_analyzer.analyze_components(preprocessed_text)

            # Clean code references
            cleaned_text = self.text_processor.clean_code_references(preprocessed_text)

            # Generate search queries
            requirements_by_type = {
                "functional": [item["text"] for item in components["functional_requirements"]],
                "non_functional": [item["text"] for item in components["non_functional_requirements"]],
                "constraints": [constraint["text"] for constraint in components["constraints"]],
                "other": []
            }

            # Combine all results
            result = {
                "original_text": text,
                "preprocessed_text": preprocessed_text,
                "cleaned_text": cleaned_text,
                "parsed_data": parsed_data,
                "entities": entities,
                "components": components,
                "project_id": project_id,
                "timestamp": datetime.now().isoformat()
            }

            # Save the result if output directory is specified
            output_file = os.path.join(self.output_dir, f"{project_id}_processed_requirements.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            logger.info(f"Saved processed requirements to {output_file}")

            # Save to data directory if requested
            if save_to_data_dir:
                # Create project directory in data directory if it doesn't exist
                project_dir = os.path.join(self.data_dir, "requirements", project_id)
                os.makedirs(project_dir, exist_ok=True)

                # Copy the original file to the project directory
                dest_file = os.path.join(project_dir, Path(file_path).name)
                shutil.copy2(file_path, dest_file)
                logger.info(f"Copied original file to {dest_file}")

                # Save the processed requirements to the project directory
                processed_file = os.path.join(project_dir, f"processed_requirements.json")
                with open(processed_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2)
                logger.info(f"Saved processed requirements to {processed_file}")

            return result

        except Exception as e:
            logger.error(f"Error processing requirements file: {e}")
            return {"error": str(e)}

    def generate_code_from_requirements(
        self,
        processed_requirements: Dict[str, Any],
        rag_type: str = "multi_hop",
        generate_code: bool = True
    ) -> Dict[str, Any]:
        """Generate code from processed requirements.

        Args:
            processed_requirements: Processed requirements
            rag_type: Type of RAG to use (basic, graph, multi_hop)
            generate_code: Whether to generate code using LLM

        Returns:
            Dictionary containing generated code
        """
        try:
            logger.info(f"Generating code from requirements using {rag_type} RAG")

            # Initialize the code synthesis workflow
            workflow = CodeSynthesisWorkflow(
                db_path=self.db_path,
                output_dir=self.output_dir
            )

            # Create a temporary file with the processed requirements text
            temp_file_path = os.path.join(self.output_dir, f"{processed_requirements.get('project_id', 'temp')}_requirements.txt")
            with open(temp_file_path, 'w', encoding='utf-8') as f:
                f.write(processed_requirements.get("original_text", ""))

            # Run the workflow with the temporary file
            result = workflow.run_workflow(
                input_file=temp_file_path,
                project_id=processed_requirements.get("project_id"),
                rag_type=rag_type,
                generate_code=generate_code
            )

            # Close the workflow
            workflow.close()

            return result

        except Exception as e:
            logger.error(f"Error generating code from requirements: {e}")
            return {"error": str(e)}

    def close(self):
        """Close all connections."""
        try:
            if hasattr(self, 'vector_search'):
                self.vector_search.close()
            if hasattr(self, 'multi_hop_rag'):
                self.multi_hop_rag.close()
            logger.info("Closed all connections")
        except Exception as e:
            logger.error(f"Error closing connections: {e}")

# Example usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Process business requirements")
    parser.add_argument("--file", required=True, help="Path to the business requirements file")
    parser.add_argument("--project-id", help="Project ID")
    parser.add_argument("--db-path", default="../.lancedb", help="Path to the LanceDB database")
    parser.add_argument("--output-dir", default="../output", help="Path to the output directory")
    parser.add_argument("--data-dir", default="../../data", help="Path to the data directory")
    parser.add_argument("--rag-type", choices=["basic", "graph", "multi_hop"], default="multi_hop", help="Type of RAG to use")
    parser.add_argument("--generate-code", action="store_true", default=True, help="Whether to generate code using LLM")
    args = parser.parse_args()

    # Initialize the processor
    processor = BusinessRequirementsProcessor(
        db_path=args.db_path,
        output_dir=args.output_dir,
        data_dir=args.data_dir
    )

    try:
        # Process the requirements file
        processed_requirements = processor.process_requirements_file(
            file_path=args.file,
            project_id=args.project_id
        )

        if "error" in processed_requirements:
            logger.error(f"Error processing requirements: {processed_requirements['error']}")
            sys.exit(1)

        # Generate code from requirements
        if args.generate_code:
            result = processor.generate_code_from_requirements(
                processed_requirements=processed_requirements,
                rag_type=args.rag_type,
                generate_code=args.generate_code
            )

            if "error" in result:
                logger.error(f"Error generating code: {result['error']}")
                sys.exit(1)

            logger.info("Code generation completed successfully")

            # Print the output file paths
            if "instructions_file" in result:
                print(f"Instructions file: {result['instructions_file']}")
            if "output_file" in result:
                print(f"Generated code file: {result['output_file']}")

    finally:
        # Close all connections
        processor.close()
