# RepoMind Codebase Analyser - New Structure

This document outlines the new structure for the codebase analyser project.

## New Directory Structure

```
codebase-analyser/
├── codebase_analyser/           # Main package
│   ├── __init__.py
│   │
│   ├── parsing/                 # Code parsing and chunking
│   │   ├── __init__.py
│   │   ├── analyser.py          # Main analyzer class
│   │   ├── ast_utils.py         # AST utility functions
│   │   ├── code_chunk.py        # Code chunk data model
│   │   ├── chunker.py           # Code chunking logic
│   │   ├── dependency_analyzer.py # Dependency analysis
│   │   ├── dependency_types.py  # Dependency type definitions
│   │   └── java_parser.py       # Java-specific parser
│   │
│   ├── database/                # Database integration
│   │   ├── __init__.py
│   │   ├── lancedb_manager.py   # LanceDB integration
│   │   ├── schema.py            # Database schema definitions
│   │   ├── schema_manager.py    # Schema validation and management
│   │   ├── db_utils.py          # Database utility functions
│   │   └── unified_storage.py   # Unified storage for vectors and graph metadata
│   │
│   ├── embeddings/              # Embedding generation
│   │   ├── __init__.py
│   │   ├── embedding_generator.py # CodeBERT integration
│   │   └── embed_chunks.py      # Embedding utility functions
│   │
│   └── graph/                   # Dependency graph functionality
│       ├── __init__.py
│       ├── dependency_graph_builder.py  # Graph construction
│       ├── visualizer.py        # Graph visualization
│       └── cli.py               # Graph CLI commands
│
├── tests/                       # Test directory
│   ├── __init__.py
│   ├── test_parsing.py          # Tests for parsing and chunking
│   ├── test_java_parser.py      # Tests for Java parser
│   ├── test_ast_utils.py        # Tests for AST utilities
│   ├── test_chunking.py         # Tests for chunking
│   ├── test_hierarchical_chunking.py # Tests for hierarchical chunking
│   ├── test_context_preservation.py # Tests for context preservation
│   ├── test_dependency_analysis.py # Tests for dependency analysis
│   ├── test_database.py         # Tests for database functionality
│   ├── test_schema.py           # Tests for schema
│   ├── test_embeddings.py       # Tests for embedding generation
│   ├── test_embed_chunks.py     # Tests for embedding chunks
│   ├── test_graph.py            # Tests for graph functionality
│   ├── test_visualization.py    # Tests for visualization
│   └── test_unified_storage.py  # Tests for unified storage
│
├── samples/                     # Sample outputs
│   ├── dependency_graph.json
│   ├── dependency_graph.png
│   ├── sample_chunks.json
│   └── sample_dependencies.json
│
├── requirements.txt             # Project dependencies
├── setup.py                     # Package installation script
└── README.md                    # Project README
```

## Import Path Updates

When moving files to the new structure, the following import path updates are needed:

1. In parsing module files:
   - Change `from ..chunking.code_chunk import CodeChunk` to `from .code_chunk import CodeChunk`
   - Change `from ..chunking.dependency_types import DependencyType` to `from .dependency_types import DependencyType`
   - Change `from ..utils.ast_utils import ...` to `from .ast_utils import ...`

2. In other modules:
   - Change `from ..chunking.code_chunk import CodeChunk` to `from ..parsing.code_chunk import CodeChunk`
   - Change `from ..chunking.dependency_types import DependencyType` to `from ..parsing.dependency_types import DependencyType`
   - Change `from ..utils.ast_utils import ...` to `from ..parsing.ast_utils import ...`

3. In test files:
   - Change `from codebase_analyser.chunking import ...` to `from codebase_analyser.parsing import ...`
   - Change `from codebase_analyser.utils import ...` to `from codebase_analyser.parsing import ...`

## Implementation Steps

1. Create the new directory structure
2. Copy files to their new locations
3. Update import paths in all files
4. Update documentation references
5. Run tests to verify the new structure works correctly

## Benefits of the New Structure

1. **Simplified Organization**: Four main modules with clear responsibilities
2. **Better Cohesion**: Related functionality is grouped together
3. **Centralized Testing**: All tests in a dedicated directory
4. **Clearer Dependencies**: More explicit dependencies between modules
5. **Easier Navigation**: Simpler structure makes it easier to find files
