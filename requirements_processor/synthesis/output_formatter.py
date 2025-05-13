
"""
Output formatter for code generation results.

This module provides functionality to format the output of code generation
for display or saving to files.
"""

import logging
import os
import json
from typing import Dict, List, Set, Optional, Any, Tuple, Union
from pathlib import Path

logger = logging.getLogger(__name__)

class OutputFormatter:
    """Formats code generation output for display or saving."""
    
    def __init__(self, output_dir: str = "output"):
        """Initialize the output formatter.
        
        Args:
            output_dir: Directory to save output files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initialized OutputFormatter with output directory: {output_dir}")
    
    def format_for_display(self, result: Dict[str, Any]) -> str:
        """Format the result for display in the console or UI.
        
        Args:
            result: Code generation result
        
        Returns:
            Formatted string
        """
        # Extract information
        code_blocks = result.get("generated_code", [])
        language = result.get("language", "unknown")
        file_type = result.get("file_type", "unknown")
        
        # Format code blocks
        formatted_code = ""
        for i, block in enumerate(code_blocks):
            block_language = block.get("language", "text")
            block_content = block.get("content", "")
            
            formatted_code += f"Code Block {i+1} ({block_language}):\n"
            formatted_code += "```" + block_language + "\n"
            formatted_code += block_content + "\n"
            formatted_code += "```\n\n"
        
        # Build the complete output
        output = f"""
## Implementation Instructions

### File to Modify
The code should be inserted into the file: {result.get('suggested_path', 'Unknown')}

### Code to Insert
{formatted_code}
"""
        
        return output
    
    def save_to_files(
        self,
        result: Dict[str, Any],
        base_filename: str,
        save_metadata: bool = True
    ) -> Dict[str, str]:
        """Save the generated code to files.
        
        Args:
            result: Code generation result
            base_filename: Base filename (without extension)
            save_metadata: Whether to save metadata
        
        Returns:
            Dictionary mapping file types to file paths
        """
        # Parse the base_filename to get the directory and filename parts
        base_path = Path(base_filename)
        output_dir = self.output_dir / base_path.parent
        filename_base = base_path.name
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract information
        code_blocks = result.get("generated_code", [])
        language = result.get("language", "unknown")
        file_type = result.get("file_type", "unknown")
        
        # Format the output as text with instructions
        formatted_output = self.format_for_display(result)
        
        # Determine suggested filename based on language and content
        suggested_filename = self._suggest_filename(code_blocks, language, file_type)
        
        # Suggest a complete file path based on language conventions
        suggested_path = self._suggest_file_path(suggested_filename, language)
        
        # Add clear instructions
        instructions = f"""
# Implementation Instructions

## Step 1: Locate the File
Find the file that needs to be modified at its current location.

## Step 2: Replace or Update the Code
Replace the existing code with the generated code below, or update the specific sections as indicated.
"""
        
        # Save as a text file
        txt_filename = f"{filename_base}.txt"
        txt_file_path = output_dir / txt_filename
        
        with open(txt_file_path, "w") as f:
            f.write(instructions + "\n\n" + formatted_output)
        
        saved_files = {"instructions_and_code": str(txt_file_path)}
        logger.info(f"Saved instructions and code to {txt_file_path}")
        
        # Save metadata if requested
        if save_metadata:
            metadata_path = output_dir / f"{filename_base}_metadata.json"
            
            # Prepare metadata
            metadata = {
                "language": language,
                "file_type": file_type,
                "model": result.get("model", "unknown"),
                "generated_files": saved_files,
                "suggested_filename": suggested_filename,
                "suggested_path": suggested_path
            }
            
            # Save metadata
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)
            
            saved_files["metadata"] = str(metadata_path)
            logger.info(f"Saved metadata to {metadata_path}")
        
        return saved_files
    
    def save_to_data_dir(
        self,
        result: Dict[str, Any],
        project_id: str,
        requirement_id: str
    ) -> Dict[str, str]:
        """
        
## Step 3: Integrate with Your Project
- Make any necessary adjustments to fit your project structure
- Add any required imports
- Ensure the code follows your project's coding standards

Save the generated code to the data directory.
        
        Args:
            result: Code generation result
            project_id: Project ID
            requirement_id: Requirement ID
            
        Returns:
            Dictionary mapping file types to file paths
        """
        # Create base filename from project and requirement IDs
        # Add a timestamp to ensure uniqueness
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Extract a short name from the requirement text for better readability
        short_name = self._generate_short_name(result.get("requirements", {}).get("text", ""))
        
        # Combine all elements for a unique, descriptive filename
        base_filename = f"{project_id}/{requirement_id}_{short_name}_{timestamp}"
        
        # Save to files
        return self.save_to_files(result, base_filename)

    def _suggest_filename(self, code_blocks: List[Dict[str, Any]], language: str, file_type: str) -> str:
        """Suggest a filename based on code content and language.
        
        Args:
            code_blocks: List of code blocks
            language: Programming language
            file_type: Type of file
        
        Returns:
            Suggested filename with appropriate extension
        """
        # Default filename based on language
        if language.lower() == "java":
            # For Java, try to extract the class name
            class_name = self._extract_java_class_name(code_blocks)
            return f"{class_name}.java" if class_name else "GeneratedClass.java"
        elif language.lower() == "python":
            return "generated_module.py"
        elif language.lower() == "javascript":
            return "generated_script.js"
        elif language.lower() == "typescript":
            return "generated_module.ts"
        elif language.lower() == "c#" or language.lower() == "csharp":
            return "GeneratedClass.cs"
        elif language.lower() == "c++":
            return "generated_class.cpp"
        elif language.lower() == "go":
            return "generated_package.go"
        else:
            # Generic fallback
            return f"generated_code.{language.lower()}"

    def _extract_java_class_name(self, code_blocks: List[Dict[str, Any]]) -> Optional[str]:
        """Extract the class name from Java code blocks.
        
        Args:
            code_blocks: List of code blocks
        
        Returns:
            Extracted class name or None if not found
        """
        import re
        
        # Look through all code blocks
        for block in code_blocks:
            if block.get("language", "").lower() in ["java", ""]:
                content = block.get("content", "")
                
                # Try to find class declaration
                class_match = re.search(r'class\s+(\w+)', content)
                if class_match:
                    return class_match.group(1)
        
        return None

    def _generate_short_name(self, requirement_text: str, max_length: int = 20) -> str:
        """Generate a short name from requirement text.
        
        Args:
            requirement_text: The requirement text
            max_length: Maximum length of the short name
        
        Returns:
            A short name derived from the requirement text
        """
        import re
        
        # Extract the first sentence or up to 100 characters
        first_part = requirement_text.split('.')[0]
        if len(first_part) > 100:
            first_part = first_part[:100]
        
        # Remove special characters and convert to lowercase
        clean_text = re.sub(r'[^a-zA-Z0-9\s]', '', first_part).lower()
        
        # Replace spaces with underscores and limit length
        words = clean_text.split()
        if not words:
            return "req"
        
        # Use the first few words to create a short name
        short_name = "_".join(words[:3])
        
        # Ensure the name isn't too long
        if len(short_name) > max_length:
            short_name = short_name[:max_length]
        
        return short_name

    def _suggest_file_path(self, filename: str, language: str) -> str:
        """Suggest a complete file path based on language conventions.
        
        Args:
            filename: Suggested filename
            language: Programming language
        
        Returns:
            Suggested complete file path
        """
        # Base project directory - can be customized based on project structure
        base_dir = "src"
        
        if language.lower() == "java":
            # Java uses package structure for directories
            # Extract package from filename if it's a fully qualified name
            if "." in filename and not filename.endswith(".java"):
                parts = filename.split(".")
                package_path = "/".join(parts[:-1])
                class_name = parts[-1]
                return f"{base_dir}/main/java/{package_path}/{class_name}.java"
            else:
                # Default package structure for Java
                clean_name = filename.replace(".java", "")
                return f"{base_dir}/main/java/com/example/{clean_name}.java"
        
        elif language.lower() == "python":
            return f"{base_dir}/{filename}"
        
        elif language.lower() in ["javascript", "typescript"]:
            return f"{base_dir}/js/{filename}"
        
        elif language.lower() in ["c#", "csharp"]:
            return f"{base_dir}/Models/{filename}"
        
        elif language.lower() == "go":
            return f"{base_dir}/pkg/{filename}"
        
        else:
            # Generic fallback
            return f"{base_dir}/{filename}"

