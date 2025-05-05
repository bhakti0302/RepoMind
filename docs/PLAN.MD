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
- [ ] 2.1.1: Install Tree-sitter and language-specific grammars
- [ ] 2.1.2: Create parser for extracting functions, classes, and methods
- [ ] 2.1.3: Implement context preservation (imports, dependencies)
- [ ] 2.1.4: Add error handling for parsing failures
- [ ] 2.1.5: Create utility functions for AST traversal

#### Story 2.2: Code Chunking Implementation
**Description**: Implement AST-aware code chunking
**Complexity**: Medium
**Dependencies**: Story 2.1

##### Tasks:
- [ ] 2.2.1: Design chunking algorithm based on AST structure
- [ ] 2.2.2: Implement logic to divide code into 150-300 line chunks
- [ ] 2.2.3: Ensure structural integrity is maintained during chunking
- [ ] 2.2.4: Add metadata to chunks for context preservation
- [ ] 2.2.5: Create utility for chunk visualization/debugging

#### Story 2.3: Vector Database Setup
**Description**: Set up LanceDB for storing code embeddings
**Complexity**: Medium
**Dependencies**: Story 2.2

##### Tasks:
- [ ] 2.3.1: Install and configure LanceDB
- [ ] 2.3.2: Create schema for code embeddings
- [ ] 2.3.3: Implement embedding generation using appropriate model
- [ ] 2.3.4: Set up storage and retrieval functions
- [ ] 2.3.5: Create indexing pipeline for efficient retrieval

### Epic 3: Business Requirements Processing
**Goal**: Implement the system to process and understand business requirements

#### Story 3.1: Natural Language Processing Setup
**Description**: Set up spaCy for processing business requirements
**Complexity**: Medium
**Dependencies**: Story 1.1

##### Tasks:
- [ ] 3.1.1: Install and configure spaCy
- [ ] 3.1.2: Set up Named Entity Recognition for requirements
- [ ] 3.1.3: Implement key component extraction
- [ ] 3.1.4: Create utility functions for text processing
- [ ] 3.1.5: Add error handling for NLP operations

#### Story 3.2: RAG Implementation
**Description**: Implement Retrieval-Augmented Generation for code synthesis
**Complexity**: High
**Dependencies**: Story 2.3, Story 3.1

##### Tasks:
- [ ] 3.2.1: Design multi-hop RAG approach
- [ ] 3.2.2: Implement architectural pattern retrieval
- [ ] 3.2.3: Create implementation details retrieval
- [ ] 3.2.4: Set up context combination mechanism
- [ ] 3.2.5: Add relevance scoring for retrieved content

#### Story 3.3: Code Synthesis System
**Description**: Implement system to generate code based on requirements
**Complexity**: High
**Dependencies**: Story 3.2

##### Tasks:
- [ ] 3.3.1: Design code synthesis workflow
- [ ] 3.3.2: Implement vector database query mechanism
- [ ] 3.3.3: Create dependency graph integration
- [ ] 3.3.4: Set up LLM prompt engineering for code generation
- [ ] 3.3.5: Implement output formatting for llm-instructions.txt

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

### Epic 8: Vector Database Maintenance
**Goal**: Implement system to keep vector database up-to-date

#### Story 8.1: Change Detection
**Description**: Implement detection of codebase changes
**Complexity**: Medium
**Dependencies**: Story 2.3

##### Tasks:
- [ ] 8.1.1: Create file system watcher for code changes
- [ ] 8.1.2: Implement change detection algorithm
- [ ] 8.1.3: Add filtering for relevant changes
- [ ] 8.1.4: Create change metadata storage
- [ ] 8.1.5: Implement debouncing for frequent changes

#### Story 8.2: Automatic Vector Database Updates
**Description**: Implement automatic updates to vector database
**Complexity**: Medium
**Dependencies**: Story 8.1

##### Tasks:
- [ ] 8.2.1: Design update workflow
- [ ] 8.2.2: Implement incremental update mechanism
- [ ] 8.2.3: Create background update process
- [ ] 8.2.4: Add progress indication for updates
- [ ] 8.2.5: Implement error recovery for failed updates

## Iteration Plan

### Iteration 1: Foundation (2 weeks)
- Epic 1: Project Setup and Infrastructure
- Story 4.1: MCP Server Implementation
- Story 5.1: Llama Integration via OpenRouter

### Iteration 2: Codebase Analysis (3 weeks)
- Story 2.1: Tree-sitter Integration
- Story 2.2: Code Chunking Implementation
- Story 2.3: Vector Database Setup
- Story 4.2: MCP Client Integration

### Iteration 3: Requirements Processing (2 weeks)
- Story 3.1: Natural Language Processing Setup
- Story 3.2: RAG Implementation
- Story 3.3: Code Synthesis System
- Story 5.2: LLM Abstraction Layer

### Iteration 4: Agent Implementation (3 weeks)
- Story 6.1: Instruction Parser
- Story 6.2: Code Generation Agent
- Story 6.3: File Operation Agent
- Story 7.3: Human-in-the-Loop Integration

### Iteration 5: VS Code Integration and Refinement (2 weeks)
- Story 7.1: Command Integration
- Story 7.2: Chat Interface Implementation
- Story 8.1: Change Detection
- Story 8.2: Automatic Vector Database Updates

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
