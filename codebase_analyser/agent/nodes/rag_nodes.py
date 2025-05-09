"""
RAG (Retrieval-Augmented Generation) nodes for the agent graph.
"""
import logging
import datetime
from typing import Dict, Any, List, Optional

# Import state
from ..state import AgentState

# Import retrieval functions
from ...retrieval.multi_hop import retrieve_architectural_patterns, retrieve_implementation_details
from ...retrieval.relevance import score_relevance, rank_by_relevance
from ...embeddings.embedding_generator import generate_embedding, cosine_similarity
from ...database.unified_storage import open_unified_storage, close_unified_storage
from ...database.graph_storage import load_dependency_graph

# Configure logging
logger = logging.getLogger(__name__)

async def retrieve_architectural_context(state: AgentState) -> Dict[str, Any]:
    """
    Retrieve architectural context from the codebase.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with architectural context
    """
    logger.info("Retrieving architectural context")
    
    try:
        # Extract requirements
        requirements = state.requirements
        
        # Extract query and language
        query = requirements.get("description", "")
        language = requirements.get("language", "python")
        
        if not query:
            logger.warning("No description found in requirements")
            return {"architectural_context": []}
        
        # Retrieve architectural patterns
        architectural_patterns = await retrieve_architectural_patterns(
            query=query,
            language=language,
            limit=5
        )
        
        logger.info(f"Retrieved {len(architectural_patterns)} architectural patterns")
        return {"architectural_context": architectural_patterns}
    except Exception as e:
        logger.error(f"Error retrieving architectural context: {e}")
        return {"architectural_context": []}

async def retrieve_implementation_context(state: AgentState) -> Dict[str, Any]:
    """
    Retrieve implementation context from the codebase.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with implementation context
    """
    logger.info("Retrieving implementation context")
    
    try:
        # Extract requirements and architectural context
        requirements = state.requirements
        architectural_context = state.architectural_context
        
        # Extract query and language
        query = requirements.get("description", "")
        language = requirements.get("language", "python")
        
        if not query:
            logger.warning("No description found in requirements")
            return {"implementation_context": []}
        
        # Retrieve implementation details using multi-hop approach
        implementation_details = await retrieve_implementation_details(
            query=query,
            language=language,
            architectural_patterns=architectural_context,
            limit=10
        )
        
        logger.info(f"Retrieved {len(implementation_details)} implementation details")
        return {"implementation_context": implementation_details}
    except Exception as e:
        logger.error(f"Error retrieving implementation context: {e}")
        return {"implementation_context": []}

async def combine_context(state: AgentState) -> Dict[str, Any]:
    """
    Combine architectural and implementation context.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with combined context
    """
    logger.info("Combining context")
    
    try:
        # Extract requirements, architectural context, and implementation context
        requirements = state.requirements
        architectural_context = state.architectural_context
        implementation_context = state.implementation_context
        
        # Extract query and language
        query = requirements.get("description", "")
        language = requirements.get("language", "python")
        
        # Format the combined context
        combined_context = format_combined_context(
            architectural_context, 
            implementation_context, 
            query, 
            language
        )
        
        logger.info("Successfully combined context")
        return {"combined_context": combined_context}
    except Exception as e:
        logger.error(f"Error combining context: {e}")
        return {"combined_context": "Error combining context: " + str(e)}

async def retrieve_and_combine_context(state: AgentState) -> Dict[str, Any]:
    """
    Retrieve and combine architectural and implementation context.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with combined context
    """
    logger.info("Retrieving and combining context")
    
    try:
        # Step 1: Retrieve architectural context
        arch_result = await retrieve_architectural_context(state)
        architectural_context = arch_result.get("architectural_context", [])
        
        # Update state with architectural context
        state_with_arch = AgentState(
            **state.dict(),
            architectural_context=architectural_context
        )
        
        # Step 2: Retrieve implementation context
        impl_result = await retrieve_implementation_context(state_with_arch)
        implementation_context = impl_result.get("implementation_context", [])
        
        # Update state with implementation context
        state_with_impl = AgentState(
            **state_with_arch.dict(),
            implementation_context=implementation_context
        )
        
        # Step 3: Combine context
        combined_result = await combine_context(state_with_impl)
        combined_context = combined_result.get("combined_context", "")
        
        logger.info("Successfully retrieved and combined context")
        return {
            "architectural_context": architectural_context,
            "implementation_context": implementation_context,
            "combined_context": combined_context
        }
    except Exception as e:
        logger.error(f"Error retrieving and combining context: {e}")
        return {
            "architectural_context": [],
            "implementation_context": [],
            "combined_context": f"Error: {str(e)}"
        }

def format_combined_context(
    architectural_patterns: List[Dict[str, Any]],
    implementation_details: List[Dict[str, Any]],
    query: str,
    language: str
) -> str:
    """
    Format the combined context for the LLM prompt.
    
    Args:
        architectural_patterns: Architectural patterns
        implementation_details: Implementation details
        query: Original query
        language: Programming language
        
    Returns:
        Formatted context string
    """
    # Sort by score if available, otherwise by similarity
    sorted_arch = sorted(
        architectural_patterns, 
        key=lambda x: x.get("combined_score", x.get("similarity", 0)), 
        reverse=True
    )
    sorted_impl = sorted(
        implementation_details, 
        key=lambda x: x.get("combined_score", x.get("similarity", 0)), 
        reverse=True
    )
    
    # Take top N
    top_arch = sorted_arch[:3]
    top_impl = sorted_impl[:5]
    
    # Format the context
    context = f"QUERY: {query}\n"
    context += f"LANGUAGE: {language}\n\n"
    
    context += "ARCHITECTURAL CONTEXT:\n"
    for i, pattern in enumerate(top_arch, 1):
        score = pattern.get("combined_score", pattern.get("similarity", 0))
        context += f"{i}. {pattern.get('name', 'Unnamed')} ({pattern.get('chunk_type', 'unknown')})\n"
        context += f"   Score: {score:.2f}\n"
        context += f"   Path: {pattern.get('file_path', 'unknown')}\n"
        context += f"   Content:\n```{language}\n{pattern.get('content', '')}\n```\n\n"
    
    context += "IMPLEMENTATION CONTEXT:\n"
    for i, detail in enumerate(top_impl, 1):
        score = detail.get("combined_score", detail.get("similarity", 0))
        context += f"{i}. {detail.get('name', 'Unnamed')} ({detail.get('chunk_type', 'unknown')})\n"
        context += f"   Score: {score:.2f}\n"
        context += f"   Path: {detail.get('file_path', 'unknown')}\n"
        context += f"   Content:\n```{language}\n{detail.get('content', '')}\n```\n\n"
    
    # Extract key patterns and concepts
    context += "KEY PATTERNS AND CONCEPTS:\n"
    
    # Extract class/interface names from architectural patterns
    arch_names = [p.get("name", "") for p in top_arch if p.get("name")]
    
    # Extract method/function names from implementation details
    impl_names = [d.get("name", "") for d in top_impl if d.get("name")]
    
    # Combine and deduplicate
    all_names = list(set(arch_names + impl_names))
    
    # Add to context
    for name in all_names:
        context += f"- {name}\n"
    
    # Add timestamp
    import datetime
    context += f"\nGenerated at: {datetime.datetime.now()}\n"
    
    return context

def get_embedding(query: str) -> List[float]:
    """
    Get embedding for a query.
    
    Args:
        query: The query text
        
    Returns:
        Embedding vector
    """
    return generate_embedding(query)

def search_codebase(
    query: str,
    chunk_types: List[str] = None,
    language: str = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Search the codebase for relevant code chunks.
    
    Args:
        query: The search query
        chunk_types: Types of chunks to search for
        language: Programming language filter
        limit: Maximum number of results
        
    Returns:
        List of relevant code chunks
    """
    try:
        # Generate embedding for the query
        query_embedding = get_embedding(query)
        
        # Open database connection
        db_connection = open_unified_storage()
        
        # Build where clause
        where = {}
        if chunk_types:
            where["chunk_type"] = chunk_types
        if language:
            where["language"] = language
        
        # Search for code chunks
        results = db_connection.search_code_chunks(
            query_embedding=query_embedding,
            limit=limit,
            where=where
        )
        
        # Close database connection
        close_unified_storage(db_connection)
        
        return results
    except Exception as e:
        logger.error(f"Error searching codebase: {e}")
        return []

def get_related_components_from_graph(
    component_ids: List[str],
    max_depth: int = 2
) -> List[str]:
    """
    Get related components from the dependency graph.
    
    Args:
        component_ids: List of component IDs
        max_depth: Maximum traversal depth
        
    Returns:
        List of related component IDs
    """
    try:
        # Load dependency graph
        dependency_graph = load_dependency_graph()
        
        related_ids = set()
        
        # Process each component
        for component_id in component_ids:
            if component_id not in dependency_graph:
                continue
            
            # Get predecessors (components that depend on this one)
            for depth in range(1, max_depth + 1):
                for node in dependency_graph.predecessors(component_id):
                    related_ids.add(node)
            
            # Get successors (components that this one depends on)
            for depth in range(1, max_depth + 1):
                for node in dependency_graph.successors(component_id):
                    related_ids.add(node)
        
        return list(related_ids)
    except Exception as e:
        logger.error(f"Error getting related components: {e}")
        return []

def refine_query_with_context(
    original_query: str,
    context: List[Dict[str, Any]]
) -> str:
    """
    Refine the query based on retrieved context.
    
    Args:
        original_query: The original query
        context: Retrieved context
        
    Returns:
        Refined query
    """
    try:
        # Extract relevant terms from the context
        terms = []
        
        for item in context:
            # Add name if available
            if "name" in item and item["name"]:
                terms.append(item["name"])
            
            # Add qualified name parts if available
            if "qualified_name" in item and item["qualified_name"]:
                parts = item["qualified_name"].split(".")
                if parts:
                    terms.append(parts[-1])  # Add the last part
        
        # Remove duplicates and filter out common words
        unique_terms = list(set(terms))
        
        # Combine with original query
        if unique_terms:
            refined_query = f"{original_query} {' '.join(unique_terms)}"
        else:
            refined_query = original_query
        
        return refined_query
    except Exception as e:
        logger.error(f"Error refining query: {e}")
        return original_query
