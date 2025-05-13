"""
Utility functions for NLP analysis.

This module provides utility functions for NLP analysis of business requirements.
"""

import os
import re
import json
import logging
from typing import Dict, List, Any, Optional, Union, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def ensure_dir(directory: str) -> bool:
    """Ensure that a directory exists.
    
    Args:
        directory: Directory path
        
    Returns:
        True if the directory exists or was created, False otherwise
    """
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Created directory: {directory}")
        return True
    except Exception as e:
        logger.error(f"Error creating directory {directory}: {e}")
        return False

def save_json(data: Dict[str, Any], file_path: str, indent: int = 2) -> bool:
    """Save data to a JSON file.
    
    Args:
        data: Data to save
        file_path: Path to the output file
        indent: Indentation level for JSON formatting
        
    Returns:
        True if the file was saved successfully, False otherwise
    """
    try:
        # Ensure the directory exists
        directory = os.path.dirname(file_path)
        if directory and not ensure_dir(directory):
            return False
        
        # Save the data to a JSON file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent)
        
        logger.info(f"Saved data to {file_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error saving data to {file_path}: {e}")
        return False

def load_json(file_path: str) -> Dict[str, Any]:
    """Load data from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Loaded data or empty dict if the file doesn't exist or is invalid
    """
    try:
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            return {}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"Loaded data from {file_path}")
        return data
    
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}")
        return {}

def extract_code_identifiers(text: str) -> List[str]:
    """Extract code identifiers from text.
    
    Args:
        text: Input text
        
    Returns:
        List of extracted code identifiers
    """
    try:
        # Match camelCase, PascalCase, snake_case, and dot-separated identifiers
        patterns = [
            r'[a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*',  # dot-separated
            r'[a-z][a-z0-9]*(?:[A-Z][a-z0-9]*)+',  # camelCase
            r'[A-Z][a-z0-9]*(?:[A-Z][a-z0-9]*)+',  # PascalCase
            r'[a-z][a-z0-9]*(?:_[a-z][a-z0-9]*)+',  # snake_case
        ]
        
        identifiers = []
        for pattern in patterns:
            identifiers.extend(re.findall(pattern, text))
        
        # Remove duplicates while preserving order
        seen = set()
        unique_identifiers = [
            identifier for identifier in identifiers
            if not (identifier in seen or seen.add(identifier))
        ]
        
        return unique_identifiers
    
    except Exception as e:
        logger.error(f"Error extracting code identifiers: {e}")
        return []

def extract_requirements_by_type(text: str) -> Dict[str, List[str]]:
    """Extract requirements by type from text.
    
    Args:
        text: Input text
        
    Returns:
        Dictionary containing requirements by type
    """
    try:
        # Split text into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # Initialize requirements by type
        requirements = {
            "functional": [],
            "non_functional": [],
            "constraints": [],
            "other": []
        }
        
        # Keywords for non-functional requirements
        nfr_keywords = [
            "performance", "security", "reliability", "usability", "maintainability",
            "scalability", "availability", "efficiency", "portability", "testability",
            "fast", "secure", "reliable", "user-friendly", "maintainable", "scalable",
            "available", "efficient", "portable", "testable"
        ]
        
        # Keywords for constraints
        constraint_keywords = [
            "must", "should", "shall", "will", "won't", "cannot", "can't",
            "never", "always", "only", "if", "when", "unless", "until"
        ]
        
        # Classify each sentence
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            sentence_lower = sentence.lower()
            
            # Check for non-functional requirements
            if any(keyword in sentence_lower for keyword in nfr_keywords):
                requirements["non_functional"].append(sentence)
            
            # Check for constraints
            elif any(keyword in sentence_lower for keyword in constraint_keywords):
                requirements["constraints"].append(sentence)
            
            # Check for functional requirements (contains a verb)
            elif re.search(r'\b(?:is|are|was|were|be|being|been|do|does|did|have|has|had|can|could|will|would|shall|should|may|might|must)\b', sentence_lower):
                requirements["functional"].append(sentence)
            
            # Other requirements
            else:
                requirements["other"].append(sentence)
        
        return requirements
    
    except Exception as e:
        logger.error(f"Error extracting requirements by type: {e}")
        return {
            "functional": [],
            "non_functional": [],
            "constraints": [],
            "other": []
        }

def generate_search_queries(requirements: Dict[str, List[str]], max_queries: int = 5) -> List[str]:
    """Generate search queries from requirements.
    
    Args:
        requirements: Requirements by type
        max_queries: Maximum number of queries to generate
        
    Returns:
        List of search queries
    """
    try:
        queries = []
        
        # Prioritize functional requirements
        for req in requirements["functional"]:
            # Extract code identifiers
            identifiers = extract_code_identifiers(req)
            
            if identifiers:
                # Use identifiers as queries
                queries.extend(identifiers)
            else:
                # Use the whole requirement as a query
                queries.append(req)
        
        # Add non-functional requirements
        for req in requirements["non_functional"]:
            queries.append(req)
        
        # Add constraints
        for req in requirements["constraints"]:
            queries.append(req)
        
        # Limit the number of queries
        return queries[:max_queries]
    
    except Exception as e:
        logger.error(f"Error generating search queries: {e}")
        return []


# Example usage
if __name__ == "__main__":
    # Example text
    example_text = """
    The UserService class should implement the authenticate method.
    The system must validate user_credentials before granting access.
    The response time should be less than 500ms for all API calls.
    If authentication fails, the system should return a 401 status code.
    """
    
    # Extract requirements by type
    requirements = extract_requirements_by_type(example_text)
    print("Requirements by Type:")
    for req_type, reqs in requirements.items():
        print(f"\n{req_type.capitalize()}:")
        for req in reqs:
            print(f"  - {req}")
    
    # Extract code identifiers
    identifiers = extract_code_identifiers(example_text)
    print("\nCode Identifiers:")
    for identifier in identifiers:
        print(f"  - {identifier}")
    
    # Generate search queries
    queries = generate_search_queries(requirements)
    print("\nSearch Queries:")
    for query in queries:
        print(f"  - {query}")
