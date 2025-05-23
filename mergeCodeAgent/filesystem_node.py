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

            # If no change is needed, return early
            if modification.get("modification_type") == "no_change":
                print(f"\n{modification.get('message', 'No changes needed')}")
                return True, None

            # If the modification type is 'replace_file', replace the entire file content
            if modification.get("modification_type") == "replace_file":
                new_content = modification.get("new_content", "")
                
                # Show git diff
                print("\nProposed changes:")
                print("=" * 80)
                diff_output = self._show_git_diff(file_path, file_content, new_content)
                if diff_output:
                    print("\nDo you want to apply these changes? (y/n): ", end='', flush=True)
                    response = input().lower()
                    if response != 'y':
                        print("Changes rejected by user")
                        return False, "Changes rejected by user"

                    # Write the new content to the file
                    with open(file_path, 'w') as f:
                        f.write(new_content)

                    print(f"Replaced entire file: {file_path}")
                    return True, None
                else:
                    print("No changes detected")
                    return True, None

            # For other modification types, proceed with the existing logic
            if file_path.endswith(".java"):
                modification = self._check_for_duplicates(file_path, file_content, modification)
                if not modification:
                    print("\nAll requested changes are already present in the file")
                    return True, None  # Skip if everything is already present

            # Apply the modification
            try:
                success, error, modified_content = self.apply_modification(file_path, file_content, modification)
                if not success:
                    return False, error

                # Show git diff
                print("\nProposed changes:")
                print("=" * 80)
                diff_output = self._show_git_diff(file_path, file_content, modified_content)
                if diff_output:
                    print("\nDo you want to apply these changes? (y/n): ", end='', flush=True)
                    response = input().lower()
                    if response != 'y':
                        print("Changes rejected by user")
                        return False, "Changes rejected by user"

                    # Write the modified content back to the file
                    with open(file_path, 'w') as f:
                        f.write(modified_content)

                    print(f"Modified file: {file_path}")
                    return True, None
                else:
                    print("No changes detected")
                    return True, None
            except Exception as e:
                return False, f"Error modifying file: {str(e)}"
        except Exception as e:
            return False, f"Error modifying file: {str(e)}"

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
        with tempfile.NamedTemporaryFile(suffix=".new", delete=False) as new_file:
            new_path = new_file.name
            new_file.write(new_content.encode())

        try:
            # Save the original file content
            original_content = None
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    original_content = f.read()

            # Write the new content to the actual file
            with open(file_path, 'w') as f:
                f.write(new_content)

            # Stage the changes in git
            subprocess.run(["git", "add", file_path], cwd=repo_root, check=True)

            # Show the diff
            result = subprocess.run(
                ["git", "diff", "--cached", "--color=always", "--unified=3"],
                cwd=repo_root,
                capture_output=True,
                text=True
            )

            # Restore the original content
            if original_content is not None:
                with open(file_path, 'w') as f:
                    f.write(original_content)
            subprocess.run(["git", "reset", file_path], cwd=repo_root, check=True)

            # Process the diff output to enhance colors
            if result.stdout:
                # ANSI color codes
                GREEN = '\033[32m'
                RED = '\033[31m'
                RESET = '\033[0m'
                BOLD = '\033[1m'

                # Split the diff into lines
                lines = result.stdout.splitlines()
                enhanced_lines = []

                for line in lines:
                    if line.startswith('+') and not line.startswith('+++'):
                        # Add green color to added lines
                        enhanced_lines.append(f"{GREEN}{line}{RESET}")
                    elif line.startswith('-') and not line.startswith('---'):
                        # Add red color to removed lines
                        enhanced_lines.append(f"{RED}{line}{RESET}")
                    elif line.startswith('@@'):
                        # Make the hunk header bold
                        enhanced_lines.append(f"{BOLD}{line}{RESET}")
                    else:
                        enhanced_lines.append(line)

                # Join the lines back together
                enhanced_diff = '\n'.join(enhanced_lines)

                # Print the enhanced diff
                print(enhanced_diff)
                return enhanced_diff
            else:
                print("No changes detected")
                return ""

        finally:
            # Clean up temporary file
            if os.path.exists(new_path):
                os.unlink(new_path)

    def _highlight_changes(self, old_lines: List[str], new_lines: List[str]) -> str:
        """
        Highlight the differences between old and new content.

        Args:
            old_lines: List of lines from the old content
            new_lines: List of lines from the new content

        Returns:
            A string with highlighted differences
        """
        from difflib import unified_diff

        # ANSI color codes
        GREEN = '\033[32m'
        RED = '\033[31m'
        RESET = '\033[0m'
        BOLD = '\033[1m'

        # Generate the diff
        diff = list(unified_diff(old_lines, new_lines, n=3))

        # Process the diff to add colors
        enhanced_diff = []
        for line in diff:
            if line.startswith('+') and not line.startswith('+++'):
                enhanced_diff.append(f"{GREEN}{line}{RESET}")
            elif line.startswith('-') and not line.startswith('---'):
                enhanced_diff.append(f"{RED}{line}{RESET}")
            elif line.startswith('@@'):
                enhanced_diff.append(f"{BOLD}{line}{RESET}")
            else:
                enhanced_diff.append(line)

        return '\n'.join(enhanced_diff)

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
            all_methods_exist = False  # Default to false - don't skip unless we have methods to check
            if method_matches:  # Only check if we have methods to check
                all_methods_exist = True
                for match in method_matches:
                    method_name = match.group(2)

                    # Skip unauthorized methods
                    if method_name in unauthorized_methods:
                        continue

                    # Create a more precise regex to match the method
                    method_regex = r'(public|private|protected)(?:\s+\w+)*\s+' + re.escape(method_name) + r'\s*\([^)]*\)\s*{'
                    if not re.search(method_regex, file_content):
                        all_methods_exist = False
                        print(f"Method {method_name} does not exist in the file")
                        break
                    else:
                        print(f"Method {method_name} already exists in the file")

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
            if all_fields_exist and all_methods_exist and (field_matches or method_matches):
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

    def check_java_syntax(self, code: str) -> Tuple[bool, Optional[str]]:
        """
        Check the syntax of Java code.

        Args:
            code: Java code to check

        Returns:
            A tuple of (is_valid, error_message)
        """
        try:
            # Create a temporary file
            import tempfile
            import os
            import subprocess

            with tempfile.NamedTemporaryFile(suffix=".java", delete=False) as temp:
                temp_path = temp.name
                temp.write(code.encode())

            # Try to compile the file
            result = subprocess.run(["javac", temp_path], capture_output=True, text=True)

            # Clean up
            os.unlink(temp_path)

            # Check if compilation was successful
            if result.returncode == 0:
                return True, None
            else:
                return False, result.stderr
        except Exception as e:
            return False, str(e)

    def _fix_common_java_syntax_issues(self, code: str) -> str:
        """
        Fix common Java syntax issues.

        Args:
            code: Java code to fix

        Returns:
            Fixed Java code
        """
        # Fix missing semicolons
        lines = code.splitlines()
        fixed_lines = []

        for line in lines:
            line_stripped = line.strip()

            # Skip empty lines, comments, and lines that already end with semicolon, brace, or are import/package statements
            if (not line_stripped or
                line_stripped.startswith("//") or
                line_stripped.startswith("/*") or
                line_stripped.endswith(";") or
                line_stripped.endswith("{") or
                line_stripped.endswith("}") or
                line_stripped.startswith("import ") or
                line_stripped.startswith("package ")):
                fixed_lines.append(line)
                continue

            # Check if this line needs a semicolon
            needs_semicolon = True

            # Don't add semicolons to method declarations, class declarations, etc.
            if (re.search(r'(public|private|protected)(?:\s+\w+)*\s+\w+\s*\([^)]*\)\s*{?$', line_stripped) or
                re.search(r'(class|interface|enum)\s+\w+', line_stripped) or
                re.search(r'if\s*\([^)]*\)', line_stripped) or
                re.search(r'for\s*\([^)]*\)', line_stripped) or
                re.search(r'while\s*\([^)]*\)', line_stripped) or
                re.search(r'switch\s*\([^)]*\)', line_stripped) or
                "}" in line_stripped):
                needs_semicolon = False

            if needs_semicolon:
                fixed_lines.append(line + ";")
            else:
                fixed_lines.append(line)

        # Fix missing braces
        code = "\n".join(fixed_lines)

        # Fix missing closing braces
        open_braces = code.count("{")
        close_braces = code.count("}")

        if open_braces > close_braces:
            # Add missing closing braces
            code += "\n" + "}" * (open_braces - close_braces)

        return code
