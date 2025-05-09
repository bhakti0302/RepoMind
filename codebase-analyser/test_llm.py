#!/usr/bin/env python3
"""
Test script for LLM functionality.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add parent directory to path to import codebase_analyser
sys.path.append(str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def test_llm():
    """Test the LLM functionality."""
    # Import after logging is configured
    from langchain.prompts import PromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    
    # Set OpenRouter API key if not already set
    if not os.environ.get("OPENROUTER_API_KEY"):
        api_key = input("Enter your OpenRouter API key: ")
        os.environ["OPENROUTER_API_KEY"] = api_key
    
    # Import LLM after setting API key
    from codebase_analyser.agent.nodes.llm_nodes import llm, LLM_AVAILABLE
    
    if not LLM_AVAILABLE or not llm:
        logger.error("LLM is not available. Please check your API key and dependencies.")
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
        
        logger.info("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_llm())