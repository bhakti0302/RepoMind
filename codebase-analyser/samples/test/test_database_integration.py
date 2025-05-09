#!/usr/bin/env python3
"""
Tests for the database integration with the Java parser adapter.
"""

import os
import sys
import unittest
import tempfile
import shutil
from pathlib import Path

# Add the parent directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from codebase_analyser.parsing.java_parser_adapter import JavaParserAdapter
from codebase_analyser.chunking.code_chunk import CodeChunk
from codebase_analyser.database.unified_storage import UnifiedStorage


class TestDatabaseIntegration(unittest.TestCase):
    """Tests for the database integration with the Java parser adapter."""
    
    def setUp(self):
        """Set up the test case."""
        self.test_files_dir = Path(os.path.join(os.path.dirname(__file__), '../java_test_project'))
        
        # Create a temporary directory for the database
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test_db')
        
        # Create a storage manager
        self.storage_manager = UnifiedStorage(
            db_path=self.db_path,
            use_minimal_schema=True,
            create_if_not_exists=True,
            read_only=False
        )
    
    def tearDown(self):
        """Clean up after the test case."""
        # Close the storage manager
        self.storage_manager.close()
        
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_store_java_chunks(self):
        """Test storing Java chunks in the database."""
        # Parse the Main.java file
        file_path = os.path.join(self.test_files_dir, 'Main.java')
        result = JavaParserAdapter.parse_file(file_path)
        
        # Convert chunks to CodeChunk objects
        chunks = []
        chunk_map = {}
        
        # First pass: create all chunks
        for chunk_data in result['chunks']:
            # Create the chunk
            chunk = CodeChunk(
                node_id=chunk_data['node_id'],
                chunk_type=chunk_data['chunk_type'],
                content=chunk_data['content'],
                file_path=chunk_data['file_path'],
                start_line=chunk_data['start_line'],
                end_line=chunk_data['end_line'],
                language=chunk_data['language'],
                name=chunk_data.get('name'),
                qualified_name=chunk_data.get('qualified_name')
            )
            
            # Add metadata and context
            if 'metadata' in chunk_data:
                chunk.metadata = chunk_data['metadata']
            if 'context' in chunk_data:
                chunk.context = chunk_data['context']
            
            # Store in map and list
            chunk_map[chunk.node_id] = chunk
            chunks.append(chunk)
        
        # Second pass: establish parent-child relationships
        for chunk_data in result['chunks']:
            if 'parent_id' in chunk_data and chunk_data['parent_id']:
                child = chunk_map.get(chunk_data['node_id'])
                parent = chunk_map.get(chunk_data['parent_id'])
                if child and parent:
                    parent.add_child(child)
        
        # Convert chunks to dictionaries
        chunk_dicts = []
        for chunk in chunks:
            chunk_dict = chunk.to_dict()
            
            # Add mock embedding
            import numpy as np
            embedding = np.random.randn(768).astype(np.float32)
            embedding = embedding / np.linalg.norm(embedding)
            chunk_dict["embedding"] = embedding.tolist()
            
            chunk_dicts.append(chunk_dict)
        
        # Store chunks in the database
        self.storage_manager.add_code_chunks_with_graph_metadata(chunks=chunk_dicts)
        
        # Query the database
        query_result = self.storage_manager.search_code_chunks(
            query="Main",
            limit=10,
            filters={"language": "java"}
        )
        
        # Check that there are results
        self.assertGreater(len(query_result), 0)
        
        # Check that the results have the expected structure
        for result in query_result:
            self.assertIn('node_id', result)
            self.assertIn('chunk_type', result)
            self.assertIn('content', result)
            self.assertIn('file_path', result)
            self.assertIn('start_line', result)
            self.assertIn('end_line', result)
            self.assertIn('language', result)
            self.assertIn('score', result)
            
            # Check that the language is Java
            self.assertEqual(result['language'], 'java')


if __name__ == '__main__':
    unittest.main()
