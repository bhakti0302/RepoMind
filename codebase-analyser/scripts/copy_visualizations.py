#!/usr/bin/env python3
"""
Copy visualizations to the correct location.
"""

import os
import shutil
from pathlib import Path

# Source directory (where manual_visualize.py saved the visualizations)
src_dir = Path("/Users/shreyah/Documents/Projects/SAP/testshreya/visualizations")

# Ensure the source directory exists
os.makedirs(src_dir, exist_ok=True)

# Project ID
project_id = "testshreya"

# Check if the visualizations exist
multi_file_path = src_dir / f"{project_id}_multi_file_relationships.png"
relationship_types_path = src_dir / f"{project_id}_relationship_types.png"

if not multi_file_path.exists() or not relationship_types_path.exists():
    print("Visualizations not found. Running manual_visualize.py...")
    os.system(f"python /Users/shreyah/Documents/Projects/SAP/RepoMind/manual_visualize.py --output-dir {src_dir}")

# Check again if the visualizations exist
if multi_file_path.exists() and relationship_types_path.exists():
    print(f"Visualizations found at {src_dir}")
    print(f"Multi-file relationships: {multi_file_path}")
    print(f"Relationship types: {relationship_types_path}")
else:
    print("Failed to generate visualizations.")
