#!/usr/bin/env python3
"""
Run all tests for the codebase analyzer.
"""

import os
import sys
import unittest
import importlib
import pkgutil

def discover_test_modules():
    """Discover all test modules in the tests directory."""
    test_modules = []
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Walk through all subdirectories
    for root, dirs, files in os.walk(current_dir):
        # Skip __pycache__ directories
        if '__pycache__' in root:
            continue
        
        # Get the relative path from the tests directory
        rel_path = os.path.relpath(root, current_dir)
        if rel_path == '.':
            rel_path = ''
        else:
            rel_path = rel_path.replace(os.path.sep, '.')
        
        # Find all test_*.py files
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                module_name = file[:-3]  # Remove .py extension
                
                # Construct the full module name
                if rel_path:
                    full_module_name = f"tests.{rel_path}.{module_name}"
                else:
                    full_module_name = f"tests.{module_name}"
                
                # Add to the list of test modules
                test_modules.append(full_module_name)
    
    return test_modules

def run_tests():
    """Run all tests."""
    # Add the parent directory to the path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Discover test modules
    test_modules = discover_test_modules()
    
    # Import each test module and add its tests to the suite
    for module_name in test_modules:
        try:
            # Import the module
            module = importlib.import_module(module_name)
            
            # Add all test cases from the module
            for name in dir(module):
                obj = getattr(module, name)
                if isinstance(obj, type) and issubclass(obj, unittest.TestCase) and obj != unittest.TestCase:
                    test_suite.addTest(unittest.makeSuite(obj))
        except (ImportError, AttributeError) as e:
            print(f"Error importing {module_name}: {e}")
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Return the result
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
