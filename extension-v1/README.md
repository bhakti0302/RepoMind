# VS Code Agentic AI Coding Assistant

An AI-powered coding assistant that analyzes business requirements, understands your codebase, and generates code using LLMs.

## Features

- **Business Requirements Analysis**: Analyze text files containing business requirements
- **Codebase Understanding**: Understand your existing codebase structure and patterns
- **Code Generation**: Generate new code based on requirements and existing patterns
- **Human-in-the-Loop**: Review and approve generated code before it's applied

## Requirements

- Visual Studio Code 1.80.0 or higher
- Node.js 14.19.0 or higher
- Internet connection for LLM API access

## Extension Settings

This extension contributes the following settings:

* `extension-v1.llmProvider`: The LLM provider to use (openrouter or openai)
* `extension-v1.modelName`: The model name to use for code generation
* `extension-v1.apiKey`: API key for the LLM provider

## Getting Started

1. Install the extension
2. Set your API key in the extension settings
3. Open a project
4. Run the "Start AI Coding Assistant" command from the command palette
5. Select a business requirements file to analyze
6. Review and approve the generated code

## Commands

* `Start AI Coding Assistant`: Launches the AI assistant interface
* `Analyze Business Requirements`: Analyzes a business requirements file
* `Generate Code from Requirements`: Generates code based on analyzed requirements
* `Open AI Assistant Chat`: Opens the chat interface
* `Sync Codebase`: Analyzes your codebase and stores the results in a database
* `Visualize Code Relationships`: Generates visualizations of code relationships
* `Show Visualizations in Chat`: Displays all available visualizations in the chat
* `Show RepoMind Log File`: Opens the current log file in the editor
* `Reset RepoMind Log File`: Resets the log file and starts a new one

## Logging System

The extension includes a comprehensive logging system that:

1. **Logs to Files**: All logs are written to files in the `logs` directory
2. **Supports Multiple Log Levels**: ERROR, WARN, INFO, DEBUG, TRACE
3. **Logs Function Calls**: Automatically logs function calls and their results
4. **Handles Log Rotation**: Automatically rotates logs when they get too large
5. **Tracks Codebase Analyzer Operations**: Records all operations performed by the codebase analyzer

### Log Levels

* **ERROR**: Critical errors that prevent the extension from functioning
* **WARN**: Warnings about potential issues
* **INFO**: General information about operations
* **DEBUG**: Detailed information for debugging
* **TRACE**: Very detailed information for tracing execution flow

### Viewing Logs

Use the `Show RepoMind Log File` command to open the current log file in the editor.

### Log File Location

Log files are stored in the `logs` directory in the workspace root. Each log file is named with a timestamp, e.g., `repomind-2023-07-01T12-00-00.log`.

## Development

### Prerequisites

- Node.js (v14.19.0 or higher)
- npm (comes with Node.js)
- Git
- Visual Studio Code

### Setup

1. Clone the repository
2. Run `npm install` to install dependencies
3. Run `npm run compile` to compile the extension

### Launching the Extension

#### Using the testshreya Folder

The extension is configured to work with the testshreya folder, which contains a sample Java project for testing the extension's functionality. This folder is located at:

```
/Users/shreyah/Documents/Projects/SAP/testshreya
```

The testshreya folder contains:
- Java source files with various relationships (inheritance, imports, etc.)
- A sample project structure for testing code analysis
- Visualization outputs from previous runs

There are multiple ways to launch the extension with the testshreya folder:

#### Method 1: Using the NPM Script

```bash
npm run testshreya
```

This will compile the extension and launch VS Code with the testshreya folder.

#### Method 2: Using the Launch Script

```bash
./launch-testshreya.sh
```

This script compiles the extension and launches VS Code with the testshreya folder. It includes error handling to ensure everything works correctly.

#### Method 3: Using the Debug Script

```bash
./debug-testshreya.sh
```

This script launches VS Code in debug mode with the testshreya folder.

#### Method 4: Using VS Code's Debug Feature

1. Open VS Code in the extension-v1 folder
2. Press F5 or click the "Run and Debug" button in the sidebar
3. Select "Run Extension" from the dropdown menu

This will use the launch.json configuration and open the extension with the testshreya folder.

### Building

Build the extension with:
```bash
npm run compile
```

Package the extension for distribution:
```bash
npm run package
```

### Troubleshooting

If you encounter issues launching the extension with the testshreya folder:

1. **Check if the testshreya folder exists**:
   ```bash
   ls -la /Users/shreyah/Documents/Projects/SAP/testshreya
   ```

2. **Verify VS Code is installed and available in your PATH**:
   ```bash
   which code
   ```

3. **Try running VS Code with the verbose flag**:
   ```bash
   code --verbose --new-window --extensionDevelopmentPath="$(pwd)" "/Users/shreyah/Documents/Projects/SAP/testshreya"
   ```

4. **Check for errors in the VS Code Developer Tools**:
   - After launching the extension, press `Ctrl+Shift+I` (or `Cmd+Option+I` on macOS) to open the Developer Tools
   - Check the Console tab for any error messages

5. **Verify the extension is being loaded**:
   - After launching VS Code, check the Extensions view to make sure the extension is listed
   - Look for "RepoMind" in the list of installed extensions

## Contributing

Please read our Contributing Guide for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
