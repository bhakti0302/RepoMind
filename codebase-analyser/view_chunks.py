import lancedb
import pandas as pd

# Connect to the database
db = lancedb.connect("./lancedb")

# View architecture chunks
arch_table = db["architecture_chunks"]
arch_chunks = arch_table.to_pandas()
print("=== Architecture Chunks ===")
for i, row in arch_chunks.iterrows():
    print(f"\nID: {row['id']}")
    print(f"Type: {row['type']}")
    print(f"File: {row['file_path']}")
    print(f"Language: {row['language']}")
    print("Content (first 100 chars):", row['content'][:100].replace('\n', ' ').strip())

# View code chunks
code_table = db["code_chunks"]
code_chunks = code_table.to_pandas()
print("\n=== Implementation Chunks ===")
for i, row in code_chunks.iterrows():
    print(f"\nID: {row['id']}")
    print(f"Type: {row['type']}")
    print(f"File: {row['file_path']}")
    print(f"Language: {row['language']}")
    print("Content (first 100 chars):", row['content'][:100].replace('\n', ' ').strip())