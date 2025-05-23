#!/usr/bin/env python3
"""
Tests for the sample Java files.
"""

import os
import sys
import unittest
from pathlib import Path

# Add the parent directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from codebase_analyser.parsing.java_parser_adapter import JavaParserAdapter


class TestSampleJavaFiles(unittest.TestCase):
    """Tests for the sample Java files."""
    
    def setUp(self):
        """Set up the test case."""
        self.test_files_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), '../java_test_project')))
        self.complex_files_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), '../complex_java')))
    
    def test_simple_java_files(self):
        """Test parsing the simple Java files."""
        # Test Main.java
        main_file = os.path.join(self.test_files_dir, 'Main.java')
        self.assertTrue(os.path.exists(main_file))
        
        result = JavaParserAdapter.parse_file(main_file)
        self.assertIsNotNone(result)
        self.assertEqual(result['language'], 'java')
        
        # Test DataProcessor.java
        processor_file = os.path.join(self.test_files_dir, 'DataProcessor.java')
        self.assertTrue(os.path.exists(processor_file))
        
        result = JavaParserAdapter.parse_file(processor_file)
        self.assertIsNotNone(result)
        self.assertEqual(result['language'], 'java')
        
        # Test ProcessedData.java
        data_file = os.path.join(self.test_files_dir, 'ProcessedData.java')
        self.assertTrue(os.path.exists(data_file))
        
        result = JavaParserAdapter.parse_file(data_file)
        self.assertIsNotNone(result)
        self.assertEqual(result['language'], 'java')
        
        # Test Logger.java
        logger_file = os.path.join(self.test_files_dir, 'Logger.java')
        self.assertTrue(os.path.exists(logger_file))
        
        result = JavaParserAdapter.parse_file(logger_file)
        self.assertIsNotNone(result)
        self.assertEqual(result['language'], 'java')
        
        # Test LogLevel.java
        log_level_file = os.path.join(self.test_files_dir, 'LogLevel.java')
        self.assertTrue(os.path.exists(log_level_file))
        
        result = JavaParserAdapter.parse_file(log_level_file)
        self.assertIsNotNone(result)
        self.assertEqual(result['language'], 'java')
    
    def test_complex_java_files(self):
        """Test parsing the complex Java files."""
        # Test Application.java
        app_file = os.path.join(self.complex_files_dir, 'src/main/java/com/example/app/Application.java')
        self.assertTrue(os.path.exists(app_file))
        
        result = JavaParserAdapter.parse_file(app_file)
        self.assertIsNotNone(result)
        self.assertEqual(result['language'], 'java')
        self.assertEqual(result['package']['name'], 'com.example.app')
        
        # Test AppConfig.java
        config_file = os.path.join(self.complex_files_dir, 'src/main/java/com/example/app/config/AppConfig.java')
        self.assertTrue(os.path.exists(config_file))
        
        result = JavaParserAdapter.parse_file(config_file)
        self.assertIsNotNone(result)
        self.assertEqual(result['language'], 'java')
        self.assertEqual(result['package']['name'], 'com.example.app.config')
        
        # Test User.java
        user_file = os.path.join(self.complex_files_dir, 'src/main/java/com/example/app/model/User.java')
        self.assertTrue(os.path.exists(user_file))
        
        result = JavaParserAdapter.parse_file(user_file)
        self.assertIsNotNone(result)
        self.assertEqual(result['language'], 'java')
        self.assertEqual(result['package']['name'], 'com.example.app.model')
        
        # Test UserService.java
        service_file = os.path.join(self.complex_files_dir, 'src/main/java/com/example/app/service/UserService.java')
        self.assertTrue(os.path.exists(service_file))
        
        result = JavaParserAdapter.parse_file(service_file)
        self.assertIsNotNone(result)
        self.assertEqual(result['language'], 'java')
        self.assertEqual(result['package']['name'], 'com.example.app.service')
        
        # Test UserRepository.java
        repo_file = os.path.join(self.complex_files_dir, 'src/main/java/com/example/app/repository/UserRepository.java')
        self.assertTrue(os.path.exists(repo_file))
        
        result = JavaParserAdapter.parse_file(repo_file)
        self.assertIsNotNone(result)
        self.assertEqual(result['language'], 'java')
        self.assertEqual(result['package']['name'], 'com.example.app.repository')
        
        # Test Logger.java
        logger_file = os.path.join(self.complex_files_dir, 'src/main/java/com/example/app/util/Logger.java')
        self.assertTrue(os.path.exists(logger_file))
        
        result = JavaParserAdapter.parse_file(logger_file)
        self.assertIsNotNone(result)
        self.assertEqual(result['language'], 'java')
        self.assertEqual(result['package']['name'], 'com.example.app.util')
        
        # Test LogLevel.java
        log_level_file = os.path.join(self.complex_files_dir, 'src/main/java/com/example/app/util/LogLevel.java')
        self.assertTrue(os.path.exists(log_level_file))
        
        result = JavaParserAdapter.parse_file(log_level_file)
        self.assertIsNotNone(result)
        self.assertEqual(result['language'], 'java')
        self.assertEqual(result['package']['name'], 'com.example.app.util')


if __name__ == '__main__':
    unittest.main()
