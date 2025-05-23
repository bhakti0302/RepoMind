#!/usr/bin/env python3
"""
Unit tests for the Java parser adapter.
"""

import os
import sys
import unittest
from pathlib import Path

# Add the parent directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from codebase_analyser.parsing.java_parser_adapter import JavaParserAdapter
from codebase_analyser.chunking.code_chunk import CodeChunk


class TestJavaParserAdapter(unittest.TestCase):
    """Test cases for the Java parser adapter."""
    
    def setUp(self):
        """Set up the test case."""
        self.test_files_dir = Path(os.path.join(os.path.dirname(__file__), '../java_test_project'))
        self.complex_files_dir = Path(os.path.join(os.path.dirname(__file__), '../complex_java'))
    
    def test_parse_simple_java_file(self):
        """Test parsing a simple Java file."""
        # Parse the Main.java file
        file_path = os.path.join(self.test_files_dir, 'Main.java')
        result = JavaParserAdapter.parse_file(file_path)
        
        # Check that the result is not None
        self.assertIsNotNone(result)
        
        # Check that the result contains the expected keys
        self.assertIn('path', result)
        self.assertIn('language', result)
        self.assertIn('content', result)
        self.assertIn('chunks', result)
        
        # Check that the language is Java
        self.assertEqual(result['language'], 'java')
        
        # Check that the path is correct
        self.assertEqual(result['path'], file_path)
        
        # Check that there are chunks
        self.assertGreater(len(result['chunks']), 0)
        
        # Check that the chunks have the expected structure
        for chunk in result['chunks']:
            self.assertIn('node_id', chunk)
            self.assertIn('chunk_type', chunk)
            self.assertIn('content', chunk)
            self.assertIn('file_path', chunk)
            self.assertIn('start_line', chunk)
            self.assertIn('end_line', chunk)
            self.assertIn('language', chunk)
            
            # Check that the language is Java
            self.assertEqual(chunk['language'], 'java')
            
            # Check that the file path is correct
            self.assertEqual(chunk['file_path'], file_path)
    
    def test_parse_complex_java_file(self):
        """Test parsing a complex Java file."""
        # Parse the Application.java file
        file_path = os.path.join(self.complex_files_dir, 'src/main/java/com/example/app/Application.java')
        result = JavaParserAdapter.parse_file(file_path)
        
        # Check that the result is not None
        self.assertIsNotNone(result)
        
        # Check that the result contains the expected keys
        self.assertIn('path', result)
        self.assertIn('language', result)
        self.assertIn('content', result)
        self.assertIn('chunks', result)
        self.assertIn('package', result)
        self.assertIn('imports', result)
        
        # Check that the language is Java
        self.assertEqual(result['language'], 'java')
        
        # Check that the path is correct
        self.assertEqual(result['path'], file_path)
        
        # Check that there are chunks
        self.assertGreater(len(result['chunks']), 0)
        
        # Check that the package is correct
        self.assertEqual(result['package']['name'], 'com.example.app')
        
        # Check that there are imports
        self.assertGreater(len(result['imports']), 0)
        
        # Check that the chunks have the expected structure
        for chunk in result['chunks']:
            self.assertIn('node_id', chunk)
            self.assertIn('chunk_type', chunk)
            self.assertIn('content', chunk)
            self.assertIn('file_path', chunk)
            self.assertIn('start_line', chunk)
            self.assertIn('end_line', chunk)
            self.assertIn('language', chunk)
            
            # Check that the language is Java
            self.assertEqual(chunk['language'], 'java')
            
            # Check that the file path is correct
            self.assertEqual(chunk['file_path'], file_path)
    
    def test_convert_to_code_chunks(self):
        """Test converting the parsed result to CodeChunk objects."""
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
        
        # Check that there are chunks
        self.assertGreater(len(chunks), 0)
        
        # Check that the chunks have the expected structure
        for chunk in chunks:
            self.assertIsInstance(chunk, CodeChunk)
            self.assertIsNotNone(chunk.node_id)
            self.assertIsNotNone(chunk.chunk_type)
            self.assertIsNotNone(chunk.content)
            self.assertIsNotNone(chunk.file_path)
            self.assertIsNotNone(chunk.start_line)
            self.assertIsNotNone(chunk.end_line)
            self.assertIsNotNone(chunk.language)
            
            # Check that the language is Java
            self.assertEqual(chunk.language, 'java')
            
            # Check that the file path is correct
            self.assertEqual(chunk.file_path, file_path)
        
        # Check parent-child relationships
        file_chunk = next((c for c in chunks if c.chunk_type == 'file'), None)
        self.assertIsNotNone(file_chunk)
        self.assertGreater(len(file_chunk.children), 0)


if __name__ == '__main__':
    unittest.main()
