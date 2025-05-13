#!/bin/bash

# Set up environment variables
export OPENAI_API_KEY="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"
export PYTHONPATH="$PYTHONPATH:$(pwd):$(pwd)/codebase-analyser"

# Set up project ID and requirement file
PROJECT_ID="Test"
REQ_FILE="data/requirements/input/logger_test_project/add_logger_req_tanya.txt"
OUTPUT_DIR="data/requirements/output"
DEBUG_DIR="data/debug"

# Create debug directory
mkdir -p "$DEBUG_DIR"

# Print debugging information
echo "Current directory: $(pwd)"
echo "PYTHONPATH: $PYTHONPATH"

# Check common locations for the LanceDB database
DB_PATHS=(
  "./codebase-analyser/.lancedb"
  "./.lancedb"
  "../.lancedb"
  "../../.lancedb"
)

for path in "${DB_PATHS[@]}"; do
  if [ -d "$path" ]; then
    echo "Found LanceDB database at: $path"
    DB_PATH="$path"
  fi
done

if [ -z "$DB_PATH" ]; then
  echo "Warning: Could not find LanceDB database in common locations"
  DB_PATH=".lancedb"  # Default fallback
fi

# Create the print_prompt.py script
echo "Creating prompt printer script..."
cat > "$DEBUG_DIR/print_prompt.py" << 'EOF'
#!/usr/bin/env python3
"""
Script to print the prompt being sent to the LLM without making the API call.
"""

import os
import sys
import json
import logging
from pathlib import Path
import importlib.util
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def patch_code_generator():
    """Patch the CodeGenerator to print the prompt without making the API call."""
    try:
        # Import the CodeGenerator class
        from codebase_analyser.requirements_processor.synthesis.code_generator import CodeGenerator
        logger.info("Successfully imported CodeGenerator")
        
        # Save the original generate_code method
        original_generate_code = CodeGenerator.generate_code
        
        @wraps(original_generate_code)
        def generate_code_wrapper(self, requirements, context_chunks, language="java", file_type="class"):
            # Get the system prompt
            system_prompt = self._get_system_prompt(language, file_type)
            
            # Get the user prompt
            user_prompt = self._prepare_prompt(requirements, context_chunks, language, file_type)
            
            # Print the prompts
            print("\n" + "="*80)
            print("SYSTEM PROMPT:")
            print("="*80)
            print(system_prompt)
            print("\n" + "="*80)
            print("USER PROMPT:")
            print("="*80)
            print(user_prompt)
            print("="*80 + "\n")
            
            # Save the prompts to files
            with open("data/debug/system_prompt.txt", "w") as f:
                f.write(system_prompt)
            
            with open("data/debug/user_prompt.txt", "w") as f:
                f.write(user_prompt)
            
            print(f"Prompts saved to data/debug/system_prompt.txt and data/debug/user_prompt.txt")
            
            # Return a dummy response
            return {
                "code": "// Prompt printing mode - no API call made",
                "explanation": "This is a dummy response for prompt printing mode."
            }
        
        # Replace the method
        CodeGenerator.generate_code = generate_code_wrapper
        logger.info("Successfully patched CodeGenerator.generate_code")
        
        return True
    
    except ImportError as e:
        logger.error(f"Failed to import CodeGenerator: {e}")
        return False

def main():
    """Main entry point."""
    # Create the debug directory if it doesn't exist
    os.makedirs("data/debug", exist_ok=True)
    
    # Patch the code generator
    success = patch_code_generator()
    
    if not success:
        sys.exit(1)
    
    print("CodeGenerator patched to print prompts without making API calls.")
    print("Run the requirements processor to see the prompts.")

if __name__ == "__main__":
    main()
EOF

# Make the script executable
chmod +x "$DEBUG_DIR/print_prompt.py"

# Run the prompt printer
echo "Installing prompt printer..."
python "$DEBUG_DIR/print_prompt.py"

# Run the requirements processor
echo "Running requirements processor to print prompts..."
python codebase-analyser/scripts/process_requirements.py \
  --project-id "$PROJECT_ID" \
  --requirement-file "$REQ_FILE" \
  --language java \
  --file-type class \
  --output-format text \
  --output-dir "$OUTPUT_DIR" \
  --model "nvidia/llama-3.3-nemotron-super-49b-v1:free" \
  --api-key "$OPENAI_API_KEY" \
  --db-path "$DB_PATH"

# Print debug information
echo ""
echo "Debug information:"
echo "  - System prompt: $DEBUG_DIR/system_prompt.txt"
echo "  - User prompt: $DEBUG_DIR/user_prompt.txt"

# Check if the debug files exist
if [ -f "$DEBUG_DIR/system_prompt.txt" ]; then
  echo "  - System prompt size: $(wc -c < "$DEBUG_DIR/system_prompt.txt") bytes"
fi

if [ -f "$DEBUG_DIR/user_prompt.txt" ]; then
  echo "  - User prompt size: $(wc -c < "$DEBUG_DIR/user_prompt.txt") bytes"
fi

echo ""
echo "To view the prompts, run:"
echo "  cat $DEBUG_DIR/system_prompt.txt"
echo "  cat $DEBUG_DIR/user_prompt.txt"