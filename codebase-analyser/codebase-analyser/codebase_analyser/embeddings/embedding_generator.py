"""
Embedding generator module for code chunks.

This module provides functionality to generate embeddings for code chunks using
pre-trained models like CodeBERT.
"""

import os
import logging
import hashlib
import json
import torch
import numpy as np
from typing import List, Dict, Any, Optional, Union, Tuple
from pathlib import Path
from tqdm import tqdm

from transformers import AutoTokenizer, AutoModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generator for code embeddings using pre-trained models."""
    
    # Default models for different programming languages
    DEFAULT_MODELS = {
        "default": "microsoft/codebert-base",
        "java": "microsoft/codebert-base",
        "python": "microsoft/codebert-base",
        "javascript": "microsoft/codebert-base",
        "typescript": "microsoft/codebert-base",
        "go": "microsoft/codebert-base",
        "ruby": "microsoft/codebert-base",
        "php": "microsoft/codebert-base",
        "c": "microsoft/codebert-base",
        "cpp": "microsoft/codebert-base",
        "csharp": "microsoft/codebert-base"
    }
    
    def __init__(
        self,
        model_name: Optional[str] = None,
        cache_dir: Optional[str] = None,
        device: Optional[str] = None,
        max_length: int = 512,
        batch_size: int = 8,
        use_pooler_output: bool = True
    ):
        """Initialize the embedding generator.
        
        Args:
            model_name: Name of the pre-trained model to use (default: microsoft/codebert-base)
            cache_dir: Directory to cache the model and tokenizer
            device: Device to use for inference (default: cuda if available, else cpu)
            max_length: Maximum sequence length for tokenization
            batch_size: Batch size for inference
            use_pooler_output: Whether to use the pooler output (CLS token) for embeddings
        """
        self.model_name = model_name or self.DEFAULT_MODELS["default"]
        self.cache_dir = cache_dir
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.max_length = max_length
        self.batch_size = batch_size
        self.use_pooler_output = use_pooler_output
        
        # Initialize tokenizer and model
        self.tokenizer = None
        self.model = None
        
        # Cache for embeddings
        self.embedding_cache = {}
        self.embedding_cache_file = None
        if cache_dir:
            os.makedirs(cache_dir, exist_ok=True)
            self.embedding_cache_file = os.path.join(cache_dir, "embedding_cache.json")
            self._load_cache()
        
        logger.info(f"Initialized embedding generator with model {self.model_name} on {self.device}")
    
    def _load_model(self):
        """Load the tokenizer and model."""
        if self.tokenizer is None or self.model is None:
            logger.info(f"Loading tokenizer and model {self.model_name}...")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                cache_dir=self.cache_dir
            )
            
            # Load model
            self.model = AutoModel.from_pretrained(
                self.model_name,
                cache_dir=self.cache_dir
            )
            
            # Move model to device
            self.model = self.model.to(self.device)
            
            # Set model to evaluation mode
            self.model.eval()
            
            logger.info(f"Model loaded successfully")
    
    def _load_cache(self):
        """Load the embedding cache from disk."""
        if self.embedding_cache_file and os.path.exists(self.embedding_cache_file):
            try:
                with open(self.embedding_cache_file, 'r') as f:
                    cache_data = json.load(f)
                
                # Convert string keys back to tuples if needed
                self.embedding_cache = {
                    k: np.array(v) for k, v in cache_data.items()
                }
                
                logger.info(f"Loaded {len(self.embedding_cache)} embeddings from cache")
            except Exception as e:
                logger.error(f"Error loading embedding cache: {e}")
                self.embedding_cache = {}
    
    def _save_cache(self):
        """Save the embedding cache to disk."""
        if self.embedding_cache_file:
            try:
                # Convert numpy arrays to lists for JSON serialization
                cache_data = {
                    k: v.tolist() for k, v in self.embedding_cache.items()
                }
                
                with open(self.embedding_cache_file, 'w') as f:
                    json.dump(cache_data, f)
                
                logger.info(f"Saved {len(self.embedding_cache)} embeddings to cache")
            except Exception as e:
                logger.error(f"Error saving embedding cache: {e}")
    
    def _compute_hash(self, text: str) -> str:
        """Compute a hash for the input text.
        
        Args:
            text: Input text to hash
            
        Returns:
            Hash string
        """
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def generate_embedding(
        self,
        code: str,
        language: Optional[str] = None
    ) -> np.ndarray:
        """Generate an embedding for a single code snippet.
        
        Args:
            code: Code snippet to embed
            language: Programming language of the code
            
        Returns:
            Embedding vector as numpy array
        """
        # Use language-specific model if available
        if language and language in self.DEFAULT_MODELS and self.model_name == self.DEFAULT_MODELS["default"]:
            model_name = self.DEFAULT_MODELS[language]
            if model_name != self.model_name:
                logger.info(f"Using language-specific model {model_name} for {language}")
                self.model_name = model_name
                self.tokenizer = None
                self.model = None
        
        # Load model if not already loaded
        self._load_model()
        
        # Check cache
        code_hash = self._compute_hash(code)
        if code_hash in self.embedding_cache:
            return self.embedding_cache[code_hash]
        
        # Tokenize code
        inputs = self.tokenizer(
            code,
            return_tensors="pt",
            max_length=self.max_length,
            padding="max_length",
            truncation=True
        )
        
        # Move inputs to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Generate embedding
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # Get embedding from model output
        if self.use_pooler_output and hasattr(outputs, "pooler_output"):
            # Use CLS token embedding (pooler output)
            embedding = outputs.pooler_output.cpu().numpy()[0]
        else:
            # Use mean of last hidden state
            embedding = outputs.last_hidden_state.mean(dim=1).cpu().numpy()[0]
        
        # Normalize embedding
        embedding = embedding / np.linalg.norm(embedding)
        
        # Cache embedding
        self.embedding_cache[code_hash] = embedding
        
        return embedding
    
    def generate_embeddings_batch(
        self,
        codes: List[str],
        languages: Optional[List[str]] = None
    ) -> List[np.ndarray]:
        """Generate embeddings for a batch of code snippets.
        
        Args:
            codes: List of code snippets to embed
            languages: List of programming languages for each snippet
            
        Returns:
            List of embedding vectors
        """
        if not codes:
            return []
        
        # Use default language if not provided
        if languages is None:
            languages = [None] * len(codes)
        
        # Load model if not already loaded
        self._load_model()
        
        # Process in batches
        embeddings = []
        for i in range(0, len(codes), self.batch_size):
            batch_codes = codes[i:i+self.batch_size]
            batch_languages = languages[i:i+self.batch_size]
            
            # Check cache for each code snippet
            batch_embeddings = []
            uncached_indices = []
            uncached_codes = []
            
            for j, code in enumerate(batch_codes):
                code_hash = self._compute_hash(code)
                if code_hash in self.embedding_cache:
                    batch_embeddings.append(self.embedding_cache[code_hash])
                else:
                    batch_embeddings.append(None)
                    uncached_indices.append(j)
                    uncached_codes.append(code)
            
            # Generate embeddings for uncached code snippets
            if uncached_codes:
                # Tokenize code
                inputs = self.tokenizer(
                    uncached_codes,
                    return_tensors="pt",
                    max_length=self.max_length,
                    padding="max_length",
                    truncation=True
                )
                
                # Move inputs to device
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                # Generate embeddings
                with torch.no_grad():
                    outputs = self.model(**inputs)
                
                # Get embeddings from model output
                if self.use_pooler_output and hasattr(outputs, "pooler_output"):
                    # Use CLS token embeddings (pooler output)
                    uncached_embeddings = outputs.pooler_output.cpu().numpy()
                else:
                    # Use mean of last hidden state
                    uncached_embeddings = outputs.last_hidden_state.mean(dim=1).cpu().numpy()
                
                # Normalize embeddings
                for k in range(len(uncached_embeddings)):
                    uncached_embeddings[k] = uncached_embeddings[k] / np.linalg.norm(uncached_embeddings[k])
                
                # Update batch embeddings and cache
                for j, idx in enumerate(uncached_indices):
                    code_hash = self._compute_hash(batch_codes[idx])
                    batch_embeddings[idx] = uncached_embeddings[j]
                    self.embedding_cache[code_hash] = uncached_embeddings[j]
            
            embeddings.extend(batch_embeddings)
        
        # Save cache
        self._save_cache()
        
        return embeddings
    
    def generate_embeddings_for_chunks(
        self,
        chunks: List[Dict[str, Any]],
        content_field: str = "content",
        language_field: str = "language",
        embedding_field: str = "embedding"
    ) -> List[Dict[str, Any]]:
        """Generate embeddings for a list of code chunks.
        
        Args:
            chunks: List of code chunk dictionaries
            content_field: Field name for the code content
            language_field: Field name for the programming language
            embedding_field: Field name to store the embedding
            
        Returns:
            List of code chunks with embeddings added
        """
        if not chunks:
            return []
        
        # Extract code and language from chunks
        codes = []
        languages = []
        for chunk in chunks:
            codes.append(chunk.get(content_field, ""))
            languages.append(chunk.get(language_field))
        
        # Generate embeddings
        embeddings = self.generate_embeddings_batch(codes, languages)
        
        # Add embeddings to chunks
        for i, embedding in enumerate(embeddings):
            chunks[i][embedding_field] = embedding.tolist()
        
        return chunks
    
    def close(self):
        """Close the embedding generator and free resources."""
        # Save cache
        self._save_cache()
        
        # Free model and tokenizer
        self.model = None
        self.tokenizer = None
        
        # Clear CUDA cache if using GPU
        if self.device == "cuda":
            torch.cuda.empty_cache()
        
        logger.info("Embedding generator closed")
