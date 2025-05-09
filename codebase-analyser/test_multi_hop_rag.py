"""
Test script for multi-hop RAG implementation.
"""
import asyncio
import logging
import sys
from pathlib import Path
import json

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the necessary components
from codebase_analyser.retrieval.multi_hop import retrieve_architectural_patterns, retrieve_implementation_details
from codebase_analyser.database.unified_storage import UnifiedStorage
from codebase_analyser.database.graph_storage import load_dependency_graph, save_dependency_graph
from codebase_analyser.embeddings.embedding_generator import generate_embedding, cosine_similarity

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

async def test_multi_hop_rag():
    """Test the multi-hop RAG implementation."""
    # Sample requirement
    query = "Implement a data exporter that can export to CSV format"
    language = "java"
    
    logger.info(f"Testing multi-hop RAG with query: {query}")
    
    try:
        # Step 1: Retrieve architectural patterns
        logger.info("Step 1: Retrieving architectural patterns")
        architectural_patterns = await retrieve_architectural_patterns(
            query=query,
            language=language,
            limit=5
        )
        
        # Log the architectural patterns
        logger.info(f"Retrieved {len(architectural_patterns)} architectural patterns")
        for i, pattern in enumerate(architectural_patterns, 1):
            logger.info(f"Pattern {i}: {pattern.get('name', 'Unnamed')} ({pattern.get('chunk_type', 'unknown')})")
            logger.info(f"  Score: {pattern.get('similarity', 0):.2f}")
            logger.info(f"  Path: {pattern.get('file_path', 'unknown')}")
            
        # Step 2: Retrieve implementation details
        logger.info("Step 2: Retrieving implementation details")
        implementation_details = await retrieve_implementation_details(
            query=query,
            language=language,
            architectural_patterns=architectural_patterns,
            limit=10
        )
        
        # Log the implementation details
        logger.info(f"Retrieved {len(implementation_details)} implementation details")
        for i, detail in enumerate(implementation_details, 1):
            logger.info(f"Detail {i}: {detail.get('name', 'Unnamed')} ({detail.get('chunk_type', 'unknown')})")
            logger.info(f"  Score: {detail.get('similarity', 0):.2f}")
            logger.info(f"  Graph Proximity: {detail.get('graph_proximity', 0):.2f}")
            logger.info(f"  Combined Score: {detail.get('combined_score', 0):.2f}")
            logger.info(f"  Path: {detail.get('file_path', 'unknown')}")
        
        # Step 3: Format the combined context
        logger.info("Step 3: Formatting combined context")
        combined_context = format_combined_context(
            architectural_patterns,
            implementation_details,
            query,
            language
        )
        
        # Log the combined context
        logger.info(f"Combined context: {combined_context[:200]}...")
        
        # Save the results to a file for inspection
        results = {
            "query": query,
            "language": language,
            "architectural_patterns": architectural_patterns,
            "implementation_details": implementation_details,
            "combined_context": combined_context
        }
        
        with open("multi_hop_rag_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        logger.info("Saved results to multi_hop_rag_results.json")
        
        logger.info("Multi-hop RAG test completed")
    except Exception as e:
        logger.error(f"Error testing multi-hop RAG: {e}")

def format_combined_context(
    architectural_patterns,
    implementation_details,
    query,
    language
):
    """Format the combined context for inspection."""
    # Sort by score or similarity
    sorted_arch = sorted(
        architectural_patterns, 
        key=lambda x: x.get("similarity", 0), 
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
    
    context += "ARCHITECTURAL PATTERNS:\n"
    for i, pattern in enumerate(top_arch, 1):
        context += f"{i}. {pattern.get('name', 'Unnamed')} ({pattern.get('chunk_type', 'unknown')})\n"
        context += f"   Score: {pattern.get('similarity', 0):.2f}\n"
        context += f"   Path: {pattern.get('file_path', 'unknown')}\n"
        context += f"   Content:\n```{language}\n{pattern.get('content', '')}\n```\n\n"
    
    context += "IMPLEMENTATION DETAILS:\n"
    for i, detail in enumerate(top_impl, 1):
        score = detail.get("combined_score", detail.get("similarity", 0))
        context += f"{i}. {detail.get('name', 'Unnamed')} ({detail.get('chunk_type', 'unknown')})\n"
        context += f"   Score: {score:.2f}\n"
        if "graph_proximity" in detail:
            context += f"   Graph Proximity: {detail.get('graph_proximity', 0):.2f}\n"
        context += f"   Path: {detail.get('file_path', 'unknown')}\n"
        context += f"   Content:\n```{language}\n{detail.get('content', '')}\n```\n\n"
    
    return context

async def test_graph_traversal():
    """Test the graph traversal functionality."""
    logger.info("Testing graph traversal")
    
    try:
        # Load the dependency graph
        graph = load_dependency_graph()
        
        if not graph or graph.number_of_nodes() == 0:
            logger.warning("No dependency graph found or graph is empty")
            logger.info("Creating a sample graph for testing")
            
            # Create a sample graph for testing
            graph = create_sample_graph()
            
            # Save the sample graph
            save_dependency_graph(graph)
            logger.info(f"Saved sample graph with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges")
        
        # Get a sample node
        if graph.number_of_nodes() > 0:
            sample_node = list(graph.nodes())[0]
            logger.info(f"Using sample node: {sample_node}")
            
            # Get related components
            from codebase_analyser.retrieval.multi_hop import get_related_components
            related = await get_related_components([sample_node], graph, max_depth=2)
            
            logger.info(f"Found {len(related)} related components")
            for node_id, proximity in related.items():
                logger.info(f"  {node_id}: {proximity:.2f}")
        else:
            logger.warning("Graph has no nodes")
    
    except Exception as e:
        logger.error(f"Error testing graph traversal: {e}")

def create_sample_graph():
    """Create a sample dependency graph for testing."""
    import networkx as nx
    
    # Create a new graph
    graph = nx.DiGraph()
    
    # Add some nodes
    nodes = [
        {"id": "class1", "name": "DataExporter", "chunk_type": "class"},
        {"id": "class2", "name": "CSVExporter", "chunk_type": "class"},
        {"id": "class3", "name": "JSONExporter", "chunk_type": "class"},
        {"id": "interface1", "name": "Exporter", "chunk_type": "interface"},
        {"id": "method1", "name": "export", "chunk_type": "method"},
        {"id": "method2", "name": "convertToCSV", "chunk_type": "method"},
        {"id": "method3", "name": "writeToFile", "chunk_type": "method"},
    ]
    
    for node in nodes:
        graph.add_node(
            node["id"],
            name=node["name"],
            chunk_type=node["chunk_type"]
        )
    
    # Add some edges
    edges = [
        ("class2", "interface1", {"type": "implements"}),
        ("class3", "interface1", {"type": "implements"}),
        ("class1", "interface1", {"type": "implements"}),
        ("method1", "class1", {"type": "belongs_to"}),
        ("method2", "class2", {"type": "belongs_to"}),
        ("method3", "class2", {"type": "belongs_to"}),
        ("method1", "method2", {"type": "calls"}),
        ("method1", "method3", {"type": "calls"}),
    ]
    
    for source, target, attrs in edges:
        graph.add_edge(source, target, **attrs)
    
    return graph

if __name__ == "__main__":
    # Run the tests
    asyncio.run(test_multi_hop_rag())
    asyncio.run(test_graph_traversal())
