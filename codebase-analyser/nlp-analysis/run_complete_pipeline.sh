#!/bin/bash

# Run the complete pipeline with OpenRouter

# Get the script directory and calculate relative paths
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CODEBASE_ANALYSER_DIR="$( dirname "$SCRIPT_DIR" )"
PROJECT_ROOT="$( dirname "$CODEBASE_ANALYSER_DIR" )"

# Set the Python path to include the current directory
# Original hardcoded path:
# export PYTHONPATH=$PYTHONPATH:/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/nlp-analysis
export PYTHONPATH=$PYTHONPATH:$SCRIPT_DIR

# Define parameters
# Original hardcoded paths:
# INPUT_FILE="/Users/bhaktichindhe/Desktop/Project/RepoMind/test-project-employee/EmployeeByDepartmentRequirement.txt"
# DB_PATH="/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/.lancedb"
# OUTPUT_DIR="/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/output"
INPUT_FILE="$PROJECT_ROOT/test-project-employee/EmployeeByDepartmentRequirement.txt"
DB_PATH="$CODEBASE_ANALYSER_DIR/.lancedb"
OUTPUT_DIR="$CODEBASE_ANALYSER_DIR/output"

# Run the code synthesis workflow
# Original hardcoded path:
# cd /Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/nlp-analysis
cd "$SCRIPT_DIR"
python3 src/code_synthesis_workflow.py \
  --input-file "$INPUT_FILE" \
  --db-path "$DB_PATH" \
  --output-dir "$OUTPUT_DIR" \
  --rag-type multi_hop \
  --generate-code

echo "Pipeline completed successfully!"
echo "Check the output files in $OUTPUT_DIR"
