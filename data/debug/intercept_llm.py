#!/usr/bin/env python3
"""
Script to intercept and save the LLM input.
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

def patch_llm_client(output_file):
    """Patch the LLM client to intercept and save the input.
    
    Args:
        output_file: Path to save the intercepted input
    """
    # Try to import the LLM client module
    try:
        from codebase_analyser.llm.llm_client import LLMClient
        logger.info("Successfully imported LLMClient")
        
        # Save the original method
        original_generate = LLMClient.generate
        
        @wraps(original_generate)
        def generate_wrapper(self, *args, **kwargs):
            # Save the input
            input_data = {
                "args": args,
                "kwargs": kwargs
            }
            
            logger.info(f"Intercepted LLM input, saving to: {output_file}")
            with open(output_file, 'w') as f:
                json.dump(input_data, f, indent=2)
            
            # Print summary
            print(f"Intercepted LLM input saved to: {output_file}")
            
            # Call the original method
            return original_generate(self, *args, **kwargs)
        
        # Replace the method
        LLMClient.generate = generate_wrapper
        logger.info("Successfully patched LLMClient.generate")
        
        return True
    
    except ImportError:
        logger.error("Failed to import LLMClient")
        return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Intercept and save the LLM input")
    parser.add_argument("--output-file", required=True, help="Path to save the intercepted input")
    
    args = parser.parse_args()
    
    # Patch the LLM client
    success = patch_llm_client(args.output_file)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
