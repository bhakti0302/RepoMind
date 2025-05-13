
"""
Context retriever for code generation.

This module provides functionality to retrieve relevant code from the codebase
based on requirements analysis.
"""

import os
import sys
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the codebase-analyser directory to the path
codebase_analyser_dir = str(Path(__file__).parent.parent.parent)
if codebase_analyser_dir not in sys.path:
    sys.path.append(codebase_analyser_dir)
    logger.info(f"Added {codebase_analyser_dir} to sys.path")

import lancedb
from codebase_analyser.embeddings.embedding_generator import EmbeddingGenerator

class ContextRetriever:
    """Retriever for code context from the codebase."""
    
    def __init__(
        self,
        db_path: Optional[str] = None,
        embedding_model: str = "microsoft/codebert-base"
    ):
        """Initialize the context retriever.
        
        Args:
            db_path: Path to the LanceDB database
            embedding_model: Model to use for embeddings
        """
        # Use the default path inside codebase-analyser if not specified
        if db_path is None:
            db_path = os.path.join(codebase_analyser_dir, ".lancedb")
        
        # Check if the database path exists
        if os.path.exists(db_path):
            logger.info(f"Database path exists: {db_path}")
        else:
            logger.warning(f"Database path does not exist: {db_path}")
            # Try to find the database in common locations
            possible_paths = [
                os.path.join(os.getcwd(), ".lancedb"),
                os.path.join(os.getcwd(), "codebase-analyser", ".lancedb"),
                os.path.join(os.path.dirname(os.getcwd()), ".lancedb"),
                os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), ".lancedb")
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    logger.info(f"Found database at alternative path: {path}")
                    db_path = path
                    break
            
        logger.info(f"Initializing context retriever with database at {db_path}")
        logger.info(f"Current working directory: {os.getcwd()}")
        logger.info(f"Python path: {sys.path}")
        
        # Connect directly to LanceDB
        try:
            self.db = lancedb.connect(db_path)
            logger.info(f"Successfully connected to LanceDB at {db_path}")
            
            # Check available tables
            try:
                table_names = self.db.table_names()
                logger.info(f"Available tables: {table_names}")
                
                # Check if code_chunks table exists
                if "code_chunks" in table_names:
                    # Get table info
                    table = self.db.open_table("code_chunks")
                    try:
                        schema = table.schema
                        logger.info(f"code_chunks table schema: {schema}")
                    except AttributeError:
                        logger.info("Could not retrieve schema (older LanceDB version)")
                    
                    # Try to get row count
                    try:
                        count = len(table.to_pandas())
                        logger.info(f"code_chunks table has {count} rows")
                    except Exception as e:
                        logger.warning(f"Could not get row count: {e}")
                else:
                    logger.warning("code_chunks table does not exist")
            except AttributeError:
                logger.warning("Could not retrieve table names (older LanceDB version)")
                # Try to open the table directly
                try:
                    table = self.db.open_table("code_chunks")
                    logger.info("Successfully opened code_chunks table")
                    # Try to get row count
                    try:
                        count = len(table.to_pandas())
                        logger.info(f"code_chunks table has {count} rows")
                    except Exception as e:
                        logger.warning(f"Could not get row count: {e}")
                except Exception as e:
                    logger.warning(f"Could not open code_chunks table: {e}")
        except Exception as e:
            logger.error(f"Error connecting to LanceDB: {e}")
            self.db = None
        
        # Initialize the embedding generator
        self.embedding_generator = EmbeddingGenerator(
            model_name=embedding_model
        )
        logger.info(f"Initialized embedding generator with model: {embedding_model}")
    
    def retrieve_by_keywords(
        self,
        keywords: List[str],
        project_id: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve code chunks by keywords.
        
        Args:
            keywords: List of keywords to search for
            project_id: Project ID to filter by
            limit: Maximum number of results to return
            filters: Additional filters to apply
        
        Returns:
            List of code chunks
        """
        try:
            # Check if database is connected
            if self.db is None:
                logger.warning("Database not connected")
                return []
            
            # Open the code_chunks table
            try:
                table = self.db.open_table("code_chunks")
                logger.info("Successfully opened code_chunks table")
            except Exception as e:
                logger.warning(f"Could not open code_chunks table: {e}")
                return []
            
            # Get all rows and filter manually
            try:
                logger.info("Getting all rows and filtering manually")
                all_rows = table.to_pandas()
                logger.info(f"Retrieved {len(all_rows)} total rows")
                
                # Filter by project_id
                if project_id:
                    all_rows = all_rows[all_rows['project_id'] == project_id]
                    logger.info(f"After project_id filter: {len(all_rows)} rows")
                
                # Apply additional filters
                if filters:
                    for key, value in filters.items():
                        if key in all_rows.columns:
                            all_rows = all_rows[all_rows[key] == value]
                    logger.info(f"After additional filters: {len(all_rows)} rows")
                
                # Filter by content containing any of the keywords
                if keywords and 'content' in all_rows.columns:
                    import pandas as pd
                    content_filters = []
                    for keyword in keywords:
                        content_filters.append(all_rows['content'].str.contains(keyword, case=False, na=False))
                    
                    # Combine filters with OR
                    if content_filters:
                        combined_filter = content_filters[0]
                        for f in content_filters[1:]:
                            combined_filter = combined_filter | f
                        all_rows = all_rows[combined_filter]
                        logger.info(f"After keyword filter: {len(all_rows)} rows")
                
                # Limit results
                results = all_rows.head(limit)
                logger.info(f"Retrieved {len(results)} results by keywords")
                
                # Convert to list of dictionaries
                return results.to_dict(orient="records")
            except Exception as e:
                logger.error(f"Error retrieving by keywords: {e}")
                return []
        except Exception as e:
            logger.warning(f"Error retrieving code chunks by keywords: {e}")
            return []

    def retrieve_by_embedding(
        self,
        text: str,
        project_id: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        language: str = "text"  # Default language is text
    ) -> List[Dict[str, Any]]:
        """Retrieve code chunks by embedding similarity.
        
        Args:
            text: Text to generate embedding from
            project_id: Project ID to filter by
            limit: Maximum number of results to return
            filters: Additional filters to apply
            language: Language of the text (default: "text")
            
        Returns:
            List of code chunks
        """
        logger.info(f"Retrieving code chunks by embedding for project: {project_id}")
        logger.info(f"Query text: {text[:100]}..." if len(text) > 100 else f"Query text: {text}")
        
        try:
            # Check if database is connected
            if self.db is None:
                logger.warning("Database not connected")
                return []
            
            # Open the code_chunks table
            try:
                table = self.db.open_table("code_chunks")
                logger.info("Successfully opened code_chunks table")
            except Exception as e:
                logger.warning(f"Could not open code_chunks table: {e}")
                return []
            
            # Generate embedding for the query
            logger.info(f"Generating embedding for query text with language: {language}")
            query_embedding = self.embedding_generator.generate_embedding(text, language)
            logger.info(f"Generated embedding of dimension: {len(query_embedding)}")
            
            # Try to get schema to find embedding column name
            embedding_column = "embedding"  # Default name
            try:
                schema = table.schema
                logger.info(f"Table schema: {schema}")
                
                # Check if embedding column exists with a different name
                possible_embedding_columns = ["embedding", "vector", "embeddings", "embedding_vector"]
                for col in possible_embedding_columns:
                    if col in str(schema):
                        embedding_column = col
                        logger.info(f"Found embedding column: {embedding_column}")
                        break
            except Exception as e:
                logger.warning(f"Could not get schema: {e}")
            
            # Try different approaches to get all rows and filter manually
            try:
                logger.info("Attempting to get all rows and filter manually")
                all_rows = table.to_pandas()
                logger.info(f"Retrieved {len(all_rows)} total rows")
                
                # Filter by project_id
                if project_id:
                    all_rows = all_rows[all_rows['project_id'] == project_id]
                    logger.info(f"After project_id filter: {len(all_rows)} rows")
                
                # Apply additional filters
                if filters:
                    for key, value in filters.items():
                        if key in all_rows.columns:
                            all_rows = all_rows[all_rows[key] == value]
                    logger.info(f"After additional filters: {len(all_rows)} rows")
                
                # If we have embeddings, calculate similarity and sort
                if embedding_column in all_rows.columns and len(all_rows) > 0:
                    import numpy as np
                    from sklearn.metrics.pairwise import cosine_similarity
                    
                    # Convert query embedding to numpy array
                    query_vector = np.array(query_embedding).reshape(1, -1)
                    
                    # Calculate similarities
                    similarities = []
                    for idx, row in all_rows.iterrows():
                        try:
                            chunk_embedding = row[embedding_column]
                            if chunk_embedding is not None:
                                chunk_vector = np.array(chunk_embedding).reshape(1, -1)
                                similarity = cosine_similarity(query_vector, chunk_vector)[0][0]
                                similarities.append((idx, similarity))
                        except Exception as e:
                            logger.warning(f"Error calculating similarity for row {idx}: {e}")
                    
                    # Sort by similarity
                    similarities.sort(key=lambda x: x[1], reverse=True)
                    
                    # Get top results
                    top_indices = [idx for idx, _ in similarities[:limit]]
                    results = all_rows.loc[top_indices]
                    logger.info(f"Retrieved {len(results)} results by similarity")
                else:
                    # If no embeddings, just return the filtered rows
                    results = all_rows.head(limit)
                    logger.info(f"Retrieved {len(results)} results without similarity")
                
                # Convert to list of dictionaries
                return results.to_dict(orient="records")
            except Exception as e:
                logger.error(f"Error retrieving by embedding: {e}")
                return []
        except Exception as e:
            logger.warning(f"Error retrieving code chunks by embedding: {e}")
            return []

    def retrieve_by_dependency(
        self,
        node_ids: List[str],
        project_id: str,
        limit: int = 10,
        dependency_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve code chunks by dependency relationships.
        
        Args:
            node_ids: List of node IDs to find dependencies for
            project_id: Project ID to filter by
            limit: Maximum number of results to return
            dependency_types: Types of dependencies to include
        
        Returns:
            List of code chunks
        """
        try:
            # Set up dependency filter
            dependency_filter = {
                "project_id": project_id
            }
            
            if dependency_types:
                dependency_filter["dependency_type"] = dependency_types
            
            # Search for dependencies
            results = self.db.search_with_dependencies(
                node_ids=node_ids,
                dependency_filter=dependency_filter,
                limit=limit
            )
            
            logger.info(f"Retrieved {len(results)} code chunks by dependency relationships")
            
            return results
        except Exception as e:
            logger.warning(f"Error retrieving code chunks by dependency: {e}")
            return []

    def retrieve_combined(
        self,
        text: str,
        keywords: List[str],
        project_id: str,
        limit: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        language: str = "text"  # Default language is text
    ) -> List[Dict[str, Any]]:
        """Retrieve code chunks using a combination of methods.
        
        Args:
            text: Text to generate embedding from
            keywords: List of keywords to search for
            project_id: Project ID to filter by
            limit: Maximum number of results to return
            filters: Additional filters to apply
            language: Language of the text (default: "text")
            
        Returns:
            List of code chunks
        """
        logger.info(f"Retrieving combined results for project: {project_id}")
        
        # Get results from both methods
        embedding_results = self.retrieve_by_embedding(
            text=text,
            project_id=project_id,
            limit=limit,
            filters=filters,
            language=language
        )
        
        keyword_results = self.retrieve_by_keywords(
            keywords=keywords,
            project_id=project_id,
            limit=limit,
            filters=filters
        )
        
        logger.info(f"Retrieved {len(embedding_results)} results by embedding and {len(keyword_results)} results by keywords")
        
        # If one method failed, return results from the other
        if not embedding_results:
            logger.info("Using only keyword results")
            return keyword_results
        
        if not keyword_results:
            logger.info("Using only embedding results")
            return embedding_results
        
        # Combine results, prioritizing those that appear in both
        combined_results = []
        seen_ids = set()
        
        # First add results that appear in both
        for result in embedding_results:
            if any(kr.get("node_id") == result.get("node_id") for kr in keyword_results):
                combined_results.append(result)
                seen_ids.add(result.get("node_id"))
        
        # Then add remaining results from embedding search
        for result in embedding_results:
            if result.get("node_id") not in seen_ids:
                combined_results.append(result)
                seen_ids.add(result.get("node_id"))
        
        # Then add remaining results from keyword search
        for result in keyword_results:
            if result.get("node_id") not in seen_ids:
                combined_results.append(result)
                seen_ids.add(result.get("node_id"))
        
        # Limit to requested number
        combined_results = combined_results[:limit]
        
        logger.info(f"Retrieved {len(combined_results)} code chunks using combined approach")
        
        return combined_results
    
    def close(self):
        """Close the database connection."""
        try:
            # Close the database connection if the method exists
            if self.db is not None:
                if hasattr(self.db, 'close'):
                    self.db.close()
                    logger.info("Closed database connection")
                else:
                    # For LanceDB 0.3.3 and similar versions that don't have an explicit close method
                    # Just set to None to release the reference
                    logger.info("LanceDB 0.3.3 connection doesn't have a close method, releasing reference")
                    self.db = None
        except Exception as e:
            logger.warning(f"Error while closing database connection: {e}")
            # Still set to None to release the reference
            self.db = None

