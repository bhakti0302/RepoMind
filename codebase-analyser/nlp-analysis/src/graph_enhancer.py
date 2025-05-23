"""
Graph Enhancer module.

This module provides functionality for enhancing search results with graph-based context.
"""

import os
import sys
import logging
import networkx as nx
from typing import Dict, List, Any, Optional, Union, Tuple, Set

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Try to import LanceDB and UnifiedStorage
try:
    import lancedb
    # Add the codebase_analyser package to the path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from codebase_analyser.database.unified_storage import UnifiedStorage
except ImportError as e:
    logger.error(f"Error importing dependencies: {e}")
    logger.error("Make sure LanceDB and codebase_analyser are installed")
    sys.exit(1)

class GraphEnhancer:
    """Enhancer for search results using graph-based context."""
    
    def __init__(
        self,
        db_path: str = ".lancedb",
        max_hops: int = 2
    ):
        """Initialize the graph enhancer.
        
        Args:
            db_path: Path to the LanceDB database
            max_hops: Maximum number of hops in the graph
        """
        self.db_path = db_path
        self.max_hops = max_hops
        self.storage = None
        self.graph = None
        
        try:
            # Initialize the unified storage
            self.storage = UnifiedStorage(db_path=db_path)
            logger.info(f"Connected to LanceDB at {db_path}")
            
            # Build the graph
            self.graph = self.storage._build_graph_from_dependencies()
            logger.info(f"Built graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")
        except Exception as e:
            logger.error(f"Error initializing graph enhancer: {e}")
            raise
    
    def get_node_neighbors(
        self,
        node_id: str,
        relationship_types: List[str] = None,
        max_neighbors: int = 10
    ) -> List[Dict[str, Any]]:
        """Get neighbors of a node in the graph.
        
        Args:
            node_id: Node ID
            relationship_types: Types of relationships to include
            max_neighbors: Maximum number of neighbors to return
            
        Returns:
            List of neighbor nodes
        """
        try:
            if not self.graph or node_id not in self.graph:
                logger.warning(f"Node {node_id} not found in the graph")
                return []
            
            # Get all neighbors
            neighbors = list(self.graph.neighbors(node_id))
            
            # Filter by relationship type if specified
            if relationship_types:
                filtered_neighbors = []
                for neighbor in neighbors:
                    edge_data = self.graph.get_edge_data(node_id, neighbor)
                    if edge_data and edge_data.get("type") in relationship_types:
                        filtered_neighbors.append(neighbor)
                neighbors = filtered_neighbors
            
            # Limit the number of neighbors
            if max_neighbors > 0 and len(neighbors) > max_neighbors:
                neighbors = neighbors[:max_neighbors]
            
            # Get node data for each neighbor
            neighbor_data = []
            for neighbor in neighbors:
                # Get node attributes
                attrs = self.graph.nodes[neighbor]
                
                # Get the edge data
                edge_data = self.graph.get_edge_data(node_id, neighbor) or {}
                
                # Create neighbor entry
                neighbor_entry = {
                    "node_id": neighbor,
                    "relationship_type": edge_data.get("type", "UNKNOWN"),
                    **attrs
                }
                
                neighbor_data.append(neighbor_entry)
            
            return neighbor_data
        
        except Exception as e:
            logger.error(f"Error getting node neighbors: {e}")
            return []
    
    def get_multi_hop_neighbors(
        self,
        node_id: str,
        max_hops: int = None,
        relationship_types: List[str] = None,
        max_neighbors_per_hop: int = 5
    ) -> Dict[int, List[Dict[str, Any]]]:
        """Get multi-hop neighbors of a node in the graph.
        
        Args:
            node_id: Node ID
            max_hops: Maximum number of hops (default: self.max_hops)
            relationship_types: Types of relationships to include
            max_neighbors_per_hop: Maximum number of neighbors per hop
            
        Returns:
            Dictionary mapping hop distance to list of neighbor nodes
        """
        try:
            if not self.graph or node_id not in self.graph:
                logger.warning(f"Node {node_id} not found in the graph")
                return {}
            
            if max_hops is None:
                max_hops = self.max_hops
            
            # Initialize result
            multi_hop_neighbors = {}
            
            # Initialize visited nodes
            visited = {node_id}
            
            # Initialize current hop
            current_hop = 1
            current_nodes = [node_id]
            
            # Traverse the graph up to max_hops
            while current_hop <= max_hops and current_nodes:
                next_nodes = []
                hop_neighbors = []
                
                # Process each node in the current hop
                for current_node in current_nodes:
                    # Get neighbors of the current node
                    neighbors = self.get_node_neighbors(
                        node_id=current_node,
                        relationship_types=relationship_types,
                        max_neighbors=max_neighbors_per_hop
                    )
                    
                    # Add unvisited neighbors to the next hop
                    for neighbor in neighbors:
                        neighbor_id = neighbor["node_id"]
                        if neighbor_id not in visited:
                            hop_neighbors.append(neighbor)
                            next_nodes.append(neighbor_id)
                            visited.add(neighbor_id)
                
                # Add neighbors for this hop
                if hop_neighbors:
                    multi_hop_neighbors[current_hop] = hop_neighbors
                
                # Move to the next hop
                current_hop += 1
                current_nodes = next_nodes
            
            return multi_hop_neighbors
        
        except Exception as e:
            logger.error(f"Error getting multi-hop neighbors: {e}")
            return {}
    
    def enhance_search_results(
        self,
        search_results: List[Dict[str, Any]],
        max_neighbors_per_result: int = 5,
        relationship_types: List[str] = None
    ) -> Dict[str, Any]:
        """Enhance search results with graph-based context.
        
        Args:
            search_results: List of search results
            max_neighbors_per_result: Maximum number of neighbors per result
            relationship_types: Types of relationships to include
            
        Returns:
            Dictionary containing enhanced search results
        """
        try:
            if not self.graph:
                logger.warning("Graph not initialized")
                return {"original_results": search_results, "enhanced_results": []}
            
            # Initialize enhanced results
            enhanced_results = []
            
            # Track visited nodes to avoid duplicates
            visited_nodes = set()
            
            # Process each search result
            for result in search_results:
                node_id = result.get("node_id")
                if not node_id or node_id in visited_nodes:
                    continue
                
                # Mark this node as visited
                visited_nodes.add(node_id)
                
                # Add the original result
                enhanced_results.append(result)
                
                # Get neighbors
                neighbors = self.get_node_neighbors(
                    node_id=node_id,
                    relationship_types=relationship_types,
                    max_neighbors=max_neighbors_per_result
                )
                
                # Add unique neighbors
                for neighbor in neighbors:
                    neighbor_id = neighbor.get("node_id")
                    if neighbor_id and neighbor_id not in visited_nodes:
                        # Get the full chunk data
                        chunk = self.storage.get_code_chunk(neighbor_id)
                        if chunk:
                            # Add relationship information
                            chunk["relationship_to_result"] = neighbor.get("relationship_type", "UNKNOWN")
                            chunk["related_to"] = node_id
                            
                            # Add to enhanced results
                            enhanced_results.append(chunk)
                            visited_nodes.add(neighbor_id)
            
            return {
                "original_results": search_results,
                "enhanced_results": enhanced_results
            }
        
        except Exception as e:
            logger.error(f"Error enhancing search results: {e}")
            return {"original_results": search_results, "enhanced_results": []}
    
    def get_architectural_components(
        self,
        search_results: List[Dict[str, Any]],
        component_types: List[str] = None,
        max_components: int = 10
    ) -> List[Dict[str, Any]]:
        """Get architectural components related to search results.
        
        Args:
            search_results: List of search results
            component_types: Types of components to include (default: class, interface, package)
            max_components: Maximum number of components to return
            
        Returns:
            List of architectural components
        """
        try:
            if not self.graph:
                logger.warning("Graph not initialized")
                return []
            
            if component_types is None:
                component_types = ["class", "interface", "package"]
            
            # Initialize components
            components = []
            
            # Track visited nodes to avoid duplicates
            visited_nodes = set()
            
            # Process each search result
            for result in search_results:
                node_id = result.get("node_id")
                if not node_id:
                    continue
                
                # Get multi-hop neighbors
                multi_hop_neighbors = self.get_multi_hop_neighbors(
                    node_id=node_id,
                    max_hops=2,
                    max_neighbors_per_hop=10
                )
                
                # Process each hop
                for hop, neighbors in multi_hop_neighbors.items():
                    for neighbor in neighbors:
                        neighbor_id = neighbor.get("node_id")
                        neighbor_type = neighbor.get("type")
                        
                        if (neighbor_id and neighbor_id not in visited_nodes and
                            neighbor_type in component_types):
                            # Get the full chunk data
                            chunk = self.storage.get_code_chunk(neighbor_id)
                            if chunk:
                                # Add to components
                                components.append(chunk)
                                visited_nodes.add(neighbor_id)
            
            # Sort components by type and name
            components.sort(key=lambda x: (x.get("chunk_type", ""), x.get("name", "")))
            
            # Limit the number of components
            if max_components > 0 and len(components) > max_components:
                components = components[:max_components]
            
            return components
        
        except Exception as e:
            logger.error(f"Error getting architectural components: {e}")
            return []
    
    def close(self):
        """Close the database connection."""
        try:
            if self.storage:
                self.storage.close()
                logger.info("Closed database connection")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")


# Example usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhance search results with graph-based context")
    parser.add_argument("--node-id", required=True, help="Node ID to start from")
    parser.add_argument("--max-hops", type=int, default=2, help="Maximum number of hops")
    parser.add_argument("--db-path", default=".lancedb", help="Path to the LanceDB database")
    args = parser.parse_args()
    
    # Initialize graph enhancer
    enhancer = GraphEnhancer(
        db_path=args.db_path,
        max_hops=args.max_hops
    )
    
    # Get multi-hop neighbors
    neighbors = enhancer.get_multi_hop_neighbors(
        node_id=args.node_id,
        max_hops=args.max_hops
    )
    
    # Print neighbors
    print(f"Multi-hop neighbors for node {args.node_id}:")
    for hop, hop_neighbors in neighbors.items():
        print(f"\nHop {hop} ({len(hop_neighbors)} neighbors):")
        for i, neighbor in enumerate(hop_neighbors, 1):
            print(f"  {i}. {neighbor.get('name', 'Unknown')} ({neighbor.get('type', 'Unknown')})")
            print(f"     Relationship: {neighbor.get('relationship_type', 'Unknown')}")
    
    # Close the connection
    enhancer.close()
