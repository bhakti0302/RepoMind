#!/bin/bash
# Convenience wrapper for process_requirements.py

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Run the Python script with the provided arguments
python "$SCRIPT_DIR/process_requirements.py" "$@"