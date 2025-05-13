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

The existing TestTanya.java class is located at Test/src/TestTanya.java.
EOF
fi

# Create a direct LLM interceptor that prints the prompt
echo "Creating LLM interceptor..."
cat > "$DEBUG_DIR/intercept_llm_print.py" << 'EOF'
#!/usr/bin/env python3
"""
Script to intercept LLM calls and print the prompt.
"""

import os
import sys
import json
import logging
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def patch_langchain():
    """Patch LangChain to print the prompt."""
    try:
        # Try to import LangChain
        from langchain_core.language_models.chat_models import BaseChatModel
        logger.info("Successfully imported LangChain BaseChatModel")
        
        # Save the original _generate method
        original_generate = BaseChatModel._generate
        
        @wraps(original_generate)
        def _generate_wrapper(self, messages, *args, **kwargs):
            # Print the messages
            print("\n" + "="*80)
            print("LLM PROMPT:")
            print("="*80)
            
            for i, message in enumerate(messages):
                print(f"[Message {i+1} - {message.type}]")
                print("-" * 40)
                print(message.content)
                print("-" * 40)
                print()
            
            # Save the messages to a file
            output_file = os.path.join("data", "debug", "llm_prompt.txt")
            with open(output_file, 'w') as f:
                for i, message in enumerate(messages):
                    f.write(f"[Message {i+1} - {message.type}]\n")
                    f.write("-" * 40 + "\n")
                    f.write(message.content + "\n")
                    f.write("-" * 40 + "\n\n")
            
            print(f"LLM prompt saved to: {output_file}")
            print("="*80 + "\n")
            
            # Call the original method
            return original_generate(self, messages, *args, **kwargs)
        
        # Replace the method
        BaseChatModel._generate = _generate_wrapper
        logger.info("Successfully patched BaseChatModel._generate")
        
        return True
    
    except ImportError as e:
        logger.error(f"Failed to import LangChain: {e}")
        return False

def patch_openai():
    """Patch OpenAI to print the prompt."""
    try:
        # Try to import OpenAI
        from openai import OpenAI
        logger.info("Successfully imported OpenAI")
        
        # Save the original chat.completions.create method
        original_create = OpenAI.chat.completions.create
        
        @wraps(original_create)
        def create_wrapper(self, *args, **kwargs):
            # Print the messages
            if "messages" in kwargs:
                print("\n" + "="*80)
                print("OPENAI PROMPT:")
                print("="*80)
                
                for i, message in enumerate(kwargs["messages"]):
                    print(f"[Message {i+1} - {message['role']}]")
                    print("-" * 40)
                    print(message["content"])
                    print("-" * 40)
                    print()
                
                # Save the messages to a file
                output_file = os.path.join("data", "debug", "openai_prompt.txt")
                with open(output_file, 'w') as f:
                    for i, message in enumerate(kwargs["messages"]):
                        f.write(f"[Message {i+1} - {message['role']}]\n")
                        f.write("-" * 40 + "\n")
                        f.write(message["content"] + "\n")
                        f.write("-" * 40 + "\n\n")
                
                print(f"OpenAI prompt saved to: {output_file}")
                print("="*80 + "\n")
            
            # Call the original method
            return original_create(self, *args, **kwargs)
        
        # Replace the method
        OpenAI.chat.completions.create = create_wrapper
        logger.info("Successfully patched OpenAI.chat.completions.create")
        
        return True
    
    except ImportError as e:
        logger.error(f"Failed to import OpenAI: {e}")
        return False

def patch_requests():
    """Patch requests to print the prompt."""
    import requests
    from requests import Session
    
    # Save the original post method
    original_post = requests.post
    original_session_post = Session.post
    
    @wraps(original_post)
    def post_wrapper(url, *args, **kwargs):
        # Check if this is an OpenRouter or OpenAI API call
        if "openrouter.ai" in url or "api.openai.com" in url:
            print("\n" + "="*80)
            print(f"API CALL TO: {url}")
            print("="*80)
            
            # Extract the payload
            if "json" in kwargs:
                payload = kwargs["json"]
                
                if "messages" in payload:
                    print("MESSAGES:")
                    for i, message in enumerate(payload["messages"]):
                        print(f"[Message {i+1} - {message['role']}]")
                        print("-" * 40)
                        print(message["content"])
                        print("-" * 40)
                        print()
                
                # Save the payload to a file
                output_file = os.path.join("data", "debug", "api_payload.json")
                with open(output_file, 'w') as f:
                    json.dump(payload, f, indent=2)
                
                print(f"API payload saved to: {output_file}")
            
            print("="*80 + "\n")
        
        # Call the original method
        return original_post(url, *args, **kwargs)
    
    @wraps(original_session_post)
    def session_post_wrapper(self, url, *args, **kwargs):
        # Check if this is an OpenRouter or OpenAI API call
        if "openrouter.ai" in url or "api.openai.com" in url:
            print("\n" + "="*80)
            print(f"SESSION API CALL TO: {url}")
            print("="*80)
            
            # Extract the payload
            if "json" in kwargs:
                payload = kwargs["json"]
                
                if "messages" in payload:
                    print("MESSAGES:")
                    for i, message in enumerate(payload["messages"]):
                        print(f"[Message {i+1} - {message['role']}]")
                        print("-" * 40)
                        print(message["content"])
                        print("-" * 40)
                        print()
                
                # Save the payload to a file
                output_file = os.path.join("data", "debug", "session_api_payload.json")
                with open(output_file, 'w') as f:
                    json.dump(payload, f, indent=2)
                
                print(f"Session API payload saved to: {output_file}")
            
            print("="*80 + "\n")
        
        # Call the original method
        return original_session_post(self, url, *args, **kwargs)
    
    # Replace the methods
    requests.post = post_wrapper
    Session.post = session_post_wrapper
    logger.info("Successfully patched requests.post and Session.post")
    
    return True

def main():
    """Main entry point."""
    # Create the debug directory
    os.makedirs(os.path.join("data", "debug"), exist_ok=True)
    
    # Patch LangChain
    langchain_patched = patch_langchain()
    
    # Patch OpenAI
    openai_patched = patch_openai()
    
    # Patch requests
    requests_patched = patch_requests()
    
    if not (langchain_patched or openai_patched or requests_patched):
        logger.error("Failed to patch any LLM client")
        sys.exit(1)
    
    print("LLM clients patched to print prompts")

if __name__ == "__main__":
    main()
EOF

# Make the interceptor executable
chmod +x "$DEBUG_DIR/intercept_llm_print.py"

# Run the interceptor
echo "Installing LLM interceptor..."
python "$DEBUG_DIR/intercept_llm_print.py"

# Run the requirements processor
echo "Running requirements processor..."
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

# Find the most recent output file for this project
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

# Print debug information
echo ""
echo "Debug information:"
echo "  - LLM prompt: $DEBUG_DIR/llm_prompt.txt"
echo "  - OpenAI prompt: $DEBUG_DIR/openai_prompt.txt"
echo "  - API payload: $DEBUG_DIR/api_payload.json"
echo "  - Session API payload: $DEBUG_DIR/session_api_payload.json"

# Check if the debug files exist
if [ -f "$DEBUG_DIR/llm_prompt.txt" ]; then
  echo "  - LLM prompt size: $(wc -c < "$DEBUG_DIR/llm_prompt.txt") bytes"
fi

if [ -f "$DEBUG_DIR/openai_prompt.txt" ]; then
  echo "  - OpenAI prompt size: $(wc -c < "$DEBUG_DIR/openai_prompt.txt") bytes"
fi

if [ -f "$DEBUG_DIR/api_payload.json" ]; then
  echo "  - API payload size: $(wc -c < "$DEBUG_DIR/api_payload.json") bytes"
fi

if [ -f "$DEBUG_DIR/session_api_payload.json" ]; then
  echo "  - Session API payload size: $(wc -c < "$DEBUG_DIR/session_api_payload.json") bytes"
fi

echo ""
echo "To view the debug files, run:"
echo "  cat $DEBUG_DIR/llm_prompt.txt"
echo "  cat $DEBUG_DIR/openai_prompt.txt"
echo "  cat $DEBUG_DIR/api_payload.json | jq"
echo "  cat $DEBUG_DIR/session_api_payload.json | jq"
