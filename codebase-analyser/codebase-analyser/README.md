# RepoMind Codebase Analyser

This service is responsible for analyzing codebases using Tree-sitter, generating semantic code chunks, creating embeddings for the vector database, and building dependency graphs.

## Key Features

- **AST Parsing**: Tree-sitter integration for multiple languages with specialized Java support
- **Semantic Code Chunking**: Hierarchical chunking with structural integrity and context preservation
- **Dependency Analysis**: Comprehensive analysis of relationships between code components
- **Vector Database**: LanceDB integration for storing and querying code embeddings
- **Code Embeddings**: Generation using CodeBERT with batch processing and caching
- **Dependency Graphs**: Optional construction and visualization of code relationships
- **Command-line Interface**: Tools for various operations including graph visualization

## Setup

1. Create a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

### Parsing and Chunking

```bash
# Parse a Java file and generate chunks
python test_parser.py samples/SimpleClass.java
```

### Generating Embeddings

```bash
# Generate embeddings for code chunks
python test_embeddings.py
```

### Building Dependency Graphs

```bash
# Build a dependency graph from code chunks
python test_dependency_graph.py
```

### Visualizing Dependency Graphs

```bash
# Visualize a dependency graph
python -m codebase_analyser.graph.cli visualize samples/dependency_graph.json --output-file samples/graph.png
```

## API Usage

```python
from codebase_analyser import CodebaseAnalyser
from codebase_analyser.database import LanceDBManager
from codebase_analyser.embeddings import EmbeddingGenerator

# Parse a codebase
analyser = CodebaseAnalyser(repo_path="/path/to/repo")
analyser.parse()
chunks = analyser.get_chunks()

# Generate embeddings
generator = EmbeddingGenerator()
for chunk in chunks:
    chunk.embedding = generator.generate_embedding(chunk.content, chunk.language)

# Store in database
db_manager = LanceDBManager(db_path="codebase-analyser/.lancedb")
db_manager.add_code_chunks([chunk.to_dict() for chunk in chunks])

# Search for similar code
query_embedding = generator.generate_embedding("def calculate_sum(a, b):", "python")
results = db_manager.search_code_chunks(query_embedding, limit=5)
```

## Java Parsing

The analyser includes specialized support for Java files, extracting:

- Package declarations
- Import statements
- Class declarations with inheritance information
- Field declarations with types
- Method declarations with return types and parameters

To test Java parsing:

```bash
python test_java_parser.py /path/to/your/JavaFile.java
```

## Testing

```bash
# Basic parsing test
python test_parser.py /path/to/your/file.ext

# Java-specific parsing
python test_java_parser.py /path/to/your/JavaFile.java

# Comprehensive Java parsing with AST analysis
python test_java_parser_comprehensive.py /path/to/your/JavaFile.java

# AST utility functions
python test_ast_utils.py /path/to/your/file.ext

# Hierarchical code chunking
python test_hierarchical_chunking.py /path/to/your/file.ext

# Context preservation and structural integrity
python test_context_preservation.py /path/to/your/file.ext

# Dependency analysis and relationship mapping
python test_dependency_analysis.py /path/to/your/file.ext

# Visualization utilities
python test_simple_visualization.py /path/to/your/file.ext
```

## Database Operations

```bash
# Test LanceDB installation and configuration
python test_lancedb.py

# Clear and recreate tables
python test_lancedb.py --clear

# Use a custom database path
python test_lancedb.py --db-path codebase-analyser/.lancedb
```

## Embedding Operations

```bash
# Test the embedding generator
python test_embeddings.py

# Visualize embeddings
python test_embeddings.py --visualize

# Embed chunks and store in database
python test_embed_chunks.py

# Clear database before embedding
python test_embed_chunks.py --clear-db

# Use a specific model
python test_embed_chunks.py --model microsoft/codebert-base
```

## Dependency Graph Operations

The dependency graph functionality provides insights into code relationships and dependencies. The graph metadata includes dependency counts, graph position, cycle detection, and relationship types.

### Building Dependency Graphs

```bash
# Build a graph from code chunks
python -m codebase_analyser.graph.cli build samples/sample_chunks.json --output-file samples/dependency_graph.json

# Store dependencies in the database
python -m codebase_analyser.graph.cli build samples/sample_chunks.json --db-path codebase-analyser/.lancedb --store-in-db
```

### Visualizing Dependency Graphs

```bash
# Generate a PNG visualization
python -m codebase_analyser.graph.cli visualize samples/dependency_graph.json --output-file samples/dependency_graph.png

# Generate a DOT file for Graphviz
python -m codebase_analyser.graph.cli visualize samples/dependency_graph.json --format dot --output-file samples/dependency_graph.dot

# Customize the visualization
python -m codebase_analyser.graph.cli visualize samples/dependency_graph.json --layout circular --node-size 1500
```

### Querying Dependencies

```bash
# Query all dependencies
python -m codebase_analyser.graph.cli query

# Query by source node
python -m codebase_analyser.graph.cli query --source-id "file:sample1.java"

# Query by dependency type
python -m codebase_analyser.graph.cli query --type "CONTAINS"
```

### Testing Graph Construction

```bash
# Run the full test pipeline
python test_dependency_graph.py

# Specify input and output
python test_dependency_graph.py --input samples/sample_chunks.json --output-dir samples/graphs
```



## Large Project Support

The codebase analyzer is optimized for large projects:

### Hierarchical Structure

```
Project
├── File 1
│   ├── Class A
│   │   ├── Method X
│   │   └── Method Y
│   └── Class B
└── File 2
    └── Function Z
```

- **Structural Relationships**: Parent-child links, root references, and depth indicators
- **Dependency Tracking**: Source-target relationships with type and strength information
- **Optimizations**:
  - Minimal schema option for reduced storage
  - Batch processing for embedding generation
  - Caching to avoid regenerating embeddings
  - Optional dimensionality reduction for very large codebases

## Database Management

### LanceDB Compatibility

- **Version Compatibility**: Works with different LanceDB versions with adaptive API handling
- **Schema Options**: Supports both minimal and full schema versions
- **Best Practices**:
  - Pin LanceDB version in requirements.txt
  - Use consistent schema across components
  - Clear and recreate tables when upgrading

### Database Utilities

```bash
# View database information
python -m codebase_analyser.database.db_utils --info

# Clear and recreate tables
python -m codebase_analyser.database.db_utils --clear

# Use full schema
python -m codebase_analyser.database.db_utils --full

# Specify database path
python -m codebase_analyser.database.db_utils --db-path codebase-analyser/.lancedb
```

### Programmatic Database Management

```python
from codebase_analyser.database import open_db_connection, close_db_connection

# Open connection
db_manager = open_db_connection(db_path="codebase-analyser/.lancedb", use_minimal_schema=True)

try:
    # Add data
    db_manager.add_code_chunks(code_chunks)
    db_manager.add_dependencies(dependencies)

    # Search
    results = db_manager.search_code_chunks(query_embedding, limit=10)
finally:
    # Close connection
    close_db_connection(db_manager)
```

## Embedding Generation

The system uses CodeBERT to generate code embeddings:

### Performance Considerations

- **Dimensions**: 768 dimensions (CodeBERT default) for most codebases
- **Storage**: ~3KB per embedding (768 dimensions with float32)
- **Scaling**:
  - 100,000 chunks: ~300MB for embeddings
  - 1 million chunks: ~3GB for embeddings
- **Optimization Options**:
  - PCA: Reduce to 384-512 dimensions with minimal information loss
  - Batch processing: Process multiple chunks at once
  - Caching: Avoid regenerating embeddings for the same code

### Embedding API

```python
from codebase_analyser.embeddings import EmbeddingGenerator

# Create generator
generator = EmbeddingGenerator(
    model_name="microsoft/codebert-base",
    cache_dir=".cache",
    batch_size=8
)

# Single embedding
code = "def hello_world():\n    print('Hello, World!')"
embedding = generator.generate_embedding(code, language="python")

# Batch processing
codes = ["public class Hello {}", "function hello() {}"]
languages = ["java", "javascript"]
embeddings = generator.generate_embeddings_batch(codes, languages)

# Store in database
from codebase_analyser.embeddings import embed_and_store_chunks
embed_and_store_chunks(chunks=code_chunks, db_path="codebase-analyser/.lancedb")
```

## Unified Storage for Vectors and Graph Metadata

The codebase analyzer includes a unified storage system that integrates code embeddings with dependency graph metadata. This allows for more efficient querying and better integration between vector search and graph-based filtering.

### Using the Unified Storage

To use the unified storage system:

```bash
python test_unified_storage.py
```

To clear the database before testing:

```bash
python test_unified_storage.py --clear-db
```

To use a specific database path:

```bash
python test_unified_storage.py --db-path codebase-analyser/.lancedb
```

To use the full schema with additional metadata:

```bash
python test_unified_storage.py --full-schema
```

### Programmatic Usage of Unified Storage

You can also use the unified storage system programmatically in your Python code:

```python
from codebase_analyser import open_unified_storage, close_unified_storage

# Open a unified storage connection
storage_manager = open_unified_storage(
    db_path="codebase-analyser/.lancedb",
    embedding_dim=768,
    use_minimal_schema=True
)

try:
    # Add code chunks with graph metadata
    storage_manager.add_code_chunks_with_graph_metadata(
        chunks=code_chunks,
        dependencies=dependencies  # Optional, will be extracted from chunks if not provided
    )

    # Search with dependency filtering
    results = storage_manager.search_with_dependencies(
        query_embedding=query_vector,
        dependency_filter={"has_imports": True},
        limit=10
    )

    # Get a chunk with its dependencies
    chunk = storage_manager.get_chunk_with_dependencies(node_id)

finally:
    # Close the connection
    close_unified_storage(storage_manager)
```

### Graph Metadata in Code Chunks

When code chunks are stored in the database, they automatically include graph metadata in their `metadata` field. This metadata includes:

```json
{
  "graph_metadata": {
    "dependency_count": 5,
    "incoming_count": 2,
    "outgoing_count": 3,
    "in_cycle": false,
    "graph_position": "intermediate",
    "instability": 0.6,
    "has_imports": true,
    "has_extends": false,
    "has_implements": true,
    "has_calls": true,
    "has_uses": false,
    "incoming_dependencies": ["node1", "node2"],
    "outgoing_dependencies": ["node3", "node4", "node5"]
  }
}
```

This metadata can be used for filtering and analysis without requiring a separate graph database.