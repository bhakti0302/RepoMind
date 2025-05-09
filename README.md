# Codebase Analyser

A tool for analyzing codebases and generating code based on requirements.

## Overview

The Codebase Analyser is a powerful tool that provides deep code understanding and intelligent code generation capabilities. It combines AST parsing, semantic code chunking, vector embeddings, and graph-based analysis to create a comprehensive understanding of your codebase.

### Key Features

- **AST Parsing**: Tree-sitter integration for multiple languages (Java, JavaScript, Python)
- **Semantic Code Chunking**: Hierarchical chunking with structural integrity
- **Vector Database**: LanceDB integration for storing and querying code embeddings
- **Dependency Analysis**: Graph-based analysis of code relationships
- **Custom Relevance Scoring**: Combined semantic similarity and graph proximity
- **Multi-hop RAG**: Intelligent code retrieval with architectural and implementation context
- **LangGraph Agent**: AI-powered code generation based on requirements
- **Configurable Prompts**: Easily test different prompts for code generation
- **LLM Integration**: Support for OpenAI and OpenRouter models

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/codebase-analyser.git
cd codebase-analyser

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
```

Alternatively, you can use the provided installation script:

```bash
python install_all_dependencies.py
```

## Setup

### Environment Variables

Set up the following environment variables for LLM integration:

```bash
# OpenAI
export OPENAI_API_KEY=your_openai_api_key
export OPENAI_MODEL=gpt-3.5-turbo  # or another model

# OpenRouter (alternative)
export OPENROUTER_API_KEY=your_openrouter_api_key
export OPENROUTER_MODEL=openai/gpt-3.5-turbo  # or another model

# For testing without LLM calls
export USE_MOCK_IMPLEMENTATIONS=1
```

### Database Location

The codebase analyzer uses LanceDB to store code embeddings and dependencies. By default, the database is stored in:

```
.lancedb
```

You can specify a different location using the `--db-path` parameter in most commands.

## Usage

### Analyzing Code

```bash
# Analyze a single file
python -m codebase_analyser.cli.analyze_file path/to/file.java

# Analyze a directory
python -m codebase_analyser.cli.analyze_dir path/to/directory

# Analyze with custom options
python -m codebase_analyser.cli.analyze_dir path/to/directory --language java --chunk-size medium --store-embeddings
```

### Searching Code

```bash
# Search for code similar to a query
python -m codebase_analyser.cli.search "implement a sorting algorithm" --language java --limit 5

# Search with custom relevance weights
python -m codebase_analyser.cli.search "implement a sorting algorithm" --alpha 0.7 --beta 0.3
```

### Testing RAG Components

```bash
# Test the RAG pipeline
python test_rag.py

# Test with custom requirements
python test_rag.py --requirements-file path/to/requirements.json

# Test with specific language
python test_rag.py --language java
```

### Generating Code

```bash
# Generate code from requirements
python -m codebase_analyser.cli.generate --requirements-file requirements/feature.json --output-file generated_code.java

# Generate with custom prompt
python -m codebase_analyser.cli.generate --requirements-file requirements/feature.json --prompt-file prompts/custom.txt
```

### Testing Different Prompts

```bash
# Test with a specific prompt template
python -m codebase_analyser.cli.prompt_tester --prompt-file prompts/code_generation.txt --requirements-file requirements/feature.json

# Compare multiple prompt templates
python -m codebase_analyser.cli.prompt_tester --prompt-dir prompts/ --requirements-file requirements/feature.json --output-dir results/
```

## Key Components

### 1. Code Parsing and Chunking
The system uses Tree-sitter to parse code into AST (Abstract Syntax Tree) and then chunks it into semantically meaningful units.

### 2. Vector Database Integration
Code chunks are stored in LanceDB along with their embeddings for efficient similarity search.

### 3. Dependency Graph
The system builds a graph of code dependencies to understand relationships between components.

### 4. Multi-hop RAG
The Retrieval-Augmented Generation system uses a multi-hop approach:
1. First hop: Retrieve architectural patterns based on semantic similarity
2. Second hop: Retrieve implementation details using both semantic and structural relevance
3. Context assembly: Combine retrieved information into a structured context for the LLM

### 5. Custom Relevance Scoring
Combines semantic similarity (vector space) with graph proximity (structural relationships) for more accurate code retrieval.

## License

MIT
