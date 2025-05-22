#!/bin/bash

# Script to copy visualizations from the central directory to the workspace directory
# This is a workaround for the issue where the extension is looking for visualizations in the wrong location

# Get the project ID (testshreya)
PROJECT_ID="testshreya"

# Define the source and destination directories
SOURCE_DIR="/Users/shreyah/Documents/Projects/SAP/RepoMind/data/visualizations/${PROJECT_ID}"
DEST_DIR="/Users/shreyah/Documents/Projects/SAP/testshreya/visualizations"

# Create the destination directory if it doesn't exist
mkdir -p "${DEST_DIR}"

# Copy all PNG files from the source directory to the destination directory
echo "Copying visualizations from ${SOURCE_DIR} to ${DEST_DIR}..."
cp -v "${SOURCE_DIR}"/*.png "${DEST_DIR}/"

# Rename the files to match the expected format
echo "Renaming files to match the expected format..."
for file in "${DEST_DIR}"/*_20*.png; do
    if [ -f "$file" ]; then
        # Extract the base name and pattern
        base=$(basename "$file")
        pattern=$(echo "$base" | sed -E "s/${PROJECT_ID}_([^_]+)_[0-9]+\.png/\1/")
        
        # Create the new name
        new_name="${DEST_DIR}/${PROJECT_ID}_${pattern}.png"
        
        # Rename the file
        echo "Renaming $file to $new_name"
        cp -f "$file" "$new_name"
    fi
done

echo "Done!"
