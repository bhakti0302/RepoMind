"""
Filesystem Node for the Merge Code Agent.

This module handles file operations (create, modify, delete) for the Merge Code Agent.
"""

import os
from typing import Dict, List, Optional, Tuple, Any

class FilesystemNode:
    """
    Filesystem Node for the Merge Code Agent.
    
    This class handles file operations (create, modify, delete) for the Merge Code Agent.
    """
    
    def __init__(self, codebase_path: str, llm_node=None):
        """
        Initialize the Filesystem Node.
        
        Args:
            codebase_path: Path to the codebase
            llm_node: LLM Node for file analysis
        """
        self.codebase_path = codebase_path
        self.llm_node = llm_node
        print(f"Filesystem Node initialized with codebase path: {codebase_path}")
    
    def execute_action(self, action: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Execute a file action.
        
        Args:
            action: The action to execute
            
        Returns:
            A tuple of (success, error_message)
        """
        action_type = action.get("action")
        file_path = action.get("file_path")
        
        if not file_path:
            return False, "No file path specified"
        
        if action_type == "create_file":
            return self._create_file(file_path, action.get("content", ""))
        elif action_type == "modify_file":
            instruction = action.get("instruction")
            if instruction:
                return self._modify_file_with_llm(file_path, instruction)
            else:
                # Fall back to the standard modification approach
                target_pattern = action.get("target_pattern")
                return self._modify_file(file_path, action.get("content", ""), target_pattern)
        elif action_type == "delete_file":
            return self._delete_file(file_path)
        else:
            return False, f"Unknown action type: {action_type}"

    def _create_file(self, file_path: str, content: str) -> Tuple[bool, Optional[str]]:
        """
        Create a new file.

        Args:
            file_path: Path to the file
            content: File content (can be a string or a list)

        Returns:
            A tuple of (success, error_message)
        """
        try:
            # Direct file operation
            full_path = os.path.join(self.codebase_path, file_path)

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            # Check if file already exists
            if os.path.exists(full_path):
                return False, f"File already exists: {file_path}"

            # Convert content to string if it's a list
            if isinstance(content, list):
                content = '\n'.join(content)

            # Write the file
            with open(full_path, 'w') as f:
                f.write(content)

            # Display the created file
            print(f"\nCreated file: {file_path}")
            print("=" * 80)
            print(content)
            print("=" * 80)

            return True, None
        
        except Exception as e:
            return False, f"Error creating file: {str(e)}"
            return False, f"Error creating file: {str(e)}"

    def _modify_file(self, file_path: str, content: str, target_pattern: str = None) -> Tuple[bool, Optional[str]]:
        """
        Modify an existing file.

        Args:
            file_path: Path to the file
            content: New content
            target_pattern: Optional pattern to replace (if None, replace the entire file)

        Returns:
            A tuple of (success, error_message)
        """
        try:
            # Direct file operation
            full_path = os.path.join(self.codebase_path, file_path)

            # Check if file exists
            if not os.path.exists(full_path):
                return False, f"File does not exist: {file_path}"

            # Read the current file content
            with open(full_path, 'r') as f:
                current_content = f.read()

            # Modify the content
            if target_pattern:
                # Replace the target pattern with the new content
                if target_pattern not in current_content:
                    return False, f"Target pattern not found: {target_pattern}"
                
                modified_content = current_content.replace(target_pattern, content)
                
                # Display the modification
                print(f"\nModified file: {file_path}")
                print("=" * 80)
                print(f"Replaced: {target_pattern}")
                print("With:")
                print(content)
                print("=" * 80)
            else:
                # Replace the entire file
                modified_content = content
                
                # Display the modification
                print(f"\nReplaced entire file: {file_path}")
                print("=" * 80)
                print(content)
                print("=" * 80)

            # Write the modified content back to the file
            with open(full_path, 'w') as f:
                f.write(modified_content)

            return True, None
        
        except Exception as e:
            return False, f"Error modifying file: {str(e)}"

    def _modify_file_with_llm(self, file_path: str, instruction: str) -> Tuple[bool, Optional[str]]:
        """
        Modify a file using LLM to determine the exact changes needed.
        
        Args:
            file_path: Path to the file to modify
            instruction: The instruction describing the modification
            
        Returns:
            A tuple of (success, error_message)
        """
        try:
            # Get the full path to the file
            full_path = os.path.join(self.codebase_path, file_path)
            
            # Check if file exists
            if not os.path.exists(full_path):
                return False, f"File does not exist: {file_path}"
            
            # Read the current file content
            with open(full_path, 'r') as f:
                current_content = f.read()
            
            # Use the LLM to analyze the file and determine the modifications
            modification = self.llm_node.analyze_file_for_modification(instruction, file_path, current_content)
            
            # Apply the modification based on the LLM's analysis
            modification_type = modification.get("modification_type")
            start_line = modification.get("start_line")
            end_line = modification.get("end_line")
            new_content = modification.get("new_content", "")
            
            # Split the current content into lines
            current_lines = current_content.splitlines()
            
            # Handle line numbers beyond file length
            if start_line > len(current_lines):
                print(f"Line number {start_line} is beyond file length {len(current_lines)}. Using last line instead.")
                start_line = len(current_lines)
            
            # Check if the content already exists
            if self._content_exists(current_content, new_content):
                print("Content already exists in the file. Skipping.")
                return True, None
            
            # Apply the modification
            if modification_type == "add_after_line":
                # Add content after the specified line
                if start_line < 1:
                    return False, f"Invalid line number: {start_line}"
                
                # Determine the indentation of the target line
                target_line = current_lines[start_line - 1] if start_line <= len(current_lines) else ""
                indentation = self._get_indentation(target_line)
                
                # Format the new content with proper indentation
                formatted_content = self._format_content(new_content, indentation, file_path)
                
                # Insert the new content after the specified line
                modified_lines = current_lines.copy()
                modified_lines.insert(start_line, formatted_content)
                
                modified_content = "\n".join(modified_lines)
                
                # Display the modification
                print(f"\nModified file: {file_path}")
                print("=" * 80)
                print(f"Added after line {start_line}:")
                print("-" * 40)
                print(formatted_content)
                print("-" * 40)
                print("=" * 80)
                
            elif modification_type == "add_before_line":
                # Add content before the specified line
                if start_line < 1:
                    return False, f"Invalid line number: {start_line}"
                
                # Determine the indentation of the target line
                target_line = current_lines[start_line - 1] if start_line <= len(current_lines) else ""
                indentation = self._get_indentation(target_line)
                
                # Format the new content with proper indentation
                formatted_content = self._format_content(new_content, indentation, file_path)
                
                # Insert the new content before the specified line
                modified_lines = current_lines.copy()
                modified_lines.insert(start_line - 1, formatted_content)
                
                modified_content = "\n".join(modified_lines)
                
                # Display the modification
                print(f"\nModified file: {file_path}")
                print("=" * 80)
                print(f"Added before line {start_line}:")
                print("-" * 40)
                print(formatted_content)
                print("-" * 40)
                print("=" * 80)
                
            elif modification_type == "replace_lines":
                # Replace the specified lines
                if start_line < 1 or end_line > len(current_lines) or start_line > end_line:
                    return False, f"Invalid line range: {start_line}-{end_line}"
                
                # Determine the indentation of the first line to be replaced
                target_line = current_lines[start_line - 1] if start_line <= len(current_lines) else ""
                indentation = self._get_indentation(target_line)
                
                # Format the new content with proper indentation
                formatted_content = self._format_content(new_content, indentation, file_path)
                
                # Get the lines being replaced
                replaced_lines = "\n".join(current_lines[start_line-1:end_line])
                
                # Replace the specified lines with the new content
                modified_lines = current_lines.copy()
                modified_lines[start_line-1:end_line] = formatted_content.splitlines()
                
                modified_content = "\n".join(modified_lines)
                
                # Display the modification
                print(f"\nModified file: {file_path}")
                print("=" * 80)
                print(f"Replaced lines {start_line}-{end_line}:")
                print("-" * 40)
                print(replaced_lines)
                print("-" * 40)
                print("With:")
                print("-" * 40)
                print(formatted_content)
                print("-" * 40)
                print("=" * 80)
                
            elif modification_type == "delete_lines":
                # Delete the specified lines
                if start_line < 1 or end_line > len(current_lines) or start_line > end_line:
                    return False, f"Invalid line range: {start_line}-{end_line}"
                
                # Get the lines being deleted
                deleted_lines = "\n".join(current_lines[start_line-1:end_line])
                
                # Delete the specified lines
                modified_lines = current_lines.copy()
                del modified_lines[start_line-1:end_line]
                
                modified_content = "\n".join(modified_lines)
                
                # Display the modification
                print(f"\nModified file: {file_path}")
                print("=" * 80)
                print(f"Deleted lines {start_line}-{end_line}:")
                print("-" * 40)
                print(deleted_lines)
                print("-" * 40)
                print("=" * 80)
                
            else:
                return False, f"Unknown modification type: {modification_type}"
            
            # Write the modified content back to the file
            with open(full_path, 'w') as f:
                f.write(modified_content)
            
            return True, None
            
        except Exception as e:
            return False, f"Error modifying file: {str(e)}"

    def _delete_file(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Delete a file.

        Args:
            file_path: Path to the file

        Returns:
            A tuple of (success, error_message)
        """
        try:
            # Direct file operation
            full_path = os.path.join(self.codebase_path, file_path)

            # Check if file exists
            if not os.path.exists(full_path):
                return False, f"File does not exist: {file_path}"

            # Display the deletion
            print(f"\nDeleted file: {file_path}")

            # Delete the file
            os.remove(full_path)

            return True, None
        
        except Exception as e:
            return False, f"Error deleting file: {str(e)}"

    def _get_indentation(self, line: str) -> str:
        """
        Get the indentation of a line.
        
        Args:
            line: The line to analyze
            
        Returns:
            The indentation string
        """
        indentation = ""
        for char in line:
            if char in (' ', '\t'):
                indentation += char
            else:
                break
        return indentation

    def _format_content(self, content: str, base_indentation: str, file_path: str) -> str:
        """
        Format content with proper indentation.
        
        Args:
            content: The content to format
            base_indentation: The base indentation to use
            file_path: The path to the file (used to determine the file type)
            
        Returns:
            The formatted content
        """
        # For Java files, use special formatting
        if file_path.endswith(".java"):
            return self._format_java_code(content, base_indentation)
        
        # For other files, use simple indentation
        formatted_lines = []
        for line in content.splitlines():
            if line.strip():  # If the line is not empty
                formatted_lines.append(base_indentation + line)
            else:
                formatted_lines.append(line)
        
        return "\n".join(formatted_lines)

    def _format_java_code(self, code: str, base_indentation: str) -> str:
        """
        Format Java code with proper indentation.
        
        Args:
            code: The code to format
            base_indentation: The base indentation to use
            
        Returns:
            The formatted code
        """
        # Split the code into lines
        lines = code.splitlines()
        
        # Format the code
        formatted_lines = []
        current_indent = base_indentation
        brace_level = 0
        
        for line in lines:
            # Strip leading and trailing whitespace
            stripped = line.strip()
            
            if not stripped:
                # Empty line, keep it as is
                formatted_lines.append("")
                continue
            
            # Check for opening braces
            if "{" in stripped:
                # This line contains an opening brace
                if stripped.endswith("{"):
                    # The line ends with an opening brace
                    formatted_lines.append(current_indent + stripped)
                    current_indent += "    "  # Add one level of indentation
                    brace_level += 1
                else:
                    # The opening brace is in the middle of the line
                    formatted_lines.append(current_indent + stripped)
                    if stripped.count("{") > stripped.count("}"):
                        # There are more opening braces than closing braces
                        current_indent += "    " * (stripped.count("{") - stripped.count("}"))
                        brace_level += (stripped.count("{") - stripped.count("}"))
            
            # Check for closing braces
            elif "}" in stripped:
                # This line contains a closing brace
                if stripped.startswith("}"):
                    # The line starts with a closing brace
                    current_indent = current_indent[:-4] if len(current_indent) >= 4 else ""  # Remove one level of indentation
                    formatted_lines.append(current_indent + stripped)
                    brace_level -= 1
                else:
                    # The closing brace is in the middle of the line
                    if stripped.count("}") > stripped.count("{"):
                        # There are more closing braces than opening braces
                        current_indent = current_indent[:-4 * (stripped.count("}") - stripped.count("{"))] if len(current_indent) >= 4 * (stripped.count("}") - stripped.count("{")) else ""
                        brace_level -= (stripped.count("}") - stripped.count("{"))
                    formatted_lines.append(current_indent + stripped)
            
            # Regular line
            else:
                formatted_lines.append(current_indent + stripped)
        
        # Join the formatted lines
        return "\n".join(formatted_lines)

    def _content_exists(self, current_content: str, new_content: str) -> bool:
        """
        Check if the new content already exists in the current content.
        
        Args:
            current_content: The current content of the file
            new_content: The new content to add
            
        Returns:
            True if the content already exists, False otherwise
        """
        # Normalize the content by removing whitespace
        normalized_current = self._normalize_content(current_content)
        normalized_new = self._normalize_content(new_content)
        
        # Check if the normalized new content is in the normalized current content
        return normalized_new in normalized_current

    def _normalize_content(self, content: str) -> str:
        """
        Normalize content by removing whitespace.
        
        Args:
            content: The content to normalize
            
        Returns:
            The normalized content
        """
        # Remove all whitespace
        return "".join(content.split())
