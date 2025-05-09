"""
Standalone test script for the RAG nodes.
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create a minimal state class for testing
class AgentState:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def dict(self):
        return self.__dict__

# Import the functions we want to test
from codebase_analyser.agent.nodes.rag_nodes import (
    get_embedding,
    cosine_similarity,
    score_relevance,
    refine_query_with_context
)

async def test_rag_functions():
    """Test basic RAG functions."""
    logger.info("Testing basic RAG functions")
    
    # Test cosine_similarity
    vec1 = [1.0, 0.0, 0.0]
    vec2 = [1.0, 0.0, 0.0]
    similarity = cosine_similarity(vec1, vec2)
    logger.info(f"Cosine similarity between identical vectors: {similarity}")
    
    # Test refine_query_with_context
    context = [
        {
            "name": "TestClass",
            "qualified_name": "com.example.TestClass",
            "chunk_type": "class"
        },
        {
            "name": "AnotherClass",
            "qualified_name": "com.example.AnotherClass",
            "chunk_type": "class"
        }
    ]
    
    original_query = "How to implement a data exporter"
    refined_query = refine_query_with_context(original_query, context)
    logger.info(f"Original query: {original_query}")
    logger.info(f"Refined query: {refined_query}")
    
    logger.info("RAG functions test completed")

if __name__ == "__main__":
    asyncio.run(test_rag_functions())