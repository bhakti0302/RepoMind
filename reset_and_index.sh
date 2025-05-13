#!/bin/bash

# Set up environment variables
export PYTHONPATH="$PYTHONPATH:$(pwd):$(pwd)/codebase-analyser"

# Define paths
FILE_PATH="Test/src/TestTanya.java"
DB_PATH="codebase-analyser/.lancedb"
PROJECT_ID="Test"

echo "Resetting database and indexing file: $FILE_PATH"
echo "Using database at: $DB_PATH"
echo "Project ID: $PROJECT_ID"

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

# Clear and create the table
echo "Clearing and creating the table..."
python clear_and_create_db.py --db-path "$DB_PATH"

# Run the indexer script
echo "Running schema-compatible indexer..."
python fix_schema_index.py \
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

# Check the database
echo "Checking the database..."
python -c "
import lancedb
import sys

try:
    # Connect to the database
    db = lancedb.connect('$DB_PATH')
    
    # Check if the code_chunks table exists
    if 'code_chunks' in db.table_names():
        # Open the table
        table = db.open_table('code_chunks')
        
        # Get the data
        df = table.to_pandas()
        
        # Filter by project_id
        filtered_df = df[df['project_id'] == '$PROJECT_ID']
        
        # Print the results
        print(f'Found {len(filtered_df)} chunks for project \"$PROJECT_ID\"')
        
        if len(filtered_df) > 0:
            print('\\nFirst few chunks:')
            for i, row in filtered_df.head(3).iterrows():
                print(f'  - {row[\"chunk_type\"]}: {row[\"name\"]} ({row[\"node_id\"]})')
                print(f'    File: {row[\"file_path\"]}')
                print(f'    Lines: {row[\"start_line\"]}-{row[\"end_line\"]}')
                print()
            
            print('Success! Entries were created in the database.')
            sys.exit(0)
        else:
            print('No entries found for the specified project.')
            sys.exit(1)
    else:
        print('The code_chunks table does not exist in the database.')
        sys.exit(1)
except Exception as e:
    print(f'Error checking database: {e}')
    sys.exit(1)
"