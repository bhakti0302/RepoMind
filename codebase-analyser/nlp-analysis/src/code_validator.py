"""
Code Validator module.

This module provides functionality for validating and refining generated code.
"""

import os
import sys
import logging
import re
import subprocess
from typing import Dict, List, Any, Optional, Union, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class CodeValidator:
    """Validator for generated code."""
    
    def __init__(
        self,
        temp_dir: str = None,
        style_config: Dict[str, Any] = None
    ):
        """Initialize the code validator.
        
        Args:
            temp_dir: Path to the temporary directory for code validation
            style_config: Configuration for code style checking
        """
        self.temp_dir = temp_dir or os.path.join(os.getcwd(), "temp")
        self.style_config = style_config or {}
        
        # Create temporary directory if it doesn't exist
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
    
    def _extract_code_blocks(self, text: str) -> Dict[str, str]:
        """Extract code blocks from text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary mapping file paths to code
        """
        try:
            # Initialize result
            code_blocks = {}
            
            # Extract file paths and code blocks
            file_pattern = r"##\s*File:\s*([^\n]+)\s*\n\s*```[^\n]*\n(.*?)```"
            matches = re.finditer(file_pattern, text, re.DOTALL)
            
            for match in matches:
                file_path = match.group(1).strip()
                code = match.group(2).strip()
                code_blocks[file_path] = code
            
            # If no file paths were found, look for standalone code blocks
            if not code_blocks:
                code_pattern = r"```[^\n]*\n(.*?)```"
                matches = re.finditer(code_pattern, text, re.DOTALL)
                
                for i, match in enumerate(matches):
                    code = match.group(1).strip()
                    code_blocks[f"code_block_{i+1}.txt"] = code
            
            return code_blocks
        
        except Exception as e:
            logger.error(f"Error extracting code blocks: {e}")
            return {}
    
    def _write_code_to_temp_files(self, code_blocks: Dict[str, str]) -> List[str]:
        """Write code blocks to temporary files.
        
        Args:
            code_blocks: Dictionary mapping file paths to code
            
        Returns:
            List of temporary file paths
        """
        try:
            # Initialize result
            temp_files = []
            
            # Write each code block to a temporary file
            for file_path, code in code_blocks.items():
                # Create a safe file path
                safe_path = os.path.join(self.temp_dir, os.path.basename(file_path))
                
                # Write the code to the file
                with open(safe_path, 'w', encoding='utf-8') as f:
                    f.write(code)
                
                temp_files.append(safe_path)
            
            return temp_files
        
        except Exception as e:
            logger.error(f"Error writing code to temporary files: {e}")
            return []
    
    def _detect_language(self, file_path: str) -> str:
        """Detect the programming language of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Detected language
        """
        # Get the file extension
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        # Map file extensions to languages
        language_map = {
            '.py': 'python',
            '.java': 'java',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.html': 'html',
            '.css': 'css',
            '.c': 'c',
            '.cpp': 'cpp',
            '.h': 'c',
            '.hpp': 'cpp',
            '.cs': 'csharp',
            '.go': 'go',
            '.rb': 'ruby',
            '.php': 'php',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.rs': 'rust',
            '.scala': 'scala',
            '.sh': 'bash',
            '.bat': 'batch',
            '.ps1': 'powershell',
            '.sql': 'sql',
            '.r': 'r',
            '.m': 'matlab',
            '.json': 'json',
            '.xml': 'xml',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.md': 'markdown'
        }
        
        return language_map.get(ext, 'unknown')
    
    def validate_syntax(self, code: str, language: str = None) -> Dict[str, Any]:
        """Validate the syntax of generated code.
        
        Args:
            code: Generated code
            language: Programming language
            
        Returns:
            Dictionary containing validation results
        """
        try:
            # Extract code blocks
            code_blocks = self._extract_code_blocks(code)
            
            if not code_blocks:
                return {
                    "valid": False,
                    "errors": ["No code blocks found"]
                }
            
            # Write code to temporary files
            temp_files = self._write_code_to_temp_files(code_blocks)
            
            # Initialize validation results
            validation_results = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "files": {}
            }
            
            # Validate each file
            for file_path in temp_files:
                # Detect language if not provided
                file_language = language or self._detect_language(file_path)
                
                # Validate syntax based on language
                file_result = self._validate_file_syntax(file_path, file_language)
                
                # Add to validation results
                validation_results["files"][os.path.basename(file_path)] = file_result
                
                # Update overall validation status
                if not file_result["valid"]:
                    validation_results["valid"] = False
                    validation_results["errors"].extend(file_result["errors"])
                
                validation_results["warnings"].extend(file_result["warnings"])
            
            return validation_results
        
        except Exception as e:
            logger.error(f"Error validating syntax: {e}")
            return {
                "valid": False,
                "errors": [str(e)]
            }
    
    def _validate_file_syntax(self, file_path: str, language: str) -> Dict[str, Any]:
        """Validate the syntax of a file.
        
        Args:
            file_path: Path to the file
            language: Programming language
            
        Returns:
            Dictionary containing validation results
        """
        try:
            # Initialize validation result
            validation_result = {
                "valid": True,
                "errors": [],
                "warnings": []
            }
            
            # Validate syntax based on language
            if language == 'python':
                # Use Python's built-in compile function
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        code = f.read()
                    
                    compile(code, file_path, 'exec')
                except SyntaxError as e:
                    validation_result["valid"] = False
                    validation_result["errors"].append(f"Syntax error at line {e.lineno}: {e.msg}")
            
            elif language in ['java', 'javascript', 'typescript', 'c', 'cpp', 'csharp']:
                # Use external tools for syntax validation
                if language == 'java':
                    cmd = ['javac', '-Xlint:all', file_path]
                elif language == 'javascript':
                    cmd = ['node', '--check', file_path]
                elif language == 'typescript':
                    cmd = ['tsc', '--noEmit', file_path]
                elif language in ['c', 'cpp']:
                    cmd = ['gcc', '-fsyntax-only', file_path]
                elif language == 'csharp':
                    cmd = ['csc', '/nologo', '/t:library', file_path]
                
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    
                    if result.returncode != 0:
                        validation_result["valid"] = False
                        validation_result["errors"].append(result.stderr.strip())
                except FileNotFoundError:
                    validation_result["warnings"].append(f"Syntax validation for {language} requires external tools that are not installed")
            
            else:
                validation_result["warnings"].append(f"Syntax validation for {language} is not supported")
            
            return validation_result
        
        except Exception as e:
            logger.error(f"Error validating file syntax: {e}")
            return {
                "valid": False,
                "errors": [str(e)],
                "warnings": []
            }
    
    def check_style(self, code: str, language: str = None) -> Dict[str, Any]:
        """Check the style of generated code.
        
        Args:
            code: Generated code
            language: Programming language
            
        Returns:
            Dictionary containing style check results
        """
        try:
            # Extract code blocks
            code_blocks = self._extract_code_blocks(code)
            
            if not code_blocks:
                return {
                    "valid": False,
                    "errors": ["No code blocks found"]
                }
            
            # Write code to temporary files
            temp_files = self._write_code_to_temp_files(code_blocks)
            
            # Initialize style check results
            style_results = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "files": {}
            }
            
            # Check style for each file
            for file_path in temp_files:
                # Detect language if not provided
                file_language = language or self._detect_language(file_path)
                
                # Check style based on language
                file_result = self._check_file_style(file_path, file_language)
                
                # Add to style check results
                style_results["files"][os.path.basename(file_path)] = file_result
                
                # Update overall style check status
                if not file_result["valid"]:
                    style_results["valid"] = False
                    style_results["errors"].extend(file_result["errors"])
                
                style_results["warnings"].extend(file_result["warnings"])
            
            return style_results
        
        except Exception as e:
            logger.error(f"Error checking style: {e}")
            return {
                "valid": False,
                "errors": [str(e)]
            }
    
    def _check_file_style(self, file_path: str, language: str) -> Dict[str, Any]:
        """Check the style of a file.
        
        Args:
            file_path: Path to the file
            language: Programming language
            
        Returns:
            Dictionary containing style check results
        """
        try:
            # Initialize style check result
            style_result = {
                "valid": True,
                "errors": [],
                "warnings": []
            }
            
            # Check style based on language
            if language == 'python':
                # Use flake8 for Python style checking
                try:
                    cmd = ['flake8', file_path]
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    
                    if result.returncode != 0:
                        style_result["valid"] = False
                        style_result["warnings"] = result.stdout.strip().split('\n')
                except FileNotFoundError:
                    style_result["warnings"].append("Style checking for Python requires flake8 to be installed")
            
            elif language == 'java':
                # Use checkstyle for Java style checking
                try:
                    cmd = ['checkstyle', file_path]
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    
                    if result.returncode != 0:
                        style_result["valid"] = False
                        style_result["warnings"] = result.stdout.strip().split('\n')
                except FileNotFoundError:
                    style_result["warnings"].append("Style checking for Java requires checkstyle to be installed")
            
            else:
                style_result["warnings"].append(f"Style checking for {language} is not supported")
            
            return style_result
        
        except Exception as e:
            logger.error(f"Error checking file style: {e}")
            return {
                "valid": False,
                "errors": [str(e)],
                "warnings": []
            }
    
    def generate_feedback(
        self,
        validation_result: Dict[str, Any],
        style_result: Dict[str, Any]
    ) -> str:
        """Generate feedback based on validation and style check results.
        
        Args:
            validation_result: Validation results
            style_result: Style check results
            
        Returns:
            Generated feedback
        """
        try:
            # Initialize feedback
            feedback = []
            
            # Add validation feedback
            if not validation_result["valid"]:
                feedback.append("## Syntax Issues")
                for error in validation_result["errors"]:
                    feedback.append(f"- {error}")
            
            # Add style feedback
            if not style_result["valid"]:
                feedback.append("\n## Style Issues")
                for warning in style_result["warnings"]:
                    feedback.append(f"- {warning}")
            
            # Add file-specific feedback
            feedback.append("\n## File-Specific Issues")
            
            # Add validation issues for each file
            for file_name, file_result in validation_result.get("files", {}).items():
                if not file_result["valid"]:
                    feedback.append(f"\n### {file_name}")
                    for error in file_result["errors"]:
                        feedback.append(f"- {error}")
            
            # Add style issues for each file
            for file_name, file_result in style_result.get("files", {}).items():
                if not file_result["valid"]:
                    feedback.append(f"\n### {file_name}")
                    for warning in file_result["warnings"]:
                        feedback.append(f"- {warning}")
            
            # If no issues were found, add a positive feedback
            if validation_result["valid"] and style_result["valid"]:
                feedback.append("No syntax or style issues were found. The code looks good!")
            
            return "\n".join(feedback)
        
        except Exception as e:
            logger.error(f"Error generating feedback: {e}")
            return f"Error generating feedback: {e}"


# Example usage
if __name__ == "__main__":
    # Create a code validator
    validator = CodeValidator()
    
    # Example code
    code = """
    ## File: UserService.java
    ```java
    public class UserService {
        private final UserRepository userRepository;
        
        public UserService(UserRepository userRepository) {
            this.userRepository = userRepository;
        }
        
        public User authenticate(String username, String password) {
            User user = userRepository.findByUsername(username);
            if (user != null && passwordEncoder.matches(password, user.getPassword())) {
                return user;
            }
            return null;
        }
    }
    ```
    """
    
    # Validate syntax
    validation_result = validator.validate_syntax(code, language="java")
    
    # Check style
    style_result = validator.check_style(code, language="java")
    
    # Generate feedback
    feedback = validator.generate_feedback(validation_result, style_result)
    
    # Print the feedback
    print(feedback)
