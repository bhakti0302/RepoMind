"""
Test script for the RAG (Retrieval-Augmented Generation) nodes using real data.
"""
import asyncio
import logging
import sys
import json
import argparse
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the necessary components
from codebase_analyser.agent.state import AgentState
from codebase_analyser.agent.nodes.nlp_nodes import process_requirements, REQUIREMENTS_PROCESSING_PROMPT
from codebase_analyser.agent.nodes.rag_nodes import retrieve_architectural_context, retrieve_implementation_context, combine_context
from codebase_analyser.database import open_unified_storage, close_unified_storage

# Fix for the prompt template issue
from langchain.prompts import PromptTemplate

# Patch the prompt template if needed
def fix_prompt_template():
    """Fix the prompt template for requirements processing."""
    try:
        # Check if the prompt template has the problematic variable
        if '\n  "intent"' in REQUIREMENTS_PROCESSING_PROMPT:
            # Fix the prompt by replacing the problematic variable
            fixed_prompt = REQUIREMENTS_PROCESSING_PROMPT.replace('{\\n  "intent"', '{"intent"')
            fixed_prompt = fixed_prompt.replace('\n  "intent"', '"intent"')
            
            # Create a new prompt template with the fixed template
            new_template = PromptTemplate(template=fixed_prompt, input_variables=["requirements"])
            
            # Monkey patch the module
            import codebase_analyser.agent.nodes.nlp_nodes
            codebase_analyser.agent.nodes.nlp_nodes.REQUIREMENTS_PROCESSING_PROMPT = fixed_prompt
            
            logger.info("Fixed prompt template for requirements processing")
            return True
    except Exception as e:
        logger.error(f"Error fixing prompt template: {e}")
    return False

async def main():
    """Main function."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Test RAG nodes with real data')
    parser.add_argument('--requirements', type=str, required=True,
                        help='Requirements text')
    parser.add_argument('--db-path', type=str, required=True,
                        help='Path to the LanceDB database')
    parser.add_argument('--language', type=str, default='java',
                        help='Programming language')
    parser.add_argument('--output', type=str, default='print_instructions.txt',
                        help='Path to save the generated instructions')
    parser.add_argument('--limit', type=int, default=5,
                        help='Maximum number of results to retrieve')
    
    args = parser.parse_args()
    
    # Check if the database exists
    if not os.path.exists(args.db_path):
        logger.error(f"Database not found at {args.db_path}")
        logger.error("Please index your codebase first using the codebase_analyser tool")
        return
    
    # Try to fix the prompt template
    fix_prompt_template()
    
    # Create initial state
    state = AgentState(requirements=args.requirements)
    
    # Process requirements
    logger.info("Processing requirements...")
    try:
        # Try to process requirements with LLM
        processed_result = await process_requirements(state)
        
        # Update state with processed requirements
        state = AgentState(
            requirements=state.requirements,
            processed_requirements=processed_result.get("processed_requirements", {}),
            errors=processed_result.get("errors", [])
        )
    except Exception as e:
        logger.error(f"Error processing requirements with LLM: {e}")
        logger.info("Falling back to simple processing...")
        
        # Import the simple processing function
        from codebase_analyser.agent.nodes.nlp_nodes import simple_process_requirements
        
        # Process requirements using simple processing
        processed_requirements = simple_process_requirements(state.requirements, args.language)
        
        # Update state with processed requirements
        state = AgentState(
            requirements=state.requirements,
            processed_requirements=processed_requirements,
            errors=state.errors + [{"stage": "requirements_processing", "message": str(e)}]
        )
    
    # Print processed requirements
    if state.processed_requirements:
        print("\n=== Processed Requirements ===\n")
        print(json.dumps(state.processed_requirements, indent=2))
    
    # Open the database connection
    logger.info(f"Opening database connection to {args.db_path}...")
    db_connection = open_unified_storage(
        db_path=args.db_path,
        use_minimal_schema=True,
        create_if_not_exists=False,
        read_only=True
    )
    
    try:
        # Retrieve architectural context
        logger.info("Retrieving architectural context...")
        arch_result = await retrieve_architectural_context(state)
        
        # Update state with architectural context
        state = AgentState(
            requirements=state.requirements,
            processed_requirements=state.processed_requirements,
            architectural_context=arch_result.get("architectural_context", []),
            errors=state.errors + arch_result.get("errors", [])
        )
        
        # Print architectural context
        if state.architectural_context:
            print(f"\n=== Architectural Context ({len(state.architectural_context)} items) ===\n")
            for i, ctx in enumerate(state.architectural_context):
                print(f"Item {i+1}: {ctx.get('name')} ({ctx.get('chunk_type')}) - Similarity: {ctx.get('similarity'):.2f}")
        
        # Retrieve implementation context
        logger.info("Retrieving implementation context...")
        impl_result = await retrieve_implementation_context(state)
        
        # Update state with implementation context
        state = AgentState(
            requirements=state.requirements,
            processed_requirements=state.processed_requirements,
            architectural_context=state.architectural_context,
            implementation_context=impl_result.get("implementation_context", []),
            errors=state.errors + impl_result.get("errors", [])
        )
        
        # Print implementation context
        if state.implementation_context:
            print(f"\n=== Implementation Context ({len(state.implementation_context)} items) ===\n")
            for i, ctx in enumerate(state.implementation_context):
                print(f"Item {i+1}: {ctx.get('name')} ({ctx.get('chunk_type')}) - Similarity: {ctx.get('similarity'):.2f}")
        
        # Combine context
        logger.info("Combining context...")
        combined_result = await combine_context(state)
        
        # Update state with combined context
        state = AgentState(
            requirements=state.requirements,
            processed_requirements=state.processed_requirements,
            architectural_context=state.architectural_context,
            implementation_context=state.implementation_context,
            combined_context=combined_result.get("combined_context", ""),
            errors=state.errors + combined_result.get("errors", [])
        )
        
        # Create the instructions file
        instructions = f"""# LLM INSTRUCTIONS

## REQUIREMENTS:
{state.requirements}

## CONTEXT:
{state.combined_context}

## PROCESSED REQUIREMENTS
Intent: {state.processed_requirements.get('intent', 'unknown')}
Language: {args.language}
Entities:
{json.dumps(state.processed_requirements.get('entities', {}), indent=2)}

## LANGUAGE: {args.language}

## TASK:
Implement the requirements above, using the provided context and generated code.
The code should be complete, well-documented, and follow best practices for {args.language}.

## GENERATED CODE:
```{args.language}

```

## OUTPUT FORMAT:
Provide your implementation in the following format:

```{args.language}
// Your code here
```
"""
        
        # Save the instructions to a file
        with open(args.output, 'w') as f:
            f.write(instructions)
        
        logger.info(f"Instructions saved to {args.output}")
        
    finally:
        # Close the database connection
        logger.info("Closing database connection...")
        close_unified_storage(db_connection)

if __name__ == "__main__":
    asyncio.run(main())