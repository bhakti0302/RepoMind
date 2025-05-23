#!/bin/bash
# Enhanced Relationship Analysis Wrapper Script
#
# This script runs the enhanced relationship analysis on a Java project
# and generates a visualization of the code relationships.
#
# Usage:
#   ./analyze_relationships.sh <path_to_repo> [output_file]

# Check if a repository path was provided
if [ -z "$1" ]; then
    echo "Error: No repository path provided"
    echo "Usage: ./analyze_relationships.sh <path_to_repo> [output_file]"
    exit 1
fi

# Set the repository path
REPO_PATH="$1"

# Set the output file (default: samples/enhanced_graph.png)
OUTPUT_FILE="${2:-samples/enhanced_graph.png}"

# Set the graph file (default: samples/dependency_graph.json)
GRAPH_FILE="samples/dependency_graph.json"

# Create the output directory if it doesn't exist
mkdir -p "$(dirname "$OUTPUT_FILE")"

# Run the enhanced relationship analysis
echo "Running enhanced relationship analysis on $REPO_PATH"
python scripts/test_enhanced_relationships.py --repo-path "$REPO_PATH" --output-file "$OUTPUT_FILE" --graph-file "$GRAPH_FILE"

# Check if the analysis was successful
if [ $? -eq 0 ]; then
    echo "Enhanced relationship analysis completed successfully"
    echo "Visualization saved to $OUTPUT_FILE"
    echo "Dependency graph saved to $GRAPH_FILE"
else
    echo "Enhanced relationship analysis failed"
    exit 1
fi
