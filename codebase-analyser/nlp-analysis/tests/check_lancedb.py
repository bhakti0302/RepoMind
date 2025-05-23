# Create a script to list LanceDB tables
#!/usr/bin/env python3

import lancedb
import os
import sys

# Path to the LanceDB database
db_path = "../.lancedb"

print(f"Checking LanceDB database at: {db_path}")

try:
    # Connect to the database
    db = lancedb.connect(db_path)
    
    # List all tables
    tables = db.table_names()
    
    print(f"Found {len(tables)} tables in the database:")
    for i, table_name in enumerate(tables, 1):
        print(f"{i}. {table_name}")
    
    # If there are tables, show a sample from the first table
    if tables:
        table = db.open_table(tables[0])
        count = table.count_rows()
        print(f"\nTable '{tables[0]}' has {count} rows")
        
        if count > 0:
            print("\nSample data (first 5 rows):")
            sample = table.to_pandas(limit=5)
            print(sample)
        else:
            print("\nTable is empty")
    else:
        print("\nNo tables found in the database")
        
except Exception as e:
    print(f"Error accessing LanceDB: {e}")


# Make the script executable

# Run the script
