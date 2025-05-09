"""
Test script for the RAG (Retrieval-Augmented Generation) nodes.
"""
import asyncio
import logging
import sys
import json
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the necessary components
from codebase_analyser.agent.state import AgentState
from codebase_analyser.agent.nodes.nlp_nodes import process_requirements
from codebase_analyser.agent.nodes.rag_nodes import retrieve_architectural_context, retrieve_implementation_context, combine_context, retrieve_and_combine_context

async def test_rag_pipeline():
    """Test the complete RAG pipeline."""
    # Sample requirements
    requirements = {
        "description": "Implement a CSV exporter that can export data to a CSV file.",
        "language": "java",
        "file_path": "src/main/java/com/example/export/CsvExporter.java",
        "additional_context": "The exporter should handle escaping of special characters and quoting of fields when necessary."
    }
    
    # Create initial state
    state = AgentState(requirements=requirements)
    
    # Process requirements
    processed_state = await process_requirements(state)
    
    # Run the complete RAG pipeline
    result = await retrieve_and_combine_context(processed_state)
    
    # Print results
    print("\n=== RAG Pipeline Results ===\n")
    print(f"Architectural Context: {len(result.get('architectural_context', []))} items")
    print(f"Implementation Context: {len(result.get('implementation_context', []))} items")
    print("\nCombined Context:")
    print(result.get('combined_context', 'No combined context available'))

async def test_individual_components():
    """Test individual RAG components."""
    # Sample requirements
    requirements = {
        "description": "Implement a CSV exporter that can export data to a CSV file.",
        "language": "java",
        "file_path": "src/main/java/com/example/export/CsvExporter.java",
        "additional_context": "The exporter should handle escaping of special characters and quoting of fields when necessary."
    }
    
    # Create initial state
    state = AgentState(requirements=requirements)
    
    # Process requirements
    processed_state = await process_requirements(state)
    
    # Test architectural context retrieval
    print("\n=== Testing Architectural Context Retrieval ===\n")
    arch_result = await retrieve_architectural_context(processed_state)
    print(f"Retrieved {len(arch_result.get('architectural_context', []))} architectural patterns")
    
    # Update state with architectural context
    state_with_arch = AgentState(
        **processed_state.dict(),
        architectural_context=arch_result.get('architectural_context', [])
    )
    
    # Test implementation context retrieval
    print("\n=== Testing Implementation Context Retrieval ===\n")
    impl_result = await retrieve_implementation_context(state_with_arch)
    print(f"Retrieved {len(impl_result.get('implementation_context', []))} implementation details")
    
    # Update state with implementation context
    state_with_impl = AgentState(
        **state_with_arch.dict(),
        implementation_context=impl_result.get('implementation_context', [])
    )
    
    # Test context combination
    print("\n=== Testing Context Combination ===\n")
    combined_result = await combine_context(state_with_impl)
    print("Combined Context:")
    print(combined_result.get('combined_context', 'No combined context available'))

if __name__ == "__main__":
    # Run the tests
    print("=== Testing RAG Components ===")
    asyncio.run(test_individual_components())
    
    print("\n=== Testing Complete RAG Pipeline ===")
    asyncio.run(test_rag_pipeline())
