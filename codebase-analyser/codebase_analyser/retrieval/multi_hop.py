"""
Multi-hop retrieval for code components.

This module implements multi-hop retrieval for code components, which combines
vector search with graph traversal to find relevant code components.
"""
import logging
import asyncio
from typing import Dict, List, Any, Optional, Set, Tuple
import networkx as nx

from ..embeddings.embedding_generator import generate_embedding, cosine_similarity
from ..database.unified_storage import UnifiedStorage
from ..database.graph_storage import load_dependency_graph

# Configure logging
logger = logging.getLogger(__name__)

# Define the utility functions that were previously imported
def open_unified_storage(
    db_path=None,
    embedding_dim=768,
    use_minimal_schema=True,
    create_if_not_exists=True,
    read_only=False
):
    """Open a unified storage connection."""
    return UnifiedStorage(
        db_path=db_path,
        embedding_dim=embedding_dim,
        use_minimal_schema=use_minimal_schema,
        create_if_not_exists=create_if_not_exists,
        read_only=read_only
    )

def close_unified_storage(storage):
    """Close a unified storage connection."""
    if storage:
        storage.close()

async def retrieve_architectural_patterns(
    query: str,
    language: str,
    limit: int = 5,
    db_connection = None
) -> List[Dict[str, Any]]:
    """
    Retrieve architectural patterns from the codebase.
    
    Args:
        query: The search query
        language: Programming language
        limit: Maximum number of results
        db_connection: Optional database connection
        
    Returns:
        List of architectural patterns
    """
    logger.info(f"Retrieving architectural patterns for query: {query}")
    
    try:
        # Open database connection if not provided
        close_after = False
        if db_connection is None:
            db_connection = open_unified_storage()
            close_after = True
        
        # Generate embedding for the query
        query_embedding = generate_embedding(query)
        
        # First hop: Search for architectural components
        results = db_connection.search_code_chunks(
            query_embedding=query_embedding,
            limit=limit * 2,  # Get more results than needed for filtering
            where={
                "chunk_type": ["class", "interface", "module", "package"],
                "language": language
            }
        )
        
        # Process results
        processed_results = []
        for result in results:
            # Add similarity score
            result["similarity"] = cosine_similarity(
                query_embedding,
                result.get("embedding", [])
            )
            processed_results.append(result)
        
        # Sort by similarity
        sorted_results = sorted(
            processed_results,
            key=lambda x: x.get("similarity", 0),
            reverse=True
        )
        
        # Take top results
        top_results = sorted_results[:limit]
        
        # Close connection if opened here
        if close_after and db_connection:
            close_unified_storage(db_connection)
        
        return top_results
    except Exception as e:
        logger.error(f"Error retrieving architectural patterns: {e}")
        # Close connection if opened here and an error occurred
        if close_after and db_connection:
            close_unified_storage(db_connection)
        return []

async def retrieve_implementation_details(
    query: str,
    language: str,
    architectural_patterns: List[Dict[str, Any]],
    limit: int = 10,
    db_connection = None
) -> List[Dict[str, Any]]:
    """
    Retrieve implementation details from the codebase using multi-hop approach.
    
    Args:
        query: The search query
        language: Programming language
        architectural_patterns: Previously retrieved architectural patterns
        limit: Maximum number of results
        db_connection: Optional database connection
        
    Returns:
        List of implementation details
    """
    logger.info(f"Retrieving implementation details for query: {query}")
    
    try:
        # Open database connection if not provided
        close_after = False
        if db_connection is None:
            db_connection = open_unified_storage()
            close_after = True
        
        # Extract component IDs from architectural patterns
        component_ids = [
            pattern.get("node_id") for pattern in architectural_patterns 
            if pattern.get("node_id")
        ]
        
        # Load dependency graph
        dependency_graph = load_dependency_graph(db_connection)
        
        # Get related components from the graph
        related_components = get_related_components_from_graph(
            component_ids,
            dependency_graph,
            max_depth=2
        )
        
        # Refine query using architectural patterns
        refined_query = refine_query_with_context(query, architectural_patterns)
        
        # Generate embedding for the refined query
        query_embedding = generate_embedding(refined_query)
        
        # Second hop: Search for implementation details
        results = db_connection.search_code_chunks(
            query_embedding=query_embedding,
            limit=limit * 2,  # Get more results than needed for filtering
            where={
                "chunk_type": ["method", "function", "field", "property"],
                "language": language
            }
        )
        
        # Process results
        processed_results = []
        for result in results:
            # Add similarity score
            result["similarity"] = cosine_similarity(
                query_embedding,
                result.get("embedding", [])
            )
            
            # Add graph proximity if available
            node_id = result.get("node_id")
            if node_id and node_id in related_components:
                result["graph_proximity"] = related_components[node_id]
            else:
                result["graph_proximity"] = 0.0
            
            # Calculate combined score
            result["combined_score"] = calculate_combined_score(
                result.get("similarity", 0),
                result.get("graph_proximity", 0)
            )
            
            processed_results.append(result)
        
        # Sort by combined score
        sorted_results = sorted(
            processed_results,
            key=lambda x: x.get("combined_score", 0),
            reverse=True
        )
        
        # Take top results
        top_results = sorted_results[:limit]
        
        # Close connection if opened here
        if close_after and db_connection:
            close_unified_storage(db_connection)
        
        return top_results
    except Exception as e:
        logger.error(f"Error retrieving implementation details: {e}")
        # Close connection if opened here and an error occurred
        if close_after and db_connection:
            close_unified_storage(db_connection)
        return []

async def get_related_components(
    component_ids: List[str],
    graph: nx.DiGraph,
    max_depth: int = 2
) -> Dict[str, float]:
    """
    Get components related to the given components.
    
    Args:
        component_ids: List of component IDs
        graph: Dependency graph
        max_depth: Maximum traversal depth
        
    Returns:
        Dictionary mapping component IDs to proximity scores
    """
    try:
        related_components = {}
        
        # Process each component
        for component_id in component_ids:
            if component_id not in graph:
                continue
            
            # Get neighbors at each depth
            for depth in range(1, max_depth + 1):
                # Calculate proximity score based on depth
                proximity = 1.0 / depth
                
                # Get predecessors (components that depend on this one)
                for node in graph.predecessors(component_id):
                    if node not in related_components or proximity > related_components[node]:
                        related_components[node] = proximity
                
                # Get successors (components that this one depends on)
                for node in graph.successors(component_id):
                    if node not in related_components or proximity > related_components[node]:
                        related_components[node] = proximity
        
        return related_components
    except Exception as e:
        logger.error(f"Error getting related components: {e}")
        return {}

def calculate_combined_score(
    similarity: float,
    graph_proximity: float,
    alpha: float = 0.7
) -> float:
    """
    Calculate combined score from similarity and graph proximity.
    
    Args:
        similarity: Similarity score
        graph_proximity: Graph proximity score
        alpha: Weight for similarity score
        
    Returns:
        Combined score
    """
    return alpha * similarity + (1 - alpha) * graph_proximity
