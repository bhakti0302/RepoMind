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

    def parse_instructions(self, instructions: str) -> List[Dict[str, Any]]:
        """
        Parse the instructions and convert them to structured actions.

        Args:
            instructions: The content of the instructions file

        Returns:
            A list of structured actions
        """
        # First, try to parse the instructions directly
        direct_actions = self._direct_parse_instructions(instructions)
        if direct_actions:
            return direct_actions
            
        # If direct parsing fails, split instructions into blocks
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
        
    def _direct_parse_instructions(self, instructions: str) -> List[Dict[str, Any]]:
        """
        Directly parse instructions without splitting into blocks.
        
        Args:
            instructions: The full instructions text
            
        Returns:
            A list of actions, or empty list if parsing fails
        """
        # Look for structured instructions with steps
        if "## Step 1:" in instructions and "## Step 2:" in instructions:
            # Extract file path from backticks
            file_path_match = re.search(r"`([^`]+)`", instructions)
            if not file_path_match:
                return []
                
            file_path = file_path_match.group(1)
            print(f"Found file path in backticks: {file_path}")
            
            # Extract code blocks
            code_blocks = re.findall(r"```(?:\w+)?\n(.*?)```", instructions, re.DOTALL)
            if not code_blocks:
                return []
                
            # Create action to create the file with the code
            return [{
                "action": "create_file",
                "file_path": file_path,
                "content": code_blocks[0]
            }]
            
        return []

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
        
        IMPORTANT GUIDELINES:
        1. Read and understand multi-step instructions as a complete sequence.
        2. When an instruction mentions creating a file at a specific path, use EXACTLY that path.
        3. If subsequent steps refer to adding code to "the file" or "above file", connect this to the previously mentioned file path.
        4. Code blocks following instructions are meant to be added to the most recently mentioned file, not created as separate files.
        5. Instructions that span multiple lines or paragraphs should be treated as a single continuous instruction.
        6. Pay special attention to file paths mentioned in the instructions.
        7. If a file path is enclosed in backticks like `path/to/file.java`, use that exact path.

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

            # Print the raw LLM response
            print("\n" + "="*80)
            print("RAW LLM RESPONSE:")
            print("="*80)
            print(content)
            print("="*80 + "\n")

            # Parse the JSON response
            import re

            # Try to extract JSON from the response
            json_match = re.search(r'({.*})', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = content

            # Parse the JSON
            try:
                # Try to parse the JSON directly
                action = json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {str(e)}")
                # Try to fix common issues with the JSON
                # 1. Replace single quotes with double quotes
                fixed_json = json_str.replace("'", '"')
                # 2. Fix the join method if present
                fixed_json = re.sub(r'\.join\("\n"\)', '', fixed_json)
                # 3. Remove any trailing commas before closing brackets
                fixed_json = re.sub(r',\s*}', '}', fixed_json)
                fixed_json = re.sub(r',\s*]', ']', fixed_json)
                
                try:
                    action = json.loads(fixed_json)
                except json.JSONDecodeError:
                    # If still failing, try to extract just the action, file_path, and content
                    try:
                        # Extract action
                        action_match = re.search(r'"action":\s*"([^"]+)"', json_str)
                        file_path_match = re.search(r'"file_path":\s*"([^"]+)"', json_str)
                        
                        if action_match and file_path_match:
                            action_type = action_match.group(1)
                            file_path = file_path_match.group(1)
                            
                            # Create a basic action
                            action = {
                                "action": action_type,
                                "file_path": file_path
                            }
                            
                            # Try to extract content if it's a create_file action
                            if action_type == "create_file":
                                # Look for content between content: and the end
                                content_match = re.search(r'"content":\s*(\[.*?\]|\{.*?\}|".*?")', json_str, re.DOTALL)
                                if content_match:
                                    content_str = content_match.group(1)
                                    # If it's an array, join the elements
                                    if content_str.startswith('[') and content_str.endswith(']'):
                                        try:
                                            content_array = json.loads(content_str)
                                            action["content"] = "\n".join(content_array)
                                        except:
                                            # Just use the raw content
                                            action["content"] = content_str
                                    else:
                                        action["content"] = content_str.strip('"')
                            
                            # If it's a modify_file action, include the instruction
                            elif action_type == "modify_file":
                                instruction_match = re.search(r'"instruction":\s*"([^"]+)"', json_str)
                                if instruction_match:
                                    action["instruction"] = instruction_match.group(1)
                        else:
                            raise ValueError("Could not extract action and file_path from JSON")
                    except Exception as ex:
                        print(f"Failed to extract action data: {str(ex)}")
                        raise ValueError(f"Could not parse LLM response as JSON: {json_str}")

            # Post-process the actions
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
            print(f"Error calling LLM API: {str(e)}")
            print("ERROR: LLM API call failed")
            raise
            
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
        Analyze a file to determine how to modify it based on an instruction.
        
        Args:
            instruction: The instruction describing the modification
            file_path: Path to the file being modified
            file_content: Current content of the file
            
        Returns:
            A dictionary with modification details including line numbers
        """
        # Count the number of lines in the file
        line_count = file_content.count("\n") + 1
        
        # Find the last closing brace for Java files
        last_brace_line = 0
        if file_path.endswith(".java"):
            lines = file_content.splitlines()
            for i, line in enumerate(lines):
                if "}" in line:
                    last_brace_line = i + 1
        
        # Create the prompt
        prompt = f"""
        You are a code modification assistant. Your task is to analyze a file and determine how to modify it based on an instruction.
        
        The instruction is:
        
        {instruction}
        
        The current content of the file '{file_path}' is:
        
        ```
        {file_content}
        ```
        
        Analyze the file carefully to understand its structure. Then determine:
        1. Exactly what lines need to be modified
        2. How they should be modified (add, replace, delete)
        3. The new content that should be added or used for replacement
        
        IMPORTANT GUIDELINES:
        - When adding a new method to a Java file, add it INSIDE the class, before the last closing brace
        - Count the lines carefully and make sure your line numbers are valid
        - The file has exactly {line_count} lines
        - Line numbers must be between 1 and {line_count} inclusive
        - For Java files, the last line with the closing brace of the class is line {last_brace_line}
        - Maintain proper indentation and code structure
        - Ensure the modification integrates well with the existing code
        
        Return a JSON object with the following fields:
        - modification_type: One of "add_after_line", "add_before_line", "replace_lines", "delete_lines"
        - start_line: The line number where the modification should start (1-based)
        - end_line: The line number where the modification should end (1-based)
        - new_content: The new content to add or replace with
        
        For example:
        {{
            "modification_type": "add_after_line",
            "start_line": 42,
            "end_line": 42,
            "new_content": "System.out.println(\\"Done\\");"
        }}
        
        Or:
        {{
            "modification_type": "replace_lines",
            "start_line": 42,
            "end_line": 45,
            "new_content": "public static void printArray(int[] array) {{\\n    for (int num : array) {{\\n        System.out.print(num + \\" \\");\\n    }}\\n    System.out.println();\\n    System.out.println(\\"Done\\");\\n}}"
        }}
        
        Only include the JSON object in your response, nothing else.
        """
        
        print("\n" + "="*80)
        print("ANALYZING FILE FOR MODIFICATION:")
        print("="*80)
        print(f"Instruction: {instruction}")
        print(f"File: {file_path}")
        print("="*80 + "\n")
        
        try:
            # Prepare the API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Prepare the request data
            data = {
                "messages": [
                    {"role": "system", "content": "You are a code modification assistant that analyzes files and determines how to modify them based on instructions."},
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
            
            # Print the raw LLM response
            print("\n" + "="*80)
            print("RAW LLM RESPONSE:")
            print("="*80)
            print(content)
            print("="*80 + "\n")
            
            # Parse the JSON response
            import re
            
            # Try to extract JSON from the response
            json_match = re.search(r'({.*})', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = content
            
            # Parse the JSON
            modification = json.loads(json_str)
            
            # Print the parsed modification
            print("\n" + "="*80)
            print("PARSED MODIFICATION:")
            print("="*80)
            print(json.dumps(modification, indent=2))
            print("="*80 + "\n")
            
            return modification
        
        except Exception as e:
            print(f"Error analyzing file for modification: {str(e)}")
            raise

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
