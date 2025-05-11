#!/bin/bash

# Set the path to your LanceDB database
DB_PATH="./lancedb"

# Run the RAG test script with real data
python test_rag.py \
  --requirements "Add System.out.println statements to each method in SimpleClass.java to log method entry and exit with appropriate parameters and return values" \
  --db-path "$DB_PATH" \
  --language java \
  --output print_instructions.txt \
  --limit 10

echo "Instructions generated in print_instructions.txt"