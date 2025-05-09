#!/bin/bash
# Development setup script for the extension

echo "Setting up development environment for VS Code Agentic AI Coding Assistant..."

# Install required dependencies
echo "Installing dependencies..."
npm install --save-dev webpack webpack-cli ts-loader typescript @types/vscode @types/node @types/mocha mocha

# Create media directory if it doesn't exist
mkdir -p media

# Compile the extension
echo "Compiling the extension..."
npm run compile

if [ $? -eq 0 ]; then
    echo "Setup completed successfully!"
    echo "You can now run the extension with: code --extensionDevelopmentPath=\"$(pwd)\""
else
    echo "Compilation failed. Please check the error messages above."
    exit 1
fi