"""
Embedding generator for code chunks.
"""
import logging
import numpy as np
from typing import List, Optional, Union, Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

# Try to import SentenceTransformer
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMER_AVAILABLE = True
    logger.info("SentenceTransformer is available")
except ImportError:
    SENTENCE_TRANSFORMER_AVAILABLE = False
    logger.warning("SentenceTransformer is not available")

# Default model name
DEFAULT_MODEL_NAME = "all-MiniLM-L6-v2"

# Global model instance
_model = None

def get_model(model_name: str = DEFAULT_MODEL_NAME) -> Any:
    """
    Get or initialize the embedding model.
    
    Args:
        model_name: Name of the model to use
        
    Returns:
        The embedding model
    """
    global _model
    
    if _model is None:
        if SENTENCE_TRANSFORMER_AVAILABLE:
            try:
                _model = SentenceTransformer(model_name)
                logger.info(f"Initialized SentenceTransformer model: {model_name}")
            except Exception as e:
                logger.error(f"Error initializing SentenceTransformer: {e}")
                _model = None
        else:
            raise ImportError("SentenceTransformer is required but not available. Install with: pip install sentence-transformers")
    
    return _model

def generate_embedding(text: str, model_name: str = DEFAULT_MODEL_NAME) -> List[float]:
    """
    Generate an embedding for the given text.
    
    Args:
        text: The text to embed
        model_name: Name of the model to use
        
    Returns:
        The embedding vector
    """
    if not text:
        # Return a zero vector for empty text
        return [0.0] * 384  # Default dimension for small models
    
    if not SENTENCE_TRANSFORMER_AVAILABLE:
        raise ImportError("SentenceTransformer is required but not available. Install with: pip install sentence-transformers")
    
    model = get_model(model_name)
    if not model:
        raise RuntimeError("Failed to initialize SentenceTransformer model")
    
    # Generate embedding
    embedding = model.encode(text)
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
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return float(np.dot(a, b) / (norm_a * norm_b))

class EmbeddingGenerator:
    """Class for generating embeddings for code chunks."""
    
    def __init__(self, model_name: str = DEFAULT_MODEL_NAME):
        """
        Initialize the embedding generator.
        
        Args:
            model_name: Name of the model to use
        """
        self.model_name = model_name
        # Initialize the model at creation time to catch errors early
        if SENTENCE_TRANSFORMER_AVAILABLE:
            self.model = get_model(model_name)
        else:
            raise ImportError("SentenceTransformer is required but not available. Install with: pip install sentence-transformers")
    
    def generate(self, text: str) -> List[float]:
        """
        Generate an embedding for the given text.
        
        Args:
            text: The text to embed
            
        Returns:
            The embedding vector
        """
        return generate_embedding(text, self.model_name)
    
    def batch_generate(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts efficiently.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        if not SENTENCE_TRANSFORMER_AVAILABLE:
            raise ImportError("SentenceTransformer is required but not available")
        
        # Handle empty texts
        embeddings = []
        non_empty_indices = []
        non_empty_texts = []
        
        for i, text in enumerate(texts):
            if not text:
                embeddings.append([0.0] * 384)  # Default dimension
            else:
                non_empty_indices.append(i)
                non_empty_texts.append(text)
        
        if non_empty_texts:
            # Generate embeddings in batch for efficiency
            batch_embeddings = self.model.encode(non_empty_texts)
            
            # Place embeddings in the correct positions
            for i, idx in enumerate(non_empty_indices):
                while len(embeddings) <= idx:
                    embeddings.append(None)
                embeddings[idx] = batch_embeddings[i].tolist()
        
        return embeddings
    
    def compare(self, text1: str, text2: str) -> float:
        """
        Compare two texts by their embeddings.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between 0 and 1
        """
        embedding1 = self.generate(text1)
        embedding2 = self.generate(text2)
        return cosine_similarity(embedding1, embedding2)
