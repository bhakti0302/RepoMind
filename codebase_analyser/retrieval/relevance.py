"""
Relevance scoring for code retrieval.
"""
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Union

# Import embedding utilities
from ..embeddings.embedding_generator import generate_embedding, cosine_similarity

# Configure logging
logger = logging.getLogger(__name__)

def score_relevance(
    items: List[Dict[str, Any]],
    requirements: Dict[str, Any],
    query_embedding: Optional[List[float]] = None
) -> List[Dict[str, Any]]:
    """
    Score the relevance of items to the requirements.
    
    Args:
        items: List of items to score
        requirements: Requirements dictionary
        query_embedding: Optional pre-computed query embedding
        
    Returns:
        List of items with added relevance scores
    """
    logger.info(f"Scoring relevance for {len(items)} items")
    
    try:
        # Extract query from requirements
        query = requirements.get("description", "")
        if not query:
            logger.warning("No description found in requirements")
            return items
        
        # Generate query embedding if not provided
        if query_embedding is None:
            query_embedding = generate_embedding(query)
        
        # Score each item
        scored_items = []
        for item in items:
            # Calculate semantic similarity
            content = item.get("content", "")
            name = item.get("name", "")
            
            # Generate content embedding
            if content:
                content_embedding = generate_embedding(content)
                semantic_similarity = cosine_similarity(query_embedding, content_embedding)
            else:
                semantic_similarity = 0.0
            
            # Get graph proximity if available
            graph_proximity = item.get("graph_proximity", 0.0)
            
            # Calculate combined score
            # Weight: 70% semantic similarity, 30% graph proximity
            combined_score = (0.7 * semantic_similarity) + (0.3 * graph_proximity)
            
            # Apply additional boosts
            
            # Boost for exact matches in content
            if query.lower() in content.lower():
                combined_score += 0.1
            
            # Boost for matches in name
            if query.lower() in name.lower():
                combined_score += 0.15
            
            # Boost for language match
            if requirements.get("language") == item.get("language"):
                combined_score += 0.05
            
            # Cap score at 1.0
            combined_score = min(combined_score, 1.0)
            
            # Add score to item
            scored_item = item.copy()
            scored_item["score"] = combined_score
            scored_items.append(scored_item)
        
        logger.info(f"Scored {len(scored_items)} items")
        return scored_items
    except Exception as e:
        logger.error(f"Error scoring relevance: {e}")
        return items

def calculate_graph_proximity(
    source_id: str,
    target_id: str,
    dependency_graph: Any,
    max_distance: int = 3
) -> float:
    """
    Calculate graph proximity between two components.
    
    Args:
        source_id: Source component ID
        target_id: Target component ID
        dependency_graph: Dependency graph
        max_distance: Maximum distance to consider
        
    Returns:
        Proximity score between 0 and 1
    """
    try:
        import networkx as nx
        
        # Check if both nodes exist in the graph
        if source_id not in dependency_graph or target_id not in dependency_graph:
            return 0.0
        
        # Calculate shortest path length
        try:
            distance = nx.shortest_path_length(dependency_graph, source_id, target_id)
        except nx.NetworkXNoPath:
            # No path exists
            return 0.0
        
        # Convert distance to proximity score
        # Distance 0 (same node) = 1.0
        # Distance 1 = 0.8
        # Distance 2 = 0.6
        # etc.
        if distance > max_distance:
            return 0.0
        
        proximity = 1.0 - (distance / (max_distance + 1))
        return proximity
    except Exception as e:
        logger.error(f"Error calculating graph proximity: {e}")
        return 0.0

def rank_by_relevance(
    items: List[Dict[str, Any]],
    requirements: Dict[str, Any],
    top_n: int = 10
) -> List[Dict[str, Any]]:
    """
    Rank items by relevance and return top N.
    
    Args:
        items: List of items to rank
        requirements: Requirements dictionary
        top_n: Number of top items to return
        
    Returns:
        List of top N most relevant items
    """
    # Score items
    scored_items = score_relevance(items, requirements)
    
    # Sort by score
    sorted_items = sorted(scored_items, key=lambda x: x.get("score", 0), reverse=True)
    
    # Return top N
    return sorted_items[:top_n]