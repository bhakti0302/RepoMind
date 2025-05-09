"""
Graph storage for dependency relationships.
"""
import logging
import os
import pickle
import networkx as nx
from typing import Dict, List, Any, Optional, Tuple

# Configure logging
logger = logging.getLogger(__name__)

# Default graph storage path
DEFAULT_GRAPH_PATH = os.path.join(os.path.expanduser("~"), ".codebase_analyser", "dependency_graph.pkl")

def save_dependency_graph(graph: nx.DiGraph, path: str = DEFAULT_GRAPH_PATH) -> bool:
    """
    Save the dependency graph to disk.
    
    Args:
        graph: The dependency graph
        path: Path to save the graph
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Save the graph
        with open(path, 'wb') as f:
            pickle.dump(graph, f)
        
        logger.info(f"Saved dependency graph to {path}")
        return True
    except Exception as e:
        logger.error(f"Error saving dependency graph: {e}")
        return False

def load_dependency_graph(path: str = DEFAULT_GRAPH_PATH) -> nx.DiGraph:
    """
    Load the dependency graph from disk.
    
    Args:
        path: Path to load the graph from
        
    Returns:
        The dependency graph
    """
    try:
        # Check if the file exists
        if not os.path.exists(path):
            logger.warning(f"Dependency graph file not found at {path}, creating new graph")
            return nx.DiGraph()
        
        # Load the graph
        with open(path, 'rb') as f:
            graph = pickle.load(f)
        
        logger.info(f"Loaded dependency graph from {path} with {len(graph.nodes)} nodes and {len(graph.edges)} edges")
        return graph
    except Exception as e:
        logger.error(f"Error loading dependency graph: {e}")
        return nx.DiGraph()

def add_dependency(
    graph: nx.DiGraph,
    source_id: str,
    target_id: str,
    dependency_type: str = "uses",
    weight: float = 1.0
) -> nx.DiGraph:
    """
    Add a dependency to the graph.
    
    Args:
        graph: The dependency graph
        source_id: Source component ID
        target_id: Target component ID
        dependency_type: Type of dependency
        weight: Edge weight
        
    Returns:
        Updated graph
    """
    try:
        # Add nodes if they don't exist
        if source_id not in graph:
            graph.add_node(source_id)
        
        if target_id not in graph:
            graph.add_node(target_id)
        
        # Add edge with attributes
        graph.add_edge(
            source_id,
            target_id,
            type=dependency_type,
            weight=weight
        )
        
        return graph
    except Exception as e:
        logger.error(f"Error adding dependency: {e}")
        return graph

def get_dependencies(
    graph: nx.DiGraph,
    component_id: str,
    max_depth: int = 1,
    direction: str = "both"
) -> Dict[str, Dict[str, Any]]:
    """
    Get dependencies for a component.
    
    Args:
        graph: The dependency graph
        component_id: Component ID
        max_depth: Maximum traversal depth
        direction: Direction of dependencies ('in', 'out', or 'both')
        
    Returns:
        Dictionary of dependencies
    """
    try:
        if component_id not in graph:
            return {}
        
        dependencies = {}
        
        # Get outgoing dependencies (components this one depends on)
        if direction in ["out", "both"]:
            for target_id in graph.successors(component_id):
                edge_data = graph.get_edge_data(component_id, target_id)
                dependencies[target_id] = {
                    "direction": "out",
                    "type": edge_data.get("type", "uses"),
                    "weight": edge_data.get("weight", 1.0)
                }
        
        # Get incoming dependencies (components that depend on this one)
        if direction in ["in", "both"]:
            for source_id in graph.predecessors(component_id):
                edge_data = graph.get_edge_data(source_id, component_id)
                dependencies[source_id] = {
                    "direction": "in",
                    "type": edge_data.get("type", "uses"),
                    "weight": edge_data.get("weight", 1.0)
                }
        
        return dependencies
    except Exception as e:
        logger.error(f"Error getting dependencies: {e}")
        return {}

def build_dependency_graph_from_chunks(
    chunks: List[Dict[str, Any]]
) -> nx.DiGraph:
    """
    Build a dependency graph from code chunks.
    
    Args:
        chunks: List of code chunks with dependency information
        
    Returns:
        Dependency graph
    """
    try:
        # Create a new graph
        graph = nx.DiGraph()
        
        # Process each chunk
        for chunk in chunks:
            chunk_id = chunk.get("id")
            if not chunk_id:
                continue
            
            # Add the chunk as a node
            graph.add_node(
                chunk_id,
                name=chunk.get("name", ""),
                qualified_name=chunk.get("qualified_name", ""),
                chunk_type=chunk.get("chunk_type", ""),
                file_path=chunk.get("file_path", "")
            )
            
            # Add dependencies
            dependencies = chunk.get("dependencies", [])
            for dep in dependencies:
                target_id = dep.get("target_id")
                if not target_id:
                    continue
                
                # Add the dependency
                graph = add_dependency(
                    graph,
                    chunk_id,
                    target_id,
                    dependency_type=dep.get("type", "uses"),
                    weight=dep.get("weight", 1.0)
                )
        
        logger.info(f"Built dependency graph with {len(graph.nodes)} nodes and {len(graph.edges)} edges")
        return graph
    except Exception as e:
        logger.error(f"Error building dependency graph: {e}")
        return nx.DiGraph()