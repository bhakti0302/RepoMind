    """
Orchestrator for the Merge Code Agent.

This module orchestrates the workflow between the LLM and Filesystem nodes,
managing state and coordinating the sequence of operations.
    """

from typing import Dict, List, Any, TypedDict, Literal
import os

from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from llm_node import LLMNode
from filesystem_node import FilesystemNode
from utils import format_actions_summary, get_action_preview


class MergeCodeAgentState(TypedDict):
    """State schema for the Merge Code Agent."""
    instructions_path: str
    codebase_path: str
    instruction_blocks: List[str]
    current_block_index: int
    actions: List[Dict[str, Any]]
    approved_actions: List[Dict[str, Any]]
    results: List[Dict[str, Any]]
    errors: List[str]
    status: str


class Orchestrator:
    """
    Orchestrator for managing the workflow between the LLM and Filesystem nodes.
    """

    def __init__(self, instructions_path: str, codebase_path: str):
        """
        Initialize the Orchestrator.

        Args:
            instructions_path: Path to the instructions file
            codebase_path: Path to the codebase directory
        """
        self.instructions_path = instructions_path
        self.codebase_path = codebase_path

        # Initialize nodes
        self.llm_node = LLMNode()
        self.filesystem_node = FilesystemNode(codebase_path)

        # Read the instructions file
        with open(instructions_path, 'r') as f:
            instructions_content = f.read()

        # Split instructions into blocks
        instruction_blocks = self.llm_node._split_instructions(instructions_content)

        # Initialize state
        self.state: MergeCodeAgentState = {
            "instructions_path": instructions_path,
            "codebase_path": codebase_path,
            "instruction_blocks": instruction_blocks,
            "current_block_index": 0,
            "actions": [],
            "approved_actions": [],
            "results": [],
            "errors": [],
            "status": "initialized"
        }

        # Initialize the graph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow.

        Returns:
            The StateGraph instance
        """
        # Define the graph
        graph = StateGraph(MergeCodeAgentState)

        # Add nodes
        graph.add_node("read_instruction_block", self._read_instruction_block)
        graph.add_node("parse_instruction_block", self._parse_instruction_block)
        graph.add_node("get_user_approval", self._get_user_approval)
        graph.add_node("execute_actions", self._execute_actions)
        graph.add_node("check_more_instructions", self._check_more_instructions)

        # Define conditional edges
        graph.add_conditional_edges(
            "check_more_instructions",
            self._has_more_instructions,
            {
                "yes": "read_instruction_block",
                "no": END
            }
        )

        # Define regular edges
        graph.add_edge("read_instruction_block", "parse_instruction_block")
        graph.add_edge("parse_instruction_block", "get_user_approval")
        graph.add_edge("get_user_approval", "execute_actions")
        graph.add_edge("execute_actions", "check_more_instructions")

        # Set the entry point
        graph.set_entry_point("read_instruction_block")

        return graph

    def _has_more_instructions(self, state: MergeCodeAgentState) -> Literal["yes", "no"]:
        """
        Check if there are more instruction blocks to process.

        Args:
            state: The current state

        Returns:
            "yes" if there are more blocks, "no" otherwise
        """
        return "yes" if state["current_block_index"] < len(state["instruction_blocks"]) else "no"

    def _read_instruction_block(self, state: MergeCodeAgentState) -> MergeCodeAgentState:
        """
        Read the current instruction block.

        Args:
            state: The current state

        Returns:
            The updated state
        """
        current_index = state["current_block_index"]
        if current_index < len(state["instruction_blocks"]):
            print(f"\nProcessing instruction block {current_index + 1}/{len(state['instruction_blocks'])}")
            print(f"Instruction: {state['instruction_blocks'][current_index]}")
        else:
            print("No more instruction blocks to process")

        return state

    def _parse_instruction_block(self, state: MergeCodeAgentState) -> MergeCodeAgentState:
        """
        Parse the current instruction block and generate structured actions.

        Args:
            state: The current state

        Returns:
            The updated state
        """
        print("Parsing instruction block...")

        try:
            current_index = state["current_block_index"]
            if current_index < len(state["instruction_blocks"]):
                instruction_block = state["instruction_blocks"][current_index]

                # Always use the real LLM API
                print("Using real LLM API")
                block_actions = self.llm_node._llm_parse_instruction_block(instruction_block)

                # Add the new actions to the existing ones
                actions = state["actions"] + block_actions

                return {
                    **state,
                    "actions": actions,
                    "status": "instructions_parsed"
                }
            else:
                return {
                    **state,
                    "status": "no_more_instructions"
                }
        except Exception as e:
            return {
                **state,
                "errors": state["errors"] + [str(e)],
                "status": "error"
            }

    def _get_user_approval(self, state: MergeCodeAgentState) -> MergeCodeAgentState:
        """
        Get user approval for the actions.

        Args:
            state: The current state

        Returns:
            The updated state
        """
        actions = state["actions"]

        if not actions:
            print("No actions to perform.")
            return {
                **state,
                "status": "no_actions"
            }

        # Display the actions to the user
        print("\n" + "=" * 80)
        print("PLANNED ACTIONS")
        print("=" * 80)
        print(format_actions_summary(actions))
        print("=" * 80 + "\n")

        # Get user approval
        approved_actions = []
        for i, action in enumerate(actions, 1):
            print(f"\nAction {i}:")
            print(get_action_preview(action))

            while True:
                choice = input(f"\nApprove this action? (y/n): ").lower()
                if choice in ["y", "n"]:
                    break
                print("Please enter 'y' or 'n'.")

            if choice == "y":
                approved_actions.append(action)
                print("Action approved.")
            else:
                print("Action rejected.")

        print(f"\nApproved {len(approved_actions)} out of {len(actions)} actions.")

        return {
            **state,
            "approved_actions": approved_actions,
            "status": "actions_approved"
        }

    def _execute_actions(self, state: MergeCodeAgentState) -> MergeCodeAgentState:
    """
    Execute the approved actions.

    Args:
        state: The current state

    Returns:
        The updated state
    """
    approved_actions = state["approved_actions"]

    if not approved_actions:
        print("No actions to execute.")
        return {
            **state,
            "status": "completed",
            "current_block_index": state["current_block_index"] + 1
        }

    print("
Executing approved actions...")

    # Execute the actions
    results = []
    for i, action in enumerate(approved_actions, 1):
        print(f"Executing action {i}/{len(approved_actions)}: {action['action']} - {action['file_path']}")
        
        # For modify_file actions, use the flexible approach
        if action['action'] == 'modify_file':
            # Check if the file exists
            file_path = action['file_path']
            full_path = os.path.join(self.codebase_path, file_path)
            
            if os.path.exists(full_path):
                # Read the current file content
                with open(full_path, 'r') as f:
                    file_content = f.read()
                
                # Use the LLM to understand how to modify the file
                try:
                    # Get the instruction from the current block
                    instruction = state['instruction_blocks'][state['current_block_index']]
                    
                    # Use the LLM to understand the modification
                    modification = self.llm_node._llm_understand_file_modification(
                        instruction, file_path, file_content
                    )
                    
                    # Apply the modification
                    success, error = self.filesystem_node._apply_modification(file_path, modification)
                    
                    result = {
                        "action": action,
                        "success": success,
                        "error": error
                    }
                    results.append(result)
                    
                    if success:
                        print(f"  Success!")
                    else:
                        print(f"  Failed: {error}")
                        
                except Exception as e:
                    print(f"  Failed: {str(e)}")
                    results.append({
                        "action": action,
                        "success": False,
                        "error": str(e)
                    })
            else:
                print(f"  Failed: File does not exist: {file_path}")
                results.append({
                    "action": action,
                    "success": False,
                    "error": f"File does not exist: {file_path}"
                })
        else:
            # For other actions, use the standard approach
            success, error = self.filesystem_node.execute_action(action)
            
            result = {
                "action": action,
                "success": success,
                "error": error
            }
            results.append(result)
            
            if success:
                print(f"  Success!")
            else:
                print(f"  Failed: {error}")

    # Count successes and failures
    successes = sum(1 for r in results if r["success"])
    failures = len(results) - successes

    print(f"
Execution completed: {successes} succeeded, {failures} failed.")

    # Move to the next instruction block
    return {
        **state,
        "results": state["results"] + results,
        "approved_actions": [],  # Clear approved actions for next block
        "current_block_index": state["current_block_index"] + 1,
        "status": "completed"
    }


    def _check_more_instructions(self, state: MergeCodeAgentState) -> MergeCodeAgentState:
        """
        Check if there are more instruction blocks to process.

        Args:
            state: The current state

        Returns:
            The updated state
        """
        current_index = state["current_block_index"]
        total_blocks = len(state["instruction_blocks"])

        if current_index < total_blocks:
            print(f"\nMoving to next instruction block ({current_index + 1}/{total_blocks})")
        else:
            print("\nAll instruction blocks processed")

        return state

    def run(self) -> MergeCodeAgentState:
        """
        Run the orchestrator.

        Returns:
            The final state
        """
        try:
            print("Using LangGraph for workflow orchestration")

            # Process each instruction block manually using the graph nodes
            state = self.state

            # Process all instruction blocks
            while state["current_block_index"] < len(state["instruction_blocks"]):
                # Read the current block
                state = self._read_instruction_block(state)

                # Parse the block
                state = self._parse_instruction_block(state)

                # Get user approval
                if state["status"] != "error":
                    state = self._get_user_approval(state)

                # Execute actions
                if state["status"] != "error" and state["approved_actions"]:
                    state = self._execute_actions(state)
                else:
                    # Move to next block even if no actions were approved
                    state = {
                        **state,
                        "current_block_index": state["current_block_index"] + 1
                    }

                # Check for errors
                if state["status"] == "error":
                    print("\nErrors occurred:")
                    for error in state["errors"]:
                        print(f"  - {error}")
                    break

                # Check if we should continue
                if state["current_block_index"] < len(state["instruction_blocks"]):
                    state = self._check_more_instructions(state)

            return state

        except Exception as e:
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                **self.state,
                "errors": self.state["errors"] + [str(e)],
                "status": "error"
            }