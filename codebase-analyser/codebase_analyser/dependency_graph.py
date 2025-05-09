"""
Dependency graph implementation for code relationships.
"""
import logging
import networkx as nx
from typing import Dict, Any, List, Optional, Set, Tuple
import os
import json

logger = logging.getLogger(__name__)

class DependencyGraph:
    """
    A graph representing dependencies between code components.
    """
    
    def __init__(self):
        """
        Initialize the dependency graph.
        """
        self.graph = nx.DiGraph()
        self.node_metadata = {}
        
    def add_node(self, node_id: str, metadata: Dict[str, Any] = None) -> None:
        """
        Add a node to the graph.
        
        Args:
            node_id: The node ID
            metadata: Optional metadata for the node
        """
        self.graph.add_node(node_id)
        if metadata:
            self.node_metadata[node_id] = metadata
            
    def add_edge(self, source: str, target: str, edge_type: str = "depends_on") -> None:
        """
        Add an edge to the graph.
        
        Args:
            source: The source node ID
            target: The target node ID
            edge_type: The type of edge
        """
        if source not in self.graph:
            self.add_node(source)
        if target not in self.graph:
            self.add_node(target)
            
        self.graph.add_edge(source, target, type=edge_type)
        
    def get_related_components(self, node_id: str, max_depth: int = 2) -> List[str]:
        """
        Get components related to the given node.
        
        Args:
            node_id: The node ID
            max_depth: Maximum traversal depth
            
        Returns:
            A list of related component IDs
        """
        if node_id not in self.graph:
            return []
            
        # Get components that depend on this node
        dependents = set()
        for depth in range(1, max_depth + 1):
            current_level = set()
            for path in nx.all_simple_paths(self.graph, source=node_id, cutoff=depth):
                if len(path) > 1:  # Exclude the source node
                    current_level.add(path[-1])
            dependents.update(current_level)
            
        # Get components that this node depends on
        dependencies = set()
        for depth in range(1, max_depth + 1):
            current_level = set()
            for path in nx.all_simple_paths(self.graph.reverse(), source=node_id, cutoff=depth):
                if len(path) > 1:  # Exclude the source node
                    current_level.add(path[-1])
            dependencies.update(current_level)
            
        # Combine and return
        return list(dependents.union(dependencies))
        
    def calculate_proximity(self, source: str, target: str) -> float:
        """
        Calculate the proximity between two nodes.
        
        Args:
            source: The source node ID
            target: The target node ID
            
        Returns:
            A proximity score between 0 and 1
        """
        if source not in self.graph or target not in self.graph:
            return 0.0
            
        try:
            # Try to find the shortest path
            path_length = nx.shortest_path_length(self.graph, source=source, target=target)
            # Convert path length to proximity (1 for direct dependency, decreasing for longer paths)
            return 1.0 / (1.0 + path_length)
        except nx.NetworkXNoPath:
            # No path exists, try the reverse direction
            try:
                path_length = nx.shortest_path_length(self.graph, source=target, target=source)
                # Slightly lower score for reverse dependencies
                return 0.8 / (1.0 + path_length)
            except nx.NetworkXNoPath:
                # No path in either direction
                return 0.0
                
    def get_node_metadata(self, node_id: str) -> Dict[str, Any]:
        """
        Get metadata for a node.
        
        Args:
            node_id: The node ID
            
        Returns:
            The node metadata
        """
        return self.node_metadata.get(node_id, {})
        
    def save(self, file_path: str) -> None:
        """
        Save the graph to a file.
        
        Args:
            file_path: The file path
        """
        data = {
            "nodes": [{"id": node, "metadata": self.node_metadata.get(node, {})} for node in self.graph.nodes()],
            "edges": [{"source": u, "target": v, "type": d.get("type", "depends_on")} for u, v, d in self.graph.edges(data=True)]
        }
        
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
            
    @classmethod
    def load(cls, file_path: str) -> 'DependencyGraph':
        """
        Load a graph from a file.
        
        Args:
            file_path: The file path
            
        Returns:
            The loaded graph
        """
        graph = cls()
        
        with open(file_path, "r") as f:
            data = json.load(f)
            
        # Add nodes
        for node_data in data.get("nodes", []):
            graph.add_node(node_data["id"], node_data.get("metadata", {}))
            
        # Add edges
        for edge_data in data.get("edges", []):
            graph.add_edge(edge_data["source"], edge_data["target"], edge_data.get("type", "depends_on"))
            
        return graph

# Singleton instance
_dependency_graph = None

def get_dependency_graph() -> Optional[DependencyGraph]:
    """
    Get the dependency graph.
    
    Returns:
        The dependency graph
    """
    global _dependency_graph
    
    if _dependency_graph is None:
        try:
            # Try to load from file
            graph_path = os.environ.get("DEPENDENCY_GRAPH_PATH", "dependency_graph.json")
            if os.path.exists(graph_path):
                _dependency_graph = DependencyGraph.load(graph_path)
            else:
                _dependency_graph = DependencyGraph()
        except Exception as e:
            logger.error(f"Error loading dependency graph: {str(e)}")
            _dependency_graph = DependencyGraph()
            
    return _dependency_graph

def build_dependency_graph(codebase_path: str) -> DependencyGraph:
    """
    Build a dependency graph from a codebase.
    
    Args:
        codebase_path: The path to the codebase
        
    Returns:
        The dependency graph
    """
    # This is a placeholder for the actual implementation
    # In a real implementation, this would parse the codebase and build the graph
    graph = DependencyGraph()
    
    # Example: Add some nodes and edges
    graph.add_node("com.example.Model", {"type": "class", "language": "java"})
    graph.add_node("com.example.Repository", {"type": "interface", "language": "java"})
    graph.add_node("com.example.Service", {"type": "class", "language": "java"})
    graph.add_node