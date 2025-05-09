"""
Feedback nodes for the agent graph.
"""
import logging
from typing import Dict, Any, List, Optional
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

from ..state import AgentState

# Configure logging
logger = logging.getLogger(__name__)

# Feedback incorporation prompt template
FEEDBACK_INCORPORATION_TEMPLATE = """
You are an expert software developer tasked with improving code based on human feedback.

# Original Requirements
{requirements}

# Generated Code
```{language}
{code}
```

# Human Feedback
{feedback}

Your task is to revise the code to address the human feedback while still meeting the original requirements.
Please provide ONLY the complete implementation for the file. Do not include any explanations, comments about your approach, or markdown formatting.

The implementation should be in {language} and should be saved to {file_path}.
"""

async def process_human_feedback(state: AgentState) -> Dict[str, Any]:
    """
    Process human feedback on the generated code.
    
    Args:
        state: The current agent state
        
    Returns:
        Updated state with processed feedback
    """
    logger.info("Processing human feedback")
    
    # If no human feedback is provided, return the state unchanged
    if not state.human_feedback:
        logger.info("No human feedback provided, skipping feedback processing")
        return {}
    
    # Process the feedback
    processed_feedback = {
        "original_feedback": state.human_feedback,
        "feedback_points": extract_feedback_points(state.human_feedback)
    }
    
    logger.info(f"Processed {len(processed_feedback['feedback_points'])} feedback points")
    
    return {
        "processed_feedback": processed_feedback
    }

def extract_feedback_points(feedback: str) -> List[Dict[str, Any]]:
    """
    Extract structured feedback points from human feedback.
    
    Args:
        feedback: The human feedback string
        
    Returns:
        List of feedback points
    """
    # Simple extraction based on line breaks
    lines = [line.strip() for line in feedback.split('\n') if line.strip()]
    
    feedback_points = []
    current_point = None
    
    for line in lines:
        if line.startswith('-') or line.startswith('*') or line.startswith('#'):
            # Start a new feedback point
            if current_point:
                feedback_points.append(current_point)
            
            current_point = {
                "description": line.lstrip('-*# ').strip(),
                "details": []
            }
        elif current_point:
            # Add to the current feedback point
            current_point["details"].append(line)
    
    # Add the last feedback point
    if current_point:
        feedback_points.append(current_point)
    
    return feedback_points

async def apply_feedback(state: AgentState) -> Dict[str, Any]:
    """
    Apply human feedback to generate improved code.
    
    Args:
        state: The current agent state
        
    Returns:
        Updated state with improved code
    """
    logger.info("Applying feedback to generate improved code")
    
    # If no processed feedback is available, return the state unchanged
    if not state.processed_feedback:
        logger.info("No processed feedback available, skipping feedback application")
        return {}
    
    # Get the LLM from the llm_nodes module
    from .llm_nodes import llm
    
    if not llm:
        logger.error("LLM not initialized, cannot apply feedback")
        error_message = "LLM not initialized. Please ensure OPENAI_API_KEY or OPENROUTER_API_KEY is set in environment variables."
        
        return {
            "errors": state.errors + [{"stage": "feedback_application", "message": error_message}]
        }
    
    try:
        # Get language and file path from processed requirements
        language = state.processed_requirements.get("language", "java") if state.processed_requirements else "java"
        file_path = state.processed_requirements.get("file_path", "output.txt") if state.processed_requirements else "output.txt"
        
        # Get requirements text
        requirements_text = state.processed_requirements.get("original_text", "") if state.processed_requirements else ""
        
        # Format the feedback as a string
        feedback_str = state.human_feedback
        
        # Create the prompt
        prompt = PromptTemplate.from_template(FEEDBACK_INCORPORATION_TEMPLATE)
        
        # Create the chain
        chain = prompt | llm | StrOutputParser()
        
        # Run the chain
        response = await chain.ainvoke({
            "requirements": requirements_text,
            "language": language,
            "code": state.generated_code,
            "feedback": feedback_str,
            "file_path": file_path
        })
        
        # Clean up the response
        code = response.strip()
        
        # Remove markdown code block markers if present
        if code.startswith("```") and code.endswith("```"):
            # Extract the language if specified
            first_line = code.split("\n")[0].strip()
            if first_line.startswith("```") and len(first_line) > 3:
                code = code[len(first_line):].strip()
            else:
                code = code[3:].strip()
            
            if code.endswith("```"):
                code = code[:-3].strip()
        
        logger.info(f"Generated improved code length: {len(code)} characters")
        
        return {
            "generated_code": code,
            "llm_response": response
        }
    except Exception as e:
        logger.error(f"Error applying feedback: {e}")
        error_message = f"Feedback application failed: {str(e)}"
        
        return {
            "errors": state.errors + [{"stage": "feedback_application", "message": error_message}]
        }