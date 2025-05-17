"""
LangGraph workflow for the Merge Code Agent.

This module defines the LangGraph workflow for parsing instructions and generating actions.
"""

from typing import Dict, List, Any, TypedDict
from langgraph.graph import StateGraph, END
import json
import re

class InstructionState(TypedDict):
    """State for the instruction parsing workflow."""
    instruction_text: str  # The full instruction text
    instruction_blocks: List[str]  # The blocks identified by the LLM
    current_block_index: int  # Index of the current block being processed
    actions: List[Dict[str, Any]]  # Actions to be executed
    context: Dict[str, Any]  # Context maintained between blocks

def create_instruction_workflow(llm_node):
    """
    Create a LangGraph workflow for parsing instructions.

    Args:
        llm_node: The LLM node to use for parsing instructions

    Returns:
        A compiled LangGraph workflow
    """
    # Create the graph
    workflow = StateGraph(InstructionState)

    # Node 1: Analyze the entire instruction file and divide into blocks
    def analyze_instructions(state: InstructionState) -> InstructionState:
        """Analyze the entire instruction file and divide it into logical blocks."""
        instruction_text = state["instruction_text"]

        # Prompt for the LLM to analyze the instructions
        prompt = f"""
        You are an expert code modification assistant. Your task is to analyze a set of instructions for modifying code and divide them into logical blocks.

        Here are the instructions:

        ```
        {instruction_text}
        ```

        Please analyze these instructions and divide them into logical blocks. Each block should represent a single task or modification.

        For example, if the instructions say to create a file and then modify another file, those would be two separate blocks.
        If the instructions contain code snippets that should be added to a file, keep the code snippets with the instructions.

        CRITICAL INSTRUCTIONS - YOU MUST FOLLOW THESE EXACTLY:
        1. ONLY ADD THE EXACT CODE MENTIONED IN THE INSTRUCTION. DO NOT ADD ANY OTHER CODE.
        2. DO NOT CREATE ANY NEW METHODS, FIELDS, OR FUNCTIONALITY THAT IS NOT EXPLICITLY MENTIONED IN THE INSTRUCTION.
        3. DO NOT BE CREATIVE OR HELPFUL BY ADDING EXTRA FUNCTIONALITY. ONLY ADD WHAT IS EXPLICITLY REQUESTED.
        4. IF THE INSTRUCTION SAYS TO ADD SPECIFIC FIELDS OR METHODS, ADD ONLY THOSE SPECIFIC FIELDS OR METHODS.
        5. DO NOT INFER OR ASSUME ADDITIONAL FUNCTIONALITY THAT MIGHT BE USEFUL.

        IMPORTANT GUIDELINES:
        1. Keep related instructions together in the same block
        2. If an instruction mentions adding specific code to a file, include that code in the same block
        3. If multiple steps are part of the same logical task, keep them in the same block
        4. Make sure each block is complete and can be understood on its own
        5. Do not split code blocks across different instruction blocks

        Return a JSON array of instruction blocks. Each block should be a string containing the complete instructions for that block.

        Example response:
        [
          "Create a new file called config.json with the following content: {...}",
          "Update the README.md file to include installation instructions"
        ]

        Only include the JSON array in your response, nothing else.
        """

        # Call the LLM API
        print("Analyzing instructions and dividing into logical blocks...")
        response = llm_node._call_llm_api(prompt)

        # Parse the response to get the blocks
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'(\[.*\])', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response

            blocks = json.loads(json_str)
        except json.JSONDecodeError:
            # If we still can't extract JSON, treat the entire response as a single block
            blocks = [instruction_text]

        print(f"Divided instructions into {len(blocks)} logical blocks")

        # Update the state
        return {
            **state,
            "instruction_blocks": blocks,
            "current_block_index": 0,
            "actions": [],
            "context": {}
        }

    # Node 2: Process the current block
    def process_block(state: InstructionState) -> InstructionState:
        """Process the current instruction block."""
        blocks = state["instruction_blocks"]
        current_index = state["current_block_index"]
        context = state["context"]

        if current_index >= len(blocks):
            # No more blocks to process
            return state

        current_block = blocks[current_index]

        print(f"\nProcessing instruction block {current_index + 1}/{len(blocks)}")
        print("=" * 80)
        print(current_block)
        print("=" * 80)

        # Create a prompt that includes context from previous blocks
        prompt = f"""
        You are an expert code modification assistant. Your task is to interpret instructions for modifying code and convert them into structured actions.

        Here is the instruction block:

        ```
        {current_block}
        ```

        Context from previous blocks:
        {json.dumps(context, indent=2)}

        CRITICAL INSTRUCTIONS - YOU MUST FOLLOW THESE EXACTLY:
        1. ONLY ADD THE EXACT CODE MENTIONED IN THE INSTRUCTION. DO NOT ADD ANY OTHER CODE.
        2. DO NOT CREATE ANY NEW METHODS, FIELDS, OR FUNCTIONALITY THAT IS NOT EXPLICITLY MENTIONED IN THE INSTRUCTION.
        3. DO NOT BE CREATIVE OR HELPFUL BY ADDING EXTRA FUNCTIONALITY. ONLY ADD WHAT IS EXPLICITLY REQUESTED.
        4. IF THE INSTRUCTION SAYS TO ADD SPECIFIC FIELDS OR METHODS, ADD ONLY THOSE SPECIFIC FIELDS OR METHODS.
        5. DO NOT INFER OR ASSUME ADDITIONAL FUNCTIONALITY THAT MIGHT BE USEFUL.

        Based on this instruction and the context, determine what file operation is being requested.
        The instruction might contain code snippets that need to be added to a file.

        For file operations, determine the appropriate action type:
        - create_file: When a new file needs to be created
        - modify_file: When an existing file needs to be changed
        - delete_file: When a file needs to be removed

        Return a JSON object with these fields:
        - action: Required. The type of action (create_file, modify_file, delete_file)
        - file_path: Required. The path to the file
        - content: The content to write (for create_file)
        - instruction: For modify_file actions, include the original instruction for file analysis

        Only include the JSON object in your response, nothing else.
        """

        # Call the LLM API
        response = llm_node._call_llm_api(prompt)

        # Parse the response to get the action
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'({.*})', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response

            action = json.loads(json_str)
        except json.JSONDecodeError:
            # If we still can't extract JSON, create a generic action
            action = {
                "action": "modify_file",
                "instruction": current_block
            }

        # Update the context based on the action
        new_context = {**context}
        if "file_path" in action:
            new_context["last_file_path"] = action["file_path"]

        # Update the state
        return {
            **state,
            "current_block_index": current_index + 1,
            "actions": state["actions"] + [action],
            "context": new_context
        }

    # Node 3: Check if there are more blocks to process
    def check_more_blocks(state: InstructionState) -> str:
        """Check if there are more blocks to process."""
        if state["current_block_index"] < len(state["instruction_blocks"]):
            return "continue"
        else:
            return "done"

    # Add the nodes to the graph
    workflow.add_node("analyze_instructions", analyze_instructions)
    workflow.add_node("process_block", process_block)

    # Add the edges
    workflow.add_edge("analyze_instructions", "process_block")
    workflow.add_conditional_edges(
        "process_block",
        check_more_blocks,
        {
            "continue": "process_block",
            "done": END
        }
    )

    # Set the entry point
    workflow.set_entry_point("analyze_instructions")

    # Compile the graph
    return workflow.compile()
