"""
Environment Loader module.

This module provides functionality for loading environment variables from a .env file.
"""

import os
import sys
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def find_env_file(start_dir: str = None) -> Optional[str]:
    """Find the .env file by traversing up the directory tree.
    
    Args:
        start_dir: Directory to start the search from
        
    Returns:
        Path to the .env file or None if not found
    """
    # Start from the current directory if not specified
    current_dir = Path(start_dir or os.getcwd())
    
    # Traverse up the directory tree
    while current_dir != current_dir.parent:
        env_file = current_dir / '.env'
        if env_file.exists():
            return str(env_file)
        current_dir = current_dir.parent
    
    return None

def load_env_file(env_file: str) -> Dict[str, str]:
    """Load environment variables from a .env file.
    
    Args:
        env_file: Path to the .env file
        
    Returns:
        Dictionary of environment variables
    """
    env_vars = {}
    
    try:
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse key-value pairs
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes if present
                    if value and value[0] == value[-1] and value[0] in ('"', "'"):
                        value = value[1:-1]
                    
                    env_vars[key] = value
    
    except Exception as e:
        logger.error(f"Error loading .env file: {e}")
    
    return env_vars

def load_env_vars(env_file: str = None) -> Dict[str, str]:
    """Load environment variables from a .env file and set them in the environment.
    
    Args:
        env_file: Path to the .env file
        
    Returns:
        Dictionary of loaded environment variables
    """
    # Find the .env file if not specified
    if not env_file:
        env_file = find_env_file()
    
    if not env_file:
        logger.warning("No .env file found")
        return {}
    
    # Load environment variables
    env_vars = load_env_file(env_file)
    
    # Set environment variables
    for key, value in env_vars.items():
        if key not in os.environ:
            os.environ[key] = value
    
    logger.info(f"Loaded {len(env_vars)} environment variables from {env_file}")
    
    return env_vars

def get_env_var(key: str, default: Any = None) -> Any:
    """Get an environment variable.
    
    Args:
        key: Environment variable key
        default: Default value if the key is not found
        
    Returns:
        Environment variable value or default
    """
    return os.environ.get(key, default)


# Load environment variables when the module is imported
load_env_vars()

# Example usage
if __name__ == "__main__":
    # Load environment variables
    env_vars = load_env_vars()
    
    # Print loaded environment variables
    print("Loaded environment variables:")
    for key, value in env_vars.items():
        # Mask sensitive information
        if 'KEY' in key or 'SECRET' in key or 'PASSWORD' in key:
            masked_value = value[:3] + '*' * (len(value) - 6) + value[-3:] if len(value) > 6 else '******'
            print(f"  {key}: {masked_value}")
        else:
            print(f"  {key}: {value}")
    
    # Get a specific environment variable
    llm_api_key = get_env_var('LLM_API_KEY')
    if llm_api_key:
        masked_key = llm_api_key[:3] + '*' * (len(llm_api_key) - 6) + llm_api_key[-3:] if len(llm_api_key) > 6 else '******'
        print(f"\nLLM API Key: {masked_key}")
    else:
        print("\nLLM API Key not found")
