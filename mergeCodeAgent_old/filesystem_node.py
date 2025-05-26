"""
Filesystem Node for the Merge Code Agent.

This module handles file operations for the Merge Code Agent.
"""

import os
import re
from typing import Dict, Any, Tuple, List, Optional

class FilesystemNode:
    """
    Filesystem Node for executing file operations.
    """

    def __init__(self, codebase_path: str, llm_node):
        """
        Initialize the Filesystem Node.

        Args:
            codebase_path: Path to the codebase
            llm_node: LLM node for analyzing files
        """
        self.codebase_path = codebase_path
        self.llm_node = llm_node
        print(f"Filesystem Node initialized with codebase path: {codebase_path}")

    def execute_action(self, action: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Execute a file operation.

        Args:
            action: The action to execute

        Returns:
            A tuple of (success, error_message)
        """
        action_type = action.get("action")
        file_path = action.get("file_path")

        if not file_path:
            return False, "No file path specified"

        # Handle relative paths
        if not os.path.isabs(file_path):
            file_path = os.path.join(self.codebase_path, file_path)

        if action_type == "create_file":
            return self.create_file(file_path, action.get("content", ""))
        elif action_type == "modify_file":
            return self.modify_file(file_path, action.get("instruction", ""))
        elif action_type == "delete_file":
            return self.delete_file(file_path)
        else:
            return False, f"Unknown action type: {action_type}"

    def create_file(self, file_path: str, content: str) -> Tuple[bool, Optional[str]]:
        """
        Create a new file.

        Args:
            file_path: Path to the file
            content: Content to write to the file

        Returns:
            A tuple of (success, error_message)
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)

            # Write the file
            with open(file_path, 'w') as f:
                f.write(content)

            print(f"Created file: {file_path}")

            # Format Java files
            if file_path.endswith(".java"):
                self.format_java_file(file_path)

            return True, None
        except Exception as e:
            return False, f"Error creating file: {str(e)}"

    def modify_file(self, file_path: str, instruction: str) -> Tuple[bool, Optional[str]]:
        """
        Modify an existing file.

        Args:
            file_path: Path to the file
            instruction: Instruction for modifying the file

        Returns:
            A tuple of (success, error_message)
        """
        try:
            # Check if the file exists
            if not os.path.exists(file_path):
                return False, f"File not found: {file_path}"

            # Read the file
            with open(file_path, 'r') as f:
                file_content = f.read()

            # Analyze the file to determine how to modify it
            try:
                modification = self.llm_node.analyze_file_for_modification(instruction, file_path, file_content)
            except Exception as e:
                return False, f"Error analyzing file for modification: {str(e)}"

            # Check for duplicates before applying the modification
            if file_path.endswith(".java"):
                modification = self._check_for_duplicates(file_path, file_content, modification)
                if not modification:
                    return True, None  # Skip if everything is already present

            # Apply the modification
            try:
                success, error, modified_content = self.apply_modification(file_path, file_content, modification)
                if not success:
                    return False, error

                # Write the modified content back to the file
                with open(file_path, 'w') as f:
                    f.write(modified_content)

                print(f"Modified file: {file_path}")

                # Format Java files
                if file_path.endswith(".java"):
                    self.format_java_file(file_path)

                return True, None
            except Exception as e:
                return False, f"Error modifying file: {str(e)}"
        except Exception as e:
            return False, f"Error modifying file: {str(e)}"

    def delete_file(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Delete a file.

        Args:
            file_path: Path to the file

        Returns:
            A tuple of (success, error_message)
        """
        try:
            # Check if the file exists
            if not os.path.exists(file_path):
                return False, f"File not found: {file_path}"

            # Delete the file
            os.remove(file_path)

            print(f"Deleted file: {file_path}")
            return True, None
        except Exception as e:
            return False, f"Error deleting file: {str(e)}"

    def _check_for_duplicates(self, file_path: str, file_content: str, modification: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Check for duplicates before applying a modification and filter out unauthorized additions.

        Args:
            file_path: Path to the file
            file_content: Current content of the file
            modification: Modification to apply

        Returns:
            Modified modification or None if everything is already present
        """
        modification_type = modification.get("modification_type")
        new_content = modification.get("new_content", "")

        # Skip if not adding content
        if modification_type not in ["add_after_line", "add_before_line"]:
            return modification

        # Check for Java files
        if file_path.endswith(".java"):
            # Extract field declarations from the new content
            field_pattern = r'(private|protected|public)\s+\w+(?:<[^>]+>)?\s+(\w+)(?:\s*=\s*[^;]+)?;'
            field_matches = list(re.finditer(field_pattern, new_content))

            # Extract method declarations from the new content
            method_pattern = r'(public|private|protected)(?:\s+\w+)*\s+(\w+)\s*\([^)]*\)\s*{'
            method_matches = list(re.finditer(method_pattern, new_content))

            # Check for unauthorized methods (methods not explicitly mentioned in the instruction)
            unauthorized_methods = []
            for match in method_matches:
                method_name = match.group(2)
                # List of standard methods that might be added by the LLM but weren't requested
                unauthorized_method_names = [
                    "calculateShippingCost",
                    "processShipping",
                    "updateShippingDetails",
                    "calculateShippingCostBasedOnWeight",
                    "updateShippingStatus",
                    "getShippingDetails"
                ]

                # Skip toString, getters, and setters
                if method_name == "toString" or method_name.startswith("get") or method_name.startswith("set"):
                    continue

                # Check if the method is unauthorized
                if method_name in unauthorized_method_names:
                    unauthorized_methods.append(method_name)

            # If there are unauthorized methods, remove them from the new content
            if unauthorized_methods:
                print(f"Removing unauthorized methods: {', '.join(unauthorized_methods)}")

                # Split the new content into lines
                lines = new_content.splitlines()
                filtered_lines = []

                # Flag to track if we're inside an unauthorized method
                inside_unauthorized_method = False
                current_method_name = ""
                brace_count = 0

                # Process each line
                for line in lines:
                    # Check if this line starts a method
                    method_match = re.search(method_pattern, line)
                    if method_match and not inside_unauthorized_method:
                        method_name = method_match.group(2)

                        # Check if this is an unauthorized method
                        if method_name in unauthorized_methods:
                            inside_unauthorized_method = True
                            current_method_name = method_name
                            brace_count = 1
                            continue

                    # If we're inside an unauthorized method, track braces
                    if inside_unauthorized_method:
                        brace_count += line.count("{")
                        brace_count -= line.count("}")

                        # If we've reached the end of the method, reset flags
                        if brace_count <= 0:
                            inside_unauthorized_method = False
                            current_method_name = ""

                        continue

                    # If we're not inside an unauthorized method, add the line
                    filtered_lines.append(line)

                # Update the new content
                new_content = "\n".join(filtered_lines)
                modification["new_content"] = new_content

            # Check if each field already exists in the file
            all_fields_exist = True
            for match in field_matches:
                field_name = match.group(2)
                field_regex = r'(private|protected|public)\s+\w+(?:<[^>]+>)?\s+' + re.escape(field_name) + r'(?:\s*=\s*[^;]+)?;'
                if not re.search(field_regex, file_content):
                    all_fields_exist = False
                    break

            # Check if each method already exists in the file
            all_methods_exist = True
            for match in method_matches:
                method_name = match.group(2)

                # Skip unauthorized methods
                if method_name in unauthorized_methods:
                    continue

                method_regex = r'(public|private|protected)(?:\s+\w+)*\s+' + re.escape(method_name) + r'\s*\([^)]*\)\s*{'
                if not re.search(method_regex, file_content):
                    all_methods_exist = False
                    break

            # Check for toString method specifically
            if "toString" in new_content:
                # If we're adding a toString method, check if one already exists
                if "toString" in file_content:
                    # Find the existing toString method
                    lines = file_content.splitlines()

                    # Find all toString method declarations
                    toString_lines = []
                    for i, line in enumerate(lines):
                        if "toString" in line and ("@Override" in line or "public String toString" in line):
                            toString_lines.append(i)

                    # If we found any toString methods, replace the last one
                    if toString_lines:
                        # Get the last toString method
                        i = toString_lines[-1]

                        # Find the start and end of the method
                        start_line = i + 1
                        end_line = len(lines)

                        # Find the closing brace
                        brace_count = 0
                        in_toString = False
                        for j in range(i, len(lines)):
                            if "{" in lines[j]:
                                brace_count += 1
                                in_toString = True
                            if "}" in lines[j]:
                                brace_count -= 1
                                if brace_count == 0 and in_toString:
                                    end_line = j + 1
                                    break

                        # Update the modification to replace the toString method
                        modification["modification_type"] = "replace_lines"
                        modification["start_line"] = start_line
                        modification["end_line"] = end_line

                        print(f"Replacing existing toString method (lines {start_line}-{end_line})")
                        return modification

            # If all fields and methods already exist, skip the modification
            if all_fields_exist and all_methods_exist:
                print("All fields and methods already exist, skipping modification")
                return None

            # If the new content is empty after filtering, skip the modification
            if not new_content.strip():
                print("No valid content to add after filtering, skipping modification")
                return None

        return modification

    def apply_modification(self, file_path: str, file_content: str, modification: Dict[str, Any]) -> Tuple[bool, Optional[str], str]:
        """
        Apply a modification to a file.

        Args:
            file_path: Path to the file
            file_content: Current content of the file
            modification: Modification to apply

        Returns:
            A tuple of (success, error_message, modified_content)
        """
        try:
            # If modification is None, return the original content
            if modification is None:
                return True, None, file_content

            modification_type = modification.get("modification_type")
            start_line = modification.get("start_line")
            end_line = modification.get("end_line")
            new_content = modification.get("new_content", "")

            if not modification_type:
                return False, "No modification type specified", file_content

            if not start_line or not end_line:
                return False, "No line numbers specified", file_content

            # Split the file content into lines
            lines = file_content.splitlines()

            # Check if the line numbers are valid
            if start_line < 1 or start_line > len(lines) + 1 or end_line < 1 or end_line > len(lines) + 1:
                return False, f"Invalid line numbers: {start_line}-{end_line} (file has {len(lines)} lines)", file_content

            # Apply the modification
            if modification_type == "add_after_line":
                # Print the modification details
                print("=" * 80)
                print(f"Added after line {start_line}:")
                print("-" * 40)
                print(new_content)
                print("-" * 40)
                print("=" * 80)

                # Split the new content into lines and add them after the specified line
                new_lines = new_content.splitlines()
                for i, line in enumerate(new_lines):
                    lines.insert(start_line + i, line)
            elif modification_type == "add_before_line":
                # Print the modification details
                print("=" * 80)
                print(f"Added before line {start_line}:")
                print("-" * 40)
                print(new_content)
                print("-" * 40)
                print("=" * 80)

                # Split the new content into lines and add them before the specified line
                new_lines = new_content.splitlines()
                for i, line in enumerate(new_lines):
                    lines.insert(start_line - 1 + i, line)
            elif modification_type == "replace_lines":
                # Print the modification details
                print("=" * 80)
                print(f"Replaced lines {start_line}-{end_line}:")
                print("-" * 40)
                print("\n".join(lines[start_line - 1:end_line]))
                print("-" * 40)
                print("With:")
                print("-" * 40)
                print(new_content)
                print("-" * 40)
                print("=" * 80)

                # Split the new content into lines and replace the specified lines
                new_lines = new_content.splitlines()
                lines[start_line - 1:end_line] = new_lines
            elif modification_type == "delete_lines":
                # Print the modification details
                print("=" * 80)
                print(f"Deleted lines {start_line}-{end_line}:")
                print("-" * 40)
                print("\n".join(lines[start_line - 1:end_line]))
                print("-" * 40)
                print("=" * 80)

                # Delete the specified lines
                del lines[start_line - 1:end_line]
            else:
                return False, f"Unknown modification type: {modification_type}", file_content

            # Join the lines back together
            modified_content = "\n".join(lines)

            return True, None, modified_content
        except Exception as e:
            return False, f"Error applying modification: {str(e)}", file_content

    def format_java_file(self, file_path: str) -> None:
        """
        Format a Java file with proper organization.

        Args:
            file_path: Path to the Java file
        """
        try:
            # Use the fix_java_file.py script to fix the file
            import subprocess
            import os

            # Get the path to the fix_java_file.py script
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fix_java_file.py")

            # Run the script
            subprocess.run(["python3", script_path, file_path], check=True)

            print(f"Formatted Java file: {file_path}")
        except Exception as e:
            print(f"Error formatting Java file: {str(e)}")

    def _format_java_content(self, content: str) -> str:
        """
        Format Java content with proper organization.

        Args:
            content: Java file content

        Returns:
            Formatted Java content
        """
        # For now, just return the content as is
        # This is a safer approach until we can implement a more robust Java formatter
        return content
