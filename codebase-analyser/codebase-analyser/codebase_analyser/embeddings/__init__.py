"""
Embeddings package for code chunks.
"""

from .embedding_generator import EmbeddingGenerator
from .embed_chunks import embed_and_store_chunks, embed_chunks_from_file

__all__ = [
    'EmbeddingGenerator',
    'embed_and_store_chunks',
    'embed_chunks_from_file'
]
