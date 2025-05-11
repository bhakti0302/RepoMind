"""
NLP-based nodes for the agent graph.
"""
import logging
import re
from typing import Dict, Any, List, Optional
import json

from ..state import AgentState
from .llm_nodes import llm
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# Configure logging
logger = logging.getLogger(__name__)

# Requirements processing prompt template
REQUIREMENTS_PROCESSING_PROMPT = """
You are an expert software developer tasked with analyzing requirements.

# Requirements
{requirements}

Your task is to analyze these requirements and extract key information.
Please provide your analysis in the following JSON format:

```json
{{
  "intent": "The main intent of the requirements (e.g., create_class, implement_function, etc.)",
  "language": "The programming language to use",
  "entities": {{
    "classes": ["List of class names mentioned"],
    "functions": ["List of function names mentioned"],
    "variables": ["List of variable names mentioned"],
    "properties": ["List of properties or fields mentioned"],
    "data_structures": ["List of data structures mentioned"]
  }},
  "key_phrases": ["List of key phrases from the requirements"],
  "code_references": ["List of references to existing code"],
  "original_text": "The original requirements text"
}}
```

Only respond with the JSON. Do not include any other text.
"""

async def process_requirements(state: AgentState) -> Dict[str, Any]:
    """
    Process requirements using NLP techniques.
    
    Args:
        state: The current agent state
        
    Returns:
        Updated state with processed requirements
    """
    try:
        logger.info("Processing requirements")
        
        # Get requirements text
        if isinstance(state.requirements, dict):
            requirements_text = state.requirements.get("description", "")
            # If language is specified in requirements, use it
            language = state.requirements.get("language", "")
        else:
            requirements_text = str(state.requirements)
            language = ""
        
        # If requirements text is empty, return error
        if not requirements_text:
            logger.error("Empty requirements")
            return {
                "errors": state.errors + [{"stage": "requirements_processing", "message": "Empty requirements"}],
                "processed_requirements": None
            }
        
        # If LLM is not available, use simple processing
        if not llm:
            logger.warning("LLM not available, using simple requirements processing")
            processed = simple_process_requirements(requirements_text, language)
            return {
                "processed_requirements": processed
            }
        
        # Use LLM for requirements processing
        prompt = PromptTemplate(template=REQUIREMENTS_PROCESSING_PROMPT, input_variables=["requirements"])
        parser = JsonOutputParser()
        
        # Create the chain
        chain = prompt | llm | parser
        
        # Run the chain
        processed = await chain.ainvoke({
            "requirements": requirements_text
        })
        
        # Ensure the response has the expected format
        if not isinstance(processed, dict):
            logger.warning(f"Unexpected LLM response format: {type(processed)}")
            processed = simple_process_requirements(requirements_text, language)
        
        # Add original text if not present
        if "original_text" not in processed:
            processed["original_text"] = requirements_text
        
        # Add language if specified in requirements and not in processed
        if language and ("language" not in processed or not processed["language"]):
            processed["language"] = language
        
        # Add file path based on intent and entities
        file_path = determine_file_path(processed)
        if file_path:
            processed["file_path"] = file_path
        
        logger.info(f"Requirements processed: intent={processed.get('intent', 'unknown')}, language={processed.get('language', 'unknown')}")
        
        return {
            "processed_requirements": processed
        }
    except Exception as e:
        logger.error(f"Error processing requirements: {e}")
        return {
            "errors": state.errors + [{"stage": "requirements_processing", "message": str(e)}],
            "processed_requirements": simple_process_requirements(requirements_text, language) if requirements_text else None
        }