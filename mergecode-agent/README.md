# Merge Code Agent

A CLI tool that follows instructions from a text file to modify a codebase, using LLM to interpret instructions and execute file operations.

## Features

- Uses LLM to interpret natural language instructions
- Supports creating, modifying, and deleting files
- Intelligent file modification with precise line-based changes
- User approval workflow for safety

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up your API key in a `.env` file:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

```bash
python run_agent.py <instructions_file> <codebase_path>
```

Example:
```bash
python run_agent.py examples/example-instructions.txt examples/test_codebase
```

Or use the demo script:
```bash
./examples/demo.sh
```

## File Structure

- `run_agent.py`: Main entry point
- `llm_node.py`: Handles LLM integration
- `filesystem_node.py`: Handles file operations
- `orchestrator.py`: Orchestrates the workflow
- `utils.py`: Utility functions
