#!/usr/bin/env python3
"""
Integration tests for the analyze_java.py script.
"""

import os
import sys
import unittest
import tempfile
import shutil
from pathlib import Path

# Add the parent directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import the analyze_java module
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
import analyze_java


class TestAnalyzeJava(unittest.TestCase):
    """Integration tests for the analyze_java.py script."""
    
    def setUp(self):
        """Set up the test case."""
        self.test_files_dir = Path(os.path.join(os.path.dirname(__file__), '../java_test_project'))
        self.complex_files_dir = Path(os.path.join(os.path.dirname(__file__), '../complex_java'))
        
        # Create a temporary directory for the database
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test_db')
    
    def tearDown(self):
        """Clean up after the test case."""
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_analyze_simple_java_project(self):
        """Test analyzing a simple Java project."""
        # Create arguments
        class Args:
            repo_path = str(self.test_files_dir)
            db_path = self.db_path
            clear_db = True
            mock_embeddings = True
            visualize = False
            output_dir = 'samples'
            graph_format = 'png'
            project_id = 'test_project'
            max_files = 100
            skip_large_files = False
            embedding_model = 'BAAI/bge-small-en-v1.5'
            embedding_cache_dir = '.cache'
            embedding_batch_size = 8
            minimal_schema = True
        
        # Run the analysis
        result = analyze_java.analyze_java_files(Args())
        
        # Check that the analysis was successful
        self.assertTrue(result)
        
        # Check that the database was created
        self.assertTrue(os.path.exists(self.db_path))
    
    def test_analyze_complex_java_project(self):
        """Test analyzing a complex Java project."""
        # Create arguments
        class Args:
            repo_path = str(self.complex_files_dir)
            db_path = self.db_path
            clear_db = True
            mock_embeddings = True
            visualize = False
            output_dir = 'samples'
            graph_format = 'png'
            project_id = 'test_project'
            max_files = 100
            skip_large_files = False
            embedding_model = 'BAAI/bge-small-en-v1.5'
            embedding_cache_dir = '.cache'
            embedding_batch_size = 8
            minimal_schema = True
        
        # Run the analysis
        result = analyze_java.analyze_java_files(Args())
        
        # Check that the analysis was successful
        self.assertTrue(result)
        
        # Check that the database was created
        self.assertTrue(os.path.exists(self.db_path))


if __name__ == '__main__':
    unittest.main()
