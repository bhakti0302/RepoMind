# Tests for Codebase Analyser

This directory contains tests for the codebase analyser package.

## Test Files

- `test_parsing.py`: Tests for parsing and chunking functionality
- `test_java_parser.py`: Tests for Java parser
- `test_ast_utils.py`: Tests for AST utilities
- `test_chunking.py`: Tests for chunking
- `test_hierarchical_chunking.py`: Tests for hierarchical chunking
- `test_context_preservation.py`: Tests for context preservation
- `test_dependency_analysis.py`: Tests for dependency analysis
- `test_database.py`: Tests for database functionality
- `test_schema.py`: Tests for schema
- `test_embeddings.py`: Tests for embedding generation
- `test_embed_chunks.py`: Tests for embedding chunks
- `test_graph.py`: Tests for graph functionality
- `test_visualization.py`: Tests for visualization
- `test_unified_storage.py`: Tests for unified storage

## Running Tests

To run all tests:

```bash
python -m unittest discover tests
```

To run a specific test:

```bash
python -m unittest tests/test_parsing.py
```

## Fixtures

The `fixtures` directory contains test fixtures:

- `sample_chunks.json`: Sample code chunks for testing
- `sample_dependencies.json`: Sample dependencies for testing
