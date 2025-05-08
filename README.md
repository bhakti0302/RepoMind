# RepoMind - Intelligent Coding Assistant

RepoMind is an AI-powered coding assistant that provides intelligent code understanding and generation capabilities. The project consists of a VS Code extension for the user interface and a codebase analysis system for deep code understanding.

## Features (Implemented)

### VS Code Extension
- Basic chat interface with modern UI
- Status bar integration
- Command palette integration
- Welcome message with suggestions

### Codebase Analysis System
- AST parsing with Tree-sitter for multiple languages
- Hierarchical semantic code chunking
- Dependency analysis and relationship mapping
- Structural integrity and context preservation
- Comprehensive metadata for code understanding
- Memory-optimized processing for large codebases
- Visualization utilities for code structure

## Epic 2: Codebase Analysis (Completed Stories)

### Story 2.1: Tree-sitter Integration
- Integrated Tree-sitter for AST parsing
- Added support for multiple programming languages
- Implemented utility functions for AST traversal and analysis
- Created specialized Java parser for detailed analysis

### Story 2.2: Semantic Code Chunking
- Designed and implemented semantic chunking algorithm based on AST structure
- Created hierarchical chunking with fine-grained and container-level chunks
- Ensured structural integrity and context preservation
- Added comprehensive metadata for dependency relationships
- Implemented visualization utilities for chunk hierarchy

### Story 2.3: Vector Database and Dependency Graph Setup (In Progress)
- Installed and configured LanceDB for storing code embeddings
- Created comprehensive schema for code chunks and dependency relationships
- Implemented version-compatible database manager with schema validation
- Added robust error handling and logging
- Designed flexible schema with minimal and full versions
- Created database utility scripts for connection management and schema updates
- Implemented embedding generation using CodeBERT
- Added batch processing for efficient embedding generation
- Implemented caching to avoid regenerating embeddings for the same code

## Prerequisites

- Node.js (v14 or later)
- VS Code (v1.80 or later)
- npm (v6 or later)
- Git

## Setup Instructions

### VS Code Extension Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/repomind.git
cd repomind
```

2. Install project dependencies:
```bash
cd extension-v1
npm install
```

3. Compile the extension:
```bash
npm run compile
```

4. Run the extension in development mode:
   - Press F5 in VS Code, or
   - Use the Run and Debug view (Ctrl+Shift+D), or
   - Run `npm run start` in the terminal

This will open a new VS Code window with the extension loaded.

### Codebase Analyser Setup

1. Navigate to the codebase-analyser directory:
```bash
cd codebase-analyser
```

2. Create a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run a test to verify the installation:
```bash
python test_parser.py samples/SimpleClass.java
```

### Additional Setup (Optional)

If you plan to develop the extension further, you might want to install:

1. Global tools:
```bash
npm install -g yo generator-code typescript @vscode/vsce
```

2. VS Code extensions:
```bash
code --install-extension dbaeumer.vscode-eslint
code --install-extension amodio.tsl-problem-matcher
code --install-extension ms-vscode.extension-test-runner
```

## Development

The project is structured as follows:

```
RepoMind/
├── extension-v1/          # VS Code Extension
│   ├── src/
│   │   ├── extension.ts   # Main extension entry point
│   │   ├── ui/            # UI components
│   │   └── test/          # Test files
│   ├── media/             # UI assets
│   └── package.json       # Extension manifest
│
├── codebase-analyser/     # Codebase Analysis System
│   ├── codebase_analyser/
│   │   ├── parsers/       # Language-specific parsers
│   │   ├── chunking/      # Code chunking and dependency analysis
│   │   └── utils/         # Utility functions
│   ├── test_*.py          # Test scripts
│   └── requirements.txt   # Python dependencies
│
└── docs/                  # Project documentation
    └── PLAN.MD            # Project plan and roadmap
```

## Testing

To run the tests:
```bash
npm test
```

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
