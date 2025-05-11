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

### VS Code Extension
- Interactive chat interface for querying the codebase
- One-click codebase synchronization
- Project-specific context for accurate responses
- File attachment capability for additional context
- Status bar integration for quick access
- Multi-project support with automatic project ID management

### Enhanced Java Parser
- Parses Java files and extracts classes, methods, fields, and their relationships
- Creates CodeChunk objects with proper parent-child relationships
- Stores chunks in the database
- Supports complex Java projects with multiple files and packages

## Quick Start

### Prerequisites
- Python 3.8 or later
- Node.js and npm (for VS Code extension)
- Visual Studio Code

### Installation

1. Set up the codebase analyser:
```bash
cd codebase-analyser
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Set up the VS Code extension:
```bash
cd ../extension-v1
npm install
npm run compile
```

### Primary User Flow: Using the VS Code Extension

The recommended way to use RepoMind is through the VS Code extension:

1. **Open your project in VS Code with the extension**:
```bash
# Navigate to the extension directory
cd extension-v1

# Compile the extension
npm run compile

# Open VS Code with your project and the extension
code --extensionDevelopmentPath=$(pwd) /path/to/your/project
```

2. **Use the extension**:
   - Look for the RepoMind icon in the activity bar
   - Click the "Sync" button to analyze your codebase
   - Wait for the synchronization to complete
   - Use the chat interface to query your codebase

The extension automatically:
- Detects your project folder
- Assigns a project ID based on the folder name
- Runs the codebase analysis
- Populates the database with code chunks and relationships
- Provides a chat interface for querying your codebase

### Alternative: Command-Line Codebase Analysis

For advanced users or testing purposes, you can also run the codebase analyzer directly from the command line. Detailed instructions are available in the [Codebase Analyser README](codebase-analyser/README.md).

The codebase analyzer provides scripts for analyzing codebases:

```bash
cd codebase-analyser
python scripts/run_codebase_analysis.py --repo-path <path_to_repo> [options]
```

For more details and options, see the [Codebase Analyser README](codebase-analyser/README.md).

### Accessing the Vector Database (for RAG Implementation)

The system stores code chunks and their embeddings in a LanceDB database. Here's how to access it for RAG implementation:

#### Direct Python Access (Recommended)

```python
# Import the UnifiedStorage class
from codebase_analyser.database.unified_storage import UnifiedStorage

# Initialize the database connection
db = UnifiedStorage()

# Search for code chunks by project ID
results = db.search_code_chunks(
    query="interface",  # Search query
    limit=10,           # Maximum number of results
    filters={"project_id": "demo"}  # Filter by project ID
)

# Access the dependency graph
graph = db._build_graph_from_dependencies()

# Calculate graph-based relevance
# (For implementing custom relevance scoring combining vector similarity with graph proximity)
import networkx as nx
source_node = "class:MyClass"
target_node = "class:Interface"
if nx.has_path(graph, source_node, target_node):
    path_length = nx.shortest_path_length(graph, source_node, target_node)
    graph_score = 1.0 / (1.0 + path_length)  # Higher score for shorter paths
```

#### Command-Line Examples

```bash
# Navigate to the codebase-analyser directory
cd codebase-analyser

# List all projects in the database
python3 -c "import lancedb; db = lancedb.connect('.lancedb'); table = db.open_table('code_chunks'); print(table.to_arrow().to_pandas()['project_id'].unique())"

# Count chunks for a specific project
python3 -c "import lancedb; db = lancedb.connect('.lancedb'); table = db.open_table('code_chunks'); print(len(table.to_arrow().to_pandas()[table.to_arrow().to_pandas()['project_id'] == 'demo']))"

# Search for chunks containing a specific term
python3 -c "import lancedb; db = lancedb.connect('.lancedb'); table = db.open_table('code_chunks'); results = table.search('class').limit(5).to_pandas(); print(results[['node_id', 'name', 'project_id']])"
```

#### Vector Search Examples

```python
from codebase_analyser.database.unified_storage import UnifiedStorage

# Initialize database
db = UnifiedStorage()

# Simple vector search with project filter
results = db.search_code_chunks(
    query="interface",  # Search query
    limit=10,           # Maximum number of results
    filters={"project_id": "demo2"}  # Filter by project ID
)

# Access the dependency graph
graph = db._build_graph_from_dependencies()

# Print node information
for node_id in graph.nodes():
    print(f"Node: {node_id}, Type: {graph.nodes[node_id].get('type')}")

# Print edge information
for source, target, data in graph.edges(data=True):
    print(f"Edge: {source} -> {target}, Type: {data.get('type')}")
```

### Running the VS Code Extension

To run the VS Code extension:

```bash
# Navigate to the extension directory
cd extension-v1

# Compile the extension
npm run compile

# Run the extension in development mode with your project
code --extensionDevelopmentPath=$(pwd) /path/to/your/project
```

Once VS Code opens with your project:
1. Look for the RepoMind icon in the activity bar
2. Click the "Sync" button to analyze your codebase
3. Wait for the synchronization to complete
4. Use the chat interface to query your codebase

The extension automatically:
- Detects your project folder
- Assigns a project ID based on the folder name
- Runs the codebase analysis
- Populates the database with code chunks and relationships

This is the recommended workflow for most users, as it provides a simple and intuitive interface for analyzing and querying your codebase.

## Testing the VS Code Extension

### Quick Verification Flow

To quickly test that the VS Code extension is working correctly:

1. **Open a Java project with the extension**:
   ```bash
   cd extension-v1
   npm run compile
   code --extensionDevelopmentPath=$(pwd) /path/to/your/java/project
   ```

2. **Synchronize the codebase**:
   - Look for the RepoMind icon in the VS Code activity bar
   - Click the "Sync" button to analyze your codebase
   - Wait for the synchronization to complete

3. **Verify database population**:
   - The database should be populated with chunks from your project
   - You can verify this by checking the LanceDB database:
   ```bash
   cd codebase-analyser
   python -c "import lancedb; db = lancedb.connect('.lancedb'); table = db.open_table('code_chunks'); import pandas as pd; df = table.to_arrow().to_pandas(); print('Project IDs:', df['project_id'].unique()); print('Number of chunks:', len(df))"
   ```

4. **Check the dependency graph**:
   - A visualization of the dependency graph should be generated
   - You can find it at: `data/projects/<project_id>/visualizations/<project_id>_dependency_graph.png`

This simple flow allows you to verify that the extension is correctly analyzing your codebase, populating the database, and generating visualizations.

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
