#!/bin/bash

# This script launches VS Code in debug mode with the testshreya folder
# It uses the launch configuration in .vscode/launch.json

# Set variables
EXTENSION_PATH="$(pwd)"
TESTSHREYA_PATH="/Users/shreyah/Documents/Projects/SAP/testshreya"

# Check if testshreya folder exists
if [ ! -d "$TESTSHREYA_PATH" ]; then
    echo "Error: testshreya folder not found at $TESTSHREYA_PATH"
    exit 1
fi

# Compile the extension
echo "Compiling extension..."
npm run compile

# Check if compilation was successful
if [ $? -ne 0 ]; then
    echo "Error: Failed to compile extension"
    exit 1
fi

# Launch VS Code in debug mode
echo "Launching VS Code in debug mode with testshreya folder..."
code --extensionDevelopmentPath="$EXTENSION_PATH" "$TESTSHREYA_PATH"

echo "VS Code launched in debug mode with testshreya folder"
