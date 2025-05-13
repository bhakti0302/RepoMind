#!/bin/bash

# Check the last commit
echo "Last commit:"
git log -1 --stat

# Find all PNG and JSON files in the last commit
png_files=$(git diff-tree --no-commit-id --name-only -r HEAD | grep '\.png$')
json_files=$(git diff-tree --no-commit-id --name-only -r HEAD | grep '\.json$')

# Display the PNG and JSON files
echo -e "\nPNG files in the last commit:"
if [ -z "$png_files" ]; then
    echo "None"
else
    echo "$png_files"
fi

echo -e "\nJSON files in the last commit:"
if [ -z "$json_files" ]; then
    echo "None"
else
    echo "$json_files"
fi

# Check if there are any PNG or JSON files to uncommit
if [ -z "$png_files" ] && [ -z "$json_files" ]; then
    echo -e "\nNo PNG or JSON files found in the last commit."
    exit 0
fi

# Ask for confirmation
read -p "Do you want to uncommit these PNG and JSON files? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    # Create a list of all files to uncommit
    files_to_uncommit=""
    for file in $png_files $json_files; do
        files_to_uncommit="$files_to_uncommit $file"
    done

    # Reset these files from the last commit
    git reset HEAD~1 $files_to_uncommit

    # Commit the remaining changes
    git commit -C ORIG_HEAD

    echo -e "\nSuccessfully uncommitted the PNG and JSON files."
    echo "These files are now in your working directory (unstaged)."
else
    echo "Operation cancelled."
fi