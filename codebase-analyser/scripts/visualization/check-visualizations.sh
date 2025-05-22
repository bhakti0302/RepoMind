#!/bin/bash

# Script to check the visualization files and their paths
# This is a debugging tool to help identify issues with visualizations

# Get the project ID (testshreya)
PROJECT_ID="testshreya"

# Define the directories
CENTRAL_DIR="/Users/shreyah/Documents/Projects/SAP/RepoMind/data/visualizations/${PROJECT_ID}"
WORKSPACE_DIR="/Users/shreyah/Documents/Projects/SAP/testshreya/visualizations"

# Check if the directories exist
echo "Checking directories..."
echo "Central directory: ${CENTRAL_DIR}"
if [ -d "${CENTRAL_DIR}" ]; then
    echo "  ✅ Central directory exists"
else
    echo "  ❌ Central directory does not exist"
fi

echo "Workspace directory: ${WORKSPACE_DIR}"
if [ -d "${WORKSPACE_DIR}" ]; then
    echo "  ✅ Workspace directory exists"
else
    echo "  ❌ Workspace directory does not exist"
    echo "  Creating workspace directory..."
    mkdir -p "${WORKSPACE_DIR}"
fi

# Check if the visualization files exist in the central directory
echo -e "\nChecking visualization files in central directory..."
for viz_type in "multi_file_relationships" "relationship_types" "class_diagram" "package_diagram" "dependency_graph" "inheritance_hierarchy"; do
    # Find the latest file matching the pattern
    latest_file=$(find "${CENTRAL_DIR}" -name "${PROJECT_ID}_${viz_type}_*.png" -type f -print0 2>/dev/null | xargs -0 ls -t 2>/dev/null | head -1)
    
    if [ -n "${latest_file}" ]; then
        echo "  ✅ ${viz_type}: ${latest_file}"
        
        # Check if the file is readable
        if [ -r "${latest_file}" ]; then
            echo "    ✅ File is readable"
            
            # Check the file size
            file_size=$(stat -f "%z" "${latest_file}" 2>/dev/null)
            if [ -n "${file_size}" ] && [ "${file_size}" -gt 0 ]; then
                echo "    ✅ File size: ${file_size} bytes"
            else
                echo "    ❌ File is empty or cannot determine size"
            fi
            
            # Check if the file is a valid PNG
            if file "${latest_file}" | grep -q "PNG image data"; then
                echo "    ✅ File is a valid PNG image"
            else
                echo "    ❌ File is not a valid PNG image"
            fi
        else
            echo "    ❌ File is not readable"
        fi
    else
        echo "  ❌ ${viz_type}: No file found"
    fi
done

# Check if the visualization files exist in the workspace directory
echo -e "\nChecking visualization files in workspace directory..."
for viz_type in "multi_file_relationships" "relationship_types" "class_diagram" "package_diagram" "dependency_graph" "inheritance_hierarchy"; do
    target_file="${WORKSPACE_DIR}/${PROJECT_ID}_${viz_type}.png"
    
    if [ -f "${target_file}" ]; then
        echo "  ✅ ${viz_type}: ${target_file}"
        
        # Check if the file is readable
        if [ -r "${target_file}" ]; then
            echo "    ✅ File is readable"
            
            # Check the file size
            file_size=$(stat -f "%z" "${target_file}" 2>/dev/null)
            if [ -n "${file_size}" ] && [ "${file_size}" -gt 0 ]; then
                echo "    ✅ File size: ${file_size} bytes"
            else
                echo "    ❌ File is empty or cannot determine size"
            fi
            
            # Check if the file is a valid PNG
            if file "${target_file}" | grep -q "PNG image data"; then
                echo "    ✅ File is a valid PNG image"
            else
                echo "    ❌ File is not a valid PNG image"
            fi
        else
            echo "    ❌ File is not readable"
        fi
    else
        echo "  ❌ ${viz_type}: No file found"
        
        # Copy the latest file from the central directory if it exists
        latest_file=$(find "${CENTRAL_DIR}" -name "${PROJECT_ID}_${viz_type}_*.png" -type f -print0 2>/dev/null | xargs -0 ls -t 2>/dev/null | head -1)
        if [ -n "${latest_file}" ]; then
            echo "    📋 Copying ${latest_file} to ${target_file}"
            cp "${latest_file}" "${target_file}"
            
            # Check if the copy was successful
            if [ -f "${target_file}" ]; then
                echo "    ✅ Copy successful"
            else
                echo "    ❌ Copy failed"
            fi
        else
            echo "    ❌ No source file found to copy"
        fi
    fi
done

echo -e "\nDone!"
