#!/usr/bin/env python3

"""
Run multi-hop RAG and then send to LLM.

This script runs the multi-hop RAG component and then sends the output to the LLM.
"""

import os
import sys
import logging

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import the components
try:
    from src.multi_hop_rag import MultiHopRAG
    from src.llm_client import NVIDIALlamaClient
    from src.env_loader import load_env_vars
except ImportError as e:
    logger.error(f"Error importing modules: {e}")
    sys.exit(1)

def run_rag_to_llm(
    input_file: str,
    db_path: str,
    output_dir: str,
    llm_api_key: str = None,
    llm_model_name: str = "nvidia/llama-3.3-nemotron-super-49b-v1:free",
    temperature: float = 0.7,
    max_tokens: int = 2000
):
    """Run multi-hop RAG and then send to LLM.

    Args:
        input_file: Path to the input file
        db_path: Path to the LanceDB database
        output_dir: Path to the output directory
        llm_api_key: API key for the LLM service
        llm_model_name: Name of the LLM model to use
        temperature: Temperature for LLM generation
        max_tokens: Maximum tokens for LLM generation
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Read the input file
        logger.info(f"Reading input file: {input_file}")
        with open(input_file, 'r') as f:
            content = f.read()

        # Use the first 100 characters as the query
        query = content[:].replace('\n', ' ').strip()
        logger.info(f"Generated query: {query}")

        # Step 1: Run multi-hop RAG
        logger.info("Step 1: Running multi-hop RAG")
        rag = MultiHopRAG(db_path=db_path, output_dir=output_dir)
        rag_result = rag.multi_hop_rag(query=query)
        logger.info(f"Completed multi-hop RAG")

        # Get the multi-hop RAG output
        multi_hop_output_file = os.path.join(output_dir, "output-multi-hop.txt")
        if os.path.exists(multi_hop_output_file):
            with open(multi_hop_output_file, 'r') as f:
                multi_hop_output = f.read()
            logger.info(f"Read {len(multi_hop_output)} characters from multi-hop RAG output")
        else:
            logger.warning(f"Multi-hop RAG output file not found: {multi_hop_output_file}")
            multi_hop_output = "No multi-hop RAG output available."

        # Step 2: Send to LLM
        logger.info("Step 2: Sending to LLM")

        # Get API key from environment if not provided
        llm_api_key = llm_api_key or os.environ.get("LLM_API_KEY")

        if not llm_api_key:
            logger.error("No LLM API key provided")
            sys.exit(1)

        # Get API base URL from environment
        api_base_url = os.environ.get("OPENAI_API_BASE_URL")
        if not api_base_url:
            logger.error("No API base URL found in environment variables")
            sys.exit(1)

        # Initialize LLM client
        llm_client = NVIDIALlamaClient(
            api_key=llm_api_key,
            model_name=llm_model_name,
            api_url=api_base_url,
            output_dir=output_dir
        )

        # Create the prompt for LLM
        prompt = f"# Business Requirements\n\n{content}\n\n"
        prompt += f"# Multi-Hop RAG Analysis\n\n{multi_hop_output}\n\n"
        prompt += "# Instructions\n\n"
        prompt += "Based on the provided business requirements and the multi-hop RAG analysis, "
        prompt += "please provide detailed instructions for implementing the necessary code changes. "
        prompt += "Include specific file paths, class names, method signatures, and any other details "
        prompt += "that would be helpful for implementing the requirements.\n\n"
        prompt += "Please structure your response as follows:\n\n"
        prompt += "1. Overview of the implementation approach\n"
        prompt += "2. Key components and their responsibilities\n"
        prompt += "3. Detailed implementation steps\n"
        prompt += "4. Code examples for critical parts\n"
        prompt += "5. Testing approach\n"

        # Generate code instructions using LLM
        llm_output = llm_client.generate(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )

        # Save the LLM output to LLM-instructions.txt
        llm_instructions_file = os.path.join(output_dir, "LLM-instructions.txt")
        with open(llm_instructions_file, 'w') as f:
            f.write(llm_output)

        logger.info(f"Saved LLM instructions to {llm_instructions_file}")

        # Clean up
        rag.close()

        # Print the output file paths
        print(f"\nMulti-hop RAG output saved to: {multi_hop_output_file}")
        print(f"LLM instructions saved to: {llm_instructions_file}")

        logger.info("Multi-hop RAG to LLM completed successfully")

    except Exception as e:
        logger.error(f"Error running multi-hop RAG to LLM: {e}")
        sys.exit(1)

def main():
    # Load environment variables
    load_env_vars()

    # Parse command-line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Run multi-hop RAG and then send to LLM")
    parser.add_argument("--input-file", default="/Users/bhaktichindhe/Desktop/Project/RepoMind/test-project-employee/EmployeeByDepartmentRequirement.txt",
                        help="Path to the input file")
    parser.add_argument("--db-path", default="/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/.lancedb",
                        help="Path to the LanceDB database")
    parser.add_argument("--output-dir", default="/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/output",
                        help="Path to the output directory")
    parser.add_argument("--llm-model", default="nvidia/llama-3.3-nemotron-super-49b-v1:free",
                        help="Name of the LLM model to use")
    parser.add_argument("--temperature", type=float, default=0.7,
                        help="Temperature for LLM generation")
    parser.add_argument("--max-tokens", type=int, default=2000,
                        help="Maximum tokens for LLM generation")

    args = parser.parse_args()

    # Log the parameters
    logger.info(f"Input file: {args.input_file}")
    logger.info(f"DB path: {args.db_path}")
    logger.info(f"Output directory: {args.output_dir}")
    logger.info(f"LLM model: {args.llm_model}")

    # Check if the input file exists
    if not os.path.exists(args.input_file):
        logger.error(f"Input file not found: {args.input_file}")
        sys.exit(1)

    # Run multi-hop RAG to LLM
    run_rag_to_llm(
        input_file=args.input_file,
        db_path=args.db_path,
        output_dir=args.output_dir,
        llm_model_name=args.llm_model,
        temperature=args.temperature,
        max_tokens=args.max_tokens
    )

    print("\nMulti-hop RAG to LLM completed successfully!")

if __name__ == "__main__":
    main()
