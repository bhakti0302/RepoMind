#!/usr/bin/env python3
"""
Test script for LLM functionality with a hardcoded API key.
"""

import os
import sys
import asyncio
import logging
import subprocess
from pathlib import Path

# Add parent directory to path to import codebase_analyser
sys.path.append(str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def install_package(package):
    """Install a package using pip."""
    try:
        logger.info(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        logger.info(f"Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install {package}: {e}")
        return False

async def test_llm():
    """Test the LLM functionality."""
    # Set the OpenRouter API key
    os.environ["OPENROUTER_API_KEY"] = "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"
    
    # Try to import required packages, install if missing
    try:
        from langchain_openai import ChatOpenAI
    except ImportError:
        logger.warning("langchain_openai not found, attempting to install...")
        if not install_package("langchain-openai"):
            logger.error("Failed to install langchain-openai. Please install it manually.")
            return
        # Try importing again
        try:
            from langchain_openai import ChatOpenAI
        except ImportError:
            logger.error("Still cannot import langchain_openai after installation. Please check your Python environment.")
            return
    
    try:
        from langchain.prompts import PromptTemplate
    except ImportError:
        logger.warning("langchain not found, attempting to install...")
        if not install_package("langchain"):
            logger.error("Failed to install langchain. Please install it manually.")
            return
        # Try importing again
        try:
            from langchain.prompts import PromptTemplate
        except ImportError:
            logger.error("Still cannot import langchain after installation. Please check your Python environment.")
            return
    
    try:
        from langchain_core.output_parsers import StrOutputParser
    except ImportError:
        logger.warning("langchain_core not found, attempting to install...")
        if not install_package("langchain-core"):
            logger.error("Failed to install langchain-core. Please install it manually.")
            return
        # Try importing again
        try:
            from langchain_core.output_parsers import StrOutputParser
        except ImportError:
            logger.error("Still cannot import langchain_core after installation. Please check your Python environment.")
            return
    
    # Create the LLM instance directly
    try:
        llm = ChatOpenAI(
            model="nvidia/llama-3.3-nemotron-super-49b-v1:free",
            temperature=0.2,
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ["OPENROUTER_API_KEY"]
        )
    except Exception as e:
        logger.error(f"Error creating ChatOpenAI instance: {e}")
        return
    
    # Create a simple prompt
    prompt = PromptTemplate.from_template(
        """
        You are a helpful assistant.
        
        Please answer the following question concisely:
        {question}
        """
    )
    
    # Create the chain
    chain = prompt | llm | StrOutputParser()
    
    # Test questions
    test_questions = [
        "What is the capital of France?",
        "Explain what a linked list is in computer science.",
        "Write a simple Python function to calculate the factorial of a number."
    ]
    
    for question in test_questions:
        logger.info(f"\n\n=== Testing question: {question} ===")
        
        try:
            # Run the chain
            response = await chain.ainvoke({"question": question})
            
            # Print the response
            logger.info(f"Response:\n{response}")
            
        except Exception as e:
            logger.error(f"Error getting response: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            logger.error(f"Error details: {e.__dict__ if hasattr(e, '__dict__') else 'No details'}")
        
        logger.info("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_llm())
