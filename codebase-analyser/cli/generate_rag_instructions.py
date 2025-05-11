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
    print("Attempting to import langchain_core.documents...")
    from langchain_core.documents import Document
    print("Successfully imported Document")
    
    print("Attempting to import langchain_core.output_parsers...")
    from langchain_core.output_parsers import StrOutputParser
    print("Successfully imported StrOutputParser")
    
    print("Attempting to import langchain_core.prompts...")
    from langchain_core.prompts import ChatPromptTemplate
    print("Successfully imported ChatPromptTemplate")
    
    print("Attempting to import langchain.text_splitter...")
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    print("Successfully imported RecursiveCharacterTextSplitter")
    
    # Try to import sentence-transformers
    try:
        from sentence_transformers import SentenceTransformer
        SENTENCE_TRANSFORMERS_AVAILABLE = True
        print("Successfully imported SentenceTransformer")
    except ImportError:
        SENTENCE_TRANSFORMERS_AVAILABLE = False
        print("Failed to import SentenceTransformer")

    # Try to import lancedb
    try:
        import lancedb
        import pandas as pd
        LANCEDB_AVAILABLE = True
        print("Successfully imported LanceDB and pandas")
    except ImportError:
        LANCEDB_AVAILABLE = False
        print("Failed to import LanceDB or pandas")
    
    # Check if both are available
    if SENTENCE_TRANSFORMERS_AVAILABLE and LANCEDB_AVAILABLE:
        EMBEDDING_AVAILABLE = True
        print("Embedding functionality is available")
    else:
        EMBEDDING_AVAILABLE = False
        print("Embedding functionality is not available")
    
    LANGCHAIN_AVAILABLE = True
    print("All LangChain imports successful, LANGCHAIN_AVAILABLE set to True")
except ImportError as e:
    LANGCHAIN_AVAILABLE = False
    EMBEDDING_AVAILABLE = False
    print(f"LangChain import error: {e}")
    print(f"Module that failed to import: {e.__class__.__module__}")

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
    top_k: int = 5
) -> List[Document]:
    """
    Retrieve relevant code examples from the vector database.
    
    Args:
        query: The query to search for
        language: The programming language
        code_db_path: Path to the code vector database
        top_k: Number of results to return
        
    Returns:
        List of relevant documents
    """
    if not EMBEDDING_AVAILABLE:
        logger.warning("Embedding functionality is not available, skipping code retrieval")
        return []
    
    try:
        logger.info(f"Retrieving code examples for query: {query}")
        
        # Set default code database path
        if code_db_path is None:
            code_db_path = os.path.join(os.path.dirname(__file__), "..", "lancedb")
        
        # Generate embedding for the query
        model = SentenceTransformer('all-MiniLM-L6-v2')
        query_embedding = model.encode(query).tolist()
        
        # Check if the vector database exists
        if not os.path.exists(code_db_path):
            logger.info(f"Vector database not found at {code_db_path}, creating sample database")
            
            # Create a sample vector database
            os.makedirs(code_db_path, exist_ok=True)
            db = lancedb.connect(code_db_path)
            
            # Create sample data
            sample_data = [{
                "id": "sample1",
                "content": f"public class Sample {{ public void hello() {{ System.out.println(\"Hello\"); }} }}",
                "file_path": "sample/Sample.java",
                "language": language,
                "type": "class",
                "vector": model.encode(f"public class Sample {{ public void hello() {{ System.out.println(\"Hello\"); }} }}").tolist()
            }]
            
            # Create a dataframe
            import pandas as pd
            df = pd.DataFrame(sample_data)
            
            # Create the table
            db.create_table("code_chunks", df)
            logger.info("Created sample vector database")
            
            # Search for relevant code
            table = db.open_table("code_chunks")
            results = table.search(query_embedding).limit(top_k).to_pandas()
            
            # Convert to documents
            docs = []
            for _, row in results.iterrows():
                docs.append(Document(
                    page_content=row["content"],
                    metadata={
                        "source": row["file_path"],
                        "language": row["language"]
                    }
                ))
            
            logger.info(f"Retrieved {len(docs)} relevant code examples")
            return docs
        else:
            logger.info(f"Loading existing vector database from {code_db_path}")
            
            # Connect to the database
            db = lancedb.connect(code_db_path)
            
            # Check if the table exists
            if "code_chunks" in db.table_names():
                # Open the table
                table = db.open_table("code_chunks")
                
                # Create a where clause for language filtering
                where_clause = f"language = '{language}'" if language else None
                
                # Search for relevant code
                query_obj = table.search(query_embedding)
                if where_clause:
                    query_obj = query_obj.where(where_clause)
                
                results = query_obj.limit(top_k).to_pandas()
                
                # Convert to documents
                docs = []
                for _, row in results.iterrows():
                    docs.append(Document(
                        page_content=row["content"],
                        metadata={
                            "source": row["file_path"],
                            "language": row["language"]
                        }
                    ))
                
                logger.info(f"Retrieved {len(docs)} relevant code examples")
                return docs
            else:
                logger.warning(f"Table 'code_chunks' not found in database at {code_db_path}")
                return []
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
        
        # Process requirements using NLP if not already processed
        if not state.processed_requirements:
            logger.info("Processing requirements using NLP")
            from codebase_analyser.agent.nodes.nlp_nodes import process_requirements
            nlp_result = await process_requirements(state)
            state = AgentState(
                requirements=state.requirements,
                processed_requirements=nlp_result.get("processed_requirements"),
                combined_context=state.combined_context,
                errors=nlp_result.get("errors", [])
            )
        
        # Extract requirements and language
        requirements = state.requirements
        language = state.processed_requirements.get("language", "java") if state.processed_requirements else "java"
        
        # Convert requirements to string if it's a dict
        if isinstance(requirements, dict):
            requirements_text = json.dumps(requirements, indent=2)
        else:
            requirements_text = requirements
        
        # Extract entities from processed requirements to enhance the query
        enhanced_query = requirements_text
        if state.processed_requirements and "entities" in state.processed_requirements:
            entities = state.processed_requirements["entities"]
            
            # Add class names to the query
            if "classes" in entities and entities["classes"]:
                enhanced_query += " " + " ".join(entities["classes"])
            
            # Add function names to the query
            if "functions" in entities and entities["functions"]:
                enhanced_query += " " + " ".join(entities["functions"])
            
            # Add key phrases to the query
            if "key_phrases" in state.processed_requirements and state.processed_requirements["key_phrases"]:
                enhanced_query += " " + " ".join(state.processed_requirements["key_phrases"])
        
        logger.info(f"Enhanced query with NLP entities: {enhanced_query}")
        
        # Retrieve relevant code examples
        relevant_docs = await retrieve_relevant_code(
            query=enhanced_query,
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
        
        # Add processed requirements to the context
        if state.processed_requirements:
            intent = state.processed_requirements.get("intent", "unknown")
            entities = state.processed_requirements.get("entities", {})
            
            enhanced_context += f"\n\n## PROCESSED REQUIREMENTS\n"
            enhanced_context += f"Intent: {intent}\n"
            enhanced_context += f"Language: {language}\n"
            
            # Add entities
            enhanced_context += "Entities:\n"
            for entity_type, entity_list in entities.items():
                if entity_list:
                    enhanced_context += f"- {entity_type}: {', '.join(entity_list)}\n"
        
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
    if not EMBEDDING_AVAILABLE:
        logger.warning("Embedding functionality is not available, skipping codebase indexing")
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
        
        # Initialize the embedding model
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Prepare data for LanceDB
        data = []
        for i, chunk in enumerate(chunks):
            # Generate embedding
            embedding = model.encode(chunk.page_content).tolist()
            
            # Create a dictionary with all fields
            item = {
                "id": f"chunk_{i}",
                "content": chunk.page_content,
                "file_path": chunk.metadata.get("source", ""),
                "language": chunk.metadata.get("language", ""),
                "type": "code_chunk",
                "vector": embedding
            }
            
            data.append(item)
        
        # Create the LanceDB database
        os.makedirs(output_path, exist_ok=True)
        db = lancedb.connect(output_path)
        
        # Create a dataframe
        import pandas as pd
        df = pd.DataFrame(data)
        
        # Create or replace the table
        if "code_chunks" in db.table_names():
            logger.info("Replacing existing code_chunks table")
            db.drop_table("code_chunks")
        
        db.create_table("code_chunks", df)
        
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
    parser.add_argument('--skip-nlp', action='store_true',
                        help='Skip NLP processing of requirements')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.debug("LANGCHAIN_AVAILABLE: " + str(LANGCHAIN_AVAILABLE))
    logger.debug("EMBEDDING_AVAILABLE: " + str(EMBEDDING_AVAILABLE))

    # Check if LangChain is available
    if not LANGCHAIN_AVAILABLE:
        logger.error("LangChain is not available. Please install it with: pip install langchain>=0.1.0 langchain-core>=0.1.0 langchain-openai>=0.1.0 faiss-cpu")
        sys.exit(1)
    
    # Check if embedding functionality is available
    if not EMBEDDING_AVAILABLE:
        logger.error("Embedding functionality is not available. Please install sentence-transformers and lancedb with: pip install sentence-transformers lancedb pandas")
        sys.exit(1)
    
    # Index codebase if requested
    if args.index_codebase:
        code_db_path = args.code_db or os.path.join(os.path.dirname(__file__), "..", "lancedb")
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
    
    # Process requirements with NLP if not skipped
    processed_requirements = None
    if not args.skip_nlp:
        try:
            logger.info("Processing requirements with NLP")
            from codebase_analyser.agent.nodes.nlp_nodes import simple_process_requirements
            
            # Use simple processing to avoid LLM dependency
            if isinstance(requirements, str):
                processed_requirements = simple_process_requirements(requirements, args.language)
            else:
                req_text = requirements.get("description", "")
                processed_requirements = simple_process_requirements(req_text, args.language)
            
            logger.info(f"Processed requirements: {processed_requirements['intent']}")
        except Exception as e:
            logger.warning(f"Error processing requirements with NLP: {e}")
            # Continue without NLP processing
    
    # Create agent state
    state = AgentState(
        requirements=requirements,
        processed_requirements=processed_requirements or {
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
