
"""
Relevance scorer for retrieved code chunks.

This module provides functionality to score the relevance of retrieved code chunks
based on various criteria.
"""

import logging
import re
from typing import Dict, List, Set, Optional, Any, Tuple, Union
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class RelevanceScorer:
    """Scores the relevance of retrieved code chunks."""
    
    def __init__(self):
        """Initialize the relevance scorer."""
        logger.info("Initialized RelevanceScorer")
    
    def score_chunks(
        self,
        chunks: List[Dict[str, Any]],
        keywords: List[str],
        entities: Dict[str, List[str]]
    ) -> List[Dict[str, Any]]:
        """Score chunks based on relevance to keywords and entities.
        
        Args:
            chunks: List of code chunks
            keywords: List of keywords to search for
            entities: Dictionary of entities extracted from the requirement
        
        Returns:
            List of chunks with relevance scores
        """
        logger.info(f"Scoring {len(chunks)} chunks with {len(keywords)} keywords")
        
        # Add debug logging for keywords and entities
        logger.info(f"Keywords: {keywords}")
        logger.info(f"Entities: {entities}")
        
        # Score each chunk
        scored_chunks = []
        for chunk in chunks:
            # Get the chunk content
            content = chunk.get("content", "")
            
            # Skip empty chunks
            if not content:
                continue
            
            # Calculate keyword score
            keyword_score = 0
            keyword_matches = 0
            for keyword in keywords:
                # Check if keyword is a string before calling lower()
                if isinstance(keyword, str) and keyword.lower() in content.lower():
                    keyword_score += 1
                    keyword_matches += 1
            
            # Normalize keyword score
            if keywords:
                keyword_score = keyword_score / len(keywords)
            
            # Calculate entity score
            entity_score = 0
            entity_matches = 0
            for entity_type, entity_list in entities.items():
                for entity in entity_list:
                    # Check if entity is a string before calling lower()
                    if isinstance(entity, str) and entity.lower() in content.lower():
                        entity_score += 1
                        entity_matches += 1
            
            # Normalize entity score
            total_entities = sum(len(entity_list) for entity_list in entities.values())
            if total_entities > 0:
                entity_score = entity_score / total_entities
            
            # Calculate combined score
            combined_score = (keyword_score + entity_score) / 2
            
            # Add scores to chunk
            chunk_with_score = chunk.copy()
            chunk_with_score["relevance_score"] = combined_score
            chunk_with_score["keyword_score"] = keyword_score
            chunk_with_score["entity_score"] = entity_score
            chunk_with_score["keyword_matches"] = keyword_matches
            chunk_with_score["entity_matches"] = entity_matches
            
            # Add debug info
            logger.debug(f"Chunk {chunk.get('node_id', 'unknown')}: combined_score={combined_score}, keyword_score={keyword_score}, entity_score={entity_score}")
            
            scored_chunks.append(chunk_with_score)
        
        # Sort by relevance score
        scored_chunks.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        # Log the top 5 chunks
        for i, chunk in enumerate(scored_chunks[:5]):
            logger.info(f"Top chunk {i+1}: score={chunk['relevance_score']}, keyword_matches={chunk['keyword_matches']}, entity_matches={chunk['entity_matches']}")
        
        return scored_chunks
    
    def filter_by_threshold(
        self,
        chunks: List[Dict[str, Any]],
        threshold: float = 0.3
    ) -> List[Dict[str, Any]]:
        """Filter chunks by relevance score threshold.
        
        Args:
            chunks: List of chunks with relevance scores
            threshold: Minimum relevance score threshold
        
        Returns:
            Filtered list of chunks
        """
        # Add debug logging
        logger.info(f"Filtering {len(chunks)} chunks with threshold {threshold}")
        
        # Filter chunks by threshold
        filtered_chunks = [chunk for chunk in chunks if chunk.get("relevance_score", 0) >= threshold]
        
        # Log the filtering results
        logger.info(f"Filtered to {len(filtered_chunks)} chunks")
        
        # If no chunks meet the threshold but we have chunks, take the top 5
        if not filtered_chunks and chunks:
            logger.warning(f"No chunks met the threshold of {threshold}. Taking top 5 chunks instead.")
            filtered_chunks = chunks[:5]
            logger.info(f"Taking top {len(filtered_chunks)} chunks")
        
        return filtered_chunks
    
    def group_by_file(
        self,
        chunks: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group chunks by file path.
        
        Args:
            chunks: List of chunks
            
        Returns:
            Dictionary mapping file paths to lists of chunks
        """
        grouped = {}
        
        for chunk in chunks:
            if "file_path" in chunk:
                file_path = chunk["file_path"]
                
                if file_path not in grouped:
                    grouped[file_path] = []
                
                grouped[file_path].append(chunk)
        
        # Sort chunks within each file by position
        for file_path, file_chunks in grouped.items():
            file_chunks.sort(key=lambda x: x.get("start_line", 0))
        
        return grouped

