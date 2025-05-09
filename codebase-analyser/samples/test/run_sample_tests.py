#!/usr/bin/env python3
"""
Run tests for the sample Java files.
"""

import os
import sys
import unittest

# Import the test module
from test_sample_java_files import TestSampleJavaFiles


def run_tests():
    """Run all tests."""
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add the test case
    test_suite.addTest(unittest.makeSuite(TestSampleJavaFiles))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Return the result
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
