# NLP Analysis Pipeline

This module provides a comprehensive NLP analysis pipeline for processing business requirements, retrieving relevant code context using RAG (Retrieval-Augmented Generation), and generating code implementations using LLM technology.

## Overview

The NLP Analysis Pipeline is designed to:

1. Parse business requirements using NLP techniques
2. Extract relevant entities and components from the requirements
3. Retrieve context from the codebase using vector search and graph-enhanced RAG
4. Generate code based on the requirements and context using an LLM
5. Provide the generated code to the user

## Setup

### Prerequisites

- Python 3.8 or higher
- LanceDB for vector storage
- NVIDIA API key for LLM access

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/codebase-analyser.git
   cd codebase-analyser
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root:
   ```
   LLM_API_KEY=your_nvidia_api_key_here
   LLM_MODEL_NAME=nvidia/llama-3.3-nemotron-super-49b-v1:free
   OUTPUT_DIR=output
   ```

## Usage

### Command Line

You can run the pipeline from the command line:

```bash
cd codebase-analyser
python nlp-analysis/src/code_synthesis_workflow.py --input-file path/to/requirements.txt --output-dir output
```

### VS Code Extension

The pipeline is integrated with a VS Code extension for a seamless user experience:

1. Install the VS Code extension
2. Open the RepoMind chat view
3. Click the "Attach File" button and select a requirements file
4. The system will process the file and generate code
5. The generated code will be displayed in the chat view and saved to `output/llm-output.txt`

## Testing

### End-to-End Testing

#### Using the Test Script

The easiest way to test the system is using the provided test script:

```bash
cd codebase-analyser
python nlp-analysis/test_system.py --input-file nlp-analysis/data/test/test_requirements.txt --output-dir output
```

This script will:
1. Load environment variables from the `.env` file
2. Initialize the workflow
3. Process the requirements file
4. Generate code using the LLM
5. Save the output to the specified directory
6. Display a summary of the results

#### Using the VS Code Extension

To test the entire system end-to-end through the VS Code extension UI, follow these steps:

1. **Launch VS Code**
   - Open VS Code with your project
   - Ensure the extension is active

2. **Prepare a Test Requirements File**
   - A sample requirements file is available at `nlp-analysis/data/test/test_requirements.txt`

3. **Use the Attach Button in VS Code UI**
   - Click the "Attach File" button in the chat UI
   - Select the test requirements file

4. **Monitor the Process**
   - The system will process the file and generate code
   - Progress updates will be displayed in the UI

5. **Check the Output Files**
   - Navigate to the `output` directory
   - Verify that `llm-instructions.txt` and `llm-output.txt` were created

For more detailed testing instructions, see `docs/PLAN2.MD`.

### Component Testing

You can test individual components separately:

```bash
# Test the requirements parser
python -m nlp-analysis.src.requirements_parser --input-file data/test/test_requirements.txt

# Test the vector search
python -m nlp-analysis.src.vector_search --query "user authentication system"

# Test the LLM client
python -m nlp-analysis.src.llm_client --prompt "Write a function to validate user credentials"
```

## Architecture

The system follows a modular architecture with the following components:

1. **Requirements Parser**: Analyzes the text using spaCy NLP
2. **Entity Extractor**: Identifies key software engineering concepts
3. **Vector Search**: Finds relevant code chunks in the LanceDB database
4. **Graph Enhancer**: Adds related code through graph relationships
5. **Multi-Hop RAG**: Performs multi-hop traversal for context retrieval
6. **LLM Client**: Connects to NVIDIA's Llama 3.3 Nemotron Super 49B model
7. **Code Synthesis Workflow**: Orchestrates the entire pipeline

## Configuration

The system can be configured through:

1. `.env` file for environment variables
2. Command-line arguments for overrides
3. VS Code extension settings

Key configuration parameters include:
- LLM API key and model name
- Temperature and max tokens for generation
- Database path and output directory
- RAG parameters (number of results, context length)

## Output

The system produces:
1. `llm-instructions.txt`: Contains the prompt sent to the LLM
2. `llm-output.txt`: Contains the generated code

## License

[MIT License](LICENSE)
