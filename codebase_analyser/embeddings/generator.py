"""
Embedding model generator for code embeddings.

This module provides functionality to generate embeddings for code snippets
using various embedding models, with support for different model types and
caching for performance optimization.
"""
import logging
import os
from typing import Dict, List, Optional, Union, Any
from functools import lru_cache
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
    logger.info("SentenceTransformer is available")
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("SentenceTransformer is not available, will use mock embeddings")

# Default model configurations
DEFAULT_MODEL_NAME = "all-MiniLM-L6-v2"
DEFAULT_EMBEDDING_DIM = 384

# Global model cache
_model_cache = {}


def get_embedding_model(
    model_name: Optional[str] = None,
    force_reload: bool = False
) -> Optional[Any]:
    """Get or load an embedding model.
    
    Args:
        model_name: Name of the model to use (default: all-MiniLM-L6-v2)
        force_reload: Whether to force reload the model even if cached
        
    Returns:
        The embedding model or None if not available
    """
    # Use environment variable or default
    model_name = model_name or os.environ.get("EMBEDDING_MODEL", DEFAULT_MODEL_NAME)
    
    # Check cache first if not forcing reload
    if not force_reload and model_name in _model_cache:
        logger.debug(f"Using cached model: {model_name}")
        return _model_cache[model_name]
    
    # Load the model
    if SENTENCE_TRANSFORMERS_AVAILABLE:
        try:
            logger.info(f"Loading embedding model: {model_name}")
            model = SentenceTransformer(model_name)
            _model_cache[model_name] = model
            return model
        except Exception as e:
            logger.error(f"Error loading embedding model {model_name}: {e}")
            return None
    else:
        logger.warning(f"SentenceTransformer not available, cannot load {model_name}")
        return None


@lru_cache(maxsize=1024)
def generate_embedding(
    text: str,
    model_name: Optional[str] = None,
    normalize: bool = True
) -> List[float]:
    """Generate an embedding for the given text.
    
    Args:
        text: The text to embed
        model_name: Name of the model to use (default: all-MiniLM-L6-v2)
        normalize: Whether to normalize the embedding vector
        
    Returns:
        The embedding vector as a list of floats
    """
    # Get the model
    model = get_embedding_model(model_name)
    
    # Generate embedding
    if model is not None:
        try:
            # Generate the embedding
            embedding = model.encode(text)
            
            # Normalize if requested
            if normalize and np.linalg.norm(embedding) > 0:
                embedding = embedding / np.linalg.norm(embedding)
            
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
    
    # Fall back to mock embedding if model is not available or error occurred
    logger.warning("Using mock embedding")
    mock_embedding = np.random.randn(DEFAULT_EMBEDDING_DIM)
    
    # Normalize if requested
    if normalize and np.linalg.norm(mock_embedding) > 0:
        mock_embedding = mock_embedding / np.linalg.norm(mock_embedding)
    
    return mock_embedding.tolist()


def batch_generate_embeddings(
    texts: List[str],
    model_name: Optional[str] = None,
    normalize: bool = True,
    batch_size: int = 32,
    show_progress: bool = False
) -> List[List[float]]:
    """Generate embeddings for a batch of texts.
    
    Args:
        texts: List of texts to embed
        model_name: Name of the model to use
        normalize: Whether to normalize the embedding vectors
        batch_size: Size of batches for processing
        show_progress: Whether to show a progress bar
        
    Returns:
        List of embedding vectors
    """
    # Get the model
    model = get_embedding_model(model_name)
    
    # Generate embeddings
    if model is not None:
        try:
            # Import tqdm if showing progress
            if show_progress:
                try:
                    from tqdm import tqdm
                    texts_iter = tqdm(texts, desc="Generating embeddings")
                except ImportError:
                    texts_iter = texts
                    logger.warning("tqdm not available, not showing progress")
            else:
                texts_iter = texts
            
            # Process in batches
            all_embeddings = []
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i+batch_size]
                batch_embeddings = model.encode(batch)
                
                # Normalize if requested
                if normalize:
                    for j, emb in enumerate(batch_embeddings):
                        norm = np.linalg.norm(emb)
                        if norm > 0:
                            batch_embeddings[j] = emb / norm
                
                all_embeddings.extend(batch_embeddings.tolist())
            
            return all_embeddings
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
    
    # Fall back to mock embeddings
    logger.warning("Using mock embeddings for batch")
    mock_embeddings = [generate_embedding(text, model_name, normalize) for text in texts]
    return mock_embeddings


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors.
    
    Args:
        vec1: First vector
        vec2: Second vector
        
    Returns:
        Cosine similarity (between -1 and 1)
    """
    # Convert to numpy arrays
    a = np.array(vec1)
    b = np.array(vec2)
    
    # Calculate cosine similarity
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return np.dot(a, b) / (norm_a * norm_b)
