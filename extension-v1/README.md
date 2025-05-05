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
4. Press F5 to launch a new window with the extension loaded

### Building

Build the extension with:
```bash
npm run compile
```

Package the extension for distribution:
```bash
npm run package
```

## Contributing

Please read our Contributing Guide for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
