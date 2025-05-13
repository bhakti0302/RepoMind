#!/bin/bash

# Run the complete pipeline with OpenRouter

# Set the Python path to include the current directory
export PYTHONPATH=$PYTHONPATH:/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/nlp-analysis

# Define parameters
INPUT_FILE="/Users/bhaktichindhe/Desktop/Project/RepoMind/test-project-employee/EmployeeByDepartmentRequirement.txt"
DB_PATH="/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/.lancedb"
OUTPUT_DIR="/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/output"

# Run the code synthesis workflow
cd /Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/nlp-analysis
python3 src/code_synthesis_workflow.py \
  --input-file "$INPUT_FILE" \
  --db-path "$DB_PATH" \
  --output-dir "$OUTPUT_DIR" \
  --rag-type multi_hop \
  --generate-code

echo "Pipeline completed successfully!"
echo "Check the output files in $OUTPUT_DIR"
