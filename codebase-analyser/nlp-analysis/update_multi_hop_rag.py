#!/usr/bin/env python3

"""
Update the multi_hop_rag.py file to use the fixed vector search.

This script updates the multi_hop_rag.py file to use the fixed vector search
implementation that doesn't rely on tantivy.
"""

import os
import sys
import re
import shutil

def update_multi_hop_rag():
    """Update the multi_hop_rag.py file to use the fixed vector search."""
    # Define file paths
    multi_hop_rag_path = "src/multi_hop_rag.py"
    backup_path = "src/multi_hop_rag.py.bak"
    
    # Create a backup of the original file
    shutil.copy2(multi_hop_rag_path, backup_path)
    print(f"Created backup of {multi_hop_rag_path} at {backup_path}")
    
    # Read the original file
    with open(multi_hop_rag_path, 'r') as f:
        content = f.read()
    
    # Update the import statement
    content = re.sub(
        r'from src.vector_search import VectorSearch',
        'from src.vector_search_fixed import VectorSearch',
        content
    )
    
    # Write the updated content back to the file
    with open(multi_hop_rag_path, 'w') as f:
        f.write(content)
    
    print(f"Updated {multi_hop_rag_path} to use the fixed vector search")

if __name__ == "__main__":
    # Change to the nlp-analysis directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Update the multi_hop_rag.py file
    update_multi_hop_rag()
