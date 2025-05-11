#!/usr/bin/env python3
"""
Script to generate LLM instructions using RAG (Retrieval Augmented Generation).

This script enhances the instruction generation by:
1. Creating embeddings of the requirements
2. Retrieving relevant code examples from a vector database
3. Incorporating the retrieved examples into the instructions

Usage:
    python -m cli.generate_rag_instructions --requirements "Create a Java class..." --output llm_instructions.txt
"""

import os
import sys
import json
import logging
import argparse
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from codebase_analyser.agent.nodes.code_generation import generate_llm_instructions
from codebase_analyser.agent.state import AgentState

# Import LangChain components
try:
    from langchain_core.documents import Document
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_openai import OpenAIEmbeddings, ChatOpenAI
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.vectorstores import FAISS
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def retrieve_relevant_code(
    query: str, 
    language: str,
    code_db_path: Optional[str] = None,
    top_k: int = 3
) -> List[Document]:
    """
    Retrieve relevant code examples from the vector database.
    
    Args:
        query: The query to search for
        language: The programming language
        code_db_path: Path to the FAISS index
        top_k: Number of examples to retrieve
        
    Returns:
        List of relevant code documents
    """
    if not LANGCHAIN_AVAILABLE:
        logger.warning("LangChain is not available, skipping code retrieval")
        return []
    
    try:
        # Default path for the vector database
        if code_db_path is None:
            code_db_path = os.path.join(os.path.dirname(__file__), "..", "code_db")
        
        # Check if the vector database exists
        if not os.path.exists(code_db_path):
            logger.warning(f"Vector database not found at {code_db_path}")
            # Create a simple in-memory database with sample code
            embeddings = OpenAIEmbeddings()
            sample_docs = [
                Document(
                    page_content=f"// Sample {language} code for demonstration\n" +
                                f"class Example {{\n    // This is a placeholder\n}}", 
                    metadata={"language": language, "source": "sample"}
                )
            ]
            vectorstore = FAISS.from_documents(sample_docs, embeddings)
            
            # Save the vector database for future use
            os.makedirs(os.path.dirname(code_db_path), exist_ok=True)
            vectorstore.save_local(code_db_path)
        else:
            # Load the existing vector database
            embeddings = OpenAIEmbeddings()
            vectorstore = FAISS.load_local(code_db_path, embeddings)
        
        # Create a retriever
        retriever = vectorstore.as_retriever(search_kwargs={"k": top_k})
        
        # Add language filter to the query
        enhanced_query = f"{query} language:{language}"
        
        # Retrieve relevant documents
        docs = retriever.invoke(enhanced_query)
        logger.info(f"Retrieved {len(docs)} relevant code examples")
        
        return docs
    except Exception as e:
        logger.error(f"Error retrieving code examples: {e}")
        return []

async def generate_rag_instructions(
    state: AgentState,
    code_db_path: Optional[str] = None,
    output_file: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate instructions file using RAG.
    
    Args:
        state: The current agent state
        code_db_path: Path to the code vector database
        output_file: Path to the output file
        
    Returns:
        Dictionary with the path to the generated file
    """
    try:
        logger.info("Generating RAG-enhanced instructions")
        
        # Extract requirements and language
        requirements = state.requirements
        language = state.processed_requirements.get("language", "java") if state.processed_requirements else "java"
        
        # Convert requirements to string if it's a dict
        if isinstance(requirements, dict):
            requirements_text = json.dumps(requirements, indent=2)
        else:
            requirements_text = requirements
        
        # Retrieve relevant code examples
        relevant_docs = await retrieve_relevant_code(
            query=requirements_text,
            language=language,
            code_db_path=code_db_path
        )
        
        # Extract code examples from the documents
        code_examples = []
        for i, doc in enumerate(relevant_docs):
            code = doc.page_content
            source = doc.metadata.get("source", "Unknown")
            code_examples.append(f"### Example {i+1} (Source: {source})\n```{language}\n{code}\n```")
        
        # Combine code examples
        combined_examples = "\n\n".join(code_examples)
        
        # Update the context with the retrieved examples
        enhanced_context = state.combined_context or ""
        if combined_examples:
            enhanced_context += f"\n\n## RELEVANT CODE EXAMPLES\n{combined_examples}"
        
        # Create a new state with the enhanced context
        enhanced_state = AgentState(
            requirements=state.requirements,
            processed_requirements=state.processed_requirements,
            combined_context=enhanced_context
        )
        
        # Generate instructions using the enhanced context
        result = await generate_llm_instructions(enhanced_state, output_file)
        
        return result
    except Exception as e:
        logger.error(f"Error generating RAG instructions: {e}")
        return {
            "errors": state.errors + [{"stage": "rag_instructions_generation", "message": str(e)}],
            "instructions_file": None
        }

async def index_codebase(
    codebase_path: str,
    output_path: str,
    language_filter: Optional[str] = None
) -> bool:
    """
    Index a codebase to create a vector database for RAG.
    
    Args:
        codebase_path: Path to the codebase
        output_path: Path to save the vector database
        language_filter: Optional filter for specific languages
        
    Returns:
        True if indexing was successful
    """
    if not LANGCHAIN_AVAILABLE:
        logger.warning("LangChain is not available, skipping codebase indexing")
        return False
    
    try:
        logger.info(f"Indexing codebase at {codebase_path}")
        
        # Map file extensions to languages
        extension_to_language = {
            ".java": "java",
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".rb": "ruby",
            ".go": "go",
            ".rs": "rust",
            ".c": "c",
            ".cpp": "cpp",
            ".cs": "csharp",
            ".php": "php",
            ".swift": "swift",
            ".kt": "kotlin"
        }
        
        # Collect code files
        code_files = []
        for root, _, files in os.walk(codebase_path):
            for file in files:
                file_path = os.path.join(root, file)
                ext = os.path.splitext(file)[1].lower()
                
                # Skip if not a code file or doesn't match language filter
                if ext not in extension_to_language:
                    continue
                
                language = extension_to_language[ext]
                if language_filter and language != language_filter:
                    continue
                
                code_files.append((file_path, language))
        
        logger.info(f"Found {len(code_files)} code files")
        
        # Load and process code files
        documents = []
        for file_path, language in code_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Skip empty files
                if not content.strip():
                    continue
                
                # Create a document
                rel_path = os.path.relpath(file_path, codebase_path)
                documents.append(Document(
                    page_content=content,
                    metadata={
                        "source": rel_path,
                        "language": language,
                        "path": file_path
                    }
                ))
            except Exception as e:
                logger.warning(f"Error reading {file_path}: {e}")
        
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
        
        chunks = text_splitter.split_documents(documents)
        logger.info(f"Split into {len(chunks)} chunks")
        
        # Create embeddings and vector store
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.from_documents(chunks, embeddings)
        
        # Save the vector store
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        vectorstore.save_local(output_path)
        
        logger.info(f"Indexed codebase saved to {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error indexing codebase: {e}")
        return False

async def main_async():
    """Async main function."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate LLM instructions file using RAG')
    parser.add_argument('--requirements', type=str, required=True, 
                        help='Requirements text or path to a JSON file containing requirements')
    parser.add_argument('--context', type=str, default='',
                        help='Context text or path to a file containing context')
    parser.add_argument('--language', type=str, default='java',
                        help='Programming language for the generated code')
    parser.add_argument('--output', type=str, default='llm_instructions.txt',
                        help='Path to save the generated instructions')
    parser.add_argument('--code-db', type=str, default=None,
                        help='Path to the code vector database')
    parser.add_argument('--index-codebase', type=str, default=None,
                        help='Path to a codebase to index before generating instructions')
    parser.add_argument('--include-code', action='store_true',
                        help='Generate code and include it in the instructions')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Check if LangChain is available
    if not LANGCHAIN_AVAILABLE:
        logger.error("LangChain is not available. Please install it with: pip install langchain>=0.1.0 langchain-core>=0.1.0 langchain-openai>=0.1.0 faiss-cpu")
        sys.exit(1)
    
    # Check for OpenAI API key
    if not os.environ.get("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY environment variable is not set. Please set it before running this script.")
        sys.exit(1)
    
    # Index codebase if requested
    if args.index_codebase:
        code_db_path = args.code_db or os.path.join(os.path.dirname(__file__), "..", "code_db")
        success = await index_codebase(
            codebase_path=args.index_codebase,
            output_path=code_db_path,
            language_filter=args.language
        )
        if not success:
            logger.error("Failed to index codebase")
            sys.exit(1)
    
    # Load requirements
    requirements = args.requirements
    if os.path.exists(requirements) and requirements.endswith('.json'):
        try:
            with open(requirements, 'r') as f:
                requirements = json.load(f)
            logger.info(f"Loaded requirements from {requirements}")
        except Exception as e:
            logger.error(f"Error loading requirements file: {str(e)}")
            sys.exit(1)
    
    # Load context
    context = args.context
    if os.path.exists(context) and not context.endswith('.json'):
        try:
            with open(context, 'r') as f:
                context = f.read()
            logger.info(f"Loaded context from {context}")
        except Exception as e:
            logger.error(f"Error loading context file: {str(e)}")
            sys.exit(1)
    
    # Create agent state
    state = AgentState(
        requirements=requirements,
        processed_requirements={
            "intent": "code_generation",
            "language": args.language,
            "original_text": requirements if isinstance(requirements, str) else json.dumps(requirements)
        },
        combined_context=context
    )
    
    # Generate the instructions file
    logger.info("Generating RAG-enhanced instructions file...")
    
    result = await generate_rag_instructions(
        state=state,
        code_db_path=args.code_db,
        output_file=args.output
    )
    
    if "instructions_file" in result and result["instructions_file"]:
        logger.info(f"Instructions file generated at: {result['instructions_file']}")
    else:
        logger.error("Failed to generate instructions file")
        if "errors" in result:
            for error in result["errors"]:
                logger.error(f"Error in {error['stage']}: {error['message']}")
        sys.exit(1)

def main():
    """Main function."""
    asyncio.run(main_async())

if __name__ == "__main__":
    main()