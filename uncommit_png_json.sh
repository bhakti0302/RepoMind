#!/bin/bash

# Uncommit all PNG and JSON files from the last commit
# This will keep the changes in your working directory

# First, find all PNG and JSON files in the last commit
png_files=$(git diff-tree --no-commit-id --name-only -r HEAD | grep '\.png$')
json_files=$(git diff-tree --no-commit-id --name-only -r HEAD | grep '\.json$')

# Check if there are any PNG or JSON files to uncommit
if [ -z "$png_files" ] && [ -z "$json_files" ]; then
    echo "No PNG or JSON files found in the last commit."
    exit 0
fi

# Create a list of all files to uncommit
files_to_uncommit=""
for file in $png_files $json_files; do
    files_to_uncommit="$files_to_uncommit $file"
done

# Reset these files from the last commit
git reset HEAD~1 $files_to_uncommit

# Commit the remaining changes
git commit -C ORIG_HEAD

echo "Successfully uncommitted the following PNG and JSON files:"
echo "$files_to_uncommit"
echo "These files are now in your working directory (unstaged)."