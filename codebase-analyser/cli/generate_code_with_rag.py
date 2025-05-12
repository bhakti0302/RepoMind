#!/usr/bin/env python3
"""
Script to generate code using Multi-Hop RAG and OpenRouter.

This script integrates multiple components:
1. Tree-sitter for code parsing and understanding
2. LanceDB for vector storage and retrieval
3. Multi-hop RAG for context-aware code retrieval
4. NLP for requirements processing
5. OpenRouter for code generation
"""
import os
import sys
import logging
import argparse
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List, Union

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import necessary components
# Import necessary components
from codebase_analyser.agent.state import AgentState
from codebase_analyser.agent.nodes.nlp_nodes import process_requirements
from codebase_analyser.retrieval.multi_hop import retrieve_architectural_patterns, retrieve_implementation_details
from codebase_analyser.database import open_unified_storage, close_unified_storage
# Fix these imports to match your actual module structure
from codebase_analyser.parsing.chunker import CodeChunker
from codebase_analyser.parsing.analyser import CodebaseAnalyser  # Use the existing analyser instead of CodeParser
# Fix embedding generator import
from codebase_analyser.embeddings.embedding_generator import generate_embedding

# Try to import LangChain components
try:
    from langchain_openai import ChatOpenAI
    from langchain.prompts import PromptTemplate
    from langchain.schema.output_parser import StrOutputParser
    LANGCHAIN_AVAILABLE = True
except ImportError:
    logger.warning("LangChain not available. Install with: pip install langchain langchain-openai")
    LANGCHAIN_AVAILABLE = False

# Try to import Tree-sitter
try:
    from tree_sitter import Language, Parser
    TREESITTER_AVAILABLE = True
except ImportError:
    logger.warning("Tree-sitter not available. Install with: pip install tree-sitter")
    TREESITTER_AVAILABLE = False

# Try to import LanceDB
try:
    import lancedb
    LANCEDB_AVAILABLE = True
except ImportError:
    logger.warning("LanceDB not available. Install with: pip install lancedb")
    LANCEDB_AVAILABLE = False

# Code generation prompt template
CODE_GENERATION_PROMPT = """
You are an expert software developer tasked with generating code based on requirements and context.

# Requirements
{requirements}

# Architectural Context
{architectural_context}

# Implementation Context
{implementation_context}

# Task
Generate {language} code that implements the requirements.
The code should be complete, well-documented, and follow the style and patterns shown in the context.
Make sure your implementation aligns with the architectural patterns and implementation details provided.

Only respond with the code. Do not include any explanations or comments outside the code.
"""

async def index_codebase(
    codebase_path: str,
    db_path: str,
    language_filter: Optional[List[str]] = None
) -> bool:
    """
    Index a codebase using Tree-sitter and store in LanceDB.
    
    Args:
        codebase_path: Path to the codebase
        db_path: Path to the database
        language_filter: Optional list of languages to filter
        
    Returns:
        True if indexing was successful
    """
    if not TREESITTER_AVAILABLE:
        logger.error("Tree-sitter is required for indexing")
        return False
    
    if not LANCEDB_AVAILABLE:
        logger.error("LanceDB is required for indexing")
        return False
    
    try:
        logger.info(f"Indexing codebase at {codebase_path}...")
        
        # Initialize code parser and chunker
        code_parser = CodeParser()
        code_chunker = CodeChunker()
        
        # Initialize vector storage
        vector_storage = VectorStorage(db_path)
        
        # Walk through the codebase
        file_count = 0
        chunk_count = 0
        
        for root, _, files in os.walk(codebase_path):
            for file in files:
                # Skip non-code files
                if not code_parser.is_supported_file(file):
                    continue
                
                # Skip files not in language filter
                file_language = code_parser.detect_language(file)
                if language_filter and file_language not in language_filter:
                    continue
                
                file_path = os.path.join(root, file)
                
                try:
                    # Parse the file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Parse and chunk the file
                    parsed_file = code_parser.parse_file(file_path, content)
                    chunks = code_chunker.chunk_file(file_path, content, parsed_file)
                    
                    # Store chunks in vector storage
                    for chunk in chunks:
                        vector_storage.add_chunk(chunk)
                        chunk_count += 1
                    
                    file_count += 1
                    if file_count % 10 == 0:
                        logger.info(f"Indexed {file_count} files, {chunk_count} chunks")
                
                except Exception as e:
                    logger.warning(f"Error processing file {file_path}: {e}")
        
        # Commit changes to vector storage
        vector_storage.commit()
        
        logger.info(f"Indexing complete. Processed {file_count} files, {chunk_count} chunks")
        return True
    
    except Exception as e:
        logger.error(f"Error indexing codebase: {e}")
        return False

def format_architectural_context(patterns: List[Dict[str, Any]]) -> str:
    """
    Format architectural patterns for the prompt.
    
    Args:
        patterns: List of architectural patterns
        
    Returns:
        Formatted context string
    """
    if not patterns:
        return "No architectural patterns found."
    
    context_parts = []
    
    for i, pattern in enumerate(patterns, 1):
        name = pattern.get("name", "Unnamed")
        chunk_type = pattern.get("chunk_type", "unknown")
        content = pattern.get("content", "")
        
        context_parts.append(f"## Pattern {i}: {name} ({chunk_type})")
        context_parts.append(f"```\n{content}\n```")
    
    return "\n\n".join(context_parts)

def format_implementation_context(details: List[Dict[str, Any]]) -> str:
    """
    Format implementation details for the prompt.
    
    Args:
        details: List of implementation details
        
    Returns:
        Formatted context string
    """
    if not details:
        return "No implementation details found."
    
    context_parts = []
    
    for i, detail in enumerate(details, 1):
        name = detail.get("name", "Unnamed")
        chunk_type = detail.get("chunk_type", "unknown")
        content = detail.get("content", "")
        score = detail.get("combined_score", 0)
        
        context_parts.append(f"## Detail {i}: {name} ({chunk_type}, Score: {score:.2f})")
        context_parts.append(f"```\n{content}\n```")
    
    return "\n\n".join(context_parts)

async def generate_code_with_multi_hop_rag(
    requirements: Union[str, Dict[str, Any]],
    language: str = "java",
    db_path: Optional[str] = None,
    openrouter_api_key: Optional[str] = None,
    model: str = "nvidia/llama-3.3-nemotron-super-49b-v1:free",
    index_before_generation: bool = False,
    codebase_path: Optional[str] = None
) -> str:
    """
    Generate code using Multi-Hop RAG and OpenRouter.
    
    Args:
        requirements: The requirements text or dict
        language: The programming language to use
        db_path: Path to the database
        openrouter_api_key: OpenRouter API key
        model: Model to use for code generation
        index_before_generation: Whether to index the codebase before generation
        codebase_path: Path to the codebase (required if index_before_generation is True)
        
    Returns:
        Generated code
    """
    if not LANGCHAIN_AVAILABLE:
        logger.error("LangChain is required for code generation")
        return "Error: LangChain is not available"
    
    # Use environment variable if API key not provided
    openrouter_api_key = openrouter_api_key or os.environ.get("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        logger.error("OpenRouter API key is required")
        return "Error: OpenRouter API key not provided"
    
    try:
        # Index codebase if requested
        if index_before_generation:
            if not codebase_path:
                logger.error("Codebase path is required for indexing")
                return "Error: Codebase path not provided for indexing"
            
            success = await index_codebase(
                codebase_path=codebase_path,
                db_path=db_path,
                language_filter=[language] if language else None
            )
            
            if not success:
                logger.error("Failed to index codebase")
                return "Error: Failed to index codebase"
        
        # Convert requirements to string if it's a dict
        requirements_text = requirements
        if isinstance(requirements, dict):
            requirements_text = requirements.get("description", "")
        
        # Create initial state
        state = AgentState(requirements=requirements)
        
        # Process requirements with NLP
        logger.info("Processing requirements with NLP...")
        processed_result = await process_requirements(state)
        
        # Update state with processed requirements
        state = AgentState(
            requirements=state.requirements,
            processed_requirements=processed_result.get("processed_requirements", {})
        )
        
        # Extract language from processed requirements if not specified
        if not language and state.processed_requirements and "language" in state.processed_requirements:
            language = state.processed_requirements["language"]
        
        # Open database connection
        logger.info(f"Opening database connection to {db_path}...")
        db_connection = open_unified_storage(
            db_path=db_path,
            use_minimal_schema=True,
            create_if_not_exists=False,
            read_only=True
        )
        
        try:
            # Enhance query with NLP-processed requirements
            enhanced_query = requirements_text
            if state.processed_requirements:
                # Add intent to query
                if "intent" in state.processed_requirements:
                    enhanced_query += f" {state.processed_requirements['intent']}"
                
                # Add entities to query
                if "entities" in state.processed_requirements:
                    entities = state.processed_requirements["entities"]
                    for entity_type, entity_list in entities.items():
                        if entity_list:
                            enhanced_query += f" {' '.join(entity_list)}"
            
            # First hop: Retrieve architectural patterns
            logger.info("First hop: Retrieving architectural patterns...")
            architectural_patterns = await retrieve_architectural_patterns(
                query=enhanced_query,
                language=language,
                limit=5,
                db_connection=db_connection
            )
            
            # Log the architectural patterns
            logger.info(f"Retrieved {len(architectural_patterns)} architectural patterns")
            for i, pattern in enumerate(architectural_patterns, 1):
                logger.info(f"Pattern {i}: {pattern.get('name', 'Unnamed')} ({pattern.get('chunk_type', 'unknown')})")
                logger.info(f"  Score: {pattern.get('similarity', 0):.2f}")
            
            # Second hop: Retrieve implementation details
            logger.info("Second hop: Retrieving implementation details...")
            implementation_details = await retrieve_implementation_details(
                query=enhanced_query,
                language=language,
                architectural_patterns=architectural_patterns,
                limit=10,
                db_connection=db_connection
            )
            
            # Log the implementation details
            logger.info(f"Retrieved {len(implementation_details)} implementation details")
            for i, detail in enumerate(implementation_details, 1):
                logger.info(f"Detail {i}: {detail.get('name', 'Unnamed')} ({detail.get('chunk_type', 'unknown')})")
                logger.info(f"  Combined Score: {detail.get('combined_score', 0):.2f}")
            
            # Format contexts for the prompt
            architectural_context = format_architectural_context(architectural_patterns)
            implementation_context = format_implementation_context(implementation_details)
            
        finally:
            # Close database connection
            logger.info("Closing database connection...")
            close_unified_storage(db_connection)
        
        # Initialize the LLM
        logger.info("Initializing LLM...")
        llm = ChatOpenAI(
            model=model,
            temperature=0.2,
            base_url="https://openrouter.ai/api/v1",
            api_key=openrouter_api_key
        )
        
        # Create the prompt
        prompt = PromptTemplate.from_template(CODE_GENERATION_PROMPT)
        
        # Create the chain
        chain = prompt | llm | StrOutputParser()
        
        # Run the chain
        logger.info("Generating code...")
        generated_code = await chain.ainvoke({
            "requirements": requirements_text,
            "architectural_context": architectural_context,
            "implementation_context": implementation_context,
            "language": language
        })
        
        # Clean up the generated code
        if generated_code.startswith("```") and generated_code.endswith("```"):
            # Extract the language if specified
            first_line = generated_code.split("\n")[0].strip()
            if first_line.startswith("```") and len(first_line) > 3:
                generated_code = generated_code[len(first_line):].strip()
            else:
                generated_code = generated_code[3:].strip()
            
            if generated_code.endswith("```"):
                generated_code = generated_code[:-3].strip()
        
        logger.info(f"Generated code with {len(generated_code)} characters")
        return generated_code
        
    except Exception as e:
        logger.error(f"Error generating code: {e}")
        return f"Error: {str(e)}"

async def main_async():
    """Async main function."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate code using Multi-Hop RAG and OpenRouter')
    parser.add_argument('--requirements', type=str, required=True, 
                        help='Requirements text or path to a JSON file containing requirements')
    parser.add_argument('--language', type=str, default='java',
                        help='Programming language for the generated code')
    parser.add_argument('--output', type=str, default='generated_code.txt',
                        help='Path to save the generated code')
    parser.add_argument('--db-path', type=str, default=None,
                        help='Path to the database')
    parser.add_argument('--api-key', type=str, default=None,
                        help='OpenRouter API key (defaults to OPENROUTER_API_KEY environment variable)')
    parser.add_argument('--model', type=str, default="nvidia/llama-3.3-nemotron-super-49b-v1:free",
                        help='Model to use for code generation')
    parser.add_argument('--index-codebase', action='store_true',
                        help='Index the codebase before generating code')
    parser.add_argument('--codebase-path', type=str, default=None,
                        help='Path to the codebase (required if --index-codebase is specified)')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Check if LangChain is available
    if not LANGCHAIN_AVAILABLE:
        logger.error("LangChain is not available. Please install it with: pip install langchain langchain-openai")
        sys.exit(1)
    
    # Check if Tree-sitter is available if indexing
    if args.index_codebase and not TREESITTER_AVAILABLE:
        logger.error("Tree-sitter is not available. Please install it with: pip install tree-sitter")
        sys.exit(1)
    
    # Check if LanceDB is available if indexing
    if args.index_codebase and not LANCEDB_AVAILABLE:
        logger.error("LanceDB is not available. Please install it with: pip install lancedb")
        sys.exit(1)
    
    # Check if codebase path is provided if indexing
    if args.index_codebase and not args.codebase_path:
        logger.error("Codebase path is required when indexing")
        sys.exit(1)
    
    # Load requirements
    requirements_text = args.requirements
    if os.path.isfile(args.requirements):
        with open(args.requirements, 'r') as f:
            if args.requirements.endswith('.json'):
                requirements_text = json.load(f).get('description', '')
            else:
                requirements_text = f.read()
    
    # Generate code
    generated_code = await generate_code_with_multi_hop_rag(
        requirements=requirements_text,
        language=args.language,
        db_path=args.db_path,
        openrouter_api_key=args.api_key,
        model=args.model,
        index_before_generation=args.index_codebase,
        codebase_path=args.codebase_path
    )
    
    # Save the generated code
    with open(args.output, 'w') as f:
        f.write(generated_code)
    
    logger.info(f"Generated code saved to {args.output}")
    print(f"\nGenerated code saved to {args.output}")

def main():
    """Main function."""
    asyncio.run(main_async())

if __name__ == "__main__":
    main()