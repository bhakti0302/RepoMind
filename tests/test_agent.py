"""
Tests for the agent implementation.
"""
import os
import json
import logging
import argparse
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional

from codebase_analyser.agent.graph import create_agent_graph, run_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test cases
TEST_CASES = [
    {
        "name": "csv_exporter",
        "requirements": {
            "description": "Implement a CSV exporter that can export data to a CSV file.",
            "language": "java",
            "file_path": "src/main/java/com/example/export/CsvExporter.java",
            "additional_context": "The exporter should handle escaping of special characters and quoting of fields when necessary."
        }
    },
    {
        "name": "json_exporter",
        "requirements": {
            "description": "Implement a JSON exporter that can export data to a JSON file.",
            "language": "java",
            "file_path": "src/main/java/com/example/export/JsonExporter.java",
            "additional_context": "The exporter should use the Gson library for JSON serialization."
        }
    },
    {
        "name": "python_data_processor",
        "requirements": {
            "description": "Implement a data processor in Python that can read CSV files, process the data, and output the results.",
            "language": "python",
            "file_path": "src/data_processor.py",
            "additional_context": "The processor should use pandas for data manipulation and support filtering and aggregation operations."
        }
    },
    {
        "name": "javascript_api_client",
        "requirements": {
            "description": "Implement a JavaScript API client that can make HTTP requests to a REST API.",
            "language": "javascript",
            "file_path": "src/api_client.js",
            "additional_context": "The client should support GET, POST, PUT, and DELETE methods, handle authentication, and provide error handling."
        }
    }
]

def load_requirements(file_path: str) -> Dict[str, Any]:
    """
    Load requirements from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        The loaded requirements
    """
    with open(file_path, 'r') as f:
        return json.load(f)

async def run_test_case(test_case: Dict[str, Any], output_dir: str, use_mock: bool = False) -> Dict[str, Any]:
    """
    Run a test case.
    
    Args:
        test_case: The test case to run
        output_dir: Directory to save output
        use_mock: Whether to use mock implementations
        
    Returns:
        The test results
    """
    # Create output directory
    test_output_dir = os.path.join(output_dir, test_case["name"])
    os.makedirs(test_output_dir, exist_ok=True)
    
    # Set environment variables for testing
    if use_mock:
        os.environ["USE_MOCK_IMPLEMENTATIONS"] = "1"
    else:
        os.environ.pop("USE_MOCK_IMPLEMENTATIONS", None)
    
    # Run the agent
    result = await run_agent(test_case["requirements"], output_dir=test_output_dir)
    
    # Save the result
    with open(os.path.join(test_output_dir, "result.json"), 'w') as f:
        json.dump(result, f, indent=2)
    
    return result

async def run_tests(output_dir: str, test_cases: List[Dict[str, Any]], use_mock: bool = False) -> Dict[str, Any]:
    """
    Run all test cases.
    
    Args:
        output_dir: Directory to save output
        test_cases: List of test cases to run
        use_mock: Whether to use mock implementations
        
    Returns:
        The test results
    """
    results = {}
    
    for test_case in test_cases:
        logger.info(f"Running test case: {test_case['name']}")
        result = await run_test_case(test_case, output_dir, use_mock)
        results[test_case["name"]] = {
            "success": result.get("validation_result", {}).get("valid", False),
            "score": result.get("validation_result", {}).get("score", 0),
            "issues": len(result.get("validation_result", {}).get("issues", [])),
            "suggestions": len(result.get("validation_result", {}).get("suggestions", []))
        }
    
    # Save summary
    with open(os.path.join(output_dir, "summary.json"), 'w') as f:
        json.dump(results, f, indent=2)
    
    return results

def main():
    """
    Main entry point.
    """
    parser = argparse.ArgumentParser(description="Test the codebase analyser agent")
    parser.add_argument("--output-dir", type=str, default="./test_output", help="Directory to save output")
    parser.add_argument("--requirements-file", type=str, help="Path to requirements JSON file")
    parser.add_argument("--use-mock", action="store_true", help="Use mock implementations")
    parser.add_argument("--test-case", type=str, help="Name of a specific test case to run")
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Determine test cases to run
    if args.requirements_file:
        # Load requirements from file
        requirements = load_requirements(args.requirements_file)
        test_cases = [{
            "name": Path(args.requirements_file).stem,
            "requirements": requirements
        }]
    elif args.test_case:
        # Find the specified test case
        test_cases = [tc for tc in TEST_CASES if tc["name"] == args.test_case]
        if not test_cases:
            logger.error(f"Test case not found: {args.test_case}")
            return
    else:
        # Use all test cases
        test_cases = TEST_CASES
    
    # Run the tests
    results = asyncio.run(run_tests(args.output_dir, test_cases, args.use_mock))
    
    # Print summary
    print("\nTest Results:")
    print("=============")
    for name, result in results.items():
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{name}: {status} (Score: {result['score']}, Issues: {result['issues']}, Suggestions: {result['suggestions']})")

if __name__ == "__main__":
    main()