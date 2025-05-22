# VS Code Agentic AI Coding Assistant - Project Plan

## Overview
This project aims to develop a VS Code extension that serves as a chat-based AI coding assistant. The assistant will read business requirements from text files, analyze the existing codebase, generate new code using an LLM, and apply the generated code to the codebase using an AI agent.

## Tech Stack
- **Languages**: TypeScript/JavaScript (primary), Python (if necessary)
- **Frameworks & Tools**:
  - LangGraph for agentic AI development
  - Tree-sitter for code parsing
  - LanceDB for vector storage
  - spaCy for natural language processing
  - MCP (Model Context Protocol) for file system operations
- **LLM**: Llama (via OpenRouter)

## Project Tracking

### Current Status
- Implementation started
- Task 1.1.1 completed: Install VS Code Extension development tools
- Task 1.1.2 completed: Create extension project using Yeoman generator
- Task 1.1.3 completed: Set up TypeScript configuration
- Task 1.1.4 completed: Configure extension manifest (package.json)
- Task 1.1.5 completed: Create basic activation function
- Task 1.1.6 completed: Set up chat interface UI components

### Project Structure
```
RepoMind/
├── codebase-analyser/              # Main project directory
│   ├── codebase_analyser/          # Python package (with underscores)
│   │   ├── nlp/                    # NLP module for requirements processing
│   │   ├── rag/                    # RAG module for context retrieval
│   │   ├── synthesis/              # Code synthesis module
│   │   ├── parsing/                # Code parsing module
│   │   ├── database/               # Database integration
│   │   └── ...                     # Other modules
│   ├── scripts/                    # Command-line scripts
│   ├── tests/                      # Test files
│   └── requirements.txt            # Dependencies
├── extension-v1/                   # VS Code extension
└── data/                           # Data directory
    ├── nlp_models/                 # spaCy models
    └── projects/                   # Project-specific data
```

### Considerations
- Focus on simplicity and correctness over scalability
- Modular design for easy extension
- College-level project (proof of concept)
- Human-in-the-loop for dangerous operations

## Epics and Stories

### Epic 1: Project Setup and Infrastructure
**Goal**: Establish the basic project structure and development environment

#### Story 1.1: VS Code Extension Scaffolding
**Description**: Set up the basic VS Code extension structure
**Complexity**: Low
**Dependencies**: None

##### Tasks:
- [x] 1.1.1: Install VS Code Extension development tools
- [x] 1.1.2: Create extension project using Yeoman generator
- [x] 1.1.3: Set up TypeScript configuration
- [x] 1.1.4: Configure extension manifest (package.json)
- [x] 1.1.5: Create basic activation function
- [x] 1.1.6: Set up chat interface UI components

#### Story 1.2: LangGraph Integration Setup
**Description**: Set up LangGraph for agent development
**Complexity**: Medium
**Dependencies**: Story 1.1

##### Tasks:
- [ ] 1.2.1: Install LangGraph dependencies
- [ ] 1.2.2: Create basic agent structure using LangGraph
- [ ] 1.2.3: Set up state management for the agent
- [ ] 1.2.4: Configure basic workflow structure
- [ ] 1.2.5: Implement human-in-the-loop functionality for critical operations

### Epic 2: Codebase Analysis System
**Goal**: Implement the system to analyze and understand the codebase

#### Story 2.1: Tree-sitter Integration
**Description**: Set up Tree-sitter for code parsing
**Complexity**: High
**Dependencies**: Story 1.1

##### Tasks:
- [x] 2.1.1: Install Tree-sitter and language-specific grammars
- [x] 2.1.2: Create parser for extracting functions, classes, and methods
- [x] 2.1.3: Implement context preservation (imports, dependencies)
- [x] 2.1.4: Add error handling for parsing failures
- [x] 2.1.5: Create utility functions for AST traversal

#### Story 2.2: Semantic Code Chunking Implementation
**Description**: Implement AST-aware semantic code chunking
**Complexity**: Medium
**Dependencies**: Story 2.1

##### Tasks:
- [x] 2.2.1: Design semantic chunking algorithm based on AST structure
- [x] 2.2.2: Implement hierarchical chunking (fine-grained and container-level)
- [x] 2.2.3: Ensure structural integrity and context preservation
- [x] 2.2.4: Add metadata for dependency relationships
- [x] 2.2.5: Create visualization utility for chunk hierarchy

#### Story 2.3: Vector Database and Dependency Graph Setup
**Description**: Set up LanceDB for storing code embeddings and dependency graph
**Complexity**: Medium
**Dependencies**: Story 2.2

##### Tasks:
- [x] 2.3.1: Install and configure LanceDB
- [x] 2.3.2: Create schema for code embeddings with metadata
- [x] 2.3.3: Implement embedding generation using CodeBERT
- [x] 2.3.4: Build dependency graph construction
- [x] 2.3.5: Create unified storage for vectors and graph metadata

###### Completed:
- Installed and configured LanceDB for storing code embeddings
- Created comprehensive schema for code chunks and dependency relationships
- Implemented version-compatible database manager with schema validation
- Added robust error handling and logging
- Designed flexible schema with minimal and full versions
- Created test scripts to verify schema functionality
- Implemented embedding generation using CodeBERT
- Added batch processing for efficient embedding generation
- Implemented caching to avoid regenerating embeddings for the same code
- Created utility scripts for embedding code chunks and storing them in the database
- Built dependency graph construction system
- Implemented visualization utilities for dependency graphs
- Created command-line interface for dependency graph operations
- Added database integration for storing and querying dependencies
- Created unified storage for vectors and graph metadata
- Implemented combined search for code by both vector similarity and graph relationships
- Added graph metadata to code chunks for efficient querying
- Created utility functions for working with the unified storage

#### Story 2.4: Relevance Scoring and Testing
**Description**: Implement custom scoring and comprehensive testing
**Complexity**: Medium
**Dependencies**: Story 2.3

##### Tasks:
- [x] 2.4.1: Develop custom relevance scoring combining semantic similarity and graph proximity
- [x] 2.4.2: Create test suite for chunking component
- [x] 2.4.3: Implement tests for embedding generation
- [x] 2.4.4: Design test cases for dependency graph construction
- [x] 2.4.5: Build end-to-end integration tests for the entire codebase analysis system

###### Completed in 2.4.1:
- Implemented weighted scoring formula: final_score = α * semantic_similarity + β * (1 / (1 + graph_distance))
- Added NetworkX integration for graph distance calculations
- Implemented bidirectional path finding for comprehensive graph traversal
- Created methods for building graphs from dependencies and calculating distances
- Added configurable weights for balancing semantic vs. structural relevance
- Created comprehensive test script with different weight configurations
- Verified that graph proximity influences search results as expected

###### Completed in 2.4.2:
- Created test_chunking.py for basic code chunking functionality
- Implemented test_hierarchical_chunking.py for parent-child relationships
- Added test_context_preservation.py to verify context is maintained
- Created visualization and output options for chunk inspection
- Implemented comprehensive validation of chunk properties and metadata

###### Completed in 2.4.3:
- Created test_embeddings.py with sample code in multiple languages
- Implemented test_embed_chunks.py for embedding code chunks
- Added similarity calculation between different code samples
- Implemented visualization options using PCA and t-SNE
- Added batch processing tests for efficient embedding generation

###### Completed in 2.4.4:
- Created test_dependency_analysis.py for dependency analysis
- Implemented test_graph.py for dependency graph construction and visualization
- Added tests for dependency metrics (fan-in, fan-out, instability)
- Implemented tests for graph visualization (PNG, DOT files)
- Added tests for dependency database storage and retrieval

###### Completed in 2.4.5:
- Created test_end_to_end_integration.py for complete system testing
- Implemented full flow from parsing source code to querying results
- Added tests for vector similarity search, dependency-filtered search, and combined scoring
- Created test files in multiple languages (Java, Python, JavaScript)
- Implemented validation of search results and dependency metadata

#### Story 2.5: Enhanced Java Parsing and Multi-File Support
**Description**: Improve Java parsing with granular chunking and better dependency analysis
**Complexity**: High
**Dependencies**: Story 2.2, Story 2.3

##### Tasks:
- [x] 2.5.1: Implement enhanced Java parser with granular chunking
- [x] 2.5.2: Add support for extracting classes, methods, and fields as separate chunks
- [x] 2.5.3: Implement hierarchical structure with parent-child relationships
- [x] 2.5.4: Enhance dependency detection between chunks
- [x] 2.5.5: Create end-to-end service for running the complete analysis pipeline

###### Completed in 2.5:
- Created enhanced Java parser using Tree-sitter for more granular code extraction
- Implemented extraction of classes, methods, and fields as separate chunks
- Added hierarchical structure with parent-child relationships between code elements
- Enhanced dependency detection between chunks (imports, inheritance, method calls)
- Created end-to-end service for running the complete analysis pipeline
- Added support for project-specific context with project_id
- Implemented visualization of dependency graphs
- Added comprehensive documentation in README

### Epic 3: Business Requirements Processing
**Goal**: Implement the system to process and understand business requirements

#### Story 3.1: Natural Language Processing Setup
**Description**: Set up spaCy for processing business requirements
**Complexity**: Medium
**Dependencies**: Story 1.1

##### Tasks:
- [x] 3.1.1: Install and configure spaCy
- [x] 3.1.2: Set up Named Entity Recognition for requirements
- [x] 3.1.3: Implement key component extraction
- [x] 3.1.4: Create utility functions for text processing
- [x] 3.1.5: Add error handling for NLP operations

###### Completed in 3.1.1:
- Added spaCy and related dependencies to requirements.txt
- Created NLP module structure with proper organization
- Implemented model loading and management functionality
- Created setup script for downloading and configuring spaCy models
- Added test script to verify spaCy installation and functionality

###### Completed in 3.1.2:
- Implemented EntityExtractor class for extracting entities from text
- Added support for extracting nouns, technical terms, and actions
- Integrated with spaCy's NER capabilities
- Created entity categorization by type

###### Completed in 3.1.3:
- Implemented ComponentAnalyzer for extracting functional and non-functional requirements
- Added support for extracting constraints and actions
- Created section-based extraction for structured requirements documents
- Implemented pattern matching for requirements identification

###### Completed in 3.1.4:
- Implemented text preprocessing functions
- Created sentence extraction utilities
- Added keyword extraction based on part-of-speech tags
- Implemented code reference cleaning functionality

###### Completed in 3.1.5:
- Added comprehensive error handling in all NLP components
- Implemented graceful fallbacks when processing fails
- Added logging for NLP operations
- Created centralized error handling mechanisms

###### NLP Module Structure:
- `requirements_parser.py`: Main parser for requirements documents
- `entity_recognition.py`: Named Entity Recognition for identifying key entities
- `component_extractor.py`: Extract components like actions, objects, and constraints
- `text_utils.py`: Utility functions for text preprocessing and analysis
- `error_handler.py`: Centralized error handling for NLP operations
- `models/`: Directory for managing spaCy models

###### Implementation Details:
- Use spaCy's pre-trained English models (en_core_web_sm/md/lg)
- Implement custom NER for software engineering concepts
- Create utility functions for text preprocessing and sentence extraction
- Add keyword extraction based on part-of-speech tagging
- Implement error handling with graceful fallbacks

#### Story 3.2: RAG Implementation
**Description**: Implement Retrieval-Augmented Generation for code synthesis
**Complexity**: High
**Dependencies**: Story 2.3, Story 3.1

##### Tasks:
- [x] 3.2.1: Implement Phase 1 - Basic Vector-Based RAG
- [x] 3.2.2: Implement Phase 2 - Graph-Enhanced Single-Hop RAG
- [x] 3.2.3: Implement Phase 3 - Full Multi-Hop Graph RAG
- [x] 3.2.4: Set up context combination mechanism
- [x] 3.2.5: Add combined relevance scoring (semantic + graph proximity)
- [ ] 3.2.6: Integrate Microsoft's GraphRAG library for advanced graph traversal

###### Completed in 3.2.1:
- Implemented VectorSearch class for searching code chunks
- Created basic query builder to convert requirements to search queries
- Implemented context window creation from top K results
- Added basic prompt engineering for code generation
- Implemented TF-IDF scoring for improved relevance

###### Completed in 3.2.2:
- Implemented GraphEnhancer class for graph-enhanced RAG
- Added support for import relationship edges in the dependency graph
- Implemented inheritance relationship edges (extends/implements)
- Created graph expansion to include direct neighbors of search results
- Added weighted scoring combining semantic similarity and graph proximity

###### Completed in 3.2.3:
- Implemented MultiHopRAG class for multi-hop traversal
- Added architectural pattern retrieval as first hop
- Created implementation details retrieval as second hop
- Implemented graph traversal to find related components
- Added context hierarchy preservation
- Created advanced context combination for multi-hop results

###### Completed in 3.2.4:
- Implemented ContextCombiner class for combining context from different sources
- Added support for prioritizing context based on relevance
- Created context window management to handle token limits
- Implemented hierarchical context organization

###### Completed in 3.2.5:
- Implemented RelevanceScorer class for combined scoring
- Added semantic similarity scoring using vector embeddings
- Implemented graph proximity scoring using NetworkX
- Created weighted scoring formula combining both approaches
- Added configurable weights for balancing semantic vs. structural relevance

###### Planned for 3.2.6:
- Integrate Microsoft's GraphRAG library (https://github.com/microsoft/graphrag)
- Implement knowledge graph construction from code chunks using GraphRAG's KnowledgeGraph class
- Use GraphRAG's specialized query understanding components (QueryAnalyzer, QueryPlanner)
- Implement advanced graph traversal algorithms (PageRank, bidirectional search, path-based relevance)
- Use GraphRAG's GraphRetriever for improved context retrieval
- Implement GraphRAG's ReasoningEngine for multi-hop reasoning
- Store generated code in the data folder with project-specific organization
- Integrate with the existing multi-hop RAG system
- Benchmark performance against the current implementation
- Optimize for code-specific retrieval tasks
- Add support for visualizing the knowledge graph

#### Story 3.3: Code Synthesis System
**Description**: Implement system to generate code based on requirements
**Complexity**: High
**Dependencies**: Story 3.2

##### Tasks:
- [x] 3.3.1: Design code synthesis workflow aligned with RAG phases
- [x] 3.3.2: Implement prompt engineering for code generation
- [x] 3.3.3: Create code validation and refinement mechanism
- [x] 3.3.4: Implement output formatting for llm-instructions.txt
- [x] 3.3.5: Add feedback loop for iterative improvement

###### Completed in 3.3.1:
- Implemented CodeSynthesisWorkflow class for end-to-end workflow
- Created modular design with separate components for each phase
- Added support for different RAG types (basic, graph, multi-hop)
- Implemented project-specific context filtering

###### Completed in 3.3.2:
- Created structured prompt templates for code generation
- Added context formatting for optimal LLM understanding
- Implemented requirements formatting for clear instruction
- Added code formatting guidelines in prompts

###### Completed in 3.3.3:
- Implemented code validation mechanisms
- Added syntax checking for generated code
- Created refinement process for improving generated code
- Implemented error handling for validation failures

###### Completed in 3.3.4:
- Created standardized output format for llm-instructions.txt
- Implemented structured sections for requirements, context, and instructions
- Added file path and language specification in output
- Created consistent formatting for code blocks

###### Completed in 3.3.5:
- Implemented feedback loop for iterative improvement
- Added support for refining code based on validation results
- Created mechanism for incorporating user feedback
- Implemented iterative generation process for complex requirements

###### Code Synthesis Workflow:
- Requirements parsing using NLP to extract key components
- Context retrieval using the appropriate RAG phase
- Code generation using retrieved context and requirements
- Validation of generated code against project standards
- Refinement based on validation feedback
- Output formatting for integration with the codebase

#### Story 3.4: SAP Documentation MCP Server
**Description**: Implement MCP server for retrieving SAP documentation on-demand
**Complexity**: Medium
**Dependencies**: Story 3.3, Story 4.1

##### Tasks:
- [ ] 3.4.1: Create SAP documentation indexing system
- [ ] 3.4.2: Implement MCP server for documentation retrieval
- [ ] 3.4.3: Create tool definitions for querying documentation
- [ ] 3.4.4: Integrate with code generation system
- [ ] 3.4.5: Implement caching and optimization

###### Planned for 3.4.1:
- Collect SAP CAP framework documentation from official sources
- Index OData service documentation and best practices
- Create vector embeddings for documentation sections
- Implement metadata extraction for documentation (version, topic, etc.)
- Create a structured database for documentation storage

###### Planned for 3.4.2:
- Implement MCP server with documentation retrieval endpoints
- Create query understanding for documentation requests
- Implement relevance scoring for documentation results
- Add filtering by documentation type and version
- Create API for retrieving documentation snippets

###### Planned for 3.4.3:
- Define tool schema for querying SAP documentation
- Implement tool calling logic in the LLM
- Create structured output format for documentation queries
- Add context-aware tool selection
- Implement error handling for documentation retrieval

###### Planned for 3.4.4:
- Integrate documentation context with code context
- Implement combined relevance scoring
- Create unified context for the LLM
- Add documentation references in generated code
- Implement documentation-aware code generation

###### Planned for 3.4.5:
- Implement caching for frequently accessed documentation
- Create background indexing for new documentation
- Add version control for documentation
- Implement incremental updates for documentation
- Create monitoring for documentation usage

### Epic 4: MCP Implementation
**Goal**: Implement Model Context Protocol for file system operations

#### Story 4.1: MCP Server Implementation
**Description**: Create a filesystem MCP server
**Complexity**: Medium
**Dependencies**: Story 1.2

##### Tasks:
- [ ] 4.1.1: Set up basic MCP server structure
- [ ] 4.1.2: Implement file reading functionality
- [ ] 4.1.3: Create tool definitions for filesystem operations
- [ ] 4.1.4: Add error handling and logging
- [ ] 4.1.5: Implement safety checks for file operations

#### Story 4.2: MCP Client Integration
**Description**: Implement MCP client in the VS Code extension
**Complexity**: Medium
**Dependencies**: Story 1.1, Story 4.1

##### Tasks:
- [ ] 4.2.1: Set up MCP client in the extension
- [ ] 4.2.2: Connect client to the MCP server
- [ ] 4.2.3: Implement tool calling functionality
- [ ] 4.2.4: Add error handling and retry logic
- [ ] 4.2.5: Create utility functions for common operations

### Epic 5: LLM Integration
**Goal**: Integrate LLM capabilities for code generation

#### Story 5.1: Llama Integration via OpenRouter
**Description**: Integrate Llama model through OpenRouter
**Complexity**: Medium
**Dependencies**: Story 1.2

##### Tasks:
- [ ] 5.1.1: Set up OpenRouter API client
- [ ] 5.1.2: Create model configuration for Llama
- [ ] 5.1.3: Implement prompt engineering for code tasks
- [ ] 5.1.4: Add response parsing and handling
- [ ] 5.1.5: Implement error handling for API failures

#### Story 5.2: LLM Abstraction Layer
**Description**: Create an abstraction layer for LLM interchangeability
**Complexity**: Medium
**Dependencies**: Story 5.1

##### Tasks:
- [ ] 5.2.1: Design LLM interface
- [ ] 5.2.2: Implement adapter pattern for different LLMs
- [ ] 5.2.3: Create configuration system for LLM selection
- [ ] 5.2.4: Add OpenAI compatibility layer
- [ ] 5.2.5: Implement caching for LLM responses

### Epic 6: Agent Workflow Implementation
**Goal**: Implement the core agent workflow using LangGraph

#### Story 6.1: Instruction Parser
**Description**: Create functionality to parse LLM instructions
**Complexity**: Medium
**Dependencies**: Story 4.2, Story 5.1

##### Tasks:
- [ ] 6.1.1: Design instruction format for llm-instructions.txt
- [ ] 6.1.2: Implement parsing logic for instructions
- [ ] 6.1.3: Create mapping between instructions and MCP tools
- [ ] 6.1.4: Add validation and error handling
- [ ] 6.1.5: Implement logging for instruction processing

#### Story 6.2: Code Generation Agent
**Description**: Implement agent for generating code based on requirements
**Complexity**: High
**Dependencies**: Story 3.3, Story 6.1

##### Tasks:
- [ ] 6.2.1: Design code generation workflow
- [ ] 6.2.2: Implement code generation nodes in LangGraph
- [ ] 6.2.3: Add context management for code generation
- [ ] 6.2.4: Implement code quality checks
- [ ] 6.2.5: Create feedback mechanism for generation failures

#### Story 6.3: File Operation Agent
**Description**: Implement agent for file operations (create/update/delete)
**Complexity**: Medium
**Dependencies**: Story 6.2

##### Tasks:
- [ ] 6.3.1: Implement file creation functionality
- [ ] 6.3.2: Implement file update functionality
- [ ] 6.3.3: Implement file deletion functionality with human approval
- [ ] 6.3.4: Add safety checks and validation
- [ ] 6.3.5: Create preview mechanism for file changes

### Epic 7: VS Code Integration
**Goal**: Integrate the agent with VS Code features

#### Story 7.1: Command Integration
**Description**: Create VS Code commands for the extension
**Complexity**: Low
**Dependencies**: Story 1.1

##### Tasks:
- [ ] 7.1.1: Implement command to start the agent
- [ ] 7.1.2: Add command to select requirements file
- [ ] 7.1.3: Create command for configuration
- [ ] 7.1.4: Implement help/documentation command
- [ ] 7.1.5: Add command for manual vector database update

#### Story 7.2: Chat Interface Implementation
**Description**: Create chat interface for user interaction
**Complexity**: Medium
**Dependencies**: Story 1.1, Story 5.1

##### Tasks:
- [ ] 7.2.1: Design chat UI components
- [ ] 7.2.2: Implement message display and history
- [ ] 7.2.3: Create input handling for user messages
- [ ] 7.2.4: Add file attachment functionality
- [ ] 7.2.5: Implement response formatting for code snippets

#### Story 7.3: Human-in-the-Loop Integration
**Description**: Implement human approval for critical operations
**Complexity**: Medium
**Dependencies**: Story 6.3, Story 7.2

##### Tasks:
- [ ] 7.3.1: Design approval UI components
- [ ] 7.3.2: Implement notification system for approval requests
- [ ] 7.3.3: Create approval dialog with diff view
- [ ] 7.3.4: Add response handling for approvals/rejections
- [ ] 7.3.5: Implement timeout handling for approval requests

### Epic 8: Multi-Project Support and Incremental Indexing
**Goal**: Enhance the system to support multiple projects and efficient incremental indexing

#### Story 8.1: Change Detection and Incremental Updates
**Description**: Implement detection of codebase changes and incremental updates
**Complexity**: High
**Dependencies**: Story 2.3

##### Tasks:
- [x] 8.1.1: Design file change tracking system
- [x] 8.1.2: Implement content-based change detection
- [x] 8.1.3: Add filtering for relevant changes
- [x] 8.1.4: Create change metadata storage
- [x] 8.1.5: Implement debouncing for frequent changes

###### Completed in 8.1:
- Created FileChangeTracker class that tracks file changes using content hashes
- Implemented content-based change detection using SHA-256 hashing
- Added filtering for relevant file types and patterns
- Created metadata storage for tracking file changes
- Implemented debouncing to avoid processing frequent changes

#### Story 8.2: Automatic Vector Database Updates
**Description**: Implement automatic updates to vector database
**Complexity**: High
**Dependencies**: Story 8.1

##### Tasks:
- [x] 8.2.1: Design update workflow
- [x] 8.2.2: Implement incremental update mechanism
- [x] 8.2.3: Create background update process
- [x] 8.2.4: Add progress indication for updates
- [x] 8.2.5: Implement error recovery for failed updates

###### Completed in 8.2:
- Designed efficient update workflow for incremental changes
- Implemented IncrementalUpdateManager for efficient database updates
- Created background update process with threading support
- Added progress indication for updates in the VS Code extension
- Implemented error recovery and logging for failed updates
- Added performance optimizations for large projects:
  - Parallel file processing using ThreadPoolExecutor
  - Batch insertion of chunks to reduce database overhead
  - Configurable worker count based on CPU cores
  - File filtering based on extensions and skip patterns
  - Optimized deletion of chunks for removed files

#### Story 8.3: Project-Specific Context
**Description**: Implement project-specific context for queries and results
**Complexity**: Medium
**Dependencies**: Story 2.3, Story 3.2

##### Tasks:
- [x] 8.3.1: Update database schema to include project_id field
- [x] 8.3.2: Modify search functions to accept project filter
- [x] 8.3.3: Implement project path capture in VS Code extension
- [x] 8.3.4: Create project ID generation based on normalized path
- [ ] 8.3.5: Add project context to all RAG queries

###### Completed in 8.3:
- Added project_id field to database schema for multi-project support
- Modified search functions to filter by project_id
- Implemented project path capture in VS Code extension
- Created project ID generation based on folder name
- Added project-specific data directory structure for visualizations and exports
- Created API endpoints for accessing project-specific data
- Updated README with instructions for querying by project ID

#### Story 8.4: Multi-Project Management
**Description**: Implement tools for managing multiple projects
**Complexity**: Medium
**Dependencies**: Story 8.3

##### Tasks:
- [ ] 8.4.1: Create project selection UI in VS Code extension
- [ ] 8.4.2: Implement project metadata storage
- [ ] 8.4.3: Add project-specific configuration options
- [ ] 8.4.4: Create project initialization workflow
- [ ] 8.4.5: Implement project status indicators
- [ ] 8.4.6: Check for non java files
- [ ] 8.4.7: Expand to other visualisations such as UML
- [ ] 8.4.8: Implement a checkpoint system

### Epic 9: SAP CAP Java Framework Support
**Goal**: Add support for parsing and analyzing SAP Cloud Application Programming (CAP) Java projects

#### Story 9.1: CAP Java Parser Implementation
**Description**: Implement specialized parser for CAP Java projects
**Complexity**: High
**Dependencies**: Story 2.1, Story 2.2

##### Tasks:
- [ ] 9.1.1: Research CAP Java framework structure and conventions
- [ ] 9.1.2: Implement CAP entity model parser
- [ ] 9.1.3: Create parser for CAP service definitions
- [ ] 9.1.4: Add support for CAP annotations and decorators
- [ ] 9.1.5: Implement CDS (Core Data Services) schema parser

#### Story 9.2: CAP Relationship Detection
**Description**: Implement detection of CAP-specific relationships
**Complexity**: High
**Dependencies**: Story 9.1

##### Tasks:
- [ ] 9.2.1: Implement entity-to-service relationship detection
- [ ] 9.2.2: Create parser for CAP event handlers
- [ ] 9.2.3: Add support for CAP-specific dependency injection
- [ ] 9.2.4: Implement detection of OData service relationships
- [ ] 9.2.5: Create visualization for CAP service architecture

#### Story 9.3: CAP-Specific Chunking and Embeddings
**Description**: Implement specialized chunking and embeddings for CAP projects
**Complexity**: Medium
**Dependencies**: Story 9.1, Story 9.2

##### Tasks:
- [ ] 9.3.1: Design CAP-specific chunking strategy
- [ ] 9.3.2: Implement specialized metadata for CAP chunks
- [ ] 9.3.3: Create CAP-aware embedding generation
- [ ] 9.3.4: Add CAP framework context to embeddings
- [ ] 9.3.5: Implement CAP-specific search optimizations

### Epic 10: Code Change Highlighting and Diff View
**Goal**: Implement a git diff-like visualization for code changes made by the agent

#### Story 10.1: Diff Generation System
**Description**: Create a system to generate diffs between original and modified code
**Complexity**: Medium
**Dependencies**: Story 6.3

##### Tasks:
- [ ] 10.1.1: Implement file content comparison algorithm
- [ ] 10.1.2: Create line-by-line diff generation
- [ ] 10.1.3: Add syntax highlighting for diff output
- [ ] 10.1.4: Implement metadata tracking for change origins
- [ ] 10.1.5: Create unified diff format compatible with VS Code

#### Story 10.2: VS Code Diff View Integration
**Description**: Integrate diff view with VS Code's native diff viewer
**Complexity**: Medium
**Dependencies**: Story 10.1

##### Tasks:
- [ ] 10.2.1: Research VS Code diff view API
- [ ] 10.2.2: Implement diff view provider
- [ ] 10.2.3: Create custom editor for viewing diffs
- [ ] 10.2.4: Add navigation controls for multi-file changes
- [ ] 10.2.5: Implement change acceptance/rejection functionality

#### Story 10.3: Change History and Audit Trail
**Description**: Implement history tracking for changes made by the agent
**Complexity**: Medium
**Dependencies**: Story 10.2

##### Tasks:
- [ ] 10.3.1: Design change history data structure
- [ ] 10.3.2: Implement change logging mechanism
- [ ] 10.3.3: Create UI for browsing change history
- [ ] 10.3.4: Add filtering and search for change history
- [ ] 10.3.5: Implement export functionality for change reports

#### Story 10.4: Real-time Change Preview
**Description**: Create real-time preview of changes before they're applied
**Complexity**: High
**Dependencies**: Story 10.1, Story 7.3

##### Tasks:
- [ ] 10.4.1: Implement in-memory diff generation
- [ ] 10.4.2: Create side-by-side preview component
- [ ] 10.4.3: Add syntax highlighting for preview
- [ ] 10.4.4: Implement interactive edit capability in preview
- [ ] 10.4.5: Create approval workflow with preview integration

### Epic 11: Advanced AI Assistant Capabilities
**Goal**: Enhance the VS Code extension with advanced code understanding and generation capabilities

#### Story 11.1: Knowledge Graph Code Understanding
**Description**: Implement knowledge graph for improved code context
**Complexity**: High
**Dependencies**: Story 2.3, Story 2.4

##### Tasks:
- [ ] 11.1.1: Convert dependency graphs to semantic knowledge graphs
- [ ] 11.1.2: Implement relationship classification beyond syntax
- [ ] 11.1.3: Add inference rules for discovering implicit relationships
- [ ] 11.1.4: Create visualization of code relationships in VS Code
- [ ] 11.1.5: Implement context-aware code navigation using the graph

#### Story 11.2: Enhanced Requirements Processing
**Description**: Improve business requirements understanding
**Complexity**: Medium
**Dependencies**: Story 3.1, Story 3.2

##### Tasks:
- [ ] 11.2.1: Implement custom NER for software requirements
- [ ] 11.2.2: Create requirements-to-code mapping visualization
- [ ] 11.2.3: Add automatic test suggestion from requirements
- [ ] 11.2.4: Implement requirements validation against existing code
- [ ] 11.2.5: Create natural language query interface for requirements

#### Story 11.3: Advanced Code Generation
**Description**: Enhance code generation capabilities
**Complexity**: High
**Dependencies**: Story 3.3, Story 6.2

##### Tasks:
- [ ] 11.3.1: Implement pattern-based code generation
- [ ] 11.3.2: Add style matching for consistent code generation
- [ ] 11.3.3: Create interactive code refinement interface
- [ ] 11.3.4: Implement context-aware code completion
- [ ] 11.3.5: Add explanation generation for complex code

#### Story 11.4: VS Code Extension Enhancements
**Description**: Add advanced features to the VS Code extension
**Complexity**: Medium
**Dependencies**: Story 7.1, Story 7.2

##### Tasks:
- [ ] 11.4.1: Implement real-time code analysis feedback
- [ ] 11.4.2: Add inline code suggestions based on context
- [ ] 11.4.3: Create interactive visualization panel
- [ ] 11.4.4: Implement code review assistant functionality
- [ ] 11.4.5: Add project-specific configuration and customization

## Key Components Reference

### LangGraph Components
- **StateGraph**: For creating the agent workflow with defined states and transitions
- **create_react_agent**: For implementing the ReAct pattern in the agent
- **Human-in-the-loop**: For implementing approval workflows for critical operations
- **MemorySaver**: For maintaining conversation history and context

### Tree-sitter Components
- **Parser**: For parsing code into Abstract Syntax Trees
- **Query**: For extracting specific patterns from the AST
- **Language**: For language-specific grammar definitions

### LanceDB Components
- **connect**: For connecting to the database
- **create_table**: For creating tables to store embeddings
- **Pipeline**: For creating indexing and retrieval pipelines

### spaCy Components
- **NER**: For Named Entity Recognition in requirements
- **Tokenizer**: For breaking text into meaningful tokens
- **Matcher**: For pattern matching in text

### MCP Components
- **MCPClient**: For connecting to the MCP server
- **MCPServer**: For exposing file system operations as tools
- **Tool**: For defining operations that can be performed

### VS Code Extension API
- **WebviewPanel**: For creating the chat interface
- **commands**: For registering extension commands
- **workspace.fs**: For file system operations
- **window.showInformationMessage**: For notifications
- **QuickPickItem**: For selection dialogs
