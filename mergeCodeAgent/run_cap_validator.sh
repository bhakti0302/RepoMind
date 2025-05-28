#!/bin/bash

# Script to run the CAP SAP Java validator on a directory of Java files

# Default directory is current directory
DIRECTORY=${1:-.}

# Print banner
echo "==================================================="
echo "        CAP SAP Java Validator Runner              "
echo "==================================================="
echo "Running on directory: $DIRECTORY"
echo

# Run the validator
python3 $(dirname "$0")/integrate_cap_validator.py --directory "$DIRECTORY"

# Check exit code
if [ $? -eq 0 ]; then
  echo "Validation completed successfully."
else
  echo "Validation failed with errors."
  exit 1
fi 