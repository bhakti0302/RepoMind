"""
Schema validation nodes for the agent graph.
"""
import logging
from typing import Dict, Any, List, Optional, Type
from pydantic import BaseModel, Field, field_validator
from langchain_core.messages import AIMessage, ToolMessage

try:
    from langgraph.prebuilt import ValidationNode
    VALIDATION_NODE_AVAILABLE = True
except ImportError:
    VALIDATION_NODE_AVAILABLE = False

from ..state import AgentState

# Configure logging
logger = logging.getLogger(__name__)

# Define schemas for validation
class CodeGenerationOutput(BaseModel):
    """Schema for code generation output."""
    code: str = Field(..., description="The generated code")
    language: str = Field(..., description="The programming language")
    file_path: str = Field(..., description="The file path to save the code")
    
    @field_validator("code")
    def code_must_not_be_empty(cls, v):
        """Validate that code is not empty."""
        if not v.strip():
            raise ValueError("Generated code cannot be empty")
        return v
    
    @field_validator("language")
    def language_must_be_valid(cls, v):
        """Validate that language is supported."""
        valid_languages = ["python", "java", "javascript", "js", "py"]
        if v.lower() not in valid_languages:
            raise ValueError(f"Language must be one of: {', '.join(valid_languages)}")
        return v

class ValidationResult(BaseModel):
    """Schema for validation result."""
    valid: bool = Field(..., description="Whether the code is valid")
    issues: List[Dict[str, Any]] = Field(default_factory=list, description="List of issues found")
    summary: str = Field(..., description="Summary of validation")

def create_validation_node(schema_type: Type[BaseModel]) -> Any:
    """
    Create a validation node for the given schema.
    
    Args:
        schema_type: The Pydantic schema to validate against
        
    Returns:
        A validation node
    """
    if not VALIDATION_NODE_AVAILABLE:
        logger.warning("ValidationNode not available, returning mock node")
        return lambda x: x
    
    return ValidationNode([schema_type])

def validate_with_schema(state: AgentState, schema_type: Type[BaseModel]) -> Dict[str, Any]:
    """
    Validate state data against a schema.
    
    Args:
        state: The current agent state
        schema_type: The Pydantic schema to validate against
        
    Returns:
        Updated state with validation results
    """
    try:
        # Create a mock AIMessage with tool calls for validation
        if schema_type == CodeGenerationOutput:
            tool_call = {
                "name": "CodeGenerationOutput",
                "args": {
                    "code": state.generated_code,
                    "language": state.processed_requirements.get("language", "python") if state.processed_requirements else "python",
                    "file_path": state.processed_requirements.get("file_path", "output.py") if state.processed_requirements else "output.py"
                },
                "id": "1"
            }
        elif schema_type == ValidationResult:
            tool_call = {
                "name": "ValidationResult",
                "args": state.validation_result,
                "id": "1"
            }
        else:
            logger.error(f"Unsupported schema type: {schema_type.__name__}")
            return {
                "errors": state.errors + [{"stage": "schema_validation", "message": f"Unsupported schema type: {schema_type.__name__}"}]
            }
        
        # Create the message
        ai_message = AIMessage(content="", tool_calls=[tool_call])
        
        # Create the validation node
        validation_node = create_validation_node(schema_type)
        
        # Validate
        result = validation_node.invoke({"messages": [ai_message]})
        
        # Check if validation succeeded
        messages = result.get("messages", [])
        for message in messages:
            if isinstance(message, ToolMessage) and message.additional_kwargs.get("is_error"):
                logger.error(f"Schema validation failed: {message.content}")
                return {
                    "errors": state.errors + [{"stage": "schema_validation", "message": message.content}]
                }
        
        logger.info(f"Schema validation succeeded for {schema_type.__name__}")
        return {}
    
    except Exception as e:
        logger.error(f"Error during schema validation: {e}")
        return {
            "errors": state.errors + [{"stage": "schema_validation", "message": str(e)}]
        }