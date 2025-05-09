"""
Test script for the LangGraph agent.
"""
import asyncio
import logging
import os
from codebase_analyser.agent import create_agent_graph, AgentState

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_agent():
    """Test the LangGraph agent with a simple example."""
    # Set environment variables for OpenRouter
    os.environ["LLM_MODEL_NAME"] = "nvidia/llama-3.3-nemotron-super-49b-v1:free"  # Using NVIDIA Llama model
    
    # Set your OpenRouter API key
    os.environ["OPENROUTER_API_KEY"] = "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"
    
    # Create the agent graph
    agent = create_agent_graph()
    
    # Create initial state
    initial_state = AgentState(
        requirements="Write a java class CSVExporter.java with methods that implements the functionality of exporting data from CSV file. Return only the java code and nothing else in response."
    )
    
    # Create configuration with thread_id
    config = {"configurable": {"thread_id": "test-thread-1"}}
    
    # Run the agent
    logger.info("Starting agent execution")
    final_state_dict = await agent.ainvoke(initial_state, config)
    
    # Print results
    logger.info("Agent execution completed")
    
    # Access the generated code from the dictionary
    if 'generated_code' in final_state_dict:
        generated_code = final_state_dict['generated_code']
        logger.info(f"Generated code:\n{generated_code}")
        
        # Save the generated code to a file
        output_dir = "generated_code"
        os.makedirs(output_dir, exist_ok=True)
        
        # Determine file extension based on content (simple heuristic)
        file_ext = ".java"  # Default to Java
        if "def " in generated_code and ":" in generated_code:
            file_ext = ".py"
        elif "function" in generated_code and "{" in generated_code:
            file_ext = ".js"
        elif "import React" in generated_code:
            file_ext = ".jsx"
        elif "<html" in generated_code.lower():
            file_ext = ".html"
        
        # Create a filename based on the requirements
        filename = "CsvExporter" + file_ext
        output_file = os.path.join(output_dir, filename)
        
        with open(output_file, "w") as f:
            f.write(generated_code)
        
        logger.info(f"Generated code saved to {output_file}")
    else:
        logger.info(f"Available keys in final state: {list(final_state_dict.keys())}")
        logger.info(f"Final state: {final_state_dict}")
    
    return final_state_dict

if __name__ == "__main__":
    asyncio.run(test_agent())
