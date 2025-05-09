"""
Embeddings package for code embeddings.

This package provides functionality for generating and working with code embeddings,
including model loading, embedding generation, and similarity calculations.
"""

from .generator import (
    get_embedding_model,
    generate_embedding,
    batch_generate_embeddings,
    cosine_similarity
)

__all__ = [
    'get_embedding_model',
    'generate_embedding',
    'batch_generate_embeddings',
    'cosine_similarity'
]
