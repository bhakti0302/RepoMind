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
{
  "intent": "The main intent of the requirements (e.g., create_class, implement_function, etc.)",
  "language": "The programming language to use",
  "entities": {
    "classes": ["List of class names mentioned"],
    "functions": ["List of function names mentioned"],
    "variables": ["List of variable names mentioned"],
    "properties": ["List of properties or fields mentioned"],
    "data_structures": ["List of data structures mentioned"]
  },
  "key_phrases": ["List of key phrases from the requirements"],
  "code_references": ["List of references to existing code"],
  "original_text": "The original requirements text"
}
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
        prompt = PromptTemplate.from_template(REQUIREMENTS_PROCESSING_PROMPT)
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

def simple_process_requirements(requirements_text: str, language: str = "") -> Dict[str, Any]:
    """
    Process requirements using simple NLP techniques when LLM is not available.
    
    Args:
        requirements_text: The requirements text
        language: The programming language (if specified)
        
    Returns:
        Processed requirements
    """
    logger.info("Using simple requirements processing")
    
    # Initialize processed requirements
    processed = {
        "intent": "unknown",
        "language": language.lower() if language else "java",  # Default to Java if not specified
        "entities": {
            "classes": [],
            "functions": [],
            "variables": [],
            "properties": [],
            "data_structures": []
        },
        "key_phrases": [],
        "code_references": [],
        "original_text": requirements_text
    }
    
    # Determine intent based on keywords
    if re.search(r"create|implement|develop|build", requirements_text, re.IGNORECASE):
        if re.search(r"class|interface", requirements_text, re.IGNORECASE):
            processed["intent"] = "create_class"
        elif re.search(r"function|method", requirements_text, re.IGNORECASE):
            processed["intent"] = "implement_function"
        elif re.search(r"api|endpoint", requirements_text, re.IGNORECASE):
            processed["intent"] = "create_api"
        else:
            processed["intent"] = "create_component"
    elif re.search(r"fix|resolve|correct", requirements_text, re.IGNORECASE):
        processed["intent"] = "fix_bug"
    elif re.search(r"refactor|improve|optimize", requirements_text, re.IGNORECASE):
        processed["intent"] = "refactor_code"
    elif re.search(r"add|extend|enhance", requirements_text, re.IGNORECASE):
        processed["intent"] = "add_feature"
    
    # Determine language if not specified
    if not language:
        if re.search(r"java|\.java", requirements_text, re.IGNORECASE):
            processed["language"] = "java"
        elif re.search(r"python|\.py", requirements_text, re.IGNORECASE):
            processed["language"] = "python"
        elif re.search(r"javascript|js|\.js", requirements_text, re.IGNORECASE):
            processed["language"] = "javascript"
        elif re.search(r"typescript|ts|\.ts", requirements_text, re.IGNORECASE):
            processed["language"] = "typescript"
        elif re.search(r"c\+\+|cpp|\.cpp", requirements_text, re.IGNORECASE):
            processed["language"] = "cpp"
        elif re.search(r"c#|csharp|\.cs", requirements_text, re.IGNORECASE):
            processed["language"] = "csharp"
    
    # Extract class names (capitalized words)
    class_pattern = r'\b[A-Z][a-zA-Z0-9]*\b'
    processed["entities"]["classes"] = list(set(re.findall(class_pattern, requirements_text)))
    
    # Extract function names (words followed by parentheses)
    function_pattern = r'\b[a-zA-Z][a-zA-Z0-9]*\s*\('
    function_matches = re.findall(function_pattern, requirements_text)
    processed["entities"]["functions"] = [match.strip('( ') for match in function_matches]
    
    # Extract properties (words after "with" or "has")
    property_pattern = r'(?:with|has)\s+([a-zA-Z][a-zA-Z0-9]*)'
    property_matches = re.findall(property_pattern, requirements_text, re.IGNORECASE)
    processed["entities"]["properties"] = property_matches
    
    # Extract data structures
    data_structures = ["list", "array", "map", "dictionary", "set", "queue", "stack", "tree", "graph"]
    for ds in data_structures:
        if re.search(r'\b' + ds + r'\b', requirements_text, re.IGNORECASE):
            processed["entities"]["data_structures"].append(ds)
    
    # Extract key phrases (noun phrases)
    # Simple approach: look for adjective + noun patterns
    key_phrase_pattern = r'\b[a-zA-Z]+\s+[a-zA-Z]+\b'
    key_phrases = re.findall(key_phrase_pattern, requirements_text)
    processed["key_phrases"] = [phrase for phrase in key_phrases if len(phrase.split()) >= 2][:5]  # Limit to 5 phrases
    
    # Add file path
    file_path = determine_file_path(processed)
    if file_path:
        processed["file_path"] = file_path
    
    return processed

def determine_file_path(processed_requirements: Dict[str, Any]) -> str:
    """
    Determine the file path based on processed requirements.
    
    Args:
        processed_requirements: The processed requirements
        
    Returns:
        The file path
    """
    language = processed_requirements.get("language", "").lower()
    intent = processed_requirements.get("intent", "").lower()
    entities = processed_requirements.get("entities", {})
    
    # Get the first class name if available
    class_name = entities.get("classes", ["Main"])[0] if entities.get("classes") else "Main"
    
    # Get the first function name if available
    function_name = entities.get("functions", ["main"])[0] if entities.get("functions") else "main"
    
    # Determine file extension based on language
    if language == "java":
        ext = ".java"
    elif language == "python":
        ext = ".py"
    elif language in ["javascript", "js"]:
        ext = ".js"
    elif language in ["typescript", "ts"]:
        ext = ".ts"
    elif language in ["cpp", "c++"]:
        ext = ".cpp"
    elif language in ["csharp", "c#"]:
        ext = ".cs"
    else:
        ext = ".txt"
    
    # Determine file name based on intent
    if intent == "create_class" and class_name:
        file_name = f"{class_name}{ext}"
    elif intent == "implement_function" and function_name:
        if language == "python":
            file_name = f"{function_name.lower()}{ext}"
        else:
            file_name = f"{function_name}{ext}"
    elif intent == "create_api":
        file_name = f"api{ext}"
    elif intent == "fix_bug" or intent == "refactor_code":
        if class_name and class_name != "Main":
            file_name = f"{class_name}{ext}"
        else:
            file_name = f"fixed_code{ext}"
    else:
        if class_name and class_name != "Main":
            file_name = f"{class_name}{ext}"
        else:
            file_name = f"output{ext}"
    
    return file_name

async def retrieve_context(state: AgentState) -> Dict[str, Any]:
    """
    Retrieve context for the requirements.
    
    Args:
        state: The current agent state
        
    Returns:
        Updated state with context
    """
    try:
        logger.info("Retrieving context")
        
        # If processed requirements are not available, return empty context
        if not state.processed_requirements:
            logger.warning("No processed requirements available for context retrieval")
            return {
                "combined_context": ""
            }
        
        # In a real implementation, this would retrieve relevant context from the codebase
        # For now, we'll just create a simple context based on the processed requirements
        
        # Get key information from processed requirements
        intent = state.processed_requirements.get("intent", "unknown")
        language = state.processed_requirements.get("language", "java")
        entities = state.processed_requirements.get("entities", {})
        
        # Create a simple context
        context = f"Creating code for intent: {intent} in language: {language}.\n"
        
        # Add entities to context
        for entity_type, entity_list in entities.items():
            if entity_list:
                context += f"{entity_type.capitalize()}: {', '.join(entity_list)}.\n"
        
        logger.info(f"Retrieved context: {len(context)} characters")
        
        return {
            "combined_context": context
        }
    except Exception as e:
        logger.error(f"Error retrieving context: {e}")
        return {
            "errors": state.errors + [{"stage": "context_retrieval", "message": str(e)}],
            "combined_context": ""
        }
