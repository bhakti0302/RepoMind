"""
Minimal standalone test script for RAG-like functionality.
"""
import logging
import numpy as np
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def mock_generate_embedding(text: str) -> List[float]:
    """
    Generate a mock embedding for testing purposes.
    
    Args:
        text: The text to embed
        
    Returns:
        A mock embedding vector
    """
    # Create a deterministic but unique embedding based on the text
    np.random.seed(hash(text) % 2**32)
    embedding = np.random.randn(384)  # 384 dimensions is common for small models
    
    # Normalize the embedding
    if np.linalg.norm(embedding) > 0:
        embedding = embedding / np.linalg.norm(embedding)
    
    return embedding.tolist()

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        vec1: First vector
        vec2: Second vector
        
    Returns:
        Cosine similarity score
    """
    if not vec1 or not vec2:
        return 0.0
    
    # Convert to numpy arrays
    a = np.array(vec1)
    b = np.array(vec2)
    
    # Calculate cosine similarity
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def score_relevance(chunk: Dict[str, Any], query: str, query_embedding: Optional[List[float]] = None) -> float:
    """
    Score the relevance of a code chunk to a query.
    
    Args:
        chunk: The code chunk to score
        query: The search query
        query_embedding: Optional pre-computed query embedding
        
    Returns:
        Relevance score between 0 and 1
    """
    try:
        # Get the query embedding if not provided
        if query_embedding is None:
            query_embedding = mock_generate_embedding(query)
        
        # Get the chunk embedding
        chunk_embedding = chunk.get("embedding", [])
        if not chunk_embedding:
            # Generate an embedding if not available
            content = chunk.get("content", "")
            chunk_embedding = mock_generate_embedding(content)
        
        # Calculate cosine similarity
        similarity = cosine_similarity(query_embedding, chunk_embedding)
        
        # Adjust score based on other factors
        score = similarity
        
        # Boost score for exact matches in content
        content = chunk.get("content", "").lower()
        if query.lower() in content:
            score += 0.1
        
        # Boost score for matches in name or qualified_name
        name = chunk.get("name", "").lower()
        qualified_name = chunk.get("qualified_name", "").lower()
        if query.lower() in name or query.lower() in qualified_name:
            score += 0.2
        
        # Cap the score at 1.0
        return min(score, 1.0)
    except Exception as e:
        logger.error(f"Error scoring relevance: {e}")
        return 0.0

def refine_query_with_context(query: str, context: List[Dict[str, Any]]) -> str:
    """
    Refine a query with context from previous results.
    
    Args:
        query: The original query
        context: Context from previous results
        
    Returns:
        Refined query
    """
    # Extract relevant terms from the context
    terms = []
    
    for item in context:
        # Add the name if available
        if "name" in item:
            terms.append(item["name"])
        
        # Add the qualified name if available
        if "qualified_name" in item:
            terms.append(item["qualified_name"].split(".")[-1])  # Just the last part
        
        # Add the chunk type if available
        if "chunk_type" in item:
            terms.append(item["chunk_type"])
    
    # Remove duplicates and join with the original query
    unique_terms = list(set(terms))
    
    if unique_terms:
        refined_query = f"{query} {' '.join(unique_terms)}"
    else:
        refined_query = query
    
    return refined_query

def test_rag_functions():
    """Test basic RAG functions."""
    logger.info("Testing basic RAG functions")
    
    # Test cosine_similarity
    vec1 = [1.0, 0.0, 0.0]
    vec2 = [1.0, 0.0, 0.0]
    similarity = cosine_similarity(vec1, vec2)
    logger.info(f"Cosine similarity between identical vectors: {similarity}")
    
    # Test with orthogonal vectors
    vec1 = [1.0, 0.0, 0.0]
    vec2 = [0.0, 1.0, 0.0]
    similarity = cosine_similarity(vec1, vec2)
    logger.info(f"Cosine similarity between orthogonal vectors: {similarity}")
    
    # Test mock_generate_embedding
    query = "How to implement a data exporter"
    embedding = mock_generate_embedding(query)
    logger.info(f"Generated mock embedding with {len(embedding)} dimensions")
    
    # Test score_relevance
    chunk = {
        "name": "DataExporter",
        "qualified_name": "com.example.DataExporter",
        "chunk_type": "class",
        "content": "public class DataExporter implements Exporter { ... }",
        "embedding": mock_generate_embedding("public class DataExporter implements Exporter { ... }")
    }
    
    relevance = score_relevance(chunk, query)
    logger.info(f"Relevance score for '{chunk['name']}': {relevance}")
    
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
    
    refined_query = refine_query_with_context(query, context)
    logger.info(f"Original query: {query}")
    logger.info(f"Refined query: {refined_query}")
    
    logger.info("RAG functions test completed")

if __name__ == "__main__":
    test_rag_functions()