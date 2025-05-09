"""
Unit tests for the RAG nodes.
"""
import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import asyncio
import json
import networkx as nx
import numpy as np

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import directly from the module to avoid circular imports
from codebase_analyser.agent.state import AgentState
# Import the functions we want to test
from codebase_analyser.agent.nodes.rag_nodes import (
    get_embedding,
    search_codebase,
    get_related_components_from_graph,
    score_relevance,
    refine_query_with_context,
    retrieve_architectural_context,
    retrieve_implementation_context,
    combine_context,
    retrieve_and_combine_context,
    dependency_graph
)

class TestRAGNodes(unittest.TestCase):
    """Test cases for RAG nodes."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a sample state
        self.sample_state = AgentState(
            requirements={
                "description": "Create a data exporter for CSV and JSON formats",
                "language": "java"
            },
            processed_requirements={
                "intent": "create data exporter",
                "entities": {
                    "formats": ["CSV", "JSON"],
                    "components": ["exporter"]
                },
                "key_phrases": ["data export", "multiple formats"],
                "code_references": ["DataExporter", "CSVExporter", "JSONExporter"],
                "language": "java",
                "original_text": "Create a data exporter for CSV and JSON formats"
            },
            architectural_context=[
                {
                    "id": "arch1",
                    "node_id": "node1",
                    "content": "public interface DataExporter { void export(Data data, String path); }",
                    "file_path": "DataExporter.java",
                    "type": "interface",
                    "score": 0.9
                }
            ],
            implementation_context=[
                {
                    "id": "impl1",
                    "node_id": "node2",
                    "content": "public class CSVExporter implements DataExporter { public void export(Data data, String path) { /* CSV export logic */ } }",
                    "file_path": "CSVExporter.java",
                    "type": "class",
                    "score": 0.85
                }
            ],
            errors=[]
        )
    
    @patch('codebase_analyser.agent.nodes.rag_nodes.generate_embedding')
    def test_get_embedding(self, mock_generate_embedding):
        """Test get_embedding function."""
        # Mock the generate_embedding function
        mock_generate_embedding.return_value = [0.1, 0.2, 0.3]
        
        # Test the function
        result = get_embedding("test query")
        
        # Verify the result
        self.assertEqual(result, [0.1, 0.2, 0.3])
        mock_generate_embedding.assert_called_once_with("test query")
    
    @patch('codebase_analyser.agent.nodes.rag_nodes.open_db_connection')
    @patch('codebase_analyser.agent.nodes.rag_nodes.close_db_connection')
    @patch('codebase_analyser.agent.nodes.rag_nodes.generate_embedding')
    def test_search_codebase(self, mock_generate_embedding, mock_close_db, mock_open_db):
        """Test search_codebase function."""
        # Mock the generate_embedding function
        mock_generate_embedding.return_value = [0.1, 0.2, 0.3]
        
        # Mock the database connection
        mock_db = MagicMock()
        mock_open_db.return_value = mock_db
        
        # Mock the search_code_chunks method
        mock_db.search_code_chunks.return_value = [
            {"id": "chunk1", "content": "test content", "chunk_type": "class"}
        ]
        
        # Test the function
        result = search_codebase("test query")
        
        # Verify the result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "chunk1")
        mock_generate_embedding.assert_called_once_with("test query")
        mock_open_db.assert_called_once()
        mock_db.search_code_chunks.assert_called_once()
        mock_close_db.assert_called_once_with(mock_db)
    
    @patch('codebase_analyser.agent.nodes.rag_nodes.nx')
    def test_get_related_components_from_graph(self, mock_nx):
        """Test get_related_components_from_graph function."""
        # Create a mock graph
        mock_graph = MagicMock()
        
        # Set up the mock predecessors and successors
        mock_nx.predecessors.return_value = ["pred1", "pred2"]
        mock_nx.successors.return_value = ["succ1", "succ2"]
        
        # Replace the dependency_graph with our mock
        original_graph = codebase_analyser.agent.nodes.rag_nodes.dependency_graph
        codebase_analyser.agent.nodes.rag_nodes.dependency_graph = mock_graph
        
        try:
            # Test the function
            result = get_related_components_from_graph(["node1"])
            
            # Verify the result
            self.assertIn("pred1", result)
            self.assertIn("pred2", result)
            self.assertIn("succ1", result)
            self.assertIn("succ2", result)
        finally:
            # Restore the original graph
            codebase_analyser.agent.nodes.rag_nodes.dependency_graph = original_graph
    
    @patch('codebase_analyser.agent.nodes.rag_nodes.generate_embedding')
    @patch('codebase_analyser.agent.nodes.rag_nodes.cosine_similarity')
    def test_score_relevance(self, mock_cosine_similarity, mock_generate_embedding):
        """Test score_relevance function."""
        # Mock the generate_embedding function
        mock_generate_embedding.return_value = [0.1, 0.2, 0.3]
        
        # Mock the cosine_similarity function
        mock_cosine_similarity.return_value = 0.8
        
        # Create a test chunk
        chunk = {
            "content": "test content with query",
            "name": "TestClass",
            "qualified_name": "com.example.TestClass",
            "embedding": [0.4, 0.5, 0.6]
        }
        
        # Test the function with a single item
        score = score_relevance(chunk, "query")
        
        # Verify the result is a float
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.8)  # Should be at least the cosine similarity
        self.assertLessEqual(score, 1.0)  # Should not exceed 1.0
    
    def test_refine_query_with_context(self):
        """Test refine_query_with_context function."""
        # Create test context
        context = [
            {
                "name": "TestClass",
                "qualified_name": "com.example.TestClass",
                "chunk_type": "class"
            },
            {
                "name": "AnotherClass",
                "qualified_name": "com.example.AnotherClass",
                "chunk_type": "class"
            }
        ]
        
        # Test the function
        result = refine_query_with_context("original query", context)
        
        # Verify the result
        self.assertIn("original query", result)
        self.assertTrue(any(term in result for term in ["TestClass", "AnotherClass", "class"]))
    
    def test_retrieve_architectural_context(self):
        """Test retrieve_architectural_context function."""
        async def _test():
            # Mock the search_codebase function
            with patch('codebase_analyser.agent.nodes.rag_nodes.search_codebase') as mock_search:
                # Set up the mock
                mock_search.return_value = [
                    {"id": "arch1", "content": "interface DataExporter", "file_path": "DataExporter.java", "chunk_type": "interface"}
                ]
                
                # Mock the score_relevance function
                with patch('codebase_analyser.agent.nodes.rag_nodes.score_relevance') as mock_score:
                    mock_score.return_value = 0.9
                    
                    # Test the function
                    result = await retrieve_architectural_context(self.sample_state)
                    
                    # Verify the results
                    self.assertIn("architectural_context", result)
                    self.assertEqual(len(result["architectural_context"]), 1)
                    self.assertEqual(result["architectural_context"][0]["id"], "arch1")
        
        # Run the async test
        asyncio.run(_test())
    
    def test_retrieve_implementation_context(self):
        """Test retrieve_implementation_context function."""
        async def _test():
            # Mock the search_codebase function
            with patch('codebase_analyser.agent.nodes.rag_nodes.search_codebase') as mock_search:
                # Set up the mock
                mock_search.return_value = [
                    {"id": "impl1", "content": "class CSVExporter implements DataExporter", "file_path": "CSVExporter.java", "chunk_type": "class"}
                ]
                
                # Mock the score_relevance function
                with patch('codebase_analyser.agent.nodes.rag_nodes.score_relevance') as mock_score:
                    mock_score.return_value = 0.85
                    
                    # Test the function
                    result = await retrieve_implementation_context(self.sample_state)
                    
                    # Verify the results
                    self.assertIn("implementation_context", result)
                    self.assertEqual(len(result["implementation_context"]), 1)
                    self.assertEqual(result["implementation_context"][0]["id"], "impl1")
        
        # Run the async test
        asyncio.run(_test())
    
    def test_combine_context(self):
        """Test combine_context function."""
        async def _test():
            # Test the function
            result = await combine_context(self.sample_state)
            
            # Verify the results
            self.assertIn("combined_context", result)
            self.assertIn("Architectural Context", result["combined_context"])
            self.assertIn("Implementation Context", result["combined_context"])
            self.assertIn("Key Patterns and Concepts", result["combined_context"])
            self.assertIn("DataExporter", result["combined_context"])
        
        # Run the async test
        asyncio.run(_test())
    
    def test_retrieve_and_combine_context(self):
        """Test retrieve_and_combine_context function."""
        async def _test():
            # Mock the individual functions
            with patch('codebase_analyser.agent.nodes.rag_nodes.retrieve_architectural_context') as mock_arch:
                mock_arch.return_value = {"architectural_context": [{"id": "arch1"}]}
                
                with patch('codebase_analyser.agent.nodes.rag_nodes.retrieve_implementation_context') as mock_impl:
                    mock_impl.return_value = {"implementation_context": [{"id": "impl1"}]}
                    
                    with patch('codebase_analyser.agent.nodes.rag_nodes.combine_context') as mock_combine:
                        mock_combine.return_value = {"combined_context": "test combined context"}
                        
                        # Test the function
                        result = await retrieve_and_combine_context(self.sample_state)
                        
                        # Verify the results
                        self.assertIn("architectural_context", result)
                        self.assertIn("implementation_context", result)
                        self.assertIn("combined_context", result)
                        self.assertEqual(result["combined_context"], "test combined context")
        
        # Run the async test
        asyncio.run(_test())

if __name__ == '__main__':
    unittest.main()
