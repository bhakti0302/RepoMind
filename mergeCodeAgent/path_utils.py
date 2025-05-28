"""
Utility functions for path handling in the Merge Code Agent.
"""

import os
import re

def normalize_path(path, base_path=None):
    """
    Normalize a path and remove any duplicated segments.
    
    Args:
        path: The path to normalize
        base_path: Optional base path to check for duplication
        
    Returns:
        Normalized path without duplications
    """
    if not path:
        return path
        
    # First, normalize the path to handle . and .. segments
    normalized = os.path.normpath(path)
    
    # If no base_path provided, just return the normalized path
    if not base_path:
        return normalized
    
    # Handle case sensitivity by using lowercase for comparison
    base_lower = base_path.lower()
    path_lower = normalized.lower()
    
    # Special handling for the common "Users/" vs "/Users/" issue
    if not os.path.isabs(normalized) and normalized.lower().startswith('users/'):
        # Add leading slash to make it absolute
        with_slash = '/' + normalized
        if os.path.normpath(with_slash).lower().startswith(base_lower):
            print(f"Fixed path missing leading slash: {normalized} -> {with_slash}")
            normalized = with_slash
            path_lower = normalized.lower()  # Update for subsequent checks
            
    # Handle paths that contain the base path more than once (duplicated segments)
    if path_lower.count(base_lower.rstrip('/\\')) > 1:
        print(f"Detected duplicated base path in: {normalized}")
        
        # Find the position of the first occurrence of base_path
        pos = path_lower.find(base_lower)
        if pos >= 0:
            # Get everything after the first occurrence of base_path
            suffix = normalized[pos + len(base_path):]
            # Find the position of the second occurrence of base_path in the suffix
            second_pos = suffix.lower().find(base_lower.lstrip('/'))
            if second_pos >= 0:
                # Everything after the second occurrence
                final_suffix = suffix[second_pos + len(base_lower.lstrip('/')):]
                # Combine the base path with the final suffix
                result = os.path.join(base_path, final_suffix.lstrip('/\\'))
                print(f"Removing duplication: {normalized} -> {result}")
                return os.path.normpath(result)
            
    # Handle the case where the path starts with a subset of base_path elements
    # This catches cases like path="Users/username/project/file" and base_path="/Users/username/project"
    if not os.path.isabs(normalized) and base_lower.startswith('/'):
        # Strip leading slash from base_path for comparison
        base_no_slash = base_lower[1:]
        
        # Check if the path starts with the base_path without the leading slash
        if path_lower.startswith(base_no_slash):
            # Get the remainder of the path after the base_path
            remainder = normalized[len(base_no_slash):].lstrip('/\\')
            
            # Reconstruct the path with the base_path
            result = os.path.join(base_path, remainder)
            print(f"Fixed path with missing leading slash: {normalized} -> {result}")
            return os.path.normpath(result)
            
    # If base_path is an absolute path and our path is relative but contains base elements
    # Extract the common parts to prevent duplication when joining
    if os.path.isabs(base_path) and not os.path.isabs(normalized):
        # Check if the relative path includes elements from the base path
        base_parts = os.path.normpath(base_path).split(os.sep)
        path_parts = normalized.split(os.sep)
        
        # Look for overlapping parts at the beginning of the path
        overlap = 0
        for i, part in enumerate(path_parts):
            if i < len(base_parts) and part.lower() == base_parts[i].lower():
                overlap += 1
            else:
                break
        
        if overlap > 0:
            # If we found overlapping parts, remove them from the relative path
            clean_path = os.path.join(*path_parts[overlap:])
            result = os.path.join(base_path, clean_path)
            print(f"Removing overlapping segments: {normalized} -> {result}")
            return os.path.normpath(result)
    
    # If the path is not absolute and doesn't contain the base path already,
    # join it with the base path
    if not os.path.isabs(normalized) and base_lower not in path_lower:
        result = os.path.join(base_path, normalized)
        return os.path.normpath(result)
    
    return normalized 