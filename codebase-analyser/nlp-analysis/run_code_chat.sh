#!/bin/bash

# Run the code chat script

# Check if a question is provided
if [ "$#" -lt 1 ]; then
    echo "Error: No question provided"
    echo "Usage: $0 \"Your question about the code\" [--history-file /path/to/history.json]"
    exit 1
fi

QUESTION="$1"
echo "Using provided question: $QUESTION"

# Check for history file parameter
HISTORY_FILE=""
if [ "$#" -gt 1 ] && [ "$2" == "--history-file" ] && [ "$#" -gt 2 ]; then
    HISTORY_FILE="$3"
    echo "Using conversation history from: $HISTORY_FILE"
fi

# Set the Python path to include the current directory
export PYTHONPATH=$PYTHONPATH:/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/nlp-analysis

# Define parameters
DB_PATH="/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/.lancedb"
OUTPUT_DIR="/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/output"

# Create logs directory if it doesn't exist
LOGS_DIR="/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/logs"
mkdir -p "$LOGS_DIR"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Create a log file with timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$LOGS_DIR/code_chat_$TIMESTAMP.log"
echo "Logging to: $LOG_FILE"

# Build the command
COMMAND="python3 code_chat.py --question \"$QUESTION\" --db-path \"$DB_PATH\" --output-dir \"$OUTPUT_DIR\""

# Add history file if provided
if [ -n "$HISTORY_FILE" ]; then
    COMMAND="$COMMAND --history-file \"$HISTORY_FILE\""
fi

# Run the code chat script
echo "Running code chat with question: $QUESTION" | tee -a "$LOG_FILE"
echo "Command: $COMMAND" | tee -a "$LOG_FILE"
cd /Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/nlp-analysis
eval "$COMMAND" 2>&1 | tee -a "$LOG_FILE"

# Check if the Python script ran successfully
if [ $? -eq 0 ]; then
    echo "Code chat completed successfully!" | tee -a "$LOG_FILE"
    echo "Check the output files in $OUTPUT_DIR" | tee -a "$LOG_FILE"
    echo "Log file: $LOG_FILE"

    # Read the response file
    RESPONSE_FILE="$OUTPUT_DIR/chat-response.txt"
    if [ -f "$RESPONSE_FILE" ]; then
        cat "$RESPONSE_FILE"
    else
        echo "Response file not found: $RESPONSE_FILE"
    fi

    exit 0
else
    echo "Code chat failed! Check the log file for details: $LOG_FILE" | tee -a "$LOG_FILE"
    exit 1
fi
