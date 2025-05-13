#!/usr/bin/env python3
"""
Script to intercept and save the code generator prompt.
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
import importlib.util
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def patch_code_generator(output_file):
    """Patch the CodeGenerator to intercept and save the prompt.
    
    Args:
        output_file: Path to save the intercepted prompt
    """
    # Try to import the CodeGenerator module
    try:
        from codebase_analyser.requirements_processor.synthesis.code_generator import CodeGenerator
        logger.info("Successfully imported CodeGenerator")
        
        # Save the original method
        original_prepare_prompt = CodeGenerator._prepare_prompt
        
        @wraps(original_prepare_prompt)
        def prepare_prompt_wrapper(self, requirements, context_chunks, language, file_type):
            # Call the original method to get the prompt
            prompt = original_prepare_prompt(self, requirements, context_chunks, language, file_type)
            
            # Save the prompt and context
            data = {
                "prompt": prompt,
                "system_prompt": self._get_system_prompt(language, file_type),
                "requirements": requirements,
                "context_chunks": context_chunks,
                "language": language,
                "file_type": file_type
            }
            
            logger.info(f"Intercepted code generator prompt, saving to: {output_file}")
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Print summary
            print(f"Intercepted code generator prompt saved to: {output_file}")
            print(f"Prompt length: {len(prompt)} characters")
            print(f"Number of context chunks: {len(context_chunks)}")
            
            return prompt
        
        # Replace the method
        CodeGenerator._prepare_prompt = prepare_prompt_wrapper
        logger.info("Successfully patched CodeGenerator._prepare_prompt")
        
        return True
    
    except ImportError as e:
        logger.error(f"Failed to import CodeGenerator: {e}")
        return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Intercept and save the code generator prompt")
    parser.add_argument("--output-file", required=True, help="Path to save the intercepted prompt")
    
    args = parser.parse_args()
    
    # Patch the code generator
    success = patch_code_generator(args.output_file)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
