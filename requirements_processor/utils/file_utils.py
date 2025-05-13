
"""
File utilities for requirements processing.

This module provides utility functions for file operations related to
requirements processing.
"""

import logging
import os
import json
import shutil
from typing import Dict, List, Set, Optional, Any, Tuple, Union
from pathlib import Path

logger = logging.getLogger(__name__)

def ensure_dir_exists(directory: Union[str, Path]) -> Path:
    """Ensure a directory exists, creating it if necessary.
    
    Args:
        directory: Directory path
        
    Returns:
        Path object for the directory
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path

def read_text_file(file_path: Union[str, Path]) -> str:
    """Read text from a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File contents as string
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def write_text_file(file_path: Union[str, Path], content: str) -> None:
    """Write text to a file.
    
    Args:
        file_path: Path to the file
        content: Content to write
    """
    # Ensure directory exists
    ensure_dir_exists(Path(file_path).parent)
    
    # Write file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def read_json_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Read JSON from a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Parsed JSON data
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_json_file(file_path: Union[str, Path], data: Dict[str, Any], indent: int = 2) -> None:
    """Write JSON to a file.
    
    Args:
        file_path: Path to the file
        data: Data to write
        indent: Indentation level
    """
    # Ensure directory exists
    ensure_dir_exists(Path(file_path).parent)
    
    # Write file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent)

def list_files(directory: Union[str, Path], pattern: str = "*") -> List[Path]:
    """List files in a directory matching a pattern.
    
    Args:
        directory: Directory path
        pattern: Glob pattern
        
    Returns:
        List of matching file paths
    """
    return list(Path(directory).glob(pattern))

def copy_file(source: Union[str, Path], destination: Union[str, Path]) -> None:
    """Copy a file.
    
    Args:
        source: Source file path
        destination: Destination file path
    """
    # Ensure destination directory exists
    ensure_dir_exists(Path(destination).parent)
    
    # Copy file
    shutil.copy2(source, destination)

def get_requirements_input_dir() -> Path:
    """Get the directory for requirements input files.
    
    Returns:
        Path to the requirements input directory
    """
    # Determine the base data directory
    base_dir = Path(__file__).parents[3] / "data" / "requirements" / "input"
    return ensure_dir_exists(base_dir)

def get_requirements_output_dir() -> Path:
    """Get the directory for requirements output files.
    
    Returns:
        Path to the requirements output directory
    """
    # Determine the base data directory
    base_dir = Path(__file__).parents[3] / "data" / "requirements" / "output"
    return ensure_dir_exists(base_dir)

def get_project_requirements_dir(project_id: str, input_dir: bool = True) -> Path:
    """Get the directory for a project's requirements.
    
    Args:
        project_id: Project ID
        input_dir: Whether to get the input directory (True) or output directory (False)
        
    Returns:
        Path to the project's requirements directory
    """
    if input_dir:
        base_dir = get_requirements_input_dir()
    else:
        base_dir = get_requirements_output_dir()
    
    return ensure_dir_exists(base_dir / project_id)

def save_requirement_file(
    project_id: str,
    requirement_id: str,
    content: str,
    is_input: bool = True
) -> Path:
    """Save a requirement file.
    
    Args:
        project_id: Project ID
        requirement_id: Requirement ID
        content: File content
        is_input: Whether this is an input file (True) or output file (False)
        
    Returns:
        Path to the saved file
    """
    # Get the appropriate directory
    directory = get_project_requirements_dir(project_id, is_input)
    
    # Create file path
    file_path = directory / f"{requirement_id}.txt"
    
    # Write file
    write_text_file(file_path, content)
    
    return file_path

def load_requirement_file(
    project_id: str,
    requirement_id: str,
    is_input: bool = True
) -> str:
    """Load a requirement file.
    
    Args:
        project_id: Project ID
        requirement_id: Requirement ID
        is_input: Whether this is an input file (True) or output file (False)
        
    Returns:
        File content
    """
    # Get the appropriate directory
    directory = get_project_requirements_dir(project_id, is_input)
    
    # Create file path
    file_path = directory / f"{requirement_id}.txt"
    
    # Read file
    return read_text_file(file_path)

