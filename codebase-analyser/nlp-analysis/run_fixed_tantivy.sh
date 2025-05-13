#!/bin/bash

# Run the pipeline with the fixed vector search

# Set the Python path to include the current directory
export PYTHONPATH=$PYTHONPATH:/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/nlp-analysis

# Define parameters
INPUT_FILE="/Users/bhaktichindhe/Desktop/Project/RepoMind/test-project-employee/EmployeeByDepartmentRequirement.txt"
DB_PATH="/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/.lancedb"
OUTPUT_DIR="/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/output"
LOGS_DIR="/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/logs"

# Change to the nlp-analysis directory
cd /Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/nlp-analysis

# Step 1: Update the multi_hop_rag.py file to use the fixed vector search
echo "Updating multi_hop_rag.py to use the fixed vector search..."
python3 update_multi_hop_rag.py

# Step 2: Install the spaCy model with logging
echo "Installing spaCy model..."
./run_with_logs.sh python3 install_spacy_model.py

# Step 3: Run the multi-hop RAG with logging
echo "Running multi-hop RAG..."
./run_with_logs.sh python3 run_rag_to_llm.py

echo "Pipeline completed successfully!"
echo "Check the output files in $OUTPUT_DIR"
echo "Check the logs in $LOGS_DIR"
