#!/bin/bash
# Setup script for VS Code Agentic AI Coding Assistant
# This script installs all necessary development tools

echo "Setting up development environment for VS Code Agentic AI Coding Assistant..."

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "Node.js is not installed. Please install Node.js v14.19.0 or higher from https://nodejs.org/"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d 'v' -f 2)
NODE_MAJOR=$(echo $NODE_VERSION | cut -d '.' -f 1)
if [ $NODE_MAJOR -lt 14 ]; then
    echo "Node.js version $NODE_VERSION is too old. Please install v14.19.0 or higher."
    exit 1
fi

echo "✓ Node.js v$NODE_VERSION is installed"

# Check for npm
if ! command -v npm &> /dev/null; then
    echo "npm is not installed. It should come with Node.js."
    exit 1
fi
echo "✓ npm $(npm -v) is installed"

# Check for Git
if ! command -v git &> /dev/null; then
    echo "Git is not installed. Please install Git from https://git-scm.com/"
    exit 1
fi
echo "✓ Git $(git --version | cut -d ' ' -f 3) is installed"

# Install global dependencies
echo "Installing Yeoman and VS Code Extension Generator..."
npm install -g yo generator-code

echo "Installing TypeScript..."
npm install -g typescript

echo "Installing VS Code Extension Manager (vsce)..."
npm install -g @vscode/vsce

# Verify installations
echo "Verifying installations..."
yo --version && echo "✓ Yeoman is installed"
tsc --version && echo "✓ TypeScript is installed"
vsce --version && echo "✓ vsce is installed"

# Check for VS Code
if ! command -v code &> /dev/null; then
    echo "VS Code is not installed or not in PATH. Please install VS Code from https://code.visualstudio.com/"
    echo "After installation, make sure the 'code' command is available in your PATH."
    echo "You can install the required VS Code extensions manually:"
    echo "- ESLint (dbaeumer.vscode-eslint)"
    echo "- TSLint Problem Matcher (amodio.tsl-problem-matcher)"
    echo "- Extension Test Runner (ms-vscode.extension-test-runner)"
else
    echo "✓ VS Code is installed"
    
    # Install required VS Code extensions
    echo "Installing required VS Code extensions..."
    code --install-extension dbaeumer.vscode-eslint
    code --install-extension amodio.tsl-problem-matcher
    code --install-extension ms-vscode.extension-test-runner
    echo "✓ Required VS Code extensions installed"
fi

# Navigate to extension directory
cd extension-v1 || mkdir -p extension-v1 && cd extension-v1

# Install project dependencies
echo "Setting up project dependencies..."
npm install --save-dev webpack webpack-cli ts-loader typescript @types/vscode @types/node @types/mocha mocha

# Install additional dependencies for testing
echo "Installing testing dependencies..."
npm install --save-dev @vscode/test-electron @vscode/test-cli

echo "Setup complete! You can now start developing the VS Code extension."
echo "To run the extension, press F5 in VS Code or run 'npm run compile && code --extensionDevelopmentPath=\$PWD'"

# Add instructions for debugging
echo ""
echo "=== DEBUGGING INSTRUCTIONS ==="
echo "1. Open the extension project in VS Code"
echo "2. Open a file in the editor (e.g., src/extension.ts)"
echo "3. Press F5 to start debugging"
echo "4. If you encounter the '${file} cannot be resolved' error:"
echo "   - Make sure you have a file open in the editor"
echo "   - Try using the Run and Debug view (Ctrl+Shift+D)"
echo "   - Or run 'npm run compile && code --extensionDevelopmentPath=\$PWD' in the terminal"
echo "==========================="
