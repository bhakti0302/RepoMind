#!/bin/bash
# Wrapper script for codebase analysis service
# Usage: ./analyze.sh /path/to/repo [options]

# Check if Python is available
if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    echo "Error: Python not found. Please install Python 3."
    exit 1
fi

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Check if repository path is provided
if [ -z "$1" ]; then
    echo "Error: Repository path is required."
    echo "Usage: ./analyze.sh /path/to/repo [options]"
    exit 1
fi

REPO_PATH="$1"
shift  # Remove the first argument (repo path)

# Run the analysis script
$PYTHON "$SCRIPT_DIR/run_codebase_analysis.py" --repo-path "$REPO_PATH" "$@"
