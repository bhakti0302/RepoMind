#!/bin/bash

# Find large files in the current commit
echo "Finding large files in your commit..."

# Get the diff between your branch and the remote
git_diff=$(git diff --name-only origin/main...tanya1.0)

# Check the size of each file
for file in $git_diff; do
    if [ -f "$file" ]; then
        size=$(du -h "$file" | cut -f1)
        size_bytes=$(du -b "$file" | cut -f1)
        
        # If file is larger than 5MB, print it
        if [ $size_bytes -gt 5000000 ]; then
            echo "$size - $file"
        fi
    fi
done