#!/bin/bash

# Script to run a command and log its output to a timestamped file in the logs directory

# Define the logs directory
LOGS_DIR="/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/logs"

# Create the logs directory if it doesn't exist
mkdir -p "$LOGS_DIR"

# Generate a timestamp for the log file
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
LOG_FILE="$LOGS_DIR/run_$TIMESTAMP.log"

# Function to display usage information
usage() {
    echo "Usage: $0 <command_to_run>"
    echo "Example: $0 ./run_fixed_pipeline.sh"
    exit 1
}

# Check if a command was provided
if [ $# -eq 0 ]; then
    echo "Error: No command provided."
    usage
fi

# Combine all arguments into a single command
COMMAND="$*"

# Print information about the run
echo "Running command: $COMMAND"
echo "Logging output to: $LOG_FILE"

# Run the command and tee its output to both the terminal and the log file
# The 'tee' command splits the output, sending it to both the terminal and the log file
# The '2>&1' redirects stderr to stdout so that error messages are also captured
{
    echo "=== Command: $COMMAND ==="
    echo "=== Started at: $(date) ==="
    echo "=== Working directory: $(pwd) ==="
    echo "=== Environment: ==="
    env | sort
    echo "=== Command output: ==="
    echo ""
    
    # Run the command and capture its exit status
    set -o pipefail  # Ensures that the exit status is from the command, not from tee
    $COMMAND 2>&1
    EXIT_STATUS=$?
    
    echo ""
    echo "=== Command completed at: $(date) ==="
    echo "=== Exit status: $EXIT_STATUS ==="
    
    # Return the original exit status
    exit $EXIT_STATUS
} | tee "$LOG_FILE"
