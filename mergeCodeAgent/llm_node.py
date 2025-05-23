"""
LLM Node for the Merge Code Agent.

This module handles reading the instructions file and converting natural language
instructions into structured actions using an LLM.
"""

from typing import Dict, List, Any, Optional
import os
import pathlib
import requests
import json
import re

from dotenv import load_dotenv

# Load environment variables from .env file
# First try the parent directory (project root)
env_path = pathlib.Path(__file__).parent.parent / '.env'
if not env_path.exists():
    # Then try the services directory
    env_path = pathlib.Path(__file__).parent.parent / 'services' / '.env'
if not env_path.exists():
    # Finally try the current directory
    env_path = pathlib.Path(__file__).parent / '.env'

load_dotenv(dotenv_path=env_path)


class LLMNode:
    """
    LLM Node for parsing instructions and generating structured actions.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LLM Node.

        Args:
            api_key: API key (optional, will use env var if not provided)
        """
        # Get API key from environment variable
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key not provided. "
                "Please provide it as an argument or set the OPENAI_API_KEY environment variable."
            )

        # Get API base URL from environment variable
        self.api_base_url = os.environ.get("OPENAI_API_BASE_URL", "https://api.openai.com/v1")

        # Construct the API URL
        if "openrouter.ai" in self.api_base_url:
            # OpenRouter API endpoint
            self.api_url = "https://openrouter.ai/api/v1/chat/completions"
            self.api_type = "openrouter"
        elif self.api_base_url.endswith("/v1"):
            # Standard OpenAI API endpoint
            self.api_url = f"{self.api_base_url}/chat/completions"
            self.api_type = "openai"
        else:
            # Other API endpoints
            self.api_url = f"{self.api_base_url}/chat/completions"
            self.api_type = "openai"

        print(f"Using API URL: {self.api_url}")
        print(f"API type: {self.api_type}")

    def read_instructions(self, instructions_path: str) -> str:
        """
        Read the instructions file.

        Args:
            instructions_path: Path to the instructions file

        Returns:
            The content of the instructions file
        """
        with open(instructions_path, 'r') as f:
            return f.read()

    def _call_llm_api(self, prompt: str) -> str:
        """
        Call the LLM API with a prompt.

        Args:
            prompt: The prompt to send to the LLM

        Returns:
            The LLM's response
        """
        try:
            # Prepare the API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            # Prepare the request data
            data = {
                "messages": [
                    {"role": "system", "content": "You are a code modification assistant that converts natural language instructions into structured actions."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0,
                "max_tokens": 2000
            }

            # Add model name for OpenRouter
            if self.api_type == "openrouter":
                # Get model name from environment variable
                model_name = os.environ.get("MODEL_NAME", "")
                if model_name:
                    data["model"] = model_name

            # Make the API request
            response = requests.post(self.api_url, headers=headers, json=data)

            # Check if the request was successful
            if response.status_code != 200:
                raise Exception(f"API request failed with status code {response.status_code}: {response.text}")

            # Parse the response
            response_json = response.json()

            # Extract the content from the response
            try:
                # Standard OpenAI API response format
                content = response_json["choices"][0]["message"]["content"]
            except (KeyError, IndexError) as e:
                # Try alternative formats if the standard format fails
                if "response" in response_json:
                    # Some API providers use a different format
                    content = response_json["response"]
                else:
                    # If we can't find the content, raise an error
                    raise ValueError(f"Could not extract content from API response: {response_json}")

            return content

        except Exception as e:
            print(f"Error calling LLM API: {str(e)}")
            print("ERROR: LLM API call failed")
            raise

    def interpret_full_instructions(self, instruction_text: str) -> List[str]:
        """
        Send the entire instructions file to the LLM for initial interpretation.
        The LLM will analyze the file and divide it into logical blocks.

        Args:
            instruction_text: The full instructions as a string

        Returns:
            A list of instruction blocks
        """
        # Create a prompt for the LLM to interpret the full instructions
        prompt = f"""
        You are an expert code modification assistant. Your task is to analyze a set of instructions for modifying code and divide them into logical blocks.

        Here are the instructions:

        ```
        {instruction_text}
        ```

        Please analyze these instructions carefully using natural language processing techniques to understand:
        1. The overall intent and purpose of the instructions
        2. The relationships between different parts of the instructions
        3. Which instructions are related and should be grouped together
        4. The specific code modifications being requested
        5. Any dependencies between different modifications

        IMPORTANT GUIDELINES:
        1. Use natural language understanding to identify logical groupings
        2. Consider the context and relationships between instructions
        3. Group related modifications together, even if they're not explicitly connected
        4. Keep instructions that depend on each other in the same block
        5. Include all necessary context in each block
        6. Preserve exact file paths and code snippets
        7. Maintain the original formatting of code
        8. Do not summarize or abbreviate code
        9. Make each block self-contained and independently executable

        Return a JSON array of instruction blocks. Each block should be a string containing the complete instructions for that task.

        Example response:
        [
          "Create a new file called config.json with the following content: {{...}}",
          "Update the README.md file to include installation instructions"
        ]

        Only include the JSON array in your response, nothing else.
        """

        # Call the LLM API
        print("Analyzing full instructions and dividing into logical blocks...")
        response = self._call_llm_api(prompt)

        try:
            # Parse the JSON response
            blocks = json.loads(response)
            if not isinstance(blocks, list):
                raise ValueError("Expected a list of instruction blocks")

            print(f"Divided instructions into {len(blocks)} logical blocks")
            return blocks
        except Exception as e:
            print(f"Error parsing LLM response: {str(e)}")
            # Try to extract a JSON array from the response
            json_match = re.search(r'\[(.*)\]', response, re.DOTALL)
            if json_match:
                try:
                    blocks_str = f"[{json_match.group(1)}]"
                    blocks = json.loads(blocks_str)
                    print(f"Divided instructions into {len(blocks)} logical blocks")
                    return blocks
                except:
                    pass

            # If all else fails, treat the entire instructions as a single block
            print("Could not parse LLM response, treating instructions as a single block")
            return [instruction_text]

    def parse_instructions(self, instructions: str) -> List[Dict[str, Any]]:
        """
        Parse the instructions and convert them to structured actions.

        Args:
            instructions: The content of the instructions file

        Returns:
            A list of structured actions
        """
        try:
            # First, send the entire instructions file to the LLM for interpretation
            instruction_blocks = self.interpret_full_instructions(instructions)

            # Import the workflow
            from instruction_workflow import create_instruction_workflow, InstructionState

            # Create the workflow
            workflow = create_instruction_workflow(self)

            # Initialize the state
            initial_state = {
                "instruction_text": instructions,
                "instruction_blocks": instruction_blocks,
                "current_block_index": 0,
                "actions": [],
                "context": {}
            }

            # Run the workflow
            print("Using LangGraph workflow for instruction parsing")
            final_state = workflow.invoke(initial_state)

            # Return the actions
            return final_state["actions"]
        except Exception as e:
            print(f"Error using LangGraph workflow: {str(e)}")
            print("Falling back to original instruction parsing method")

            # Split instructions into lines/paragraphs
            instruction_blocks = self._split_instructions(instructions)
            print(f"Split instructions into {len(instruction_blocks)} blocks")

            # Process each instruction block
            actions = []
            for i, block in enumerate(instruction_blocks):
                if not block.strip():
                    continue

                print(f"\nProcessing instruction block {i+1}/{len(instruction_blocks)}")
                print("=" * 80)
                print(block)
                print("=" * 80)

                # Always use the real LLM
                print("Using real LLM API")
                block_actions = self._llm_parse_instruction_block(block)

                actions.extend(block_actions)

            return actions

    def _split_instructions(self, instructions: str) -> List[str]:
        """
        Split instructions into logical blocks for processing.
        This method is more flexible to handle different instruction formats.

        Args:
            instructions: The full instructions text

        Returns:
            List of instruction blocks
        """
        # More flexible approach to split instructions
        blocks = []
        current_block = []

        # Split by lines first
        lines = instructions.split('\n')

        # Common action verbs that might start a new instruction
        action_verbs = [
            "create", "add", "make", "generate",  # Creation verbs
            "modify", "update", "change", "edit", "alter",  # Modification verbs
            "delete", "remove", "erase", "eliminate"  # Deletion verbs
        ]

        # File-related keywords that might indicate a file operation
        file_keywords = ["file", "directory", "folder", "module", "class", "script"]

        for line in lines:
            line_lower = line.strip().lower()

            # Check if this line likely starts a new instruction
            is_new_instruction = False

            # Check for action verbs followed by file keywords
            for verb in action_verbs:
                for keyword in file_keywords:
                    if line_lower.startswith(verb) and keyword in line_lower:
                        is_new_instruction = True
                        break
                if is_new_instruction:
                    break

            # If this looks like a new instruction and we already have content,
            # save the current block and start a new one
            if is_new_instruction and current_block:
                blocks.append('\n'.join(current_block))
                current_block = [line]
            else:
                current_block.append(line)

        # Add the last block if it's not empty
        if current_block:
            blocks.append('\n'.join(current_block))

        # If we couldn't split into multiple blocks, try a simpler approach
        if len(blocks) <= 1 and len(instructions.strip()) > 0:
            # Try splitting by double newlines (paragraphs)
            paragraph_blocks = instructions.split('\n\n')
            if len(paragraph_blocks) > 1:
                return [block.strip() for block in paragraph_blocks if block.strip()]

        return blocks

    def _llm_parse_instruction_block(self, instruction_block: str) -> List[Dict[str, Any]]:
        """
        Use the LLM to parse a single instruction block into structured actions.

        Args:
            instruction_block: A single instruction block

        Returns:
            A list of structured actions for this block
        """
        # Preprocess the instruction block
        preprocessed_instruction = self._preprocess_instruction_block(instruction_block)

        # Prompt template for instruction parsing
        prompt = f"""
        You are a code modification assistant. Your task is to parse natural language instructions
        for modifying a codebase and convert them into structured actions.

        CRITICAL INSTRUCTIONS - YOU MUST FOLLOW THESE EXACTLY:
        1. Use natural language understanding to determine the intent of the instruction
        2. Consider all possible ways the instruction might be phrased
        3. Look for code snippets or complete file content in the instruction
        4. Determine if the instruction is asking for a complete file replacement or specific modifications
        5. For partial modifications, identify the exact location and type of change needed
        6. Ensure the changes maintain code structure and formatting
        7. Only include code that is explicitly mentioned or clearly implied by the instruction
        8. Do not add any additional functionality or code that wasn't requested

        IMPORTANT GUIDELINES:
        1. Read and understand multi-step instructions as a complete sequence
        2. When an instruction mentions a file path, use exactly that path
        3. If subsequent steps refer to "the file" or similar, connect this to the previously mentioned file path
        4. Code blocks following instructions are meant to be added to the most recently mentioned file
        5. Instructions that span multiple lines or paragraphs should be treated as a single continuous instruction
        6. Pay special attention to file paths mentioned in the instructions
        7. If a file path is enclosed in backticks like `path/to/file.java`, use that exact path

        The instruction is:

        ```
        {preprocessed_instruction}
        ```

        Analyze the instruction carefully to understand what file operation is being requested.
        Instructions can be phrased in many different ways, so use your understanding of natural language
        to determine the intent.

        For file operations, determine the appropriate action type:
        - create_file: When a new file needs to be created
        - modify_file: When an existing file needs to be changed
        - delete_file: When a file needs to be removed

        For modify_file actions, include the original instruction so that the file can be analyzed
        to determine the exact changes needed.

        Based on your analysis, structure your response as a JSON object with these possible fields:
        - action: Required. The type of action (create_file, modify_file, delete_file)
        - file_path: Required. The path to the file
        - content: The content to write (for create_file)
        - instruction: For modify_file actions, include the original instruction for file analysis

        Examples of how to interpret different instructions:

        1. "Create a new file called config.json with the following content: {...}"
           {{
             "action": "create_file",
             "file_path": "config.json",
             "content": "{{...}}"
           }}

        2. "Update the README.md file to include installation instructions"
           {{
             "action": "modify_file",
             "file_path": "README.md",
             "instruction": "Update the README.md file to include installation instructions"
           }}

        3. "In the App.java file, modify the printMessage method to add a 'Done' message"
           {{
             "action": "modify_file",
             "file_path": "App.java",
             "instruction": "In the App.java file, modify the printMessage method to add a 'Done' message"
           }}

        4. "Delete the old-config.yaml file"
           {{
             "action": "delete_file",
             "file_path": "old-config.yaml"
           }}

        Use your best judgment to interpret the instruction and provide the most appropriate structured action.
        Only include the JSON object in your response, nothing else.
        """

        # Print the instruction block being sent to the LLM
        print("\n" + "="*80)
        print("INSTRUCTION BLOCK SENT TO LLM:")
        print("="*80)
        print(preprocessed_instruction)
        print("="*80 + "\n")

        # Call the LLM API
        print(f"Calling LLM API")
        content = self._call_llm_api(prompt)

        # Print the raw LLM response
        print("\n" + "="*80)
        print("RAW LLM RESPONSE:")
        print("="*80)
        print(content)
        print("="*80 + "\n")

        # Parse the JSON response
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'({.*})', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = content

            # Parse the JSON
            action = json.loads(json_str)

            # Post-process the action
            action = self._postprocess_actions([action], instruction_block)[0]

            # Print the parsed action
            print("\n" + "="*80)
            print("PARSED ACTION:")
            print("="*80)
            print(json.dumps(action, indent=2))
            print("="*80 + "\n")

            # Ensure it's in a list
            if isinstance(action, dict):
                return [action]
            elif isinstance(action, list):
                return action
            else:
                raise ValueError(f"Unexpected response format: {type(action)}")

        except Exception as e:
            print(f"Error parsing LLM response: {str(e)}")
            print("ERROR: LLM response parsing failed")
            raise

    def _preprocess_instruction_block(self, instruction_block: str) -> str:
        """
        Preprocess an instruction block to improve LLM understanding.

        Args:
            instruction_block: The instruction block to preprocess

        Returns:
            The preprocessed instruction block
        """
        # Extract file paths from common patterns
        file_path_patterns = [
            r"Create a (?:new )?file (?:at|called|named) ['\"]?([\w\/\.\-]+)['\"]?",
            r"Create ['\"]?([\w\/\.\-]+)['\"]?",
            r"Add (?:to|in) ['\"]?([\w\/\.\-]+)['\"]?",
            r"Modify ['\"]?([\w\/\.\-]+)['\"]?"
        ]

        file_paths = []
        for pattern in file_path_patterns:
            matches = re.finditer(pattern, instruction_block, re.IGNORECASE)
            for match in matches:
                file_paths.append(match.group(1))

        # Look for file paths in backticks
        backtick_matches = re.finditer(r"`([^`]+)`", instruction_block)
        for match in backtick_matches:
            path = match.group(1)
            if "/" in path or "." in path:  # Likely a file path
                file_paths.append(path)

        # If file paths were found, add a summary at the beginning
        if file_paths:
            summary = "DETECTED FILE PATHS:\n"
            for i, path in enumerate(file_paths, 1):
                summary += f"{i}. {path}\n"

            instruction_block = summary + "\n" + instruction_block

        # Look for code blocks and connect them to file paths
        code_blocks = re.findall(r"```(?:\w+)?\n(.*?)```", instruction_block, re.DOTALL)
        if code_blocks and file_paths:
            summary = "\nCODE BLOCKS SHOULD BE ADDED TO THE MENTIONED FILES, NOT CREATED AS SEPARATE FILES.\n"
            instruction_block = instruction_block + summary

        return instruction_block

    def _postprocess_actions(self, actions: List[Dict[str, Any]], instruction_block: str) -> List[Dict[str, Any]]:
        """
        Postprocess actions to correct common issues.

        Args:
            actions: The actions returned by the LLM
            instruction_block: The original instruction block

        Returns:
            The corrected actions
        """
        # Extract file paths from common patterns
        file_path_patterns = [
            r"Create a (?:new )?file (?:at|called|named) ['\"]?([\w\/\.\-]+)['\"]?",
            r"Create ['\"]?([\w\/\.\-]+)['\"]?",
            r"Add (?:to|in) ['\"]?([\w\/\.\-]+)['\"]?",
            r"Modify ['\"]?([\w\/\.\-]+)['\"]?"
        ]

        file_paths = []
        for pattern in file_path_patterns:
            matches = re.finditer(pattern, instruction_block, re.IGNORECASE)
            for match in matches:
                file_paths.append(match.group(1))

        # Look for file paths in backticks
        backtick_matches = re.finditer(r"`([^`]+)`", instruction_block)
        for match in backtick_matches:
            path = match.group(1)
            if "/" in path or "." in path:  # Likely a file path
                file_paths.append(path)

        # If we have file paths from the instruction but the LLM used generic paths
        if file_paths and actions:
            generic_paths = ["new_file.txt", "file.txt", "code.txt", "output.txt", "a"]

            for action in actions:
                if action.get("file_path") in generic_paths and file_paths:
                    # Replace generic path with the first extracted path
                    print(f"Replacing generic path '{action.get('file_path')}' with '{file_paths[0]}'")
                    action["file_path"] = file_paths[0]
                    # Remove this path from the list so we don't reuse it
                    file_paths.pop(0)

        # Check for code blocks that should be added to files
        code_blocks = re.findall(r"```(?:\w+)?\n(.*?)```", instruction_block, re.DOTALL)

        # If we have create_file actions without content but code blocks exist
        for action in actions:
            if action.get("action") == "create_file" and not action.get("content") and code_blocks:
                # Use the first code block as content
                print(f"Adding code block to create_file action for '{action.get('file_path')}'")
                action["content"] = code_blocks[0]
                # Remove this code block from the list so we don't reuse it
                code_blocks.pop(0)

        return actions

    def analyze_file_for_modification(self, instruction: str, file_path: str, file_content: str) -> Dict[str, Any]:
        """
        Analyze a file to determine how to modify it based on the instruction.

        Args:
            instruction: The instruction for modifying the file
            file_path: Path to the file
            file_content: Current content of the file

        Returns:
            A dictionary containing the modification details
        """
        # Analyze the file to determine how to modify it
        prompt = f"""
        You are an expert code modification assistant. Your task is to analyze a file and determine how to modify it based on the given instruction.

        File Path: {file_path}
        Current Content:
        ```
        {file_content}
        ```

        Instruction:
        ```
        {instruction}
        ```

        Please analyze the file and determine the appropriate modifications. If the instruction involves adding a method, ensure it is placed at the appropriate location (e.g., imports at the top, declarations at the top, methods in the appropriate class).

        Return a JSON object with the following structure:
        {{
            "modification_type": "replace_file",
            "new_content": "The complete new content of the file after modifications"
        }}

        Only include the JSON object in your response, nothing else.
        """

        # Call the LLM API
        response = self._call_llm_api(prompt)

        # Parse the response
        try:
            modification = json.loads(response)
            return modification
        except json.JSONDecodeError:
            raise ValueError(f"Could not parse LLM response as JSON: {response}")

    def _show_git_diff(self, file_path: str, old_content: str, new_content: str) -> str:
        """
        Show a git-style diff of the changes in the actual repository with colored output.

        Args:
            file_path: Path to the file
            old_content: Old content of the file
            new_content: New content of the file

        Returns:
            The diff output as a string, or empty string if no changes
        """
        import tempfile
        import subprocess
        import os
        import re

        # Get the repository root directory
        repo_root = self.codebase_path

        # Create a temporary file for the new content
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write(new_content)
            temp_file_path = temp_file.name

        # Stage the changes in git
        subprocess.run(["git", "add", file_path], cwd=repo_root, check=True)

        # Run git diff to show the staged changes
        diff_output = subprocess.run(["git", "diff", "--cached"], cwd=repo_root, capture_output=True, text=True).stdout

        # Restore the original file content
        with open(file_path, 'w') as f:
            f.write(old_content)

        # Clean up the temporary file
        os.unlink(temp_file_path)

        # Highlight added lines in green
        diff_lines = diff_output.splitlines()
        highlighted_diff = []
        for line in diff_lines:
            if line.startswith('+'):
                highlighted_diff.append(f"\033[92m{line}\033[0m")  # Green for added lines
            elif line.startswith('-'):
                highlighted_diff.append(f"\033[91m{line}\033[0m")  # Red for removed lines
            else:
                highlighted_diff.append(line)

        return '\n'.join(highlighted_diff)

    def process_instructions(self, instructions_path: str) -> List[Dict[str, Any]]:
        """
        Process the instructions file and return structured actions.

        Args:
            instructions_path: Path to the instructions file

        Returns:
            A list of structured actions
        """
        instructions = self.read_instructions(instructions_path)
        return self.parse_instructions(instructions)

    def analyze_instruction_block(self, instruction_block: str) -> dict:
        """
        Analyze a single instruction block and return a structured action.
        """
        # Let the LLM handle the parsing logic entirely
        return self._llm_parse_instruction_block(instruction_block)[0]
