# RepoMind Codebase Analyser

This service is responsible for analyzing codebases using Tree-sitter, generating semantic code chunks, and creating embeddings for the vector database.

## Features

- AST parsing with Tree-sitter for multiple languages
- Specialized Java parsing support
- Hierarchical semantic code chunking
- Comprehensive dependency analysis
- Structural integrity and context preservation
- Dependency graph construction with metrics
- Code embedding generation using CodeBERT
- Efficient batch processing and caching for embeddings
- LanceDB integration for vector storage
- Visualization utilities for code structure

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

## Usage

```python
from codebase_analyser import CodebaseAnalyser
from codebase_analyser.database import LanceDBManager

# General usage
analyser = CodebaseAnalyser(repo_path="/path/to/repo")
analyser.parse()
chunks = analyser.get_chunks()

# Java-specific parsing
java_files = analyser.parse_java_files()
for java_file in java_files:
    print(f"Found class: {java_file['classes'][0]['name']}")

# Accessing dependency information
for chunk in chunks:
    # Get the dependency graph from the file chunk
    if chunk.chunk_type == 'file' and 'dependency_graph' in chunk.metadata:
        dependency_graph = chunk.metadata['dependency_graph']
        print(f"Found {len(dependency_graph['edges'])} dependencies")

        # Print graph-level metrics
        print(f"Coupling score: {dependency_graph['metrics']['coupling_score']}")
        print(f"Cohesion score: {dependency_graph['metrics']['cohesion_score']}")

    # Get chunk-level dependency metrics
    if 'dependency_metrics' in chunk.metadata:
        metrics = chunk.metadata['dependency_metrics']
        print(f"Chunk: {chunk.name}, Fan-in: {metrics['fan_in']}, Fan-out: {metrics['fan_out']}")

# Using LanceDB for vector storage
db_manager = LanceDBManager(db_path=".lancedb")
db_manager.create_tables()

# Store code chunks in the database
code_chunks_data = []
for chunk in chunks:
    # Create a dictionary with the chunk data
    chunk_data = {
        "embedding": chunk.embedding,  # Assuming embeddings have been generated
        "node_id": chunk.node_id,
        "chunk_type": chunk.chunk_type,
        "content": chunk.content,
        "file_path": chunk.file_path,
        "start_line": chunk.start_line,
        "end_line": chunk.end_line,
        "language": chunk.language,
        "name": chunk.name or "",
        "qualified_name": chunk.qualified_name or "",
        "metadata": chunk.metadata,
        "context": chunk.context
    }
    code_chunks_data.append(chunk_data)

# Add chunks to the database
db_manager.add_code_chunks(code_chunks_data)

# Search for similar code chunks
query_embedding = generate_embedding("def calculate_sum(a, b):")  # Placeholder function
results = db_manager.search_code_chunks(query_embedding, limit=5)
for result in results:
    print(f"Found similar chunk: {result['name']} ({result['file_path']})")
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

### Basic Parsing Test

To test basic parsing functionality:

```bash
python test_parser.py /path/to/your/file.ext
```

### Java Parsing Test

To test Java-specific parsing:

```bash
python test_java_parser.py /path/to/your/JavaFile.java
```

### Comprehensive Java Parsing Test

For a more detailed Java parsing test with full AST analysis:

```bash
python test_java_parser_comprehensive.py /path/to/your/JavaFile.java
```

### AST Utilities Test

To test the AST utility functions:

```bash
python test_ast_utils.py /path/to/your/file.ext
```

### Hierarchical Chunking Test

To test the hierarchical code chunking functionality:

```bash
python test_hierarchical_chunking.py /path/to/your/file.ext
```

### Context Preservation Test

To test context preservation and structural integrity:

```bash
python test_context_preservation.py /path/to/your/file.ext
```

### Dependency Analysis Test

To test dependency analysis and relationship mapping:

```bash
python test_dependency_analysis.py /path/to/your/file.ext
```

### Visualization Test

To test the visualization utilities:

```bash
python test_simple_visualization.py /path/to/your/file.ext
```

### LanceDB Test

To test the LanceDB installation and configuration:

```bash
python test_lancedb.py
```

To clear existing tables and recreate them:

```bash
python test_lancedb.py --clear
```

To specify a custom database path:

```bash
python test_lancedb.py --db-path /path/to/your/database
```

### Embedding Tests

To test the embedding generator:

```bash
python test_embeddings.py
```

To visualize the embeddings:

```bash
python test_embeddings.py --visualize
```

To test embedding code chunks and storing them in the database:

```bash
python test_embed_chunks.py
```

To clear the database before embedding:

```bash
python test_embed_chunks.py --clear-db
```

To use a specific model:

```bash
python test_embed_chunks.py --model microsoft/codebert-base
```

### Database Schema Management

#### LanceDB Version Compatibility

The codebase is designed to work with different versions of LanceDB, but there are some compatibility issues to be aware of:

- **API Differences**:
  - Different versions of LanceDB have different APIs for search
  - Older versions use `search(query_vector, k=limit)`
  - Newer versions use `search(query_vector).limit(limit)`

- **Vector Column Name**:
  - LanceDB expects a specific column name for the vector field
  - Our implementation tries both default and "embedding" as the vector column name

- **Schema Consistency**:
  - It's important to maintain schema consistency when accessing tables
  - Our implementation detects the actual schema and adapts data to fit it

- **Recommended Solution**:
  - Pin the LanceDB version in your requirements.txt (e.g., `lancedb==0.3.3`)
  - Use a consistent schema across all components
  - If upgrading LanceDB, clear and recreate tables to ensure schema consistency

The codebase includes a database utility script for managing the LanceDB database. This script can be used to:

- Open and close database connections
- Clear and recreate tables
- View database information
- Switch between minimal and full schema versions

#### Using the Database Utility Script

To view database information (tables, schemas, row counts):

```bash
python -m codebase_analyser.database.db_utils --info
```

To clear all tables and recreate them with the minimal schema:

```bash
python -m codebase_analyser.database.db_utils --clear
```

To use the full schema (with additional metadata fields):

```bash
python -m codebase_analyser.database.db_utils --full
```

To specify a custom database path:

```bash
python -m codebase_analyser.database.db_utils --db-path /path/to/your/database
```

#### Programmatic Database Management

You can also manage the database programmatically in your Python code:

```python
from codebase_analyser.database import open_db_connection, close_db_connection

# Open a database connection with the minimal schema
db_manager = open_db_connection(db_path=".lancedb", use_minimal_schema=True)

try:
    # Perform database operations
    # ...

    # Clear and recreate tables if needed
    db_manager.clear_tables()

    # Add data to the database
    db_manager.add_code_chunks(code_chunks)
    db_manager.add_dependencies(dependencies)

finally:
    # Always close the connection when done
    close_db_connection(db_manager)
```

### Embedding Generation

The codebase includes functionality for generating embeddings for code chunks using CodeBERT:

#### Embedding Dimensions and Performance Considerations

When working with code embeddings, the dimension size affects both accuracy and performance:

- **Practical Recommendations**:
  - For codebases up to ~1 million lines: 768 dimensions (CodeBERT default) works well
  - For very large codebases (10+ million lines): You might consider dimensionality reduction techniques

- **Dimensionality Reduction Options**:
  - **PCA**: Can reduce to 384-512 dimensions with minimal loss of information
  - **Random Projection**: Fast reduction method that preserves distances well
  - **Autoencoders**: Can learn compressed representations while preserving semantic meaning

- **Storage Impact**:
  - Each embedding with 768 dimensions (using float32) requires ~3KB of storage
  - For 100,000 code chunks: ~300MB for embeddings alone
  - For 1 million code chunks: ~3GB for embeddings

```python
from codebase_analyser.embeddings import EmbeddingGenerator

# Create an embedding generator
generator = EmbeddingGenerator(
    model_name="microsoft/codebert-base",  # Default model
    cache_dir=".cache",                     # Optional cache directory
    batch_size=8                            # Batch size for efficiency
)

# Generate an embedding for a single code snippet
code = "def hello_world():\n    print('Hello, World!')"
embedding = generator.generate_embedding(code, language="python")

# Generate embeddings for multiple code snippets
codes = ["public class Hello {}", "function hello() {}"]
languages = ["java", "javascript"]
embeddings = generator.generate_embeddings_batch(codes, languages)

# Generate embeddings for code chunks and store them in the database
from codebase_analyser.embeddings import embed_and_store_chunks

# Embed and store code chunks
embed_and_store_chunks(
    chunks=code_chunks,
    db_path=".lancedb",
    model_name="microsoft/codebert-base",
    cache_dir=".cache",
    batch_size=8
)

# Embed code chunks from a JSON file
from codebase_analyser.embeddings import embed_chunks_from_file

embed_chunks_from_file(
    file_path="samples/sample_chunks.json",
    db_path=".lancedb",
    model_name="microsoft/codebert-base",
    cache_dir=".cache"
)
```

#### Schema Updates

If you need to update the database schema:

1. Modify the schema definitions in `codebase_analyser/database/schema.py`
2. Clear the existing tables using the utility script
3. The new schema will be applied when the tables are recreated

```bash
# After updating schema.py
python -m codebase_analyser.database.db_utils --clear
```

## Dependency Analysis

The codebase analyser includes a comprehensive dependency analysis system that:

1. **Identifies different types of dependencies**:
   - Inheritance relationships (extends, implements)
   - Method calls
   - Field usage
   - Container relationships
   - Import dependencies

2. **Generates a dependency graph** with:
   - Nodes representing code chunks
   - Edges representing dependencies between chunks
   - Metadata about dependency types, strengths, and locations

3. **Calculates graph-level metrics**:
   - Coupling score (ratio of actual dependencies to possible dependencies)
   - Cohesion score (inverse of the number of connected components)
   - Dependency depth (longest path in the dependency graph)
   - Cyclic dependencies (cycles in the dependency graph)

4. **Calculates chunk-level metrics**:
   - Fan-in (number of incoming dependencies)
   - Fan-out (number of outgoing dependencies)
   - Instability (fan-out / (fan-in + fan-out))
   - Abstractness (ratio of abstract elements)
   - Distance from main sequence (|abstractness + instability - 1|)

This dependency information is valuable for:
- Understanding code structure and relationships
- Identifying areas with high coupling or cyclic dependencies
- Planning refactoring efforts
- Visualizing code architecture

### Optional Metadata Parameters

The following metadata parameters are optional and can be removed to reduce memory usage:

1. **In Dependency Objects**:
   - `locations`: Specific locations of dependencies in the code
   - `description`: Human-readable descriptions of dependencies
   - `is_direct` and `is_required`: Flags for dependency classification

2. **In Dependency Graph**:
   - `cyclic_dependencies`: List of cycles in the dependency graph
   - Detailed edge information can be simplified to just source and target IDs

3. **In Chunk Metadata**:
   - `content`: The actual code content (largest memory consumer)
   - `context`: Full context information can be reduced to essential imports only

### Reducing Memory Usage

To reduce memory usage when working with large codebases, you can:

```python
# 1. Configure the chunker to exclude optional metadata
analyser = CodebaseAnalyser(
    repo_path="/path/to/repo",
    include_locations=False,  # Don't store dependency locations
    include_descriptions=False,  # Don't store dependency descriptions
    simplified_graph=True  # Use simplified dependency graph
)

# 2. Remove content from chunks after analysis
for chunk in chunks:
    # Keep only essential metadata
    if 'dependency_metrics' in chunk.metadata:
        # Keep only the core metrics
        essential_metrics = {
            'fan_in': chunk.metadata['dependency_metrics']['fan_in'],
            'fan_out': chunk.metadata['dependency_metrics']['fan_out'],
            'instability': chunk.metadata['dependency_metrics']['instability']
        }
        chunk.metadata['dependency_metrics'] = essential_metrics

    # Remove the content (largest memory consumer)
    chunk.content = ""

    # Simplify context to just package and essential imports
    if chunk.context:
        simplified_context = {}
        if 'package' in chunk.context:
            simplified_context['package'] = chunk.context['package']
        chunk.context = simplified_context

# 3. Simplify the dependency graph in file chunks
for chunk in chunks:
    if chunk.chunk_type == 'file' and 'dependency_graph' in chunk.metadata:
        graph = chunk.metadata['dependency_graph']

        # Keep only essential node information
        for node in graph['nodes']:
            essential_keys = ['id', 'type', 'name']
            for key in list(node.keys()):
                if key not in essential_keys:
                    del node[key]

        # Keep only essential edge information
        simplified_edges = []
        for edge in graph['edges']:
            simplified_edges.append({
                'source': edge['source_id'],
                'target': edge['target_id'],
                'type': edge['type']
            })
        graph['edges'] = simplified_edges

        # Keep only essential metrics
        essential_metrics = {
            'coupling_score': graph['metrics']['coupling_score'],
            'cohesion_score': graph['metrics']['cohesion_score']
        }
        graph['metrics'] = essential_metrics
```

### Memory Usage Comparison

| Configuration | Memory Usage | Features Preserved |
|---------------|--------------|-------------------|
| Full metadata | High         | All features      |
| No locations  | Medium       | Most features     |
| Essential only| Low          | Core relationships|

Choose the configuration that best balances your memory constraints with your analysis needs.
