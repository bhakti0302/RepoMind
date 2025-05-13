# Merge Code Agent

A CLI tool that follows instructions from a text file to modify a codebase, using LLM to interpret instructions and execute file operations. The agent can create, modify, and delete files based on natural language instructions, making it a powerful tool for automating code changes.

## Features

- Uses LLM to interpret natural language instructions
- Supports creating, modifying, and deleting files
- Intelligent file modification with precise line-based changes
- Proper code formatting and indentation
- Multi-step instruction understanding
- User approval workflow for safety
- Detailed output showing exactly what changes are being made

## Prerequisites

- Python 3.8 or higher
- An OpenAI API key or compatible API (like OpenRouter)
- pip (Python package installer)

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/mergecode-agent.git
   cd mergecode-agent
   ```

2. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your API key**:
   
   Create a `.env` file in the root directory with your API key:
   
   For OpenAI:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```
   
   For OpenRouter:
   ```
   OPENAI_API_KEY=your_openrouter_api_key_here
   OPENAI_API_BASE_URL=https://openrouter.ai/api/v1
   ```

## Usage

### Basic Usage

Run the agent with an instructions file and a target codebase path:

```bash
python run_agent.py <instructions_file> <codebase_path>
```

Example:
```bash
python run_agent.py examples/example-instructions.txt examples/test_codebase
```

### Demo Script

You can also use the included demo script to see the agent in action:

```bash
./examples/demo.sh
```

### Instruction File Format

The instruction file can contain natural language instructions for modifying code. The agent supports both simple instructions and multi-step instructions.

#### Simple Instructions:

```
Add a method to Example.java that calculates the factorial of a number.
```

#### Multi-Step Instructions:

```
# Implementation Instructions

## Step 1: Create a New File
Create a new file at the following path:
`path/to/your/file.java`

## Step 2: Add the Generated Code in the above file

## Generated Code (java class)
```java
public class YourClass {
    // Your code here
}
```
```

## Examples

The `examples` directory contains several example instruction files and a test codebase that you can use to try out the agent:

- `example-instructions.txt`: Simple instructions for modifying files
- `data_processor_req.txt`: Multi-step instructions for creating a new file
- `multi-step-test.txt`: Another example of multi-step instructions

## Advanced Configuration

### Environment Variables

You can configure the agent using the following environment variables in your `.env` file:

- `OPENAI_API_KEY`: Your API key for OpenAI or compatible service
- `OPENAI_API_BASE_URL`: Base URL for the API (default: https://api.openai.com/v1)
- `MODEL_NAME`: Specific model to use with OpenRouter (optional)

### Custom Prompts

The agent uses carefully crafted prompts to guide the LLM in understanding instructions and analyzing files. You can customize these prompts by modifying the `llm_node.py` file.

## Architecture

The Merge Code Agent is built with a modular architecture:

- `run_agent.py`: Main entry point that parses command-line arguments and runs the agent
- `llm_node.py`: Handles all interactions with the LLM, including instruction parsing and file analysis
- `filesystem_node.py`: Handles file operations (create, modify, delete)
- `orchestrator.py`: Orchestrates the workflow between the LLM and filesystem nodes
- `utils.py`: Utility functions used by the other components

## Troubleshooting

### API Key Issues

If you encounter errors related to the API key:
- Make sure your `.env` file is in the correct location
- Check that your API key is valid and has not expired
- Verify that you have sufficient credits/quota for the API

### File Modification Issues

If the agent is not modifying files correctly:
- Check the instruction format to ensure it's clear and specific
- Look at the LLM's analysis output to see how it's interpreting the instructions
- Try breaking down complex instructions into simpler ones

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
