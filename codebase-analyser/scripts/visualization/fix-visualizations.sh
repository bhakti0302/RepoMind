#!/bin/bash

# Script to fix visualization display issues
# This script copies the latest visualization files to the workspace directory with the correct names

# Get the project ID (testshreya)
PROJECT_ID="testshreya"

# Define the directories
CENTRAL_DIR="/Users/shreyah/Documents/Projects/SAP/RepoMind/data/visualizations/${PROJECT_ID}"
WORKSPACE_DIR="/Users/shreyah/Documents/Projects/SAP/testshreya/visualizations"

# Create the workspace directory if it doesn't exist
if [ ! -d "${WORKSPACE_DIR}" ]; then
    mkdir -p "${WORKSPACE_DIR}"
    echo "Created workspace directory: ${WORKSPACE_DIR}"
fi

# Function to find the latest file matching a pattern
find_latest_file() {
    local pattern="$1"
    local dir="$2"
    find "${dir}" -name "${pattern}" -type f -print0 2>/dev/null | xargs -0 ls -t 2>/dev/null | head -1
}

# Copy the latest visualization files to the workspace directory with the correct names
echo "Copying visualization files to workspace directory..."

# Define the visualization types
VISUALIZATION_TYPES=(
    "multi_file_relationships"
    "relationship_types"
    "class_diagram"
    "package_diagram"
    "dependency_graph"
    "inheritance_hierarchy"
)

# Copy each visualization type
for viz_type in "${VISUALIZATION_TYPES[@]}"; do
    # Find the latest file
    latest_file=$(find_latest_file "${PROJECT_ID}_${viz_type}_*.png" "${CENTRAL_DIR}")

    if [ -n "${latest_file}" ]; then
        # Define the target file
        target_file="${WORKSPACE_DIR}/${PROJECT_ID}_${viz_type}.png"

        # Copy the file
        echo "Copying ${latest_file} to ${target_file}"
        cp "${latest_file}" "${target_file}"

        # Check if the copy was successful
        if [ -f "${target_file}" ]; then
            echo "  ✅ Copy successful"
        else
            echo "  ❌ Copy failed"
        fi
    else
        echo "No file found for ${viz_type}"
    fi
done

# Copy special visualizations
SPECIAL_VISUALIZATIONS=(
    "customer_java_highlight.png"
    "project_graph_customer_highlight.png"
)

for special_viz in "${SPECIAL_VISUALIZATIONS[@]}"; do
    source_file="${CENTRAL_DIR}/${special_viz}"
    target_file="${WORKSPACE_DIR}/${special_viz}"

    if [ -f "${source_file}" ]; then
        echo "Copying ${source_file} to ${target_file}"
        cp "${source_file}" "${target_file}"

        # Check if the copy was successful
        if [ -f "${target_file}" ]; then
            echo "  ✅ Copy successful"
        else
            echo "  ❌ Copy failed"
        fi
    else
        echo "No file found for ${special_viz}"
    fi
done

# List the files in the workspace directory
echo -e "\nFiles in workspace directory:"
ls -la "${WORKSPACE_DIR}"

echo -e "\nDone!"
