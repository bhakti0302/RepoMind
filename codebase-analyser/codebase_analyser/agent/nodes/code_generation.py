"""
Code generation nodes for the agent.

This module contains functions for generating code based on requirements and context.
"""

import os
import json
import logging
from typing import Dict, Any, Optional

from codebase_analyser.agent.state import AgentState

# Configure logging
logger = logging.getLogger(__name__)

async def generate_llm_instructions(
    state: AgentState, 
    output_file: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate instructions file for LLMs based on requirements and context.
    
    Args:
        state: The current agent state
        output_file: Path to the output file
        
    Returns:
        Updated state with path to the instructions file
    """
    try:
        logger.info("Generating LLM instructions file")
        
        # Set default output file if not provided
        if output_file is None:
            # Create output directory if it doesn't exist
            output_dir = os.path.join(os.getcwd(), "output")
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, "llm-instructions.txt")
        
        # Create directory if it doesn't exist
        output_dir = os.path.dirname(os.path.abspath(output_file))
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Get requirements and context
        requirements = state.requirements
        context = state.combined_context
        
        # Get language from processed requirements
        language = state.processed_requirements.get("language", "java") if state.processed_requirements else "java"
        
        # Get generated code if available
        generated_code = state.generated_code if hasattr(state, "generated_code") and state.generated_code else ""
        
        # Format the instructions
        instructions = f"""# LLM INSTRUCTIONS

## REQUIREMENTS:
{requirements}

## CONTEXT:
{context}

## LANGUAGE: {language}

## TASK:
Implement the requirements above, using the provided context and generated code.
The code should be complete, well-documented, and follow best practices for {language}.

## GENERATED CODE:
```{language}
{generated_code}
```

## OUTPUT FORMAT:
Provide your implementation in the following format:

```{language}
// Your code here
```
"""
        
        # Write the instructions to the file
        with open(output_file, "w") as f:
            f.write(instructions)
        
        logger.info(f"Generated LLM instructions file at {output_file}")
        
        return {
            "instructions_file": output_file
        }
    except Exception as e:
        logger.error(f"Error generating LLM instructions: {e}")
        return {
            "errors": state.errors + [{"stage": "llm_instructions_generation", "message": str(e)}],
            "instructions_file": None
        }

async def generate_code_from_instructions(
    state: AgentState,
    instructions_file: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate code based on LLM instructions file.
    
    Args:
        state: The current agent state
        instructions_file: Path to the instructions file
        
    Returns:
        Updated state with generated code
    """
    try:
        logger.info("Generating code from instructions")
        
        # Use the instructions file from state if not provided
        if not instructions_file and "instructions_file" in state:
            instructions_file = state.instructions_file
        
        if not instructions_file or not os.path.exists(instructions_file):
            logger.error("Instructions file not found")
            return {
                "errors": state.errors + [{"stage": "code_generation", "message": "Instructions file not found"}],
                "generated_code": None
            }
        
        # Read the instructions file
        with open(instructions_file, "r") as f:
            instructions = f.read()
        
        # Here you would typically call an LLM to generate code based on the instructions
        # For now, we'll just return a mock implementation
        
        # Extract language from instructions
        language = "java"  # Default
        if "## LANGUAGE:" in instructions:
            language_line = [line for line in instructions.split("\n") if "## LANGUAGE:" in line][0]
            language = language_line.split("## LANGUAGE:")[1].strip()
        
        # Mock generated code
        if language.lower() == "java":
            generated_code = """
public class CodeGenerator {
    public static void main(String[] args) {
        System.out.println("Generated code based on instructions");
    }
}
"""
        elif language.lower() == "python":
            generated_code = """
def main():
    print("Generated code based on instructions")

if __name__ == "__main__":
    main()
"""
        else:
            generated_code = f"// Generated code for {language}"
        
        logger.info(f"Generated code with {len(generated_code)} characters")
        
        return {
            "generated_code": generated_code,
            "language": language
        }
    except Exception as e:
        logger.error(f"Error generating code from instructions: {e}")
        return {
            "errors": state.errors + [{"stage": "code_generation", "message": str(e)}],
            "generated_code": None
        }

async def generate_instructions_with_code(
    state: AgentState,
    output_file: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate instructions file with the generated code.
    
    Args:
        state: The current agent state
        output_file: Path to the output file
        
    Returns:
        Updated state with path to the instructions file
    """
    try:
        logger.info("Generating instructions file with code")
        
        # If no code is generated, generate it first
        if not hasattr(state, "generated_code") or not state.generated_code:
            logger.info("No code found in state, generating code first")
            from .llm_nodes import generate_code
            code_result = await generate_code(state)
            state = AgentState(**{**state.__dict__, **code_result})
        
        # Generate the instructions file
        return await generate_llm_instructions(state, output_file)
    except Exception as e:
        logger.error(f"Error generating instructions with code: {e}")
        return {
            "errors": state.errors + [{"stage": "instructions_with_code_generation", "message": str(e)}],
            "instructions_file": None
        }
