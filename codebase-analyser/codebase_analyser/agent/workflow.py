"""
Agent workflow module.

This module defines the workflow for the agent, orchestrating the different nodes
to process requirements, generate code, validate it, and generate documentation and tests.
"""

import logging
import asyncio
from typing import Dict, Any, Optional

from .state import AgentState
from .nodes.nlp_nodes import process_requirements
from .nodes.context_nodes import retrieve_context
from .nodes.llm_nodes import generate_code, generate_documentation, generate_tests
from .nodes.validation_nodes import validate_code

# Configure logging
logger = logging.getLogger(__name__)

async def run_agent_workflow(state: AgentState) -> AgentState:
    """
    Run the agent workflow.
    
    Args:
        state: The initial agent state
        
    Returns:
        The final agent state
    """
    logger.info("Starting agent workflow")
    
    try:
        # Process requirements
        logger.info("Processing requirements")
        result = await process_requirements(state)
        state.update(result)
        
        # If there are errors, return early
        if state.errors:
            logger.error(f"Errors during requirements processing: {state.errors}")
            return state
        
        # Retrieve context
        logger.info("Retrieving context")
        result = await retrieve_context(state)
        state.update(result)
        
        # Generate code
        logger.info("Generating code")
        result = await generate_code(state)
        state.update(result)
        
        # If there are errors or no code was generated, return early
        if state.errors or not state.generated_code:
            logger.error(f"Errors during code generation: {state.errors}")
            return state
        
        # Validate code
        logger.info("Validating code")
        result = await validate_code(state)
        state.update(result)
        
        # Generate documentation
        logger.info("Generating documentation")
        result = await generate_documentation(state)
        state.update(result)
        
        # Generate tests
        logger.info("Generating tests")
        result = await generate_tests(state)
        state.update(result)
        
        logger.info("Agent workflow completed successfully")
        return state
    
    except Exception as e:
        logger.error(f"Error in agent workflow: {e}")
        state.errors.append({
            "stage": "workflow",
            "message": str(e)
        })
        return state