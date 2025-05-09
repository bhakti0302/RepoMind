"""
Output nodes for the agent graph.
"""
import logging
import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from ..state import AgentState

# Configure logging
logger = logging.getLogger(__name__)

async def prepare_output_for_downstream(state: AgentState) -> Dict[str, Any]:
    """
    Prepare output for downstream agents.
    
    Args:
        state: The current agent state
        
    Returns:
        Updated state with output for downstream agents
    """
    logger.info("Preparing output for downstream agents")
    
    try:
        # Get language and file path from processed requirements
        language = state.processed_requirements.get("language", "java") if state.processed_requirements else "java"
        file_path = state.processed_requirements.get("file_path", "output.txt") if state.processed_requirements else "output.txt"
        
        # Create downstream data
        downstream_data = {
            "code": state.generated_code,
            "language": language,
            "file_path": file_path,
            "validation": state.validation_result,
            "metadata": {
                "requirements": state.requirements,
                "errors": state.errors,
                "timestamp": state.timestamp.isoformat() if state.timestamp else None
            }
        }
        
        # Add MCP-compatible format for file operations
        mcp_data = create_mcp_data(state)
        if mcp_data:
            downstream_data["mcp"] = mcp_data
        
        # Add VS Code extension compatible format
        vscode_data = create_vscode_data(state)
        if vscode_data:
            downstream_data["vscode"] = vscode_data
        
        logger.info(f"Prepared downstream data with {len(downstream_data)} keys")
        
        return {
            "downstream_data": downstream_data
        }
    except Exception as e:
        logger.error(f"Error preparing output for downstream agents: {e}")
        return {
            "downstream_data": {
                "error": str(e),
                "code": state.generated_code
            }
        }

def create_mcp_data(state: AgentState) -> Dict[str, Any]:
    """
    Create Model Context Protocol (MCP) compatible data.
    
    Args:
        state: The current agent state
        
    Returns:
        MCP compatible data
    """
    try:
        # Get file path from processed requirements
        file_path = state.processed_requirements.get("file_path", "output.txt") if state.processed_requirements else "output.txt"
        
        # Create MCP data
        mcp_data = {
            "operations": [
                {
                    "type": "file_write",
                    "path": file_path,
                    "content": state.generated_code
                }
            ],
            "metadata": {
                "source": "codebase_analyser",
                "timestamp": datetime.now().isoformat(),
                "validation": state.validation_result.get("status", "unknown") if state.validation_result else "unknown"
            }
        }
        
        return mcp_data
    except Exception as e:
        logger.error(f"Error creating MCP data: {e}")
        return {}

def create_vscode_data(state: AgentState) -> Dict[str, Any]:
    """
    Create VS Code extension compatible data.
    
    Args:
        state: The current agent state
        
    Returns:
        VS Code compatible data
    """
    try:
        # Get file path and language from processed requirements
        file_path = state.processed_requirements.get("file_path", "output.txt") if state.processed_requirements else "output.txt"
        language = state.processed_requirements.get("language", "java") if state.processed_requirements else "java"
        
        # Create VS Code data
        vscode_data = {
            "file": {
                "path": file_path,
                "content": state.generated_code,
                "language": language
            },
            "diagnostics": []
        }
        
        # Add diagnostics if validation failed
        if state.validation_result and not state.validation_result.get("valid", True):
            for issue in state.validation_result.get("issues", []):
                diagnostic = {
                    "severity": "error" if issue.get("severity") == "error" else "warning",
                    "message": issue.get("message", "Unknown issue"),
                    "line": issue.get("line", 1),
                    "column": issue.get("column", 1)
                }
                vscode_data["diagnostics"].append(diagnostic)
        
        return vscode_data
    except Exception as e:
        logger.error(f"Error creating VS Code data: {e}")
        return {}

def save_output_to_file(state: AgentState) -> Dict[str, Any]:
    """
    Save the generated code to a file.
    
    Args:
        state: The current agent state
        
    Returns:
        Updated state
    """
    try:
        # If no code is generated, return
        if not state.generated_code:
            logger.error("No code to save")
            return {}
        
        # Get file path from processed requirements
        file_path = state.processed_requirements.get("file_path", "output.txt") if state.processed_requirements else "output.txt"
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        # Save the code to the file
        with open(file_path, "w") as f:
            f.write(state.generated_code)
        
        logger.info(f"Saved generated code to {file_path}")
        
        return {
            "file_path": file_path
        }
    except Exception as e:
        logger.error(f"Error saving output to file: {e}")
        return {
            "errors": state.errors + [{"stage": "save_output", "message": str(e)}]
        }

def create_file_operation_commands(state: AgentState) -> List[Dict[str, Any]]:
    """
    Create file operation commands for downstream agents.
    
    Args:
        state: The current agent state
        
    Returns:
        List of file operation commands
    """
    try:
        # Get file path from processed requirements
        file_path = state.processed_requirements.get("file_path", "output.txt") if state.processed_requirements else "output.txt"
        
        # Create file operation commands
        commands = [
            {
                "command": "write_file",
                "args": {
                    "path": file_path,
                    "content": state.generated_code
                }
            }
        ]
        
        # Add additional commands based on validation
        if state.validation_result and state.validation_result.get("valid", True):
            # If validation passed, add command to execute the file if it's a script
            if file_path.endswith(".py") or file_path.endswith(".sh"):
                commands.append({
                    "command": "execute_file",
                    "args": {
                        "path": file_path
                    }
                })
        
        return commands
    except Exception as e:
        logger.error(f"Error creating file operation commands: {e}")
        return []
