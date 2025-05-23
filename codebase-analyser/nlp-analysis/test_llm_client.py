#!/usr/bin/env python3

"""
Test the LLM client.

This script tests the LLM client with a simple prompt.
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

# Import the LLM client
try:
    from src.llm_client import NVIDIALlamaClient
    from src.env_loader import load_env_vars
except ImportError as e:
    logger.error(f"Error importing modules: {e}")
    sys.exit(1)

def test_llm_client():
    """Test the LLM client with a simple prompt."""
    # Load environment variables
    load_env_vars()
    
    # Get API key from environment
    api_key = os.environ.get("LLM_API_KEY")
    if not api_key:
        logger.error("No API key found in environment variables")
        sys.exit(1)
    
    # Initialize the LLM client
    client = NVIDIALlamaClient(
        api_key=api_key,
        model_name="nvidia/llama-3.3-nemotron-super-49b-v1:free",
        output_dir="/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/output"
    )
    
    # Test prompt
    prompt = "Write a simple Java class that represents an Employee with id, name, and department properties."
    
    # Generate text
    logger.info(f"Generating text for prompt: {prompt}")
    response = client.generate(
        prompt=prompt,
        temperature=0.7,
        max_tokens=500
    )
    
    # Print the response
    print("\nLLM Response:")
    print("-------------")
    print(response)
    
    # Save the response to a file
    output_file = "/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/output/test_llm_output.txt"
    with open(output_file, "w") as f:
        f.write(response)
    
    logger.info(f"Saved response to {output_file}")

if __name__ == "__main__":
    test_llm_client()
