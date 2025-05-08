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

# End-to-end integration test
python test_end_to_end_integration.py --clear-db

# Custom relevance scoring test
python test_custom_relevance.py --clear-db --alpha 0.7 --beta 0.3
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

```bash
# Build graph
python -m codebase_analyser.graph.cli build samples/sample_chunks.json --output-file samples/dependency_graph.json
python -m codebase_analyser.graph.cli build samples/sample_chunks.json --db-path codebase-analyser/.lancedb --store-in-db

# Visualize graph
python -m codebase_analyser.graph.cli visualize samples/dependency_graph.json --output-file samples/dependency_graph.png
python -m codebase_analyser.graph.cli visualize samples/dependency_graph.json --format dot --layout circular --node-size 1500

# Query dependencies
python -m codebase_analyser.graph.cli query
python -m codebase_analyser.graph.cli query --source-id "file:sample1.java" --type "CONTAINS"

# Test graph construction
python test_dependency_graph.py --input samples/sample_chunks.json --output-dir samples/graphs
```



## Large Project Support

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

**Optimizations**:
- Minimal schema option for reduced storage
- Batch processing for embedding generation
- Caching to avoid regenerating embeddings
- Optional dimensionality reduction (PCA) for very large codebases

## Database Management

```bash
# Database utilities
python -m codebase_analyser.database.db_utils --info
python -m codebase_analyser.database.db_utils --clear --full --db-path codebase-analyser/.lancedb
```

```python
# Direct database API
from codebase_analyser.database import open_db_connection, close_db_connection

db_manager = open_db_connection(db_path="codebase-analyser/.lancedb", use_minimal_schema=True)
db_manager.add_code_chunks(code_chunks)
db_manager.add_dependencies(dependencies)
results = db_manager.search_code_chunks(query_embedding, limit=10)
close_db_connection(db_manager)
```

### LanceDB Options
- **Schema**: Minimal (default) or full schema with additional metadata
- **Compatibility**: Works with different LanceDB versions via adaptive API handling
- **Storage**: Default path is `codebase-analyser/.lancedb`

## Embedding Generation

```python
from codebase_analyser.embeddings import EmbeddingGenerator

# Create generator
generator = EmbeddingGenerator(
    model_name="microsoft/codebert-base",
    cache_dir=".cache",
    batch_size=8
)

# Generate embeddings
embedding = generator.generate_embedding(code, language="python")
embeddings = generator.generate_embeddings_batch(codes, languages)

# Store in database
from codebase_analyser.embeddings import embed_and_store_chunks
embed_and_store_chunks(chunks=code_chunks, db_path="codebase-analyser/.lancedb")
```

### Performance Options
- **Dimensions**: 768 (default) or reduce to 384-512 with PCA for large codebases
- **Batch Processing**: Process multiple chunks at once (8-16 recommended)
- **Caching**: Avoid regenerating embeddings for unchanged code

## Unified Storage

```bash
# Test unified storage
python test_unified_storage.py --clear-db

# Options
python test_unified_storage.py --db-path codebase-analyser/.lancedb --full-schema
```

### Unified Storage API

```python
from codebase_analyser import open_unified_storage, close_unified_storage

storage_manager = open_unified_storage(
    db_path="codebase-analyser/.lancedb",
    embedding_dim=768,
    use_minimal_schema=True
)

# Add chunks with graph metadata
storage_manager.add_code_chunks_with_graph_metadata(chunks=code_chunks)

# Search with dependency filtering
results = storage_manager.search_with_dependencies(
    query_embedding=query_vector,
    dependency_filter={"has_imports": True},
    limit=10
)

# Search with combined scoring
results = storage_manager.search_with_combined_scoring(
    query_embedding=query_vector,
    query_node_id="file:path/to/file.py",
    alpha=0.7,  # Semantic weight
    beta=0.3,   # Graph weight
    limit=10
)

# Get chunk with dependencies
chunk = storage_manager.get_chunk_with_dependencies(node_id)

# Close connection
close_unified_storage(storage_manager)
```

### Graph Metadata Schema

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

## Custom Relevance Scoring

```bash
# Test with default weights (α=0.7, β=0.3)
python test_custom_relevance.py --clear-db

# Customize weights
python test_custom_relevance.py --alpha 0.5 --beta 0.5
```

Formula: `final_score = α * semantic_similarity + β * (1 / (1 + graph_distance))`

- Combines vector similarity with graph proximity
- Adjustable weights to prioritize semantic or structural relevance
- Uses NetworkX for graph distance calculations

## End-to-End Integration Testing

```bash
# Basic test
python test_end_to_end_integration.py --clear-db

# Options
python test_end_to_end_integration.py --db-path /path/to/db --real-embeddings --full-schema
python test_end_to_end_integration.py --test-dir /path/to/test/files --keep-test-dir
```

Tests the complete pipeline:
- Parses files in multiple languages (Java, Python, JavaScript)
- Generates chunks and embeddings
- Stores in database with graph metadata
- Tests search methods (vector, dependency-filtered, combined scoring)
- Validates chunk retrieval with dependencies