#!/bin/bash

# Script to run the Merge Agent after the pipeline completes
# This version is designed to run in interactive mode in the VS Code terminal

# Check if the LLM instructions file exists
LLM_INSTRUCTIONS_FILE="/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/output/LLM-instructions.txt"
# Also check for the alternative file name (llm-output.txt)
if [ ! -f "$LLM_INSTRUCTIONS_FILE" ]; then
    LLM_INSTRUCTIONS_FILE="/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/output/llm-output.txt"
fi
TARGET_PROJECT="/Users/bhaktichindhe/Desktop/Project/EmployeeManagementSystem"

# Create logs directory if it doesn't exist
LOGS_DIR="/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/logs"
mkdir -p "$LOGS_DIR"

# Create a log file with timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$LOGS_DIR/merge_agent_$TIMESTAMP.log"

# Function to log messages both to console and log file
log_message() {
    echo "$1"
    echo "$1" >> "$LOG_FILE"
}

log_message "==================================================================="
log_message "                     MERGE AGENT INTERACTIVE MODE                  "
log_message "==================================================================="
log_message "Logging to: $LOG_FILE"

# Check if the LLM instructions file exists
if [ ! -f "$LLM_INSTRUCTIONS_FILE" ]; then
    log_message "Error: LLM instructions file not found: $LLM_INSTRUCTIONS_FILE"
    exit 1
fi

# Check if the target project directory exists
if [ ! -d "$TARGET_PROJECT" ]; then
    log_message "Creating target project directory: $TARGET_PROJECT"
    mkdir -p "$TARGET_PROJECT"
fi

# Path to the Merge Agent
MERGE_AGENT_PATH="/Users/bhaktichindhe/Desktop/Project/RepoMind/mergeCodeAgent"

# Check if the Merge Agent exists
if [ ! -d "$MERGE_AGENT_PATH" ]; then
    log_message "Error: Merge Agent directory not found: $MERGE_AGENT_PATH"
    exit 1
fi

# Run the Merge Agent in interactive mode
log_message "Running Merge Agent with instructions from: $LLM_INSTRUCTIONS_FILE"
log_message "Target project: $TARGET_PROJECT"
log_message "==================================================================="
log_message "The Merge Agent will now run in interactive mode."
log_message "You will be prompted to approve each action (y/n)."
log_message "==================================================================="

cd "$MERGE_AGENT_PATH"
# Run the agent without redirecting stdin, so it can receive user input
# We still log the output to the log file using tee
python3 run_agent.py "$LLM_INSTRUCTIONS_FILE" "$TARGET_PROJECT" 2>&1 | tee -a "$LOG_FILE"

# Check if the Merge Agent ran successfully
EXIT_CODE=${PIPESTATUS[0]}
if [ $EXIT_CODE -eq 0 ]; then
    log_message "==================================================================="
    log_message "Merge Agent completed successfully!"
    log_message "Check the target project at: $TARGET_PROJECT"
    log_message "Log file: $LOG_FILE"
    log_message "==================================================================="
    exit 0
else
    log_message "==================================================================="
    log_message "Merge Agent failed with exit code: $EXIT_CODE"
    log_message "Check the log file for details: $LOG_FILE"
    log_message "==================================================================="
    exit 1
fi
