# RepoMind - Intelligent Coding Assistant

RepoMind is an AI-powered coding assistant that provides intelligent code understanding and generation capabilities. The project consists of a codebase analysis system for deep code understanding and a VS Code extension for the user interface.

## Project Components

1. **Codebase Analyser**: Advanced code analysis system for parsing, chunking, and understanding code
2. **VS Code Extension**: User interface for interacting with the codebase analyser
3. **Documentation**: Comprehensive documentation for the project

## Features

### Codebase Analysis System
- AST parsing with Tree-sitter for multiple languages
- Hierarchical semantic code chunking
- Dependency analysis and relationship mapping
- Structural integrity and context preservation
- Comprehensive metadata for code understanding
- Memory-optimized processing for large codebases
- Vector database integration with LanceDB
- Code embedding generation using CodeBERT
- Optional dependency graph visualization
- Unified storage for vectors and graph metadata
- Command-line interface for various operations

### Enhanced Java Parser
- Parses Java files and extracts classes, methods, fields, and their relationships
- Creates CodeChunk objects with proper parent-child relationships
- Stores chunks in the database
- Supports complex Java projects with multiple files and packages

## Quick Start

### Prerequisites
- Python 3.8 or later
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/repomind.git
cd repomind
```

2. Set up the codebase analyser:
```bash
cd codebase-analyser
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Running the Java Analyzer

The main script for analyzing Java projects is `analyze_java.py`. You can run it with the following command:

```bash
cd codebase-analyser
python scripts/analyze_java.py <path_to_java_project> [options]
```

Options:
- `--clear-db`: Clear the database before adding new chunks
- `--mock-embeddings`: Use mock embeddings instead of generating real ones
- `--visualize`: Generate visualization of the dependency graph
- `--project-id`: Project ID for the chunks
- `--max-files`: Maximum number of files to process (default: 100)
- `--skip-large-files`: Skip files larger than 1MB
- `--minimal-schema`: Use minimal schema for the database

Example:
```bash
python scripts/analyze_java.py samples/complex_java --clear-db --mock-embeddings --visualize
```

This will:
1. Parse all Java files in the specified directory
2. Extract classes, methods, and their relationships
3. Generate embeddings for the code chunks
4. Store the chunks in the LanceDB database
5. Generate a visualization of the dependency graph

## Project Structure

```
RepoMind/
├── codebase-analyser/           # Codebase analysis system
│   ├── codebase_analyser/       # Main package
│   │   ├── parsing/             # Code parsing and chunking
│   │   ├── database/            # Database integration with LanceDB
│   │   ├── embeddings/          # Code embedding generation
│   │   └── visualization/       # Visualization utilities
│   ├── scripts/                 # Utility scripts
│   │   ├── analyze_java.py      # Main script for analyzing Java projects
│   │   └── ...
│   ├── tests/                   # Test directory
│   │   ├── parsing/             # Tests for parsing components
│   │   ├── database/            # Tests for database components
│   │   └── ...
│   └── samples/                 # Sample files and outputs
│       ├── java_test_project/   # Simple Java project
│       ├── complex_java/        # Complex Java project
│       └── ...
│
├── extension-v1/                # VS Code extension
│
└── docs/                        # Documentation
    └── PLAN.MD                  # Project plan and roadmap
```

## Completed Components

### 1. Tree-sitter Integration
- Integrated Tree-sitter for AST parsing
- Added support for multiple programming languages
- Implemented utility functions for AST traversal and analysis
- Created specialized Java parser for detailed analysis

### 2. Semantic Code Chunking
- Designed and implemented semantic chunking algorithm based on AST structure
- Created hierarchical chunking with fine-grained and container-level chunks
- Ensured structural integrity and context preservation
- Added comprehensive metadata for dependency relationships
- Implemented visualization utilities for chunk hierarchy

### 3. Vector Database Integration
- Installed and configured LanceDB for storing code embeddings
- Created comprehensive schema for code chunks and dependency relationships
- Implemented version-compatible database manager with schema validation
- Added robust error handling and logging
- Designed flexible schema with minimal and full versions
- Created database utility scripts for connection management

### 4. Code Embedding Generation
- Implemented embedding generation using CodeBERT
- Added batch processing for efficient embedding generation
- Implemented caching to avoid regenerating embeddings for the same code
- Created utility scripts for embedding code chunks and storing them in the database

### 5. Dependency Graph Construction
- Built dependency graph construction system
- Implemented visualization utilities for code relationships
- Created command-line interface for dependency graph operations
- Added database integration for storing and querying dependencies

## Documentation

For more detailed information, see the following documentation:

- [Project Plan](docs/PLAN.MD) - Detailed project plan and roadmap
- [Codebase Analyser README](codebase-analyser/README.md) - Detailed documentation for the codebase analyser

## License

This project is licensed under the MIT License - see the LICENSE file for details.
