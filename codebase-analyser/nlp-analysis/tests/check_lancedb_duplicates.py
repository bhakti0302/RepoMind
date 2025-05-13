# Create a script to check for duplicates in LanceDB
#!/usr/bin/env python3

import lancedb
import pandas as pd
import hashlib
from collections import defaultdict

# Set display options
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', 50)

# Connect to the database
db_path = "/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/.lancedb"  # Adjust this path to your LanceDB location
print(f"Checking LanceDB database at: {db_path}")

try:
    # Connect to the database
    db = lancedb.connect(db_path)
    
    # List all tables
    tables = db.table_names()
    print(f"Found {len(tables)} tables in the database")
    
    # Check each table for duplicates
    for table_name in tables:
        print(f"\nChecking table '{table_name}' for duplicates...")
        table = db.open_table(table_name)
        
        # Get all rows
        df = table.to_pandas()
        print(f"Table has {len(df)} rows")
        
        # Check for duplicate file_paths
        if 'file_path' in df.columns:
            file_path_counts = df['file_path'].value_counts()
            duplicates = file_path_counts[file_path_counts > 1]
            if not duplicates.empty:
                print(f"Found {len(duplicates)} duplicate file paths:")
                print(duplicates.head(10))
            else:
                print("No duplicate file paths found")
        
        # Check for duplicate content using content hashes
        if 'content' in df.columns:
            # Create content hashes
            df['content_hash'] = df['content'].apply(lambda x: hashlib.md5(str(x).encode()).hexdigest())
            
            # Count hash occurrences
            hash_counts = df['content_hash'].value_counts()
            content_duplicates = hash_counts[hash_counts > 1]
            
            if not content_duplicates.empty:
                print(f"Found {len(content_duplicates)} duplicate content hashes:")
                print(content_duplicates.head(10))
                
                # Show some examples of duplicate content
                print("\nExamples of duplicate content:")
                for hash_val in content_duplicates.index[:3]:  # Show first 3 duplicates
                    dupe_rows = df[df['content_hash'] == hash_val]
                    print(f"\nHash: {hash_val}, {len(dupe_rows)} occurrences")
                    for i, (idx, row) in enumerate(dupe_rows.iterrows(), 1):
                        if i <= 2:  # Show only first 2 instances of each duplicate
                            print(f"Instance {i}:")
                            if 'file_path' in row:
                                print(f"  File: {row['file_path']}")
                            content_preview = row['content'][:100] + "..." if len(row['content']) > 100 else row['content']
                            print(f"  Content: {content_preview}")
            else:
                print("No duplicate content found")
    
except Exception as e:
    print(f"Error checking LanceDB: {e}")


# Make the script executable
#chmod +x check_lancedb_duplicates.py

# Run the script
#python3 check_lancedb_duplicates.py