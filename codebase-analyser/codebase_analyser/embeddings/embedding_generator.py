"""
Embedding generator for code chunks.
"""

import logging
import numpy as np
from typing import List, Optional, Any, Union

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generator for code embeddings."""
    
    def __init__(
        self,
        model_name: str = "BAAI/bge-small-en-v1.5",
        cache_dir: Optional[str] = None,
        batch_size: int = 8
    ):
        """Initialize the embedding generator.
        
        Args:
            model_name: Name of the model to use
            cache_dir: Directory to cache the model
            batch_size: Batch size for embedding generation
        """
        self.model_name = model_name
        self.cache_dir = cache_dir
        self.batch_size = batch_size
        
        # Initialize the model
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name, cache_folder=cache_dir)
            logger.info(f"Loaded embedding model: {model_name}")
        except ImportError:
            logger.warning("sentence-transformers not installed. Using mock embeddings.")
            self.model = None
    
    def generate_embedding(self, content: str, language: str) -> np.ndarray:
        """Generate an embedding for a code chunk.
        
        Args:
            content: Content of the code chunk
            language: Programming language of the code chunk
            
        Returns:
            Embedding as a numpy array
        """
        if self.model is None:
            # Generate a mock embedding
            embedding = np.random.randn(768).astype(np.float32)
            # Normalize the embedding
            embedding = embedding / np.linalg.norm(embedding)
            return embedding
        
        # Generate the embedding
        embedding = self.model.encode(content, normalize_embeddings=True)
        return embedding
    
    def generate_embeddings_batch(self, contents: List[str], languages: List[str]) -> List[np.ndarray]:
        """Generate embeddings for a batch of code chunks.
        
        Args:
            contents: List of code chunk contents
            languages: List of programming languages
            
        Returns:
            List of embeddings as numpy arrays
        """
        if self.model is None:
            # Generate mock embeddings
            embeddings = []
            for _ in range(len(contents)):
                embedding = np.random.randn(768).astype(np.float32)
                embedding = embedding / np.linalg.norm(embedding)
                embeddings.append(embedding)
            return embeddings
        
        # Generate the embeddings
        embeddings = self.model.encode(contents, normalize_embeddings=True)
        return embeddings
    
    def close(self) -> None:
        """Close the embedding generator."""
        # Nothing to do for SentenceTransformer
        pass
