#!/bin/bash

# Set up environment variables
export PYTHONPATH="$PYTHONPATH:$(pwd):$(pwd)/codebase-analyser"

# Define paths
FILE_PATH="Test/src/TestTanya.java"
DB_PATH="codebase-analyser/.lancedb"
PROJECT_ID="Test"

echo "Indexing file: $FILE_PATH"
echo "Using database at: $DB_PATH"
echo "Project ID: $PROJECT_ID"
echo "Current directory: $(pwd)"
echo "PYTHONPATH: $PYTHONPATH"

# Check if the file exists
if [ ! -f "$FILE_PATH" ]; then
  echo "Error: File $FILE_PATH does not exist."
  exit 1
fi

# Check if the database directory exists
if [ ! -d "$DB_PATH" ]; then
  echo "Creating database directory: $DB_PATH"
  mkdir -p "$DB_PATH"
fi

# Install lancedb if not already installed
pip install lancedb numpy

# Run the indexer script
echo "Running schema-based indexer..."
python schema_based_index.py \
  --file-path "$FILE_PATH" \
  --db-path "$DB_PATH" \
  --project-id "$PROJECT_ID"

# Check if the indexer script ran successfully
if [ $? -eq 0 ]; then
  echo "Indexing complete. File has been added to the LanceDB database."
else
  echo "Error: Indexing failed. See above for details."
  exit 1
fi