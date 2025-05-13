#!/bin/bash

# Set up environment variables for OpenRouter
export OPENAI_API_KEY="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"
export PYTHONPATH="$PYTHONPATH:$(pwd):$(pwd)/codebase-analyser"

# Set up project ID and requirement file
PROJECT_ID="Test"
REQ_FILE="data/requirements/input/test_project/data_processor_req.txt"
OUTPUT_DIR="data/requirements/output"

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
mkdir -p "data/requirements/input/test_project"

# Create a sample requirements file if it doesn't exist
if [ ! -f "$REQ_FILE" ]; then
  echo "Creating sample requirements file: $REQ_FILE"
  cat > "$REQ_FILE" << EOF
Create a Java class called DataProcessor that can:
1. Process a list of strings and return processed data objects
2. Calculate the total length of all strings in a list
3. Filter strings by a minimum length threshold
EOF
fi

# Run the requirements processor with the Nvidia Llama model
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

# Find the most recent output file for this project (macOS compatible)
if [ -d "$OUTPUT_DIR/$PROJECT_ID" ]; then
  LATEST_OUTPUT=$(ls -t "$OUTPUT_DIR/$PROJECT_ID"/data_processor_req_*.txt 2>/dev/null | head -1)
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
