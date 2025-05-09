#!/usr/bin/env python3
"""
Script to set the OpenRouter API key in all necessary places.
"""
import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def set_api_key(api_key):
    """Set the OpenRouter API key in the environment and update relevant files."""
    # Set the API key in the environment
    os.environ["OPENROUTER_API_KEY"] = api_key
    logger.info("Set OPENROUTER_API_KEY in the environment")
    
    # Update run_test.py
    run_test_path = Path(__file__).parent / "run_test.py"
    if run_test_path.exists():
        with open(run_test_path, "r") as f:
            content = f.read()
        
        # Replace the API key
        if 'os.environ["OPENROUTER_API_KEY"] = ' in content:
            content = content.replace(
                'os.environ["OPENROUTER_API_KEY"] = "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"',
                f'os.environ["OPENROUTER_API_KEY"] = "{api_key}"'
            )
            
            with open(run_test_path, "w") as f:
                f.write(content)
            logger.info(f"Updated API key in {run_test_path}")
    
    # Update test_agent.py
    test_agent_path = Path(__file__).parent / "test_agent.py"
    if test_agent_path.exists():
        with open(test_agent_path, "r") as f:
            content = f.read()
        
        # Replace the API key
        if 'os.environ["OPENROUTER_API_KEY"] = ' in content:
            content = content.replace(
                'os.environ["OPENROUTER_API_KEY"] = "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"',
                f'os.environ["OPENROUTER_API_KEY"] = "{api_key}"'
            )
            
            with open(test_agent_path, "w") as f:
                f.write(content)
            logger.info(f"Updated API key in {test_agent_path}")
    
    # Create a .env file
    env_path = Path(__file__).parent / ".env"
    with open(env_path, "w") as f:
        f.write(f"OPENROUTER_API_KEY={api_key}\n")
        f.write("OPENROUTER_MODEL=nvidia/llama-3.3-nemotron-super-49b-v1:free\n")
    logger.info(f"Created .env file at {env_path}")
    
    # Create a script to load the API key
    load_env_path = Path(__file__).parent / "load_env.py"
    with open(load_env_path, "w") as f:
        f.write("""#!/usr/bin/env python3
\"\"\"
Script to load environment variables from .env file.
\"\"\"
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"Loaded environment variables from {env_path}")
else:
    print(f"Warning: .env file not found at {env_path}")

# Check if OPENROUTER_API_KEY is set
if "OPENROUTER_API_KEY" in os.environ:
    print("OPENROUTER_API_KEY is set")
else:
    print("Warning: OPENROUTER_API_KEY is not set")
""")
    logger.info(f"Created load_env.py script at {load_env_path}")
    
    # Make the script executable
    os.chmod(load_env_path, 0o755)
    
    logger.info("API key has been set in all necessary places")
    logger.info("You can now run the tests with the API key")

if __name__ == "__main__":
    # Get the API key from command line or use the default
    api_key = sys.argv[1] if len(sys.argv) > 1 else "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"
    
    set_api_key(api_key)