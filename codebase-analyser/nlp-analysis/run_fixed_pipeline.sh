#!/bin/bash

# Run the complete pipeline with the fixed code

# Check if a file path is provided
if [ "$#" -eq 1 ]; then
    INPUT_FILE="$1"
    echo "Using provided input file: $INPUT_FILE"
else
    # Default input file if none is provided
    INPUT_FILE="/Users/bhaktichindhe/Desktop/Project/RepoMind/test-project-employee/EmployeeByDepartmentRequirement.txt"
    echo "No input file provided, using default: $INPUT_FILE"
fi

# Set the Python path to include the current directory
export PYTHONPATH=$PYTHONPATH:/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/nlp-analysis

# Define parameters
DB_PATH="/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/.lancedb"
OUTPUT_DIR="/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/output"
LOGS_DIR="/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/logs"

# Create logs and output directories if they don't exist
mkdir -p "$LOGS_DIR"
mkdir -p "$OUTPUT_DIR"

# Create a log file with timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$LOGS_DIR/pipeline_$TIMESTAMP.log"
echo "Logging to: $LOG_FILE"

# Step 1: Install the spaCy model
echo "Installing spaCy model..." | tee -a "$LOG_FILE"
cd /Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/nlp-analysis
python3 install_spacy_model.py >> "$LOG_FILE" 2>&1

# Step 2: Run the multi-hop RAG with the input file
echo "Running multi-hop RAG with input file: $INPUT_FILE" | tee -a "$LOG_FILE"
cd /Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/nlp-analysis
python3 run_rag_to_llm.py --input-file "$INPUT_FILE" --db-path "$DB_PATH" --output-dir "$OUTPUT_DIR" >> "$LOG_FILE" 2>&1

# Check if the Python script ran successfully
if [ $? -eq 0 ]; then
    echo "Pipeline completed successfully!" | tee -a "$LOG_FILE"
    echo "Check the output files in $OUTPUT_DIR" | tee -a "$LOG_FILE"
    echo "Log file: $LOG_FILE"

    # Step 3: Notify that the pipeline is complete and Merge Agent will be launched in a separate terminal
    echo "Pipeline completed successfully!" | tee -a "$LOG_FILE"
    echo "The Merge Agent will now be launched in a separate terminal window." | tee -a "$LOG_FILE"
    echo "You will be able to interact with it directly to approve or reject code changes." | tee -a "$LOG_FILE"

    # Create a marker file to indicate the pipeline has completed successfully
    PIPELINE_COMPLETE_MARKER="/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/output/pipeline_complete"
    echo "$(date)" > "$PIPELINE_COMPLETE_MARKER"

    # Exit successfully - the extension will handle launching the mergeCodeAgent in a terminal
    exit 0
else
    echo "Pipeline failed! Check the log file for details: $LOG_FILE" | tee -a "$LOG_FILE"
    exit 1
fi
