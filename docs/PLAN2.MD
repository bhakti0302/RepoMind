# Epic 3: Business Requirements Processing - Implementation Plan

## Overview
This plan outlines the implementation of Epic 3, which focuses on processing business requirements using natural language processing (NLP), performing vector search and retrieval-augmented generation (RAG) using existing LanceDB data, and generating output via LLM.

## Architecture
The implementation will follow a pipeline architecture with the following components:

1. **Input Processing**: Handle business requirement text files uploaded from the extension UI
2. **NLP Analysis**: Process requirements to extract key components and entities
3. **Vector Search**: Find relevant code chunks based on requirements
4. **RAG Implementation**: Enhance search results with graph-based context
5. **LLM Integration**: Generate output based on requirements and retrieved context
6. **Output Formatting**: Format LLM output and save to a text file

## Project Structure
```
codebase-analyser/
├── nlp-analysis/                     # New module for NLP processing
│   ├── src/                          # Source code
│   │   ├── __init__.py               # Package initialization
│   │   ├── requirements_parser.py    # Parse business requirements
│   │   ├── entity_extractor.py       # Extract entities from requirements
│   │   ├── component_analyzer.py     # Analyze components in requirements
│   │   ├── text_processor.py         # Process and clean text
│   │   ├── utils.py                  # Utility functions
│   │   ├── vector_search.py          # Vector-based search using LanceDB
│   │   ├── rag_implementation.py     # RAG implementation
│   │   └── main.py                   # Main entry point
│   ├── data/                         # Sample data
│   │   └── sample_requirements.txt   # Sample business requirements
│   └── tests/                        # Test files
│       ├── test_requirements_parser.py
│       ├── test_entity_extractor.py
│       └── test_vector_search.py
├── codebase_analyser/                # Existing codebase analysis package
│   ├── database/                     # Database integration
│   │   └── unified_storage.py        # Unified storage for vectors and graph metadata
│   └── ...                           # Other existing modules
└── ...                               # Other existing directories
```

## Implementation Plan

### Phase 1: NLP Analysis Setup (Tasks 3.1.1 to 3.1.5) ✅

#### Task 3.1.1: Install and Configure spaCy ✅
- ✅ Install spaCy and related dependencies
- ✅ Download and configure appropriate spaCy models
- ✅ Create utility functions for model loading and management
- ✅ Implement basic text processing functionality

#### Task 3.1.2: Set up Named Entity Recognition for Requirements ✅
- ✅ Configure spaCy's NER pipeline for software engineering concepts
- ✅ Create custom entity types for software components (e.g., classes, methods, APIs)
- ✅ Implement entity extraction from business requirements
- ✅ Add visualization for extracted entities

#### Task 3.1.3: Implement Key Component Extraction ✅
- ✅ Create component analyzer to identify actions, objects, and constraints
- ✅ Implement extraction of functional requirements
- ✅ Add support for non-functional requirements
- ✅ Create structured representation of requirements

#### Task 3.1.4: Create Utility Functions for Text Processing ✅
- ✅ Implement text preprocessing (tokenization, lemmatization, etc.)
- ✅ Create sentence extraction utilities
- ✅ Add keyword extraction based on part-of-speech tags
- ✅ Implement code reference cleaning functionality

#### Task 3.1.5: Add Error Handling for NLP Operations ✅
- ✅ Implement robust error handling for NLP operations
- ✅ Add fallback mechanisms for failed operations
- ✅ Create logging for NLP processing steps
- ✅ Implement validation for NLP results

### Phase 2: RAG Implementation (Tasks 3.2.1 to 3.2.5) ✅

#### Task 3.2.1: Implement Phase 1 - Basic Vector-Based RAG ✅
- ✅ Create query builder to convert requirements to search queries
- ✅ Implement vector search using existing LanceDB infrastructure
- ✅ Add result filtering and ranking
- ✅ Create context window builder for top K results

#### Task 3.2.2: Implement Phase 2 - Graph-Enhanced Single-Hop RAG ✅
- ✅ Extend vector search with graph relationship awareness
- ✅ Implement neighbor expansion for search results
- ✅ Add relationship-based filtering
- ✅ Create combined scoring mechanism

#### Task 3.2.3: Implement Phase 3 - Full Multi-Hop Graph RAG ✅
- ✅ Implement architectural pattern retrieval as first hop
- ✅ Create implementation details retrieval as second hop
- ✅ Add graph traversal for related components
- ✅ Implement context hierarchy preservation

#### Task 3.2.4: Set up Context Combination Mechanism ✅
- ✅ Create context window builder for multi-hop results
- ✅ Implement context deduplication
- ✅ Add context prioritization based on relevance
- ✅ Create context formatting for LLM consumption

#### Task 3.2.5: Add Combined Relevance Scoring ✅
- ✅ Implement weighted scoring combining semantic similarity and graph proximity
- ✅ Add configurable weights for different result types
- ✅ Create result explanation mechanism
- ✅ Implement result visualization

### Phase 3: Code Synthesis System (Tasks 3.3.1 to 3.3.5) ✅

#### Task 3.3.1: Design Code Synthesis Workflow ✅
- ✅ Create end-to-end workflow for code synthesis
- ✅ Implement pipeline stages and data flow
- ✅ Add configuration options for workflow
- ✅ Create logging and monitoring for workflow execution

#### Task 3.3.2: Implement Prompt Engineering for Code Generation ✅
- ✅ Design prompt templates for code generation
- ✅ Implement dynamic prompt building based on requirements
- ✅ Add context integration into prompts
- ✅ Create few-shot examples for common patterns

#### Task 3.3.3: Create Code Validation and Refinement Mechanism ✅
- ✅ Implement syntax validation for generated code
- ✅ Add style checking against project standards
- ✅ Create refinement prompts for improving code
- ✅ Implement iterative refinement process

#### Task 3.3.4: Implement Output Formatting for llm-instructions.txt ✅
- ✅ Design format for llm-instructions.txt
- ✅ Implement structured output generation
- ✅ Add metadata and explanations to output
- ✅ Create formatting utilities for different output types

#### Task 3.3.5: Add Feedback Loop for Iterative Improvement ✅
- ✅ Implement feedback collection mechanism
- ✅ Create feedback integration into refinement process
- ✅ Add learning from feedback for future generations
- ✅ Implement metrics for measuring improvement

## Integration with VS Code Extension ✅

### File Attachment Handling ✅
- ✅ Implement file attachment button in the chat UI
- ✅ Create handler for uploaded business requirement files
- ✅ Add file validation and preprocessing
- ✅ Implement progress indication for file processing

### Processing Pipeline Integration ✅
- ✅ Create command to trigger requirements processing
- ✅ Implement background processing with progress indication
- ✅ Add notification for completed processing
- ✅ Create error handling and user feedback

### Output Display ✅
- ✅ Implement display of processing results in chat
- ✅ Create formatted view for generated code
- ✅ Add options to save output to file
- ✅ Implement diff view for code changes

## Testing Strategy

### Unit Testing
- Test individual components of the NLP analysis pipeline
- Verify entity extraction and component analysis
- Test vector search and RAG implementation
- Validate LLM prompt building and response parsing

### Integration Testing
- Test end-to-end processing pipeline
- Verify correct integration between NLP, RAG, and LLM components
- Test file attachment and processing workflow
- Validate output generation and formatting

### Performance Testing
- Measure processing time for different requirement sizes
- Test scalability with large codebases
- Optimize vector search and RAG implementation
- Benchmark LLM response times

## Implementation Timeline

### Week 1: NLP Analysis Setup ✅
- ✅ Complete tasks 3.1.1 to 3.1.5
- ✅ Set up basic NLP pipeline
- ✅ Implement entity extraction and component analysis
- ✅ Create utility functions and error handling

### Week 2: RAG Implementation ✅
- ✅ Complete tasks 3.2.1 to 3.2.5
- ✅ Implement vector search
- ✅ Implement graph enhancement
- ✅ Create context combination mechanism
- ✅ Add relevance scoring and result ranking

### Week 3: Code Synthesis System ✅
- ✅ Complete tasks 3.3.1 to 3.3.5
- ✅ Implement prompt engineering and LLM integration
- ✅ Create code validation and refinement
- ✅ Add output formatting and feedback loop

### Week 4: Integration and Testing ✅
- ✅ Integrate with VS Code extension
- ✅ Implement file attachment handling
- ✅ Create end-to-end processing pipeline
- ⏳ Test and optimize the complete system

## Current Progress

### Completed
- ✅ Created the `nlp-analysis` folder structure with src, data, and tests directories
- ✅ Implemented the requirements parser with spaCy integration
- ✅ Created the entity extractor with custom patterns for software engineering concepts
- ✅ Implemented the component analyzer for extracting actions, constraints, and requirements
- ✅ Added text processor for cleaning and normalizing text
- ✅ Created utility functions for file handling, JSON operations, and code identifier extraction
- ✅ Implemented main processing script to tie everything together
- ✅ Added sample business requirements for testing
- ✅ Implemented vector search using the existing LanceDB infrastructure
- ✅ Created relevance scorer for filtering and ranking search results
- ✅ Implemented context builder for creating context windows from search results
- ✅ Created graph enhancer for adding graph-based context to search results
- ✅ Implemented single-hop graph-enhanced RAG
- ✅ Created multi-hop RAG with architectural pattern retrieval
- ✅ Implemented context hierarchy preservation
- ✅ Created context combiner for multi-hop results
- ✅ Implemented context deduplication and prioritization
- ✅ Added combined relevance scoring with configurable weights
- ✅ Implemented result explanation mechanism
- ✅ Created end-to-end code synthesis workflow
- ✅ Implemented prompt engineering for code generation
- ✅ Created code validation and refinement mechanism
- ✅ Implemented output formatting for llm-instructions.txt
- ✅ Added feedback loop for iterative improvement
- ✅ Created file attachment handler for VS Code extension
- ✅ Implemented processing pipeline integration
- ✅ Added output display for processing results
- ✅ Created main VS Code integration module
- ✅ Implemented LLM client for NVIDIA Llama 3.3 Nemotron Super 49B
- ✅ Integrated LLM client with existing pipeline
- ✅ Added LLM output processing and storage
- ✅ Created .env file for configuration
- ✅ Implemented environment variable loader
- ✅ Updated components to use environment variables

### In Progress
- ⏳ Implementing comprehensive testing
- ⏳ Optimizing performance for large codebases

### Next Steps
- Add user feedback collection
- Create documentation for the system
- Implement automated testing
- Deploy the system to production
- Train the team on using the system

## LLM Integration Plan

### Task 5.1: Implement LLM Client for Code Generation ✅
- ✅ Create LLM client module for NVIDIA Llama 3.3 Nemotron Super 49B
- ✅ Implement API authentication and request handling
- ✅ Add prompt formatting specific to the model
- ✅ Implement response parsing and error handling

### Task 5.2: Integrate LLM Client with Existing Pipeline ✅
- ✅ Connect LLM client to code synthesis workflow
- ✅ Add configuration options for model parameters
- ✅ Implement retry mechanism for API failures
- ✅ Create logging for prompt and response tracking

### Task 5.3: Implement Output Processing ✅
- ✅ Store LLM responses in llm-output.txt
- ✅ Add code extraction from LLM responses
- ✅ Implement formatting for extracted code
- ✅ Create diff view between requirements and generated code

### Task 5.4: Add Feedback Mechanism
- Implement user feedback collection for LLM outputs
- Create mechanism to improve prompts based on feedback
- Add tracking for prompt-response quality
- Implement A/B testing for different prompt strategies

### Task 5.5: Implement Environment Variable Configuration ✅
- ✅ Create .env file for storing configuration
- ✅ Implement environment variable loader
- ✅ Update LLM client to use environment variables
- ✅ Update workflow to use environment variables

## Conclusion
This plan outlines the implementation of Epic 3, focusing on processing business requirements, performing vector search and RAG, and generating output via LLM. The implementation follows a pipeline architecture with clear separation of concerns and has been successfully integrated with the VS Code extension for a seamless user experience.

The NLP analysis phase has been completed, with all components for parsing, entity extraction, and component analysis implemented. The RAG implementation phase has been completed, with vector search, graph enhancement, and context building functionality implemented. The Code Synthesis System phase has also been completed, with workflow design, prompt engineering, code validation, output formatting, and feedback loop implemented. The VS Code integration has been completed, with file attachment handling, processing pipeline integration, and output display functionality implemented.

Additionally, we have successfully implemented LLM integration with NVIDIA's Llama 3.3 Nemotron Super 49B model. The LLM client handles API authentication, request handling, response parsing, and error handling. It has been integrated with the existing pipeline to generate code based on the processed requirements and retrieved context. The generated code is stored in llm-output.txt for further processing and review.

The next steps will focus on comprehensive testing, performance optimization, user feedback collection, and documentation creation. The system is now ready for user testing and can be further refined based on feedback.

## Summary of Implementation

We've successfully completed all the major components of Epic 3, including the VS Code Extension integration. Here's a summary of what we've accomplished:

### Completed Phases:

1. **NLP Analysis Setup (Phase 1)** ✅
   - Created the `nlp-analysis` folder structure with src, data, and tests directories
   - Implemented the requirements parser with spaCy integration
   - Created the entity extractor with custom patterns for software engineering concepts
   - Implemented the component analyzer for extracting actions, constraints, and requirements
   - Added text processor for cleaning and normalizing text
   - Created utility functions for file handling, JSON operations, and code identifier extraction

2. **RAG Implementation (Phase 2)** ✅
   - Implemented vector search using the existing LanceDB infrastructure
   - Created relevance scorer for filtering and ranking search results
   - Implemented context builder for creating context windows from search results
   - Created graph enhancer for adding graph-based context to search results
   - Implemented single-hop and multi-hop graph-enhanced RAG
   - Created context combiner for multi-hop results
   - Implemented context deduplication and prioritization
   - Added combined relevance scoring with configurable weights

3. **Code Synthesis System (Phase 3)** ✅
   - Created end-to-end code synthesis workflow
   - Implemented prompt engineering for code generation
   - Created code validation and refinement mechanism
   - Implemented output formatting for llm-instructions.txt
   - Added feedback loop for iterative improvement

4. **VS Code Extension Integration** ✅
   - Created file attachment handler for VS Code extension
   - Implemented processing pipeline integration
   - Added output display for processing results
   - Created main VS Code integration module

5. **LLM Integration** ✅
   - Implemented LLM client for NVIDIA Llama 3.3 Nemotron Super 49B
   - Added API authentication and request handling
   - Integrated LLM client with existing pipeline
   - Implemented retry mechanism for API failures
   - Added logging for prompt and response tracking
   - Stored LLM responses in llm-output.txt
   - Implemented code extraction from LLM responses

### System Capabilities:

The completed system can now:
1. Parse business requirements using NLP techniques
2. Extract relevant entities and components from the requirements
3. Generate search queries based on the extracted information
4. Perform vector search and graph-enhanced RAG to retrieve relevant code
5. Build context windows from the search results
6. Generate prompts for code generation
7. Validate and refine the generated code
8. Format the output for llm-instructions.txt
9. Collect feedback for iterative improvement
10. Handle file attachments in the VS Code extension
11. Process requirements in the background with progress indication
12. Display processing results in the VS Code extension
13. Connect to NVIDIA's Llama 3.3 Nemotron Super 49B model API
14. Generate code based on requirements and context
15. Store generated code in llm-output.txt
16. Handle API errors and implement retry mechanisms
17. Load configuration from .env file
18. Use environment variables for flexible configuration
19. Support command-line overrides for environment variables

The system is now ready for user testing and can be further refined based on feedback.

## End-to-End Testing Through VS Code UI

To test the entire system end-to-end through the VS Code extension UI, follow these steps:

### Prerequisites
1. Ensure your `.env` file is properly configured with your NVIDIA API key:
   ```
   LLM_API_KEY=your_nvidia_api_key_here
   LLM_MODEL_NAME=nvidia/llama-3.3-nemotron-super-49b-v1:free
   OUTPUT_DIR=output
   ```

2. Make sure all dependencies are installed.

3. Ensure the VS Code extension is installed and activated.

### Testing Steps

1. **Launch VS Code**
   - Open VS Code with your project
   - Ensure the extension is active by checking the status bar at the bottom
   - If not active, run the command "RepoMind: Open Chat View" from the command palette (Ctrl+Shift+P)

2. **Prepare a Test Requirements File**
   - A sample requirements file is available at `codebase-analyser/nlp-analysis/data/test/test_requirements.txt`
   - You can also create your own requirements file with clear business requirements for code generation

3. **Use the Attach Button in VS Code UI**
   - Look for the "Attach File" button in the chat UI (below the chat window)
   - Click on it to open the file picker
   - Navigate to and select your requirements file (e.g., `codebase-analyser/nlp-analysis/data/test/test_requirements.txt`)
   - Confirm the selection

4. **Verify File Upload**
   - The UI should show a confirmation message: "Attached file: test_requirements.txt"
   - The system will automatically trigger the code generation process

5. **Monitor the Process**
   - The status bar at the bottom will show "Generating code..."
   - A progress notification will appear showing "Processing requirements..."
   - The chat UI will display progress updates as the system processes the file

6. **Wait for Processing to Complete**
   - The process may take a few minutes depending on the complexity of the requirements
   - The system will:
     - Parse the requirements
     - Retrieve context using RAG
     - Generate code using the LLM
     - Save the output to files

7. **View the Results in the Chat UI**
   - Once processing is complete, the chat UI will display:
     - A success message: "Code generation completed!"
     - A preview of the generated code
     - A link to the full output file

8. **Check the Output Files**
   - Navigate to the output directory: `codebase-analyser/output/`
   - Verify that the following files were created:
     - `llm-instructions.txt`: Contains the prompt sent to the LLM
     - `llm-output.txt`: Contains the generated code
   - Open these files to examine their contents

9. **Validate the Results**
   - Check that the generated code in `llm-output.txt` addresses the requirements
   - Verify that the code is properly formatted and structured
   - Ensure that all necessary components specified in the requirements are included

### Troubleshooting

If you encounter issues during testing:

1. **"Codebase analyser directory not found" Error**
   - Make sure you have opened the correct workspace in VS Code
   - The workspace should either:
     - Contain the `codebase-analyser` directory
     - Be the `codebase-analyser` directory itself
     - Be a subdirectory of the `codebase-analyser` directory
   - Check the directory structure to ensure it matches the expected layout

2. **Python-related Errors**
   - Make sure Python 3 is installed and in your PATH
   - Verify that all required Python packages are installed:
     ```bash
     pip install -r codebase-analyser/requirements.txt
     ```
   - Check that the `vscode_integration.py` file exists at `codebase-analyser/nlp-analysis/src/vscode_integration.py`

3. **LLM API Errors**
   - Ensure your `.env` file is correctly configured with a valid API key:
     ```
     LLM_API_KEY=your_nvidia_api_key_here
     ```
   - Check that the API key has not expired
   - Verify that you have internet connectivity for API calls

4. **File Path Issues**
   - Ensure the input file exists and is readable
   - Verify that the output directory is writable
   - Check for any special characters in file paths that might cause issues

5. **Check the VS Code Output Panel**
   - Open the Output panel (View > Output)
   - Select "RepoMind" from the dropdown
   - Look for error messages or warnings
   - The debug information will show the paths being used

6. **Check the Terminal Output**
   - If you're running the extension in development mode, check the Debug Console
   - Look for Python errors or exceptions
   - The stderr output will provide details about any Python errors

7. **Try the Command-Line Test**
   - If the VS Code extension is not working, try the command-line test script:
     ```bash
     cd codebase-analyser
     python nlp-analysis/test_system.py --input-file nlp-analysis/data/test/test_requirements.txt --output-dir output
     ```
   - This can help isolate whether the issue is with the VS Code extension or the underlying Python code

This end-to-end test validates that the VS Code extension UI correctly integrates with the NLP Analysis Pipeline, from file attachment to LLM output generation.



I want to test a end to end flow of the project. 
1. I want to open the vs code entension and run the sync codebase for the directory.
2. I do not want to run codebase-analyser for the codebase-alayser directore, i want to do it for a separate directory where I want to open the vs code extension. 
3. I want to add a requirements file and generate code from it. 
4. I want to check the output files are generated correctly. 
5. I want to check the output is displayed in the chat ui.
6. 
mkdir ~/test-project-bhakti
cd ~/test-project-bhakti

/Users/bhaktichindhe/Desktop/Project/RepoMind/path/to/codebase-analyser