#!/usr/bin/env python3

"""
End-to-End RAG Workflow Test Script.

This script tests the entire RAG workflow from processing business requirements
to generating code using the LLM. It verifies:
1. NLP processing of requirements
2. Vector search functionality
3. Multi-hop RAG implementation
4. LLM code generation
5. End-to-end workflow

Usage:
    python test_end_to_end_rag_workflow.py --input-file path/to/requirements.txt --db-path path/to/db --output-dir path/to/output
"""

import os
import sys
import logging
import argparse
import json
import time
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the components
try:
    from src.code_synthesis_workflow import CodeSynthesisWorkflow
    from src.entity_extractor import EntityExtractor
    from src.component_analyzer import ComponentAnalyzer
    from src.vector_search import VectorSearch
    from src.multi_hop_rag import MultiHopRAG
    from src.llm_client import NVIDIALlamaClient
    from src.env_loader import load_env_vars
except ImportError as e:
    logger.error(f"Error importing modules: {e}")
    sys.exit(1)

def ensure_dir(directory: str) -> None:
    """Ensure a directory exists.
    
    Args:
        directory: Directory path to ensure exists
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Created directory: {directory}")

def save_json(data: Dict[str, Any], file_path: str) -> None:
    """Save data to a JSON file.
    
    Args:
        data: Data to save
        file_path: Path to the file
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    logger.info(f"Saved JSON data to {file_path}")

def test_nlp_processing(input_file: str, output_dir: str) -> Dict[str, Any]:
    """Test NLP processing of requirements.
    
    Args:
        input_file: Path to the input file
        output_dir: Path to the output directory
        
    Returns:
        Dictionary containing NLP processing results
    """
    logger.info("Testing NLP processing...")
    
    # Read the input file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Initialize components
    entity_extractor = EntityExtractor()
    component_analyzer = ComponentAnalyzer()
    
    # Extract entities
    entities = entity_extractor.extract_entities(content)
    logger.info(f"Extracted {sum(len(entities[key]) for key in entities if isinstance(entities[key], list))} entities")
    
    # Analyze components
    components = component_analyzer.analyze_components(content)
    logger.info(f"Analyzed components: {len(components.get('functional_requirements', []))} functional requirements, {len(components.get('non_functional_requirements', []))} non-functional requirements")
    
    # Save results
    nlp_results = {
        "entities": entities,
        "components": components
    }
    
    save_json(nlp_results, os.path.join(output_dir, "nlp_results.json"))
    
    return nlp_results

def test_vector_search(db_path: str, query: str, output_dir: str) -> Dict[str, Any]:
    """Test vector search functionality.
    
    Args:
        db_path: Path to the LanceDB database
        query: Search query
        output_dir: Path to the output directory
        
    Returns:
        Dictionary containing vector search results
    """
    logger.info("Testing vector search...")
    
    # Initialize vector search
    vector_search = VectorSearch(db_path=db_path)
    
    # Search for code chunks
    search_results = vector_search.search(query=query, limit=5)
    logger.info(f"Found {len(search_results)} results for query: '{query}'")
    
    # Save results
    search_results_file = os.path.join(output_dir, "vector_search_results.json")
    
    # Convert search results to a serializable format
    serializable_results = []
    for result in search_results:
        serializable_result = {}
        for key, value in result.items():
            if isinstance(value, (str, int, float, bool, list, dict)) or value is None:
                serializable_result[key] = value
            else:
                serializable_result[key] = str(value)
        serializable_results.append(serializable_result)
    
    save_json({"query": query, "results": serializable_results}, search_results_file)
    
    # Close the connection
    vector_search.close()
    
    return {"query": query, "results": search_results}

def test_multi_hop_rag(db_path: str, query: str, output_dir: str) -> Dict[str, Any]:
    """Test multi-hop RAG implementation.
    
    Args:
        db_path: Path to the LanceDB database
        query: Search query
        output_dir: Path to the output directory
        
    Returns:
        Dictionary containing multi-hop RAG results
    """
    logger.info("Testing multi-hop RAG...")
    
    # Initialize multi-hop RAG
    rag = MultiHopRAG(db_path=db_path, output_dir=output_dir)
    
    # Implement multi-hop RAG
    rag_result = rag.multi_hop_rag(query=query)
    logger.info(f"Completed multi-hop RAG for query: '{query}'")
    
    # Save results
    rag_results_file = os.path.join(output_dir, "multi_hop_rag_results.json")
    
    # Convert RAG results to a serializable format
    serializable_result = {}
    for key, value in rag_result.items():
        if key != "context":  # Skip the context as it can be very large
            if isinstance(value, (str, int, float, bool, list, dict)) or value is None:
                serializable_result[key] = value
            else:
                serializable_result[key] = str(value)
    
    save_json(serializable_result, rag_results_file)
    
    # Close the connection
    rag.close()
    
    return rag_result

def test_llm_code_generation(prompt: str, output_dir: str) -> Optional[str]:
    """Test LLM code generation.
    
    Args:
        prompt: Prompt for the LLM
        output_dir: Path to the output directory
        
    Returns:
        Generated code or None if LLM client is not available
    """
    logger.info("Testing LLM code generation...")
    
    # Load environment variables
    load_env_vars()
    
    # Get API key from environment
    api_key = os.environ.get("LLM_API_KEY")
    if not api_key:
        logger.warning("No API key found in environment variables. Skipping LLM test.")
        return None
    
    # Initialize the LLM client
    try:
        client = NVIDIALlamaClient(
            api_key=api_key,
            model_name=os.environ.get("LLM_MODEL_NAME", "nvidia/llama-3.3-nemotron-super-49b-v1:free"),
            output_dir=output_dir
        )
        
        # Generate code
        logger.info(f"Generating code for prompt: '{prompt[:100]}...'")
        response = client.generate(
            prompt=prompt,
            temperature=0.7,
            max_tokens=1000
        )
        
        # Save the response to a file
        output_file = os.path.join(output_dir, "llm_generated_code.txt")
        with open(output_file, "w") as f:
            f.write(response)
        
        logger.info(f"Saved generated code to {output_file}")
        
        return response
    
    except Exception as e:
        logger.error(f"Error testing LLM code generation: {e}")
        return None

def test_end_to_end_workflow(input_file: str, db_path: str, output_dir: str) -> Dict[str, Any]:
    """Test the end-to-end workflow.
    
    Args:
        input_file: Path to the input file
        db_path: Path to the LanceDB database
        output_dir: Path to the output directory
        
    Returns:
        Dictionary containing workflow results
    """
    logger.info("Testing end-to-end workflow...")
    
    # Initialize the workflow
    workflow = CodeSynthesisWorkflow(
        db_path=db_path,
        output_dir=output_dir
    )
    
    # Run the workflow
    start_time = time.time()
    result = workflow.run_workflow(
        input_file=input_file,
        rag_type="multi_hop",
        generate_code=True
    )
    end_time = time.time()
    
    # Calculate execution time
    execution_time = end_time - start_time
    logger.info(f"Workflow completed in {execution_time:.2f} seconds")
    
    # Check for errors
    if "error" in result:
        logger.error(f"Workflow failed: {result['error']}")
        return {"error": result["error"], "execution_time": execution_time}
    
    # Save workflow results
    workflow_results_file = os.path.join(output_dir, "workflow_results.json")
    
    # Convert workflow results to a serializable format
    serializable_result = {
        "execution_time": execution_time,
        "instructions_file": result.get("instructions_file"),
        "output_file": result.get("output_file")
    }
    
    if "llm_error" in result:
        serializable_result["llm_error"] = result["llm_error"]
    
    save_json(serializable_result, workflow_results_file)
    
    # Close connections
    workflow.close()
    
    return {**result, "execution_time": execution_time}

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test the end-to-end RAG workflow")
    parser.add_argument("--input-file", required=True, help="Path to the input file")
    parser.add_argument("--db-path", default="../.lancedb", help="Path to the LanceDB database")
    parser.add_argument("--output-dir", default="./output", help="Path to the output directory")
    parser.add_argument("--skip-llm", action="store_true", help="Skip LLM code generation test")
    args = parser.parse_args()
    
    # Ensure output directory exists
    ensure_dir(args.output_dir)
    
    # Test NLP processing
    nlp_results = test_nlp_processing(args.input_file, args.output_dir)
    
    # Generate a query from the NLP results
    query_parts = []
    
    # Add nouns
    if 'nouns' in nlp_results["entities"]:
        query_parts.extend(nlp_results["entities"]["nouns"][:5])
    
    # Add technical terms
    if 'technical_terms' in nlp_results["entities"]:
        query_parts.extend(nlp_results["entities"]["technical_terms"][:3])
    
    # Add functional requirements
    for req in nlp_results["components"].get("functional_requirements", [])[:2]:
        query_parts.append(req.get('text', ''))
    
    # If no query parts, use a default query
    if not query_parts:
        query = "employee department management system"
    else:
        # Create the query
        query = " ".join(query_parts)
    
    # Test vector search
    vector_search_results = test_vector_search(args.db_path, query, args.output_dir)
    
    # Test multi-hop RAG
    rag_results = test_multi_hop_rag(args.db_path, query, args.output_dir)
    
    # Test LLM code generation if not skipped
    if not args.skip_llm:
        # Create a prompt for the LLM
        prompt = f"# Requirements\n\n"
        
        # Add functional requirements
        prompt += "## Functional Requirements\n\n"
        for req in nlp_results["components"].get("functional_requirements", [])[:5]:
            prompt += f"- {req.get('text', '')}\n"
        
        # Add non-functional requirements
        prompt += "\n## Non-Functional Requirements\n\n"
        for req in nlp_results["components"].get("non_functional_requirements", [])[:3]:
            prompt += f"- {req.get('text', '')}\n"
        
        # Add context from RAG
        prompt += f"\n# Context\n\n{rag_results.get('context', '')[:2000]}\n\n"
        
        # Add instructions
        prompt += "# Instructions\n\n"
        prompt += "Based on the provided requirements and context, implement the necessary code changes.\n\n"
        prompt += "Please provide your implementation in the following format:\n\n"
        prompt += "## File: [file_path]\n\n"
        prompt += "```[language]\n// Your code here\n```\n\n"
        
        # Test LLM code generation
        generated_code = test_llm_code_generation(prompt, args.output_dir)
    else:
        logger.info("Skipping LLM code generation test")
        generated_code = None
    
    # Test end-to-end workflow
    workflow_results = test_end_to_end_workflow(args.input_file, args.db_path, args.output_dir)
    
    # Print summary
    print("\nTest Summary:")
    print("=============")
    print(f"Input File: {args.input_file}")
    print(f"Database Path: {args.db_path}")
    print(f"Output Directory: {args.output_dir}")
    print(f"NLP Processing: {len(nlp_results['entities'].get('nouns', []))} nouns, {len(nlp_results['components'].get('functional_requirements', []))} functional requirements")
    print(f"Vector Search: {len(vector_search_results['results'])} results")
    print(f"Multi-Hop RAG: {len(rag_results.get('architectural_patterns', []))} architectural patterns, {len(rag_results.get('implementation_details', []))} implementation details")
    
    if generated_code:
        print(f"LLM Code Generation: {len(generated_code.split())} words")
    else:
        print("LLM Code Generation: Skipped")
    
    print(f"End-to-End Workflow: {'Success' if 'error' not in workflow_results else 'Failed'}")
    print(f"Execution Time: {workflow_results.get('execution_time', 0):.2f} seconds")
    
    if "error" in workflow_results:
        print(f"Error: {workflow_results['error']}")
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    main()
