"""
Human-in-the-loop feedback functionality for the agent.
"""
import os
import logging
import asyncio
from typing import Dict, Any, Optional
import tempfile
import subprocess

logger = logging.getLogger(__name__)

async def get_human_feedback(code: str, prompt: str = None) -> Dict[str, Any]:
    """
    Get feedback from a human reviewer.
    
    Args:
        code: The code to review
        prompt: Optional prompt for the reviewer
        
    Returns:
        A dictionary with the feedback results
    """
    # Check if human feedback is enabled
    if os.environ.get("ENABLE_HUMAN_FEEDBACK", "0") != "1":
        logger.info("Human feedback is disabled, automatically approving")
        return {
            "approved": True,
            "feedback": "",
            "modified_code": code
        }
    
    # Check if we're in a CI environment
    if os.environ.get("CI", "0") == "1":
        logger.info("Running in CI environment, automatically approving")
        return {
            "approved": True,
            "feedback": "",
            "modified_code": code
        }
    
    # Create a temporary file with the code
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        code_file = f.name
        f.write(code)
    
    # Create a temporary file for the prompt
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        prompt_file = f.name
        f.write(prompt or "Please review the generated code and provide feedback.")
    
    try:
        # Determine the editor to use
        editor = os.environ.get("EDITOR", "code" if os.name == "nt" else "nano")
        
        # Print instructions
        print("\n" + "=" * 80)
        print("HUMAN FEEDBACK REQUIRED")
        print("=" * 80)
        print(f"The prompt is:\n\n{prompt or 'Please review the generated code and provide feedback.'}\n")
        print("The code has been saved to a temporary file.")
        print(f"Opening the file in {editor}...")
        print("Please review the code, make any necessary changes, and save the file.")
        print("=" * 80)
        
        # Open the editor
        try:
            subprocess.run([editor, code_file], check=True)
        except subprocess.CalledProcessError:
            logger.warning(f"Failed to open {editor}, trying fallback editor")
            # Try a fallback editor
            fallback_editor = "notepad" if os.name == "nt" else "vi"
            subprocess.run([fallback_editor, code_file], check=True)
        
        # Read the modified code
        with open(code_file, "r") as f:
            modified_code = f.read()
        
        # Ask for approval
        while True:
            response = input("Do you approve this code? (yes/no/edit): ").lower()
            if response in ["yes", "y"]:
                approved = True
                feedback = input("Optional feedback: ")
                break
            elif response in ["no", "n"]:
                approved = False
                feedback = input("Please provide feedback: ")
                break
            elif response in ["edit", "e"]:
                # Reopen the editor
                try:
                    subprocess.run([editor, code_file], check=True)
                except subprocess.CalledProcessError:
                    subprocess.run([fallback_editor, code_file], check=True)
                
                # Read the modified code again
                with open(code_file, "r") as f:
                    modified_code = f.read()
            else:
                print("Invalid response. Please enter 'yes', 'no', or 'edit'.")
        
        return {
            "approved": approved,
            "feedback": feedback,
            "modified_code": modified_code
        }
    finally:
        # Clean up temporary files
        try:
            os.unlink(code_file)
            os.unlink(prompt_file)
        except Exception as e:
            logger.warning(f"Failed to clean up temporary files: {e}")

async def apply_human_feedback(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply human feedback to the generated code.
    
    Args:
        state: The current state
        
    Returns:
        The updated state with human feedback applied
    """
    try:
        # Get the generated code
        generated_code = state.get("generated_code", "")
        if not generated_code:
            logger.warning("No generated code to review")
            return state
        
        # Create a prompt for the reviewer
        requirements = state.get("requirements", {})
        prompt = f"Please review the generated code for the following requirements:\n\n"
        prompt += f"Description: {requirements.get('description', 'No description provided')}\n"
        if "language" in requirements:
            prompt += f"Language: {requirements.get('language')}\n"
        if "file_path" in requirements:
            prompt += f"Target File: {requirements.get('file_path')}\n"
        if "additional_context" in requirements:
            prompt += f"Additional Context: {requirements.get('additional_context')}\n"
        
        # Get human feedback
        feedback_result = await get_human_feedback(generated_code, prompt)
        
        # Update the state
        updated_state = {
            **state,
            "generated_code": feedback_result.get("modified_code", generated_code),
            "human_feedback": feedback_result
        }
        
        # Add to metadata
        if "metadata" not in updated_state:
            updated_state["metadata"] = {}
        updated_state["metadata"]["human_feedback"] = feedback_result
        
        return updated_state
    except Exception as e:
        logger.error(f"Error applying human feedback: {str(e)}")
        return state