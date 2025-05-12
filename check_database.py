import lancedb
import pandas as pd

# Connect to the database
db_path = "/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/.lancedb"
db = lancedb.connect(db_path)

# List all tables
print("Tables in the database:", db.table_names())

# Open the code_chunks table
table = db.open_table("code_chunks")

# Convert to pandas DataFrame for easy viewing
df = table.to_pandas()

# Show basic information
print(f"Number of chunks: {len(df)}")
print(f"Project IDs: {df['project_id'].unique()}")
print(f"Languages: {df['language'].unique()}")

# Show a sample of the data
print("\nSample data:")
print(df[['node_id', 'name', 'chunk_type', 'file_path', 'language']].head())