# Merge Code Agent

A CLI tool that follows instructions from a text file to modify a codebase, using LLM to interpret instructions, a Filesystem Node to execute file operations, and LangGraph to orchestrate the workflow.

## Features

- **Natural Language Instructions**: Understands natural language instructions without requiring special formatting
- **Context-Aware Processing**: Analyzes the entire instruction file to understand the context and relationships between different parts
- **Code Snippet Handling**: Properly handles instructions that contain code snippets
- **Duplicate Detection**: Checks for duplicates before applying modifications to avoid adding the same code multiple times
- **Automatic Formatting**: Formats Java files to ensure proper organization and formatting
- **User Approval**: Gets user approval before executing each action

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/merge-code-agent.git
cd merge-code-agent
```

2. Install the dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Usage

```bash
python run_agent.py <instructions_file> <codebase_path>
```

For example:
```bash
python run_agent.py examples/testshreya_modify.txt /path/to/your/codebase/
```

## Instruction File Format

The instruction file should contain natural language instructions for modifying the codebase. For example:

```
Modify the Order.java file in /path/to/your/codebase/ to add shipping functionality.

Add these new fields to the Order class:
private String status = "NEW";
private String deliveryMethod = "STANDARD";
private boolean expressShipping = false;
private Date shippingDate;

Add these new getter and setter methods:
public String getStatus() {
    return status;
}

public void setStatus(String status) {
    this.status = status;
}

...
```

## Architecture

The Merge Code Agent consists of the following components:

1. **LLM Node (`llm_node.py`)**: Handles communication with the LLM API and instruction parsing
2. **Filesystem Node (`filesystem_node.py`)**: Handles file operations (create, modify, delete)
3. **Instruction Workflow (`instruction_workflow.py`)**: Defines the LangGraph workflow for parsing instructions
4. **Run Agent (`run_agent.py`)**: The main entry point that ties everything together

### Workflow

1. The user runs `run_agent.py` with an instructions file and codebase path
2. The script initializes the LLM node and filesystem node
3. The LLM node reads the instructions file and uses LangGraph to parse it:
   - The entire file is sent to the LLM to divide into logical blocks
   - Each block is processed to generate actions
4. The script executes each action with user approval:
   - For each action, it calls the filesystem node's `execute_action` method
   - The filesystem node executes the action (create, modify, or delete a file)
   - For modify actions, it uses the LLM to analyze the file and determine how to modify it
   - After modifying a Java file, it automatically formats it

## License

This project is licensed under the MIT License - see the LICENSE file for details.
