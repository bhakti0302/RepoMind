"""
Main test runner script.
"""

import sys
import os
import logging
import argparse
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def run_test(test_script, args=None):
    """Run a test script.
    
    Args:
        test_script: Path to the test script
        args: Additional arguments to pass to the test script
    """
    try:
        # Build the command
        cmd = [sys.executable, test_script]
        if args:
            cmd.extend(args)
        
        # Run the command
        logger.info(f"Running test: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True)
        
        return result.returncode == 0
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Test failed: {e}")
        return False
    
    except Exception as e:
        logger.error(f"Error running test: {e}")
        return False

def run_all_tests(db_path, output_dir):
    """Run all tests.
    
    Args:
        db_path: Path to the LanceDB database
        output_dir: Path to the output directory
    """
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define the tests to run
    tests = [
        {
            "name": "Entity Extractor",
            "script": os.path.join(script_dir, "test_entity_extractor.py"),
            "args": []
        },
        {
            "name": "Component Analyzer",
            "script": os.path.join(script_dir, "test_component_analyzer.py"),
            "args": []
        },
        {
            "name": "Vector Search",
            "script": os.path.join(script_dir, "test_vector_search.py"),
            "args": ["--db-path", db_path]
        },
        {
            "name": "RAG Implementation",
            "script": os.path.join(script_dir, "test_rag.py"),
            "args": ["--db-path", db_path, "--output-dir", output_dir]
        },
        {
            "name": "End-to-End Pipeline",
            "script": os.path.join(script_dir, "test_pipeline.py"),
            "args": ["--db-path", db_path, "--output-dir", output_dir]
        }
    ]
    
    # Run each test
    results = {}
    for test in tests:
        print(f"\n=== Running {test['name']} Test ===\n")
        success = run_test(test["script"], test["args"])
        results[test["name"]] = "Passed" if success else "Failed"
    
    # Print the summary
    print("\n=== Test Summary ===\n")
    for test_name, result in results.items():
        print(f"{test_name}: {result}")
    
    # Return True if all tests passed
    return all(result == "Passed" for result in results.values())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run tests")
    parser.add_argument("--db-path", default="../.lancedb", help="Path to the LanceDB database")
    parser.add_argument("--output-dir", default="../output", help="Path to the output directory")
    parser.add_argument("--test", choices=["entity", "component", "vector", "rag", "pipeline", "all"], default="all", help="Test to run")
    args = parser.parse_args()
    
    # Create the output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Run the specified test
    if args.test == "entity":
        run_test(os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_entity_extractor.py"))
    elif args.test == "component":
        run_test(os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_component_analyzer.py"))
    elif args.test == "vector":
        run_test(os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_vector_search.py"), ["--db-path", args.db_path])
    elif args.test == "rag":
        run_test(os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_rag.py"), ["--db-path", args.db_path, "--output-dir", args.output_dir])
    elif args.test == "pipeline":
        run_test(os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_pipeline.py"), ["--db-path", args.db_path, "--output-dir", args.output_dir])
    else:
        run_all_tests(args.db_path, args.output_dir)