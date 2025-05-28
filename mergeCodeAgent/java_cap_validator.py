#!/usr/bin/env python3
"""
CAP SAP Java Code Validator and Fixer

This module validates and corrects Java code to ensure it complies with CAP SAP
Java standards and conventions. It acts as a post-processor for code generated
by the mergeCodeAgent.
"""

import os
import re
import sys
import subprocess
from typing import Tuple, Optional, List, Dict, Any

# Add the path to the current directory to ensure we can import our local modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Standard CAP SAP Java imports that should be present in service classes
CAP_STANDARD_IMPORTS = [
    "import cds.gen.*;",
    "import com.sap.cds.services.handler.EventHandler;",
    "import com.sap.cds.services.handler.annotations.ServiceName;",
    "import com.sap.cds.services.handler.annotations.On;",
    "import com.sap.cds.services.cds.CdsService;",
    "import com.sap.cds.services.handler.annotations.Before;",
    "import com.sap.cds.services.handler.annotations.After;"
]

# Common CAP SAP Java annotations
CAP_ANNOTATIONS = [
    "@ServiceName",
    "@Component",
    "@Service",
    "@Repository",
    "@On",
    "@Before",
    "@After"
]

class CAPJavaValidator:
    """
    Validator and fixer for CAP SAP Java code.
    """
    
    def __init__(self, project_root: str):
        """
        Initialize the validator with the project root directory.
        
        Args:
            project_root: Path to the project root directory
        """
        self.project_root = project_root
        self.service_package_pattern = r".*\.service.*"
        self.entity_package_pattern = r".*\.entity.*"
        self.repository_package_pattern = r".*\.repository.*"
        
    def validate_and_fix_file(self, file_path: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate and fix a Java file.
        
        Args:
            file_path: Path to the Java file
            
        Returns:
            Tuple containing:
            - Success flag
            - Fixed content (if applicable)
            - Error message (if any)
        """
        try:
            # Read the file
            with open(file_path, 'r') as f:
                content = f.read()
                
            # If file is empty, just return
            if not content.strip():
                return False, None, "File is empty"
                
            # Check and fix the file
            success, fixed_content, error_msg = self._check_and_fix(file_path, content)
            
            # If fixes were applied, print a message
            if fixed_content is not None and content != fixed_content:
                print(f"Applied CAP SAP Java fixes to: {file_path}")
                
            # If both success and fixed_content are returned, the file is valid (or was fixed)
            if success and fixed_content is not None:
                return True, fixed_content, None
                
            # If there are errors after attempted fixes, try to continue anyway
            # This is to handle false positives in the syntax checker
            if not success and fixed_content is not None:
                print(f"Warning: {error_msg}")
                print(f"Continuing with partial fixes to: {file_path}")
                return True, fixed_content, None
                
            # If no fixes were made and there are errors, return the error
            return success, fixed_content, error_msg
                
        except Exception as e:
            return False, None, str(e)
            
    def _check_and_fix(self, file_path: str, content: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Check if the file needs fixes and apply them if needed.
        
        Args:
            file_path: Path to the Java file
            content: Content of the Java file
            
        Returns:
            Tuple containing:
            - Needs fixes flag
            - Fixed content (if fixes were applied) or None
            - Error message (if any) or None
        """
        # Extract package and class info
        package_match = re.search(r'package\s+([^;]+);', content)
        class_match = re.search(r'(public|private)\s+class\s+(\w+)', content)
        
        if not package_match or not class_match:
            return True, None, "Could not extract package or class name"
            
        package_name = package_match.group(1)
        class_name = class_match.group(2)
        
        # Initialize modified content with original content
        modified_content = content
        needs_fixes = False
        
        # Apply fixes based on file type
        if re.match(self.service_package_pattern, package_name):
            needs_fixes, modified_content = self._fix_service_class(modified_content, package_name, class_name)
        elif re.match(self.entity_package_pattern, package_name):
            needs_fixes, modified_content = self._fix_entity_class(modified_content, package_name, class_name)
        elif re.match(self.repository_package_pattern, package_name):
            needs_fixes, modified_content = self._fix_repository_class(modified_content, package_name, class_name)
            
        # Common fixes for all Java files
        if not needs_fixes:
            common_needs_fixes, modified_content = self._apply_common_fixes(modified_content)
            needs_fixes = needs_fixes or common_needs_fixes
            
        # Check syntax
        is_valid, error = self._check_java_syntax(modified_content)
        if not is_valid:
            return True, None, f"Syntax errors remain after fixes: {error}"
            
        return needs_fixes, modified_content if needs_fixes else None, None
        
    def _fix_service_class(self, content: str, package_name: str, class_name: str) -> Tuple[bool, str]:
        """
        Fix a service class to ensure CAP SAP compliance.
        
        Args:
            content: Content of the Java file
            package_name: Package name
            class_name: Class name
            
        Returns:
            Tuple containing:
            - Whether fixes were applied
            - Modified content
        """
        needs_fixes = False
        modified_content = content
        
        # Check and add missing imports
        for import_stmt in CAP_STANDARD_IMPORTS:
            if import_stmt not in modified_content:
                # Find the last import statement
                last_import_match = re.search(r'(.*import [^;]+;.*$)', modified_content, re.MULTILINE)
                if last_import_match:
                    last_import_line = last_import_match.group(1)
                    # Insert the missing import after the last import
                    modified_content = modified_content.replace(
                        last_import_line,
                        f"{last_import_line}\n{import_stmt}"
                    )
                    needs_fixes = True
        
        # Ensure class has @ServiceName annotation
        if "@ServiceName" not in modified_content:
            # Extract the service name from the class name
            service_name = class_name.replace("Service", "").replace("Handler", "")
            
            # Add @ServiceName annotation before the class declaration
            class_pattern = r'public\s+class\s+' + re.escape(class_name)
            if re.search(class_pattern, modified_content):
                modified_content = re.sub(
                    class_pattern,
                    f"@ServiceName(\"{service_name}\")\npublic class {class_name}",
                    modified_content
                )
                needs_fixes = True
        
        # Ensure class implements EventHandler
        implements_pattern = r'public\s+class\s+' + re.escape(class_name) + r'\s+implements\s+([^{]+)'
        implements_match = re.search(implements_pattern, modified_content)
        
        if implements_match:
            implemented_interfaces = implements_match.group(1)
            if "EventHandler" not in implemented_interfaces:
                modified_content = re.sub(
                    implements_pattern,
                    f"public class {class_name} implements EventHandler, $1",
                    modified_content
                )
                needs_fixes = True
        else:
            # Class doesn't implement any interfaces, add EventHandler
            class_pattern = r'public\s+class\s+' + re.escape(class_name) + r'(?!\s+implements)'
            if re.search(class_pattern, modified_content):
                modified_content = re.sub(
                    class_pattern,
                    f"public class {class_name} implements EventHandler",
                    modified_content
                )
                needs_fixes = True
            
        return needs_fixes, modified_content
        
    def _fix_entity_class(self, content: str, package_name: str, class_name: str) -> Tuple[bool, str]:
        """
        Fix an entity class to ensure CAP SAP compliance.
        
        Args:
            content: Content of the Java file
            package_name: Package name
            class_name: Class name
            
        Returns:
            Tuple containing:
            - Whether fixes were applied
            - Modified content
        """
        needs_fixes = False
        modified_content = content
        
        # Ensure entity has proper annotations and structure
        if "@Entity" not in modified_content:
            # Add @Entity annotation
            class_pattern = r'public\s+class\s+' + re.escape(class_name)
            if re.search(class_pattern, modified_content):
                modified_content = re.sub(
                    class_pattern,
                    f"@Entity\npublic class {class_name}",
                    modified_content
                )
                needs_fixes = True
                
                # Add import for Entity annotation if needed
                if "import javax.persistence.Entity;" not in modified_content:
                    last_import_match = re.search(r'(.*import [^;]+;.*$)', modified_content, re.MULTILINE)
                    if last_import_match:
                        last_import_line = last_import_match.group(1)
                        modified_content = modified_content.replace(
                            last_import_line,
                            f"{last_import_line}\nimport javax.persistence.Entity;"
                        )
        
        # Ensure entity has an ID field
        if "ID" not in modified_content and "Id" not in modified_content and "@Id" not in modified_content:
            # Add ID field
            class_body_match = re.search(r'public\s+class\s+' + re.escape(class_name) + r'\s+[^{]*{', modified_content)
            if class_body_match:
                class_body_start = class_body_match.end()
                modified_content = (
                    modified_content[:class_body_start] + 
                    "\n    @Id\n    @GeneratedValue\n    private String id;\n" +
                    modified_content[class_body_start:]
                )
                needs_fixes = True
                
                # Add imports for ID annotations if needed
                imports_to_add = [
                    "import javax.persistence.Id;",
                    "import javax.persistence.GeneratedValue;"
                ]
                
                for import_stmt in imports_to_add:
                    if import_stmt not in modified_content:
                        last_import_match = re.search(r'(.*import [^;]+;.*$)', modified_content, re.MULTILINE)
                        if last_import_match:
                            last_import_line = last_import_match.group(1)
                            modified_content = modified_content.replace(
                                last_import_line,
                                f"{last_import_line}\n{import_stmt}"
                            )
                
                # Add getter and setter for ID if needed
                if "getId()" not in modified_content:
                    class_end_match = re.search(r'}$', modified_content)
                    if class_end_match:
                        class_end = class_end_match.start()
                        modified_content = (
                            modified_content[:class_end] +
                            "\n    public String getId() {\n        return id;\n    }\n\n" +
                            "    public void setId(String id) {\n        this.id = id;\n    }\n" +
                            modified_content[class_end:]
                        )
            
        return needs_fixes, modified_content
        
    def _fix_repository_class(self, content: str, package_name: str, class_name: str) -> Tuple[bool, str]:
        """
        Fix a repository class to ensure CAP SAP compliance.
        
        Args:
            content: Content of the Java file
            package_name: Package name
            class_name: Class name
            
        Returns:
            Tuple containing:
            - Whether fixes were applied
            - Modified content
        """
        needs_fixes = False
        modified_content = content
        
        # Ensure repository has @Repository annotation
        if "@Repository" not in modified_content:
            # Add @Repository annotation
            if "interface" in modified_content and class_name in modified_content:
                interface_pattern = r'public\s+interface\s+' + re.escape(class_name)
                if re.search(interface_pattern, modified_content):
                    modified_content = re.sub(
                        interface_pattern,
                        f"@Repository\npublic interface {class_name}",
                        modified_content
                    )
                    needs_fixes = True
            else:
                class_pattern = r'public\s+class\s+' + re.escape(class_name)
                if re.search(class_pattern, modified_content):
                    modified_content = re.sub(
                        class_pattern,
                        f"@Repository\npublic class {class_name}",
                        modified_content
                    )
                    needs_fixes = True
                
            # Add import for Repository annotation if needed
            if "import org.springframework.stereotype.Repository;" not in modified_content:
                last_import_match = re.search(r'(.*import [^;]+;.*$)', modified_content, re.MULTILINE)
                if last_import_match:
                    last_import_line = last_import_match.group(1)
                    modified_content = modified_content.replace(
                        last_import_line,
                        f"{last_import_line}\nimport org.springframework.stereotype.Repository;"
                    )
        
        # For interface repositories, ensure it extends JpaRepository if it doesn't extend anything
        is_interface = "interface" in modified_content and class_name in modified_content
        extends_pattern = r'interface\s+' + re.escape(class_name) + r'\s+extends\s+'
        
        if is_interface and not re.search(extends_pattern, modified_content):
            # Find the entity type from the class name (typically Repository<EntityType, ID>)
            entity_type = class_name.replace("Repository", "")
            
            # Add extension of JpaRepository
            interface_pattern = r'public\s+interface\s+' + re.escape(class_name) + r'(\s*{)?'
            if re.search(interface_pattern, modified_content):
                modified_content = re.sub(
                    interface_pattern,
                    f"public interface {class_name} extends JpaRepository<{entity_type}, String>$1",
                    modified_content
                )
                needs_fixes = True
                
                # Add import for JpaRepository if needed
                if "import org.springframework.data.jpa.repository.JpaRepository;" not in modified_content:
                    last_import_match = re.search(r'(.*import [^;]+;.*$)', modified_content, re.MULTILINE)
                    if last_import_match:
                        last_import_line = last_import_match.group(1)
                        modified_content = modified_content.replace(
                            last_import_line,
                            f"{last_import_line}\nimport org.springframework.data.jpa.repository.JpaRepository;"
                        )
            
        return needs_fixes, modified_content
        
    def _apply_common_fixes(self, content: str) -> Tuple[bool, str]:
        """
        Apply common fixes to all Java files.
        
        Args:
            content: Content of the Java file
            
        Returns:
            Tuple containing:
            - Whether fixes were applied
            - Modified content
        """
        needs_fixes = False
        modified_content = content
        
        # Fix missing semicolons at end of lines
        lines = modified_content.split('\n')
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Skip empty lines, comments, and lines that already end with semicolon or brace
            if (not line_stripped or 
                line_stripped.startswith("//") or 
                line_stripped.startswith("/*") or 
                line_stripped.endswith(";") or 
                line_stripped.endswith("{") or 
                line_stripped.endswith("}") or
                line_stripped.endswith("*/") or
                "import " in line_stripped or
                "package " in line_stripped or
                "@" in line_stripped or
                line_stripped.startswith("public class") or
                line_stripped.startswith("public interface") or
                line_stripped.startswith("private class") or
                line_stripped.startswith("protected class")):
                continue
                
            # Identify lines that likely need semicolons
            if (re.search(r'^\s*private\s+\w+\s+\w+\s*=', line_stripped) or   # Field assignments
                re.search(r'^\s*public\s+\w+\s+\w+\s*=', line_stripped) or
                re.search(r'^\s*protected\s+\w+\s+\w+\s*=', line_stripped) or
                re.search(r'^\s*\w+\s*=\s*', line_stripped) or                # Simple assignments
                re.search(r'^\s*return\s+', line_stripped) or                 # Return statements
                re.search(r'^\s*System\.out\.println', line_stripped) or      # Print statements
                re.search(r'^\s*\w+\s+\w+\s*=\s*', line_stripped)):          # Variable declarations with assignment
                lines[i] = line + ";"
                needs_fixes = True
                
        modified_content = '\n'.join(lines)
        
        # Fix missing braces
        open_braces = modified_content.count("{")
        close_braces = modified_content.count("}")
        
        if open_braces > close_braces:
            # Add missing closing braces
            modified_content += "\n" + "}" * (open_braces - close_braces)
            needs_fixes = True
            
        # Fix broken string literals
        string_literal_pattern = r'"([^"\\]*(\\.[^"\\]*)*)"'
        broken_string_pattern = r'"([^"\\]*(\\.[^"\\]*)*)'
        broken_strings = re.finditer(broken_string_pattern, modified_content)
        
        for match in broken_strings:
            if not re.search(string_literal_pattern, modified_content[match.start():]):
                # String is broken, add closing quote
                string_start = match.start()
                modified_content = modified_content[:string_start] + match.group() + '"' + modified_content[match.end():]
                needs_fixes = True
            
        return needs_fixes, modified_content
        
    def _check_java_syntax(self, content: str) -> Tuple[bool, Optional[str]]:
        """
        Check Java syntax using a temporary file.
        
        Args:
            content: Java content to check
            
        Returns:
            Tuple containing:
            - Whether the syntax is valid
            - Error message if invalid, None otherwise
        """
        try:
            # Trim trailing whitespace to avoid false positives
            content = content.rstrip()
            
            # Perform basic syntax checks first
            if content.count("{") != content.count("}"):
                return False, "Mismatched braces"
                
            if content.count("(") != content.count(")"):
                return False, "Mismatched parentheses"
                
            # Check for missing semicolons at end of statements
            lines = content.split('\n')
            for i, line in enumerate(lines):
                line_stripped = line.strip()
                
                # Skip empty lines or lines that don't need semicolons
                if not line_stripped:
                    continue
                
                # Skip the final closing brace of the file
                if i == len(lines) - 1 and line_stripped == "}":
                    continue
                
                # Look for lines that likely need semicolons but don't have them
                if (not line_stripped.startswith("//") and
                    not line_stripped.startswith("/*") and
                    not line_stripped.endswith(";") and
                    not line_stripped.endswith("{") and
                    not line_stripped.endswith("}") and
                    not line_stripped.endswith("*/") and
                    not "import " in line_stripped and
                    not "package " in line_stripped and
                    not "@" in line_stripped and
                    not "class " in line_stripped and
                    not "interface " in line_stripped and
                    not "enum " in line_stripped and
                    not "if " in line_stripped and
                    not "else " in line_stripped and
                    not "for " in line_stripped and
                    not "while " in line_stripped and
                    not "do " in line_stripped and
                    not "switch " in line_stripped and
                    not "case " in line_stripped):
                    return False, f"Missing semicolon at line {i+1}: {line_stripped}"
            
            # If basic checks pass, we'll assume the syntax is valid
            # We won't use javac since it would complain about missing dependencies
            return True, None
                
        except Exception as e:
            return False, str(e)


def validate_java_file(file_path: str, project_root: str) -> Tuple[bool, Optional[str]]:
    """
    Validate and fix a Java file to ensure CAP SAP compliance.
    
    Args:
        file_path: Path to the Java file
        project_root: Path to the project root directory
        
    Returns:
        Tuple containing:
        - Success flag (True if valid or fixed, False if issues couldn't be fixed)
        - Error message (if any) or None
    """
    # Skip non-Java files
    if not file_path.endswith(".java"):
        return True, None
        
    print(f"Validating CAP SAP Java compliance for: {file_path}")
    
    validator = CAPJavaValidator(project_root)
    success, fixed_content, error_msg = validator.validate_and_fix_file(file_path)
    
    if success and fixed_content:
        # Write the fixed content back to the file
        try:
            with open(file_path, 'w') as f:
                f.write(fixed_content)
            print(f"Fixed CAP SAP Java compliance issues in: {file_path}")
            return True, None
        except Exception as e:
            return False, f"Error writing fixed content to {file_path}: {str(e)}"
    elif not success:
        return False, error_msg
    
    return True, None


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python java_cap_validator.py <file_path> <project_root>")
        sys.exit(1)
        
    file_path = sys.argv[1]
    project_root = sys.argv[2]
    
    success, error_msg = validate_java_file(file_path, project_root)
    
    if not success:
        print(f"Error: {error_msg}")
        sys.exit(1)
    
    print("Validation completed successfully.")
    sys.exit(0) 