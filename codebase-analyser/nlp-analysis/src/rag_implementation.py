"""
RAG Implementation module.

This module provides functionality for implementing Retrieval-Augmented Generation (RAG).
"""

import os
import sys
import logging
import json
from typing import Dict, List, Any, Optional, Union, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import local modules
from src.vector_search import VectorSearch
from src.utils import save_json, load_json, ensure_dir

class RAGImplementation:
    """Implementation of Retrieval-Augmented Generation (RAG)."""
    
    def __init__(
        self,
        db_path: str = ".lancedb",
        output_dir: str = None,
        max_context_length: int = 4000
    ):
        """Initialize the RAG implementation.
        
        Args:
            db_path: Path to the LanceDB database
            output_dir: Path to the output directory
            max_context_length: Maximum length of the context in tokens
        """
        self.db_path = db_path
        self.output_dir = output_dir
        self.max_context_length = max_context_length
        self.vector_search = None
        
        try:
            # Initialize vector search
            self.vector_search = VectorSearch(db_path=db_path)
            logger.info(f"Initialized vector search with database at {db_path}")
            
            # Create output directory if specified
            if output_dir:
                ensure_dir(output_dir)
        except Exception as e:
            logger.error(f"Error initializing RAG implementation: {e}")
            raise
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate the number of tokens in a text.
        
        Args:
            text: Input text
            
        Returns:
            Estimated number of tokens
        """
        # Simple estimation: 1 token ≈ 4 characters
        return len(text) // 4
    
    def _format_chunk_for_context(self, chunk: Dict[str, Any]) -> str:
        """Format a code chunk for inclusion in the context.
        
        Args:
            chunk: Code chunk
            
        Returns:
            Formatted chunk text
        """
        chunk_type = chunk.get("chunk_type", "Unknown")
        name = chunk.get("name", "Unknown")
        file_path = chunk.get("file_path", "Unknown")
        start_line = chunk.get("start_line", 0)
        end_line = chunk.get("end_line", 0)
        content = chunk.get("content", "")
        
        header = f"// {chunk_type.upper()}: {name}\n"
        header += f"// FILE: {file_path} (Lines {start_line}-{end_line})\n"
        
        return f"{header}\n{content}\n\n"
    
    def basic_rag(
        self,
        query: str,
        project_id: str = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Implement basic vector-based RAG.
        
        Args:
            query: Search query
            project_id: Project ID to filter results
            limit: Maximum number of results
            
        Returns:
            Dictionary containing search results and context
        """
        try:
            if not self.vector_search:
                logger.error("Vector search not initialized")
                return {"error": "Vector search not initialized"}
            
            # Search for code chunks
            results = self.vector_search.search(
                query=query,
                project_id=project_id,
                limit=limit
            )
            
            # Build context
            context = ""
            context_chunks = []
            total_tokens = 0
            
            for result in results:
                # Format the chunk for context
                chunk_text = self._format_chunk_for_context(result)
                chunk_tokens = self._estimate_tokens(chunk_text)
                
                # Check if adding this chunk would exceed the maximum context length
                if total_tokens + chunk_tokens > self.max_context_length:
                    break
                
                # Add the chunk to the context
                context += chunk_text
                context_chunks.append(result)
                total_tokens += chunk_tokens
            
            # Create result
            rag_result = {
                "query": query,
                "project_id": project_id,
                "results": results,
                "context": context,
                "context_chunks": context_chunks,
                "total_tokens": total_tokens
            }
            
            # Save the result if output directory is specified
            if self.output_dir:
                output_file = os.path.join(self.output_dir, "basic_rag_result.json")
                save_json(rag_result, output_file)
                logger.info(f"Saved basic RAG result to {output_file}")
            
            return rag_result
        
        except Exception as e:
            logger.error(f"Error implementing basic RAG: {e}")
            return {"error": str(e)}
    
    def graph_enhanced_rag(
        self,
        query: str,
        project_id: str = None,
        limit: int = 10,
        neighbor_limit: int = 5
    ) -> Dict[str, Any]:
        """Implement graph-enhanced RAG.
        
        Args:
            query: Search query
            project_id: Project ID to filter results
            limit: Maximum number of results
            neighbor_limit: Maximum number of neighbors to include
            
        Returns:
            Dictionary containing search results and context
        """
        try:
            if not self.vector_search:
                logger.error("Vector search not initialized")
                return {"error": "Vector search not initialized"}
            
            # Search for code chunks
            results = self.vector_search.search(
                query=query,
                project_id=project_id,
                limit=limit
            )
            
            # Get related chunks for each result
            all_chunks = []
            seen_node_ids = set()
            
            # Add the original results
            for result in results:
                node_id = result.get("node_id")
                if node_id and node_id not in seen_node_ids:
                    all_chunks.append(result)
                    seen_node_ids.add(node_id)
            
            # Add related chunks
            for result in results:
                node_id = result.get("node_id")
                if not node_id:
                    continue
                
                # Get related chunks
                related_chunks = self.vector_search.get_related_chunks(
                    node_id=node_id,
                    limit=neighbor_limit
                )
                
                # Add unique related chunks
                for chunk in related_chunks:
                    related_node_id = chunk.get("node_id")
                    if related_node_id and related_node_id not in seen_node_ids:
                        all_chunks.append(chunk)
                        seen_node_ids.add(related_node_id)
            
            # Build context
            context = ""
            context_chunks = []
            total_tokens = 0
            
            for chunk in all_chunks:
                # Format the chunk for context
                chunk_text = self._format_chunk_for_context(chunk)
                chunk_tokens = self._estimate_tokens(chunk_text)
                
                # Check if adding this chunk would exceed the maximum context length
                if total_tokens + chunk_tokens > self.max_context_length:
                    break
                
                # Add the chunk to the context
                context += chunk_text
                context_chunks.append(chunk)
                total_tokens += chunk_tokens
            
            # Create result
            rag_result = {
                "query": query,
                "project_id": project_id,
                "results": results,
                "related_chunks": [c for c in all_chunks if c not in results],
                "context": context,
                "context_chunks": context_chunks,
                "total_tokens": total_tokens
            }
            
            # Save the result if output directory is specified
            if self.output_dir:
                output_file = os.path.join(self.output_dir, "graph_enhanced_rag_result.json")
                save_json(rag_result, output_file)
                logger.info(f"Saved graph-enhanced RAG result to {output_file}")
            
            return rag_result
        
        except Exception as e:
            logger.error(f"Error implementing graph-enhanced RAG: {e}")
            return {"error": str(e)}
    
    def multi_query_rag(
        self,
        queries: List[str],
        project_id: str = None,
        limit_per_query: int = 5,
        total_limit: int = 20
    ) -> Dict[str, Any]:
        """Implement multi-query RAG.
        
        Args:
            queries: List of search queries
            project_id: Project ID to filter results
            limit_per_query: Maximum number of results per query
            total_limit: Maximum total number of results
            
        Returns:
            Dictionary containing search results and context
        """
        try:
            if not self.vector_search:
                logger.error("Vector search not initialized")
                return {"error": "Vector search not initialized"}
            
            # Search for code chunks using multiple queries
            results = self.vector_search.multi_query_search(
                queries=queries,
                project_id=project_id,
                limit_per_query=limit_per_query,
                total_limit=total_limit
            )
            
            # Build context
            context = ""
            context_chunks = []
            total_tokens = 0
            
            for result in results:
                # Format the chunk for context
                chunk_text = self._format_chunk_for_context(result)
                chunk_tokens = self._estimate_tokens(chunk_text)
                
                # Check if adding this chunk would exceed the maximum context length
                if total_tokens + chunk_tokens > self.max_context_length:
                    break
                
                # Add the chunk to the context
                context += chunk_text
                context_chunks.append(result)
                total_tokens += chunk_tokens
            
            # Create result
            rag_result = {
                "queries": queries,
                "project_id": project_id,
                "results": results,
                "context": context,
                "context_chunks": context_chunks,
                "total_tokens": total_tokens
            }
            
            # Save the result if output directory is specified
            if self.output_dir:
                output_file = os.path.join(self.output_dir, "multi_query_rag_result.json")
                save_json(rag_result, output_file)
                logger.info(f"Saved multi-query RAG result to {output_file}")
            
            return rag_result
        
        except Exception as e:
            logger.error(f"Error implementing multi-query RAG: {e}")
            return {"error": str(e)}
    
    def close(self):
        """Close the database connection."""
        try:
            if self.vector_search:
                self.vector_search.close()
                logger.info("Closed database connection")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")


# Example usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Implement RAG")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--project-id", help="Project ID to filter results")
    parser.add_argument("--db-path", default=".lancedb", help="Path to the LanceDB database")
    parser.add_argument("--output-dir", default="output", help="Path to the output directory")
    parser.add_argument("--rag-type", choices=["basic", "graph", "multi"], default="basic",
                        help="Type of RAG to implement")
    args = parser.parse_args()
    
    # Initialize RAG implementation
    rag = RAGImplementation(
        db_path=args.db_path,
        output_dir=args.output_dir
    )
    
    # Implement RAG based on the specified type
    if args.rag_type == "basic":
        result = rag.basic_rag(
            query=args.query,
            project_id=args.project_id
        )
    elif args.rag_type == "graph":
        result = rag.graph_enhanced_rag(
            query=args.query,
            project_id=args.project_id
        )
    elif args.rag_type == "multi":
        # Split the query into multiple queries
        queries = [q.strip() for q in args.query.split(";")]
        result = rag.multi_query_rag(
            queries=queries,
            project_id=args.project_id
        )
    
    # Print summary
    print(f"\nRAG Implementation Summary ({args.rag_type}):")
    print(f"Query: {args.query}")
    print(f"Project ID: {args.project_id or 'None'}")
    print(f"Found {len(result.get('results', []))} results")
    print(f"Context length: {result.get('total_tokens', 0)} tokens")
    print(f"Output directory: {args.output_dir}")
    
    # Close the connection
    rag.close()
