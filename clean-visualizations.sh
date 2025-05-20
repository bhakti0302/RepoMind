#!/bin/bash

# Script to clean up the visualization directory and ensure only the correct files exist
# This is a workaround for the issue where the extension is having trouble displaying visualizations

# Get the project ID (testshreya)
PROJECT_ID="testshreya"

# Define the workspace directory
WORKSPACE_DIR="/Users/shreyah/Documents/Projects/SAP/testshreya/visualizations"

# Create a temporary directory
TEMP_DIR="${WORKSPACE_DIR}/temp"
mkdir -p "${TEMP_DIR}"

echo "Cleaning up visualization directory: ${WORKSPACE_DIR}"

# Move the correct files to the temporary directory
echo "Moving correct files to temporary directory..."
mv "${WORKSPACE_DIR}/${PROJECT_ID}_class_diagram.png" "${TEMP_DIR}/" 2>/dev/null
mv "${WORKSPACE_DIR}/${PROJECT_ID}_dependency_graph.png" "${TEMP_DIR}/" 2>/dev/null
mv "${WORKSPACE_DIR}/${PROJECT_ID}_inheritance_hierarchy.png" "${TEMP_DIR}/" 2>/dev/null
mv "${WORKSPACE_DIR}/${PROJECT_ID}_multi_file_relationships.png" "${TEMP_DIR}/" 2>/dev/null
mv "${WORKSPACE_DIR}/${PROJECT_ID}_package_diagram.png" "${TEMP_DIR}/" 2>/dev/null
mv "${WORKSPACE_DIR}/${PROJECT_ID}_relationship_types.png" "${TEMP_DIR}/" 2>/dev/null
mv "${WORKSPACE_DIR}/customer_java_highlight.png" "${TEMP_DIR}/" 2>/dev/null
mv "${WORKSPACE_DIR}/project_graph_customer_highlight.png" "${TEMP_DIR}/" 2>/dev/null

# Remove all files in the workspace directory
echo "Removing all files in the workspace directory..."
rm -f "${WORKSPACE_DIR}"/*.png

# Move the correct files back to the workspace directory
echo "Moving correct files back to the workspace directory..."
mv "${TEMP_DIR}"/* "${WORKSPACE_DIR}/" 2>/dev/null

# Remove the temporary directory
rmdir "${TEMP_DIR}"

# Copy the latest files from the central directory if they don't exist in the workspace
echo "Copying latest files from central directory if needed..."
CENTRAL_DIR="/Users/shreyah/Documents/Projects/SAP/RepoMind/data/visualizations/${PROJECT_ID}"

# Function to find the latest file matching a pattern
find_latest_file() {
    local pattern="$1"
    local dir="$2"
    find "${dir}" -name "${pattern}" -type f -print0 | xargs -0 ls -t | head -1
}

# For each visualization type, copy the latest file if it doesn't exist
for viz_type in "class_diagram" "dependency_graph" "inheritance_hierarchy" "multi_file_relationships" "package_diagram" "relationship_types"; do
    target_file="${WORKSPACE_DIR}/${PROJECT_ID}_${viz_type}.png"
    if [ ! -f "${target_file}" ]; then
        latest_file=$(find_latest_file "${PROJECT_ID}_${viz_type}_*.png" "${CENTRAL_DIR}")
        if [ -n "${latest_file}" ]; then
            echo "Copying ${latest_file} to ${target_file}"
            cp "${latest_file}" "${target_file}"
        fi
    fi
done

# Copy special visualizations if they don't exist
for special_viz in "customer_java_highlight.png" "project_graph_customer_highlight.png"; do
    target_file="${WORKSPACE_DIR}/${special_viz}"
    source_file="${CENTRAL_DIR}/${special_viz}"
    if [ ! -f "${target_file}" ] && [ -f "${source_file}" ]; then
        echo "Copying ${source_file} to ${target_file}"
        cp "${source_file}" "${target_file}"
    fi
done

echo "Listing files in workspace directory:"
ls -la "${WORKSPACE_DIR}"

echo "Done!"
