#!/bin/bash

# This script removes common binary files from your commit

# List of common binary file extensions
binary_extensions=("png" "jpg" "jpeg" "gif" "bmp" "tiff" "psd" 
                  "mp4" "mov" "avi" "wmv" "flv" "mkv"
                  "mp3" "wav" "ogg" "flac"
                  "pdf" "doc" "docx" "ppt" "pptx" "xls" "xlsx"
                  "zip" "tar" "gz" "7z" "rar"
                  "exe" "dll" "so" "dylib"
                  "bin" "dat" "model" "weights" "h5" "pkl" "onnx")

# Find binary files in the current commit
echo "Finding binary files in your commit..."

# Get the diff between your branch and the remote
git_diff=$(git diff --name-only origin/main...tanya1.0)

# Check each file extension
binary_files=""
for file in $git_diff; do
    if [ -f "$file" ]; then
        # Get file extension
        extension="${file##*.}"
        
        # Check if it's in our list of binary extensions
        for bin_ext in "${binary_extensions[@]}"; do
            if [ "$extension" = "$bin_ext" ]; then
                size=$(du -h "$file" | cut -f1)
                echo "$size - $file"
                binary_files="$binary_files $file"
                break
            fi
        done
    fi
done

if [ -z "$binary_files" ]; then
    echo "No binary files found in your commit."
    exit 0
fi

# Ask for confirmation
read -p "Do you want to remove these binary files from your commit? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Remove binary files from Git but keep them in the working directory
    for file in $binary_files; do
        git rm --cached "$file"
        echo "Removed $file from Git (still exists in your working directory)"
    done
    
    # Add these files to .gitignore
    echo -e "\n# Binary files removed from repository" >> .gitignore
    for file in $binary_files; do
        echo "$file" >> .gitignore
    done
    
    git add .gitignore
    git commit -m "Remove binary files and add them to .gitignore"
    
    echo "Binary files have been removed from Git and added to .gitignore."
    echo "Try pushing again: git push origin tanya1.0"
else
    echo "Operation cancelled."
fi