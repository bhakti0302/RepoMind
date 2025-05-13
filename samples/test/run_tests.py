#!/usr/bin/env python3
"""
Run all tests for the Java parser adapter.
"""

import os
import sys
import unittest

# Add the parent directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import the test modules
from test_java_parser_adapter import TestJavaParserAdapter
from test_analyze_java import TestAnalyzeJava
from test_database_integration import TestDatabaseIntegration


def run_tests():
    """Run all tests."""
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add the test cases
    test_suite.addTest(unittest.makeSuite(TestJavaParserAdapter))
    test_suite.addTest(unittest.makeSuite(TestAnalyzeJava))
    test_suite.addTest(unittest.makeSuite(TestDatabaseIntegration))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Return the result
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
