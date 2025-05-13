#!/bin/bash

# This script removes large files from your commit but keeps them in your working directory

# Find large files in the current commit
echo "Finding large files in your commit..."

# Get the diff between your branch and the remote
git_diff=$(git diff --name-only origin/main...tanya1.0)

# Check the size of each file and store large files
large_files=""
for file in $git_diff; do
    if [ -f "$file" ]; then
        size=$(du -h "$file" | cut -f1)
        size_bytes=$(du -b "$file" | cut -f1)
        
        # If file is larger than 5MB, add it to the list
        if [ $size_bytes -gt 5000000 ]; then
            echo "$size - $file"
            large_files="$large_files $file"
        fi
    fi
done

if [ -z "$large_files" ]; then
    echo "No large files found in your commit."
    exit 0
fi

# Ask for confirmation
read -p "Do you want to remove these large files from your commit? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Remove large files from Git but keep them in the working directory
    for file in $large_files; do
        git rm --cached "$file"
        echo "Removed $file from Git (still exists in your working directory)"
    done
    
    # Add these files to .gitignore
    echo -e "\n# Large files removed from repository" >> .gitignore
    for file in $large_files; do
        echo "$file" >> .gitignore
    done
    
    git add .gitignore
    git commit -m "Remove large files and add them to .gitignore"
    
    echo "Large files have been removed from Git and added to .gitignore."
    echo "Try pushing again: git push origin tanya1.0"
else
    echo "Operation cancelled."
fi