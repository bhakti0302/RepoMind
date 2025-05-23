"""
Main module for NLP analysis.

This module provides the main entry point for NLP analysis of business requirements.
"""

import os
import sys
import logging
import argparse
from typing import Dict, List, Any, Optional, Union

# Add the parent directory to the path to import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.requirements_parser import RequirementsParser
from src.entity_extractor import EntityExtractor
from src.component_analyzer import ComponentAnalyzer
from src.text_processor import TextProcessor
from src.utils import save_json, load_json, ensure_dir, generate_search_queries

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def process_requirements(
    input_file: str,
    output_dir: str = None,
    model_name: str = "en_core_web_md"
) -> Dict[str, Any]:
    """Process business requirements.
    
    Args:
        input_file: Path to the input file
        output_dir: Path to the output directory
        model_name: Name of the spaCy model to use
        
    Returns:
        Dictionary containing processed requirements
    """
    try:
        # Create output directory if specified
        if output_dir:
            ensure_dir(output_dir)
        
        # Initialize components
        parser = RequirementsParser(model_name=model_name)
        extractor = EntityExtractor(nlp=parser.nlp)
        analyzer = ComponentAnalyzer(nlp=parser.nlp)
        processor = TextProcessor(nlp=parser.nlp)
        
        logger.info(f"Processing requirements file: {input_file}")
        
        # Process the file
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Preprocess the text
        preprocessed_text = processor.preprocess_text(text)
        
        # Parse the requirements
        parsed_data = parser.parse(preprocessed_text)
        
        # Extract entities
        entities = extractor.extract_entities(preprocessed_text)
        
        # Analyze components
        components = analyzer.analyze_components(preprocessed_text)
        
        # Clean code references
        cleaned_text = processor.clean_code_references(preprocessed_text)
        
        # Generate search queries
        requirements_by_type = {
            "functional": components["functional_requirements"],
            "non_functional": components["non_functional_requirements"],
            "constraints": [],
            "other": []
        }
        
        # Convert to the format expected by generate_search_queries
        for req_type in requirements_by_type:
            requirements_by_type[req_type] = [item["text"] for item in requirements_by_type[req_type]]
        
        # Add constraints
        for constraint in components["constraints"]:
            requirements_by_type["constraints"].append(constraint["text"])
        
        # Generate search queries
        search_queries = generate_search_queries(requirements_by_type)
        
        # Combine all results
        result = {
            "original_text": text,
            "preprocessed_text": preprocessed_text,
            "cleaned_text": cleaned_text,
            "parsed_data": parsed_data,
            "entities": entities,
            "components": components,
            "search_queries": search_queries
        }
        
        # Save the result if output directory is specified
        if output_dir:
            output_file = os.path.join(output_dir, "processed_requirements.json")
            save_json(result, output_file)
            logger.info(f"Saved processed requirements to {output_file}")
        
        return result
    
    except Exception as e:
        logger.error(f"Error processing requirements: {e}")
        return {"error": str(e)}

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Process business requirements using NLP")
    parser.add_argument("input_file", help="Path to the input file")
    parser.add_argument("--output-dir", help="Path to the output directory")
    parser.add_argument("--model", default="en_core_web_md", help="Name of the spaCy model to use")
    args = parser.parse_args()
    
    # Process the requirements
    result = process_requirements(
        input_file=args.input_file,
        output_dir=args.output_dir,
        model_name=args.model
    )
    
    # Check for errors
    if "error" in result:
        logger.error(f"Failed to process requirements: {result['error']}")
        sys.exit(1)
    
    # Print summary
    print("\nRequirements Processing Summary:")
    print(f"Input file: {args.input_file}")
    
    if args.output_dir:
        print(f"Output directory: {args.output_dir}")
        print(f"Output file: {os.path.join(args.output_dir, 'processed_requirements.json')}")
    
    print(f"\nExtracted {len(result['entities']['all'])} entities")
    print(f"Identified {len(result['components']['actions'])} actions")
    print(f"Found {len(result['components']['functional_requirements'])} functional requirements")
    print(f"Found {len(result['components']['non_functional_requirements'])} non-functional requirements")
    print(f"Generated {len(result['search_queries'])} search queries")
    
    print("\nTop Search Queries:")
    for i, query in enumerate(result['search_queries'][:5], 1):
        print(f"{i}. {query}")
    
    print("\nProcessing completed successfully.")

if __name__ == "__main__":
    main()
