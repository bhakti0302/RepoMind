#!/bin/bash

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

# Launch VS Code with the extension and testshreya folder
echo "Launching VS Code with testshreya folder..."
echo "Extension path: $EXTENSION_PATH"
echo "Testshreya path: $TESTSHREYA_PATH"

# Use the --new-window flag to ensure it opens in a new window
code --new-window --extensionDevelopmentPath="$EXTENSION_PATH" "$TESTSHREYA_PATH"

# Check if VS Code was launched successfully
if [ $? -ne 0 ]; then
    echo "Error: Failed to launch VS Code"
    exit 1
fi

echo "VS Code launched successfully with testshreya folder"
