#!/bin/bash

# Find large files in the tanya1.0 branch
echo "Finding large files in the tanya1.0 branch..."

# Get the current branch
current_branch=$(git rev-parse --abbrev-ref HEAD)
echo "Current branch: $current_branch"

# Get all files tracked in the current branch
echo "Getting all tracked files in the current branch..."
git_files=$(git ls-files)

# Check the size of each file
echo "Checking file sizes..."
large_files_found=false

for file in $git_files; do
    if [ -f "$file" ]; then
        size=$(du -h "$file" | cut -f1)
        size_bytes=$(du -b "$file" | cut -f1)
        
        # If file is larger than 5MB, print it
        if [ $size_bytes -gt 5000000 ]; then
            echo "$size - $file"
            large_files_found=true
        fi
    fi
done

if [ "$large_files_found" = false ]; then
    echo "No large files found in the current branch."
fi

echo "Scan complete."