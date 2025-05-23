"""
GraphRAG Module.

This module implements advanced graph-based RAG techniques for improved code retrieval.
"""

import os
import sys
import logging
import json
import networkx as nx
import numpy as np
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Try different import paths to handle both direct and package imports
try:
    # Try direct imports first (when running from the same directory)
    from vector_search import VectorSearch
    from graph_enhancer import GraphEnhancer
    from context_builder import ContextBuilder
    from relevance_scorer import RelevanceScorer
except ImportError:
    # Fall back to package imports (when imported as a module)
    from src.vector_search import VectorSearch
    from src.graph_enhancer import GraphEnhancer
    from src.context_builder import ContextBuilder
    from src.relevance_scorer import RelevanceScorer

class GraphRAG:
    """GraphRAG implementation with advanced graph traversal algorithms."""
    
    def __init__(
        self,
        db_path: str = "../.lancedb",
        output_dir: str = None,
        data_dir: str = "../../data",
        max_context_length: int = 4000,
        max_hops: int = 3,
        relationship_weights: Dict[str, float] = None
    ):
        """Initialize the GraphRAG.
        
        Args:
            db_path: Path to the LanceDB database
            output_dir: Path to the output directory
            data_dir: Path to the data directory
            max_context_length: Maximum context length
            max_hops: Maximum number of hops
            relationship_weights: Weights for different relationship types
        """
        self.db_path = db_path
        self.output_dir = output_dir
        self.data_dir = data_dir
        self.max_context_length = max_context_length
        self.max_hops = max_hops
        
        # Default relationship weights if not provided
        self.relationship_weights = relationship_weights or {
            "CONTAINS": 1.0,
            "IMPLEMENTS": 0.9,
            "EXTENDS": 0.8,
            "IMPORTS": 0.7,
            "USES": 0.6,
            "CALLS": 0.5,
            "REFERENCES": 0.4,
            "UNKNOWN": 0.3
        }
        
        # Initialize components
        try:
            self.vector_search = VectorSearch(db_path=db_path)
            self.graph_enhancer = GraphEnhancer(db_path=db_path, max_hops=max_hops)
            self.context_builder = ContextBuilder(max_context_length=max_context_length)
            self.relevance_scorer = RelevanceScorer()
            logger.info(f"Initialized GraphRAG with database at {db_path}")
        except Exception as e:
            logger.error(f"Error initializing GraphRAG: {e}")
            raise
        
        # Initialize graph
        self.graph = None
        self.node_embeddings = {}
        self.node_pagerank = {}
        self.node_info = {}
    
    def build_graph(self, seed_nodes: List[Dict[str, Any]]) -> nx.DiGraph:
        """Build a graph from seed nodes.
        
        Args:
            seed_nodes: List of seed nodes
            
        Returns:
            NetworkX DiGraph
        """
        try:
            # Initialize graph
            graph = nx.DiGraph()
            
            # Add seed nodes to the graph
            for node in seed_nodes:
                node_id = node.get("node_id")
                if not node_id:
                    continue
                
                # Add node to the graph
                graph.add_node(
                    node_id,
                    type=node.get("type", "UNKNOWN"),
                    file_path=node.get("file_path", ""),
                    content=node.get("content", ""),
                    score=node.get("score", 0.0),
                    is_seed=True
                )
                
                # Store node info
                self.node_info[node_id] = node
            
            # Expand the graph with neighbors
            visited = set(graph.nodes())
            for node_id in list(graph.nodes()):
                self._expand_node(graph, node_id, visited)
            
            # Calculate PageRank
            self.node_pagerank = nx.pagerank(graph, weight="weight")
            
            # Store the graph
            self.graph = graph
            
            logger.info(f"Built graph with {len(graph.nodes())} nodes and {len(graph.edges())} edges")
            
            return graph
        
        except Exception as e:
            logger.error(f"Error building graph: {e}")
            return nx.DiGraph()
    
    def _expand_node(
        self,
        graph: nx.DiGraph,
        node_id: str,
        visited: Set[str],
        current_hop: int = 1
    ) -> None:
        """Expand a node in the graph.
        
        Args:
            graph: NetworkX DiGraph
            node_id: Node ID to expand
            visited: Set of visited node IDs
            current_hop: Current hop count
        """
        if current_hop > self.max_hops:
            return
        
        # Get neighbors
        neighbors = self.graph_enhancer.get_node_neighbors(
            node_id=node_id,
            relationship_types=list(self.relationship_weights.keys()),
            max_neighbors=10
        )
        
        # Add neighbors to the graph
        for neighbor in neighbors:
            neighbor_id = neighbor.get("node_id")
            if not neighbor_id or neighbor_id in visited:
                continue
            
            # Add node to the graph
            graph.add_node(
                neighbor_id,
                type=neighbor.get("type", "UNKNOWN"),
                file_path=neighbor.get("file_path", ""),
                content=neighbor.get("content", ""),
                score=0.0,
                is_seed=False
            )
            
            # Add edge to the graph
            relationship_type = neighbor.get("relationship_type", "UNKNOWN")
            weight = self.relationship_weights.get(relationship_type, 0.3)
            graph.add_edge(
                node_id,
                neighbor_id,
                relationship_type=relationship_type,
                weight=weight
            )
            
            # Mark as visited
            visited.add(neighbor_id)
            
            # Store node info
            self.node_info[neighbor_id] = neighbor
            
            # Recursively expand the neighbor
            self._expand_node(graph, neighbor_id, visited, current_hop + 1)
    
    def find_paths(
        self,
        graph: nx.DiGraph,
        source_nodes: List[str],
        target_nodes: List[str],
        max_paths: int = 5,
        max_path_length: int = 5
    ) -> List[List[str]]:
        """Find paths between source and target nodes.
        
        Args:
            graph: NetworkX DiGraph
            source_nodes: List of source node IDs
            target_nodes: List of target node IDs
            max_paths: Maximum number of paths to find
            max_path_length: Maximum path length
            
        Returns:
            List of paths (each path is a list of node IDs)
        """
        try:
            all_paths = []
            
            # Find paths from each source to each target
            for source in source_nodes:
                for target in target_nodes:
                    if source == target:
                        continue
                    
                    try:
                        # Find shortest paths
                        paths = list(nx.all_simple_paths(
                            graph,
                            source=source,
                            target=target,
                            cutoff=max_path_length
                        ))
                        
                        # Sort paths by length (shortest first)
                        paths.sort(key=len)
                        
                        # Add paths to the result
                        all_paths.extend(paths[:max_paths])
                    except (nx.NetworkXNoPath, nx.NodeNotFound):
                        continue
            
            # Sort paths by length (shortest first)
            all_paths.sort(key=len)
            
            # Limit the number of paths
            return all_paths[:max_paths]
        
        except Exception as e:
            logger.error(f"Error finding paths: {e}")
            return []
    
    def score_nodes(
        self,
        graph: nx.DiGraph,
        query: str,
        paths: List[List[str]]
    ) -> Dict[str, float]:
        """Score nodes based on graph structure and query relevance.
        
        Args:
            graph: NetworkX DiGraph
            query: Search query
            paths: List of paths
            
        Returns:
            Dictionary mapping node IDs to scores
        """
        try:
            # Initialize scores
            scores = {}
            
            # Score based on PageRank
            for node_id, score in self.node_pagerank.items():
                scores[node_id] = score
            
            # Score based on path membership
            path_counts = defaultdict(int)
            for path in paths:
                for node_id in path:
                    path_counts[node_id] += 1
            
            # Normalize path counts
            max_path_count = max(path_counts.values()) if path_counts else 1
            for node_id, count in path_counts.items():
                scores[node_id] = scores.get(node_id, 0.0) + (count / max_path_count) * 0.5
            
            # Score based on query relevance
            for node_id in graph.nodes():
                node_info = self.node_info.get(node_id, {})
                content = node_info.get("content", "")
                
                # Calculate relevance score
                relevance_score = self.relevance_scorer.score_relevance(
                    query=query,
                    text=content
                )
                
                # Add to the score
                scores[node_id] = scores.get(node_id, 0.0) + relevance_score * 0.3
            
            # Normalize scores
            max_score = max(scores.values()) if scores else 1.0
            for node_id in scores:
                scores[node_id] /= max_score
            
            return scores
        
        except Exception as e:
            logger.error(f"Error scoring nodes: {e}")
            return {}
    
    def retrieve_context(
        self,
        query: str,
        project_id: str = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Retrieve context using GraphRAG.
        
        Args:
            query: Search query
            project_id: Project ID
            limit: Maximum number of results to return
            
        Returns:
            Dictionary containing retrieved context
        """
        try:
            # Step 1: Get initial results using vector search
            initial_results = self.vector_search.search(
                query=query,
                project_id=project_id,
                limit=limit
            )
            
            # Step 2: Build the graph
            graph = self.build_graph(initial_results)
            
            # Step 3: Find important nodes using PageRank
            pagerank = nx.pagerank(graph, weight="weight")
            important_nodes = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:limit]
            important_node_ids = [node_id for node_id, _ in important_nodes]
            
            # Step 4: Find paths between important nodes
            paths = self.find_paths(
                graph=graph,
                source_nodes=important_node_ids[:limit//2],
                target_nodes=important_node_ids[limit//2:limit],
                max_paths=10,
                max_path_length=self.max_hops
            )
            
            # Step 5: Score nodes
            node_scores = self.score_nodes(graph, query, paths)
            
            # Step 6: Get the top-scoring nodes
            top_nodes = sorted(node_scores.items(), key=lambda x: x[1], reverse=True)[:limit]
            top_node_ids = [node_id for node_id, _ in top_nodes]
            
            # Step 7: Get the full chunks for the top nodes
            top_chunks = []
            for node_id in top_node_ids:
                chunk = self.vector_search.get_chunk_by_id(node_id)
                if chunk:
                    # Add the score
                    chunk["score"] = node_scores.get(node_id, 0.0)
                    top_chunks.append(chunk)
            
            # Step 8: Build the context
            context_result = self.context_builder.build_context(
                chunks=top_chunks,
                query=query
            )
            
            # Step 9: Return the result
            return {
                "query": query,
                "context": context_result["context"],
                "context_chunks": context_result["context_chunks"],
                "total_tokens": context_result["total_tokens"],
                "graph_nodes": len(graph.nodes()),
                "graph_edges": len(graph.edges()),
                "paths": paths
            }
        
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return {"error": str(e)}
    
    def close(self):
        """Close the connections."""
        try:
            if hasattr(self, 'vector_search'):
                self.vector_search.close()
            if hasattr(self, 'graph_enhancer'):
                self.graph_enhancer.close()
            logger.info("Closed connections")
        except Exception as e:
            logger.error(f"Error closing connections: {e}")

# Example usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Retrieve context using GraphRAG")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--project-id", help="Project ID")
    parser.add_argument("--db-path", default="../.lancedb", help="Path to the LanceDB database")
    parser.add_argument("--output-dir", default="./output", help="Path to the output directory")
    args = parser.parse_args()
    
    # Initialize GraphRAG
    graphrag = GraphRAG(
        db_path=args.db_path,
        output_dir=args.output_dir
    )
    
    try:
        # Retrieve context
        result = graphrag.retrieve_context(
            query=args.query,
            project_id=args.project_id
        )
        
        # Print the result
        print(f"Query: {args.query}")
        print(f"Graph nodes: {result['graph_nodes']}")
        print(f"Graph edges: {result['graph_edges']}")
        print(f"Total tokens: {result['total_tokens']}")
        print(f"Context: {result['context'][:200]}...")
    
    finally:
        # Close connections
        graphrag.close()
