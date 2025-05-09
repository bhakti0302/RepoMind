"""
LangGraph-based agent for code generation.
"""
import logging
from typing import Dict, Any, Optional, Literal, List, Union, AsyncIterator
import os
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import state
from .state import AgentState

# Import nodes
from .nodes.llm_nodes import generate_code
from .nodes.validation_nodes import validate_code
from .nodes.rag_nodes import retrieve_and_combine_context
from .nodes.feedback_nodes import process_human_feedback, apply_feedback
from .nodes.output_nodes import prepare_output_for_downstream, save_output_to_file
from .nodes.schema_validation import validate_with_schema, CodeGenerationOutput, ValidationResult

# Try to import LangGraph
try:
    from langgraph.graph import StateGraph
    from langgraph.checkpoint import InMemorySaver
    from langgraph.prebuilt import ToolNode
    LANGGRAPH_AVAILABLE = True
    logger.info("LangGraph is available")
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logger.warning("LangGraph is not available, using mock implementation")

# Constants
MAX_RETRIES = 3
END = "end"

def create_agent_graph(checkpointer=None):
    """
    Create the agent graph.
    
    Args:
        checkpointer: Optional checkpointer for the graph
        
    Returns:
        Compiled StateGraph for the agent
    """
    if not LANGGRAPH_AVAILABLE:
        logger.warning("LangGraph is not available, returning mock graph")
        return "mock_graph"
    
    # Create the graph
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("retrieve_context", retrieve_and_combine_context)
    graph.add_node("generate_code", generate_code)
    graph.add_node("validate_code", validate_code)
    graph.add_node("validate_schema", lambda state: validate_with_schema(state, CodeGenerationOutput))
    graph.add_node("process_feedback", process_human_feedback)
    graph.add_node("apply_feedback", apply_feedback)
    graph.add_node("prepare_output", prepare_output_for_downstream)
    graph.add_node("save_output", save_output_to_file)
    
    # Add basic edges
    graph.add_edge("retrieve_context", "generate_code")
    graph.add_edge("generate_code", "validate_schema")
    graph.add_edge("validate_schema", "validate_code")
    graph.add_edge("process_feedback", "apply_feedback")
    graph.add_edge("apply_feedback", "generate_code")
    graph.add_edge("prepare_output", "save_output")
    
    # Define conditional edges for validation
    def should_regenerate(state: AgentState) -> str:
        """Determine if code should be regenerated based on validation results."""
        # Check if validation result exists
        if not state.validation_result:
            return "prepare_output"
            
        # Check if code is valid
        if state.validation_result.get("valid", True):
            return "prepare_output"
        
        # Check retry count
        retry_count = len([e for e in state.errors if e.get("stage") == "code_generation"])
        if retry_count >= MAX_RETRIES:
            logger.warning(f"Reached maximum retries ({MAX_RETRIES}), proceeding with current code")
            return "prepare_output"
        
        # Regenerate code
        logger.info(f"Code validation failed, regenerating (attempt {retry_count + 1}/{MAX_RETRIES})")
        return "retrieve_context"
    
    # Add conditional edges for validation
    graph.add_conditional_edges(
        "validate_code",
        should_regenerate,
        {
            "prepare_output": "prepare_output",
            "retrieve_context": "retrieve_context"
        }
    )
    
    # Add edge from save_output to end
    graph.add_edge("save_output", END)
    
    # Set the entry point
    graph.set_entry_point("retrieve_context")
    
    # Compile the graph
    memory_saver = checkpointer or InMemorySaver()
    return graph.compile(checkpointer=memory_saver)

async def run_agent(requirements: Dict[str, Any], prompt_template: Optional[str] = None) -> Dict[str, Any]:
    """
    Run the agent with the given requirements.
    
    Args:
        requirements: The requirements for code generation
        prompt_template: Optional prompt template to use
        
    Returns:
        Dictionary with generated code, validation results, and other outputs
    """
    try:
        logger.info("Running agent with requirements: %s", requirements)
        
        if not LANGGRAPH_AVAILABLE:
            logger.error("LangGraph is not available, cannot run agent")
            return {
                "code": "// Error: LangGraph is not available",
                "validation": {"status": "error", "message": "LangGraph is not available"},
                "feedback": None,
                "downstream_data": None
            }
        
        # Create the graph
        graph = create_agent_graph()
        
        # Create the initial state
        initial_state = AgentState(
            requirements=requirements,
            prompt_template=prompt_template,
            timestamp=datetime.now()
        )
        
        # Run the graph
        result = await graph.ainvoke(initial_state)
        
        # Extract the output for downstream agents
        downstream_data = result.downstream_data if hasattr(result, "downstream_data") else None
        
        return {
            "code": result.generated_code,
            "validation": result.validation_result,
            "feedback": result.human_feedback,
            "downstream_data": downstream_data
        }
    except Exception as e:
        logger.error(f"Error running agent: {str(e)}")
        return {
            "code": f"// Error: {str(e)}",
            "validation": {"status": "error", "message": str(e)},
            "feedback": None,
            "downstream_data": None
        }

async def stream_agent(requirements: Dict[str, Any], prompt_template: Optional[str] = None) -> AsyncIterator[Dict[str, Any]]:
    """
    Stream the agent execution with the given requirements.
    
    Args:
        requirements: The requirements for code generation
        prompt_template: Optional prompt template to use
        
    Returns:
        Async iterator with intermediate states
    """
    try:
        logger.info("Streaming agent with requirements: %s", requirements)
        
        if not LANGGRAPH_AVAILABLE:
            logger.error("LangGraph is not available, cannot stream agent")
            yield {
                "status": "error",
                "message": "LangGraph is not available",
                "step": "initialization"
            }
            return
        
        # Create the graph
        graph = create_agent_graph()
        
        # Create the initial state
        initial_state = AgentState(
            requirements=requirements,
            prompt_template=prompt_template,
            timestamp=datetime.now()
        )
        
        # Stream the graph execution
        async for event, state in graph.astream(initial_state, stream_mode="values"):
            # Extract relevant information from the state
            step_output = {
                "status": "in_progress",
                "step": event,
                "timestamp": datetime.now().isoformat()
            }
            
            # Add step-specific information
            if event == "retrieve_context":
                step_output["combined_context"] = state.combined_context if hasattr(state, "combined_context") else None
            elif event == "generate_code":
                step_output["generated_code"] = state.generated_code if hasattr(state, "generated_code") else None
            elif event == "validate_code":
                step_output["validation_result"] = state.validation_result if hasattr(state, "validation_result") else None
            elif event == "prepare_output":
                step_output["downstream_data"] = state.downstream_data if hasattr(state, "downstream_data") else None
            elif event == END:
                step_output["status"] = "completed"
                step_output["final_code"] = state.generated_code if hasattr(state, "generated_code") else None
                step_output["validation"] = state.validation_result if hasattr(state, "validation_result") else None
            
            yield step_output
    except Exception as e:
        logger.error(f"Error streaming agent: {str(e)}")
        yield {
            "status": "error",
            "message": str(e),
            "step": "unknown"
        }

def visualize_agent_graph(output_file: str = "agent_graph.png"):
    """
    Visualize the agent graph and save it to a file.
    
    Args:
        output_file: The file to save the visualization to
    """
    if not LANGGRAPH_AVAILABLE:
        logger.error("LangGraph is not available, cannot visualize graph")
        return
    
    try:
        # Create the graph
        graph = create_agent_graph()
        
        # Get the graph visualization
        if hasattr(graph, "get_graph"):
            graph_viz = graph.get_graph()
            
            # Save the visualization
            if hasattr(graph_viz, "save"):
                graph_viz.save(output_file)
                logger.info(f"Graph visualization saved to {output_file}")
            else:
                logger.error("Graph visualization object does not have a save method")
        else:
            logger.error("Graph object does not have a get_graph method")
    except Exception as e:
        logger.error(f"Error visualizing agent graph: {str(e)}")

def get_agent_info() -> Dict[str, Any]:
    """
    Get information about the agent.
    
    Returns:
        Dictionary with agent information
    """
    return {
        "name": "CodeGenerationAgent",
        "description": "LangGraph-based agent for code generation",
        "version": "0.1.0",
        "nodes": [
            "retrieve_context",
            "generate_code",
            "validate_schema",
            "validate_code",
            "process_feedback",
            "apply_feedback",
            "prepare_output",
            "save_output"
        ],
        "entry_point": "retrieve_context",
        "max_retries": MAX_RETRIES,
        "langgraph_available": LANGGRAPH_AVAILABLE
    }
