#!/usr/bin/env python3

"""
Code Chat Script.

This script takes a question about code and sends it to the LLM with context about the project.
"""

import os
import sys
import logging
import json
import argparse
from typing import Dict, List, Any, Optional, Union, Tuple

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import the components
try:
    from src.llm_client import NVIDIALlamaClient
    from src.env_loader import load_env_vars
    from src.multi_hop_rag import MultiHopRAG
except ImportError as e:
    logger.error(f"Error importing modules: {e}")
    sys.exit(1)

def process_code_question(
    question: str,
    db_path: str,
    output_dir: str,
    conversation_history: List[Dict[str, str]] = None,
    llm_api_key: str = None,
    llm_model_name: str = "nvidia/llama-3.3-nemotron-super-49b-v1:free",
    temperature: float = 0.7,
    max_tokens: int = 2000
) -> str:
    """Process a question about code and generate a response.

    Args:
        question: The question about code
        db_path: Path to the LanceDB database
        output_dir: Path to the output directory
        conversation_history: Previous conversation history
        llm_api_key: API key for the LLM service
        llm_model_name: Name of the LLM model to use
        temperature: Temperature for LLM generation
        max_tokens: Maximum tokens for LLM generation

    Returns:
        The generated response
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Step 1: Run RAG to get context about the code
        logger.info("Step 1: Running RAG to get context")
        rag = MultiHopRAG(db_path=db_path, output_dir=output_dir)
        rag_result = rag.multi_hop_rag(query=question)
        logger.info(f"Completed RAG")

        # Get the RAG output
        chat_context_file = os.path.join(output_dir, "chat-context.txt")

        # Check if rag_result is a dictionary or a string
        if isinstance(rag_result, dict):
            # If it's a dictionary, extract the context
            context = rag_result.get("context", "")
            with open(chat_context_file, 'w') as f:
                f.write(context)
            logger.info(f"Saved RAG context to {chat_context_file}")
        else:
            # If it's a string, write it directly
            with open(chat_context_file, 'w') as f:
                f.write(str(rag_result))
            logger.info(f"Saved RAG context to {chat_context_file}")

        # Step 2: Send to LLM
        logger.info("Step 2: Sending to LLM")

        # Get API key from environment if not provided
        llm_api_key = llm_api_key or os.environ.get("LLM_API_KEY")

        if not llm_api_key:
            logger.error("No LLM API key provided")
            sys.exit(1)

        # Get API base URL from environment
        api_base_url = os.environ.get("OPENAI_API_BASE_URL")
        if not api_base_url:
            logger.error("No API base URL found in environment variables")
            sys.exit(1)

        # Initialize LLM client
        llm_client = NVIDIALlamaClient(
            api_key=llm_api_key,
            model_name=llm_model_name,
            api_url=api_base_url,
            output_dir=output_dir
        )

        # Initialize conversation history if not provided
        if conversation_history is None:
            conversation_history = []

        # Create the system prompt
        system_prompt = (
            "You are an AI assistant that helps with code-related questions. "
            "You have access to information about the user's codebase. "
            "Provide helpful, accurate, and concise responses. "
            "When referring to code, use proper formatting and syntax highlighting. "
            "If you're not sure about something, be honest about your limitations."
        )

        # Create the prompt for LLM
        prompt = f"# Question\n\n{question}\n\n"

        # Check if rag_result is a dictionary or a string
        if isinstance(rag_result, dict):
            # If it's a dictionary, extract the context and other relevant information
            context = rag_result.get("context", "")
            architectural_patterns = rag_result.get("architectural_patterns", [])
            implementation_details = rag_result.get("implementation_details", [])
            related_components = rag_result.get("related_components", [])
            domain_entities = rag_result.get("domain_entities", [])

            # Add the context to the prompt
            prompt += f"# Code Context\n\n{context}\n\n"

            # Add architectural patterns if available
            if architectural_patterns:
                prompt += f"# Architectural Patterns\n\n"
                for pattern in architectural_patterns:
                    prompt += f"- {pattern}\n"
                prompt += "\n"

            # Add implementation details if available
            if implementation_details:
                prompt += f"# Implementation Details\n\n"
                for detail in implementation_details:
                    prompt += f"- {detail}\n"
                prompt += "\n"

            # Add related components if available
            if related_components:
                prompt += f"# Related Components\n\n"
                for component in related_components:
                    prompt += f"- {component}\n"
                prompt += "\n"

            # Add domain entities if available
            if domain_entities:
                prompt += f"# Domain Entities\n\n"
                for entity in domain_entities:
                    prompt += f"- {entity}\n"
                prompt += "\n"
        else:
            # If it's a string, add it directly
            prompt += f"# Code Context\n\n{rag_result}\n\n"

        # Add conversation history if available
        if conversation_history:
            prompt += "# Conversation History\n\n"
            for entry in conversation_history:
                prompt += f"User: {entry.get('user', '')}\n"
                prompt += f"Assistant: {entry.get('assistant', '')}\n\n"

        # Generate response using LLM
        llm_output = llm_client.generate(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt
        )

        # Save the LLM output to chat-response.txt
        chat_response_file = os.path.join(output_dir, "chat-response.txt")
        with open(chat_response_file, 'w') as f:
            f.write(llm_output)

        logger.info(f"Saved chat response to {chat_response_file}")

        # Clean up
        rag.close()

        # Update conversation history
        conversation_history.append({
            "user": question,
            "assistant": llm_output
        })

        # Save conversation history
        conversation_history_file = os.path.join(output_dir, "conversation-history.json")
        with open(conversation_history_file, 'w') as f:
            json.dump(conversation_history, f, indent=2)

        logger.info(f"Saved conversation history to {conversation_history_file}")

        return llm_output

    except Exception as e:
        logger.error(f"Error processing code question: {e}")
        return f"Error processing your question: {e}"

def main():
    # Load environment variables
    load_env_vars()

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Process a question about code")
    parser.add_argument("--question", required=True, help="The question about code")
    parser.add_argument("--db-path", default="/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/.lancedb",
                        help="Path to the LanceDB database")
    parser.add_argument("--output-dir", default="/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/output",
                        help="Path to the output directory")
    parser.add_argument("--llm-model", default="nvidia/llama-3.3-nemotron-super-49b-v1:free",
                        help="Name of the LLM model to use")
    parser.add_argument("--temperature", type=float, default=0.7,
                        help="Temperature for LLM generation")
    parser.add_argument("--max-tokens", type=int, default=2000,
                        help="Maximum tokens for LLM generation")
    parser.add_argument("--history-file", help="Path to the conversation history JSON file")

    args = parser.parse_args()

    # Log the parameters
    logger.info(f"Question: {args.question}")
    logger.info(f"DB path: {args.db_path}")
    logger.info(f"Output directory: {args.output_dir}")
    logger.info(f"LLM model: {args.llm_model}")

    # Load conversation history if provided
    conversation_history = None
    if args.history_file and os.path.exists(args.history_file):
        try:
            with open(args.history_file, 'r') as f:
                conversation_history = json.load(f)
            logger.info(f"Loaded conversation history from {args.history_file} with {len(conversation_history)} entries")
        except Exception as e:
            logger.error(f"Error loading conversation history: {e}")
            conversation_history = None

    # Process the question
    response = process_code_question(
        question=args.question,
        db_path=args.db_path,
        output_dir=args.output_dir,
        conversation_history=conversation_history,
        llm_model_name=args.llm_model,
        temperature=args.temperature,
        max_tokens=args.max_tokens
    )

    # Print the response
    print(response)

if __name__ == "__main__":
    main()
