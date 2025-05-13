#!/bin/bash

# Set up environment variables for OpenRouter
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
echo "Checking for LanceDB database..."

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
else
  echo "Using LanceDB database at: $DB_PATH"
fi

# Ensure the requirements file directory exists
mkdir -p "data/requirements/input/logger_test_project"

# Create a sample requirements file for adding logging functionality
if [ ! -f "$REQ_FILE" ]; then
  echo "Creating sample requirements file: $REQ_FILE"
  cat > "$REQ_FILE" << EOF
Enhance the existing TestTanya.java class by adding a new method to the exsting code:

1. Add a Java method implementing quick sort
2. Add error handling with appropriate logging for exceptional cases
Use the context provided as well to understand the exisiting code. Return the entire class with the new method added.

The existing TestTanya.java class is located at Test/src/TestTanya.java.
EOF
fi

# Create a script to extract context from LanceDB
echo "Creating context extraction script..."
cat > "$DEBUG_DIR/extract_context.py" << 'EOF'
#!/usr/bin/env python3
"""
Script to extract context from LanceDB for debugging.
"""

import os
import sys
import json
import logging
import lancedb
import argparse
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def extract_context(db_path, project_id, output_file):
    """Extract context from LanceDB for debugging.
    
    Args:
        db_path: Path to the LanceDB database
        project_id: Project ID to filter by
        output_file: Path to save the extracted context
    """
    logger.info(f"Connecting to database: {db_path}")
    db = lancedb.connect(db_path)
    
    # Check if the code_chunks table exists
    if "code_chunks" not in db.table_names():
        logger.error("Code chunks table does not exist")
        return False
    
    # Open the table
    table = db.open_table("code_chunks")
    
    # Get all chunks for the project
    logger.info(f"Extracting chunks for project: {project_id}")
    try:
        df = table.to_pandas()
        project_chunks = df[df["project_id"] == project_id]
        
        logger.info(f"Found {len(project_chunks)} chunks for project '{project_id}'")
        
        # Convert to list of dictionaries
        chunks = []
        for _, row in project_chunks.iterrows():
            chunk = row.to_dict()
            
            # Convert numpy arrays to lists
            for key, value in chunk.items():
                if hasattr(value, 'tolist'):
                    chunk[key] = value.tolist()
            
            chunks.append(chunk)
        
        # Save to file
        logger.info(f"Saving context to: {output_file}")
        with open(output_file, 'w') as f:
            json.dump(chunks, f, indent=2)
        
        # Print summary
        print(f"Extracted {len(chunks)} chunks for project '{project_id}'")
        print(f"Context saved to: {output_file}")
        
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
        
        return True
    
    except Exception as e:
        logger.error(f"Error extracting context: {e}")
        return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Extract context from LanceDB for debugging")
    parser.add_argument("--db-path", required=True, help="Path to the LanceDB database")
    parser.add_argument("--project-id", required=True, help="Project ID to filter by")
    parser.add_argument("--output-file", required=True, help="Path to save the extracted context")
    
    args = parser.parse_args()
    
    # Extract context
    success = extract_context(args.db_path, args.project_id, args.output_file)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF

# Make the script executable
chmod +x "$DEBUG_DIR/extract_context.py"

# Create a script to intercept the LLM input
echo "Creating LLM input interceptor..."
cat > "$DEBUG_DIR/intercept_llm.py" << 'EOF'
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
EOF

# Make the script executable
chmod +x "$DEBUG_DIR/intercept_llm.py"

# Create a script to intercept the code generator prompt
echo "Creating code generator prompt interceptor..."
cat > "$DEBUG_DIR/intercept_code_generator.py" << 'EOF'
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
EOF

# Make the script executable
chmod +x "$DEBUG_DIR/intercept_code_generator.py"

# Create a modified version of process_requirements.py that saves the RAG context
echo "Creating modified process_requirements.py..."
cat > "$DEBUG_DIR/process_requirements_debug.py" << 'EOF'
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
EOF

# Make the script executable
chmod +x "$DEBUG_DIR/process_requirements_debug.py"

# Extract context from LanceDB
echo "Extracting context from LanceDB..."
python "$DEBUG_DIR/extract_context.py" \
  --db-path "$DB_PATH" \
  --project-id "$PROJECT_ID" \
  --output-file "$DEBUG_DIR/lancedb_context.json"

# Patch the LLM client to intercept the input
echo "Patching LLM client..."
python "$DEBUG_DIR/intercept_llm.py" \
  --output-file "$DEBUG_DIR/llm_input.json"

# Patch the code generator to intercept the prompt
echo "Patching code generator..."
python "$DEBUG_DIR/intercept_code_generator.py" \
  --output-file "$DEBUG_DIR/code_generator_prompt.json"

# Run the requirements processor with the modified script
echo "Running requirements processor with debugging..."
python "$DEBUG_DIR/process_requirements_debug.py" \
  --project-id "$PROJECT_ID" \
  --requirement-file "$REQ_FILE" \
  --language java \
  --file-type class \
  --output-format text \
  --output-dir "$OUTPUT_DIR" \
  --model "nvidia/llama-3.3-nemotron-super-49b-v1:free" \
  --api-key "$OPENAI_API_KEY" \
  --db-path "$DB_PATH"

# Find the most recent output file for this project (macOS compatible)
if [ -d "$OUTPUT_DIR/$PROJECT_ID" ]; then
  LATEST_OUTPUT=$(ls -t "$OUTPUT_DIR/$PROJECT_ID"/add_logger_req_tanya*.txt 2>/dev/null | head -1)
else
  LATEST_OUTPUT=""
fi

if [ -z "$LATEST_OUTPUT" ]; then
  echo "No output file found. Check for errors in the processing."
  exit 1
fi

# Print the result
echo "Processing complete. Results saved to $LATEST_OUTPUT"
cat "$LATEST_OUTPUT"

# Print debug information
echo ""
echo "Debug information:"
echo "  - LanceDB context: $DEBUG_DIR/lancedb_context.json"
echo "  - RAG context: $DEBUG_DIR/rag_context.json"
echo "  - Requirement details: $DEBUG_DIR/requirement_details.json"
echo "  - Code generator prompt: $DEBUG_DIR/code_generator_prompt.json"
echo "  - LLM input: $DEBUG_DIR/llm_input.json"
echo "  - LLM API request: $DEBUG_DIR/llm_input_request.json"

# Check if the debug files exist
if [ -f "$DEBUG_DIR/lancedb_context.json" ]; then
  echo "  - LanceDB context size: $(wc -c < "$DEBUG_DIR/lancedb_context.json") bytes"
fi

if [ -f "$DEBUG_DIR/rag_context.json" ]; then
  echo "  - RAG context size: $(wc -c < "$DEBUG_DIR/rag_context.json") bytes"
fi

if [ -f "$DEBUG_DIR/requirement_details.json" ]; then
  echo "  - Requirement details size: $(wc -c < "$DEBUG_DIR/requirement_details.json") bytes"
fi

if [ -f "$DEBUG_DIR/code_generator_prompt.json" ]; then
  echo "  - Code generator prompt size: $(wc -c < "$DEBUG_DIR/code_generator_prompt.json") bytes"
fi

if [ -f "$DEBUG_DIR/llm_input.json" ]; then
  echo "  - LLM input size: $(wc -c < "$DEBUG_DIR/llm_input.json") bytes"
fi

if [ -f "$DEBUG_DIR/llm_input_request.json" ]; then
  echo "  - LLM API request size: $(wc -c < "$DEBUG_DIR/llm_input_request.json") bytes"
fi

echo ""
echo "To view the debug files, run:"
echo "  cat $DEBUG_DIR/lancedb_context.json | jq"
echo "  cat $DEBUG_DIR/rag_context.json | jq"
echo "  cat $DEBUG_DIR/requirement_details.json | jq"
echo "  cat $DEBUG_DIR/code_generator_prompt.json | jq"
echo "  cat $DEBUG_DIR/llm_input.json | jq"
echo "  cat $DEBUG_DIR/llm_input_request.json | jq"
