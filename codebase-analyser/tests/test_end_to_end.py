#!/usr/bin/env python3
"""
End-to-end tests for the codebase analyzer.

This script tests the complete flow from requirements processing to code generation:
1. Process requirements with NLP
2. Retrieve context from the vector store
3. Generate code using the LLM
4. Validate the generated code
"""

import os
import sys
import json
import pytest
import logging
import tempfile
import shutil
from pathlib import Path
import asyncio
from typing import Dict, Any, List

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from codebase_analyser.agent.graph import run_agent
from codebase_analyser.database import open_unified_storage, close_unified_storage
from codebase_analyser.embeddings.embedding_generator import EmbeddingGenerator  # Import directly from the module
from codebase_analyser.agent.state import AgentState

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test cases
TEST_CASES = [
    {
        "name": "java_csv_exporter",
        "requirements": {
            "description": "Implement a CSV exporter that can export data to a CSV file.",
            "language": "java",
            "file_path": "src/main/java/com/example/export/CsvExporter.java",
            "additional_context": "The exporter should handle escaping of special characters and quoting of fields when necessary."
        },
        "expected_elements": [
            "class CsvExporter",
            "export",
            "CSV",
            "escaping",
            "quoting"
        ]
    },
    {
        "name": "python_data_processor",
        "requirements": {
            "description": "Create a data processor that can filter, transform, and aggregate data from multiple sources.",
            "language": "python",
            "file_path": "src/data_processing/processor.py",
            "additional_context": "The processor should be able to handle CSV, JSON, and database inputs."
        },
        "expected_elements": [
            "class DataProcessor",
            "filter",
            "transform",
            "aggregate",
            "CSV",
            "JSON",
            "database"
        ]
    },
    {
        "name": "javascript_api_client",
        "requirements": {
            "description": "Implement an API client that can make HTTP requests to a REST API.",
            "language": "javascript",
            "file_path": "src/api/client.js",
            "additional_context": "The client should handle authentication, error handling, and retries."
        },
        "expected_elements": [
            "class ApiClient",
            "HTTP",
            "REST",
            "authentication",
            "error handling",
            "retries"
        ]
    }
]

@pytest.fixture
def setup_test_environment():
    """Set up the test environment."""
    # Create a temporary directory for test outputs
    temp_dir = tempfile.mkdtemp()
    
    # Set environment variables for testing
    os.environ["USE_MOCK_EMBEDDINGS"] = "1"  # Use mock embeddings for testing
    
    yield temp_dir
    
    # Clean up
    shutil.rmtree(temp_dir)

@pytest.fixture
def setup_test_database():
    """Set up a test database."""
    # Create a temporary directory for the database
    db_dir = tempfile.mkdtemp()
    db_path = os.path.join(db_dir, "test.lancedb")
    
    # Set up the database
    storage_manager = open_unified_storage(
        db_path=db_path,
        use_minimal_schema=True,
        create_if_not_exists=True,
        read_only=False
    )
    
    # Add some test data
    test_chunks = [
        {
            "node_id": "com.example.export.CsvExporter",
            "name": "CsvExporter",
            "content": "public class CsvExporter { public void export(List<String[]> data, String filePath) { ... } }",
            "type": "class_definition",
            "language": "java",
            "path": "src/main/java/com/example/export/CsvExporter.java",
            "embedding": [0.1] * 768  # Mock embedding
        },
        {
            "node_id": "com.example.data.DataProcessor",
            "name": "DataProcessor",
            "content": "public class DataProcessor { public void process(Data data) { ... } }",
            "type": "class_definition",
            "language": "java",
            "path": "src/main/java/com/example/data/DataProcessor.java",
            "embedding": [0.2] * 768  # Mock embedding
        },
        {
            "node_id": "com.example.api.ApiClient",
            "name": "ApiClient",
            "content": "public class ApiClient { public Response get(String url) { ... } }",
            "type": "class_definition",
            "language": "java",
            "path": "src/main/java/com/example/api/ApiClient.java",
            "embedding": [0.3] * 768  # Mock embedding
        }
    ]
    
    storage_manager.add_code_chunks_with_graph_metadata(chunks=test_chunks)
    
    # Close the database
    close_unified_storage(storage_manager)
    
    yield db_path
    
    # Clean up
    shutil.rmtree(db_dir)

@pytest.mark.asyncio
@pytest.mark.parametrize("test_case", TEST_CASES)
async def test_end_to_end(setup_test_environment, setup_test_database, test_case):
    """
    Test the end-to-end flow for a specific test case.
    
    Args:
        setup_test_environment: Test environment fixture
        setup_test_database: Test database fixture
        test_case: The test case to run
    """
    # Set up
    output_dir = os.path.join(setup_test_environment, test_case["name"])
    os.makedirs(output_dir, exist_ok=True)
    
    # Set environment variables
    os.environ["DB_PATH"] = setup_test_database
    os.environ["USE_MOCK_LLM"] = "1"  # Use mock LLM for testing
    
    # Run the agent
    result = await run_agent(test_case["requirements"], output_dir=output_dir)
    
    # Save the result
    with open(os.path.join(output_dir, "result.json"), 'w') as f:
        json.dump(result, f, indent=2)
    
    # Assertions
    assert result is not None, "Result should not be None"
    assert "code" in result, "Result should contain generated code"
    assert result["code"], "Generated code should not be empty"
    
    # Check for expected elements in the generated code
    for element in test_case["expected_elements"]:
        assert element.lower() in result["code"].lower(), f"Generated code should contain '{element}'"
    
    # Check that the file was created
    output_file = os.path.join(output_dir, os.path.basename(test_case["requirements"]["file_path"]))
    assert os.path.exists(output_file), f"Output file {output_file} should exist"
    
    # Log success
    logger.info(f"Test case {test_case['name']} passed")

@pytest.mark.asyncio
async def test_error_handling(setup_test_environment):
    """
    Test error handling in the agent.
    
    Args:
        setup_test_environment: Test environment fixture
    """
    # Set up
    output_dir = os.path.join(setup_test_environment, "error_handling")
    os.makedirs(output_dir, exist_ok=True)
    
    # Set environment variables to force errors
    os.environ["DB_PATH"] = "nonexistent_path"
    os.environ["USE_MOCK_LLM"] = "0"  # Don't use mock LLM
    os.environ["OPENAI_API_KEY"] = "invalid_key"  # Invalid API key
    
    # Create an invalid requirements object
    invalid_requirements = {
        "description": "",  # Empty description
        "language": "unknown_language",  # Invalid language
        "file_path": ""  # Empty file path
    }
    
    # Run the agent
    result = await run_agent(invalid_requirements, output_dir=output_dir)
    
    # Save the result
    with open(os.path.join(output_dir, "result.json"), 'w') as f:
        json.dump(result, f, indent=2)
    
    # Assertions
    assert result is not None, "Result should not be None"
    assert "code" in result, "Result should contain generated code field"
    assert not result["code"], "Generated code should be empty due to errors"
    assert not result["validation_status"], "Validation status should be False"
    assert "metadata" in result, "Result should contain metadata"
    assert "errors" in result["metadata"], "Metadata should contain errors"
    assert len(result["metadata"]["errors"]) > 0, "There should be at least one error"
    
    # Log success
    logger.info("Error handling test passed")

@pytest.mark.asyncio
async def test_human_in_the_loop(setup_test_environment, setup_test_database):
    """
    Test human-in-the-loop functionality.
    
    Args:
        setup_test_environment: Test environment fixture
        setup_test_database: Test database fixture
    """
    # Set up
    output_dir = os.path.join(setup_test_environment, "human_in_the_loop")
    os.makedirs(output_dir, exist_ok=True)
    
    # Set environment variables
    os.environ["DB_PATH"] = setup_test_database
    os.environ["USE_MOCK_LLM"] = "1"  # Use mock LLM for testing
    os.environ["ENABLE_HUMAN_FEEDBACK"] = "1"  # Enable human feedback
    
    # Create a test case that requires human feedback
    test_case = {
        "description": "Implement a user authentication system with OAuth2 support.",
        "language": "java",
        "file_path": "src/main/java/com/example/auth/AuthService.java",
        "additional_context": "The system should support Google and Facebook OAuth providers.",
        "require_human_feedback": True
    }
    
    # Mock human feedback function
    async def mock_human_feedback(code, prompt):
        return {
            "approved": True,
            "feedback": "Looks good, but add more comments.",
            "modified_code": code + "\n// Additional comments added by human reviewer\n"
        }
    
    # Patch the human feedback function
    import codebase_analyser.agent.human_feedback
    original_get_human_feedback = codebase_analyser.agent.human_feedback.get_human_feedback
    codebase_analyser.agent.human_feedback.get_human_feedback = mock_human_feedback
    
    try:
        # Run the agent
        result = await run_agent(test_case, output_dir=output_dir)
        
        # Save the result
        with open(os.path.join(output_dir, "result.json"), 'w') as f:
            json.dump(result, f, indent=2)
        
        # Assertions
        assert result is not None, "Result should not be None"
        assert "code" in result, "Result should contain generated code"
        assert result["code"], "Generated code should not be empty"
        assert "// Additional comments added by human reviewer" in result["code"], "Generated code should contain human feedback"
        assert "metadata" in result, "Result should contain metadata"
        assert "human_feedback" in result["metadata"], "Metadata should contain human feedback information"
        assert result["metadata"]["human_feedback"]["approved"], "Human feedback should be approved"
        
        # Log success
        logger.info("Human-in-the-loop test passed")
    finally:
        # Restore the original function
        codebase_analyser.agent.human_feedback.get_human_feedback = original_get_human_feedback

def main():
    """Run the tests."""
    # Run pytest
    pytest.main(["-xvs", __file__])

if __name__ == "__main__":
    main()
