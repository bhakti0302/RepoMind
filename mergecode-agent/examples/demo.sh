#!/bin/bash
# Demo script to show how to use the Merge Code Agent

# Set the current directory to the script's directory
cd "$(dirname "$0")"
cd ..

# Run the Merge Code Agent with the example instructions
python3 run_agent.py examples/example-instructions.txt examples/test_codebase
