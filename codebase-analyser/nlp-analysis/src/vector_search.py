# """
# Vector Search module.

# This module provides functionality for performing vector search on code chunks.
# """

# import os
# import sys
# import logging
# import numpy as np
# from typing import Dict, List, Any, Optional, Union, Tuple

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
# )
# logger = logging.getLogger(__name__)

# # Try to import LanceDB and UnifiedStorage
# try:
#     import lancedb
#     # Add the codebase_analyser package to the path
#     sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
#     from codebase_analyser.database.unified_storage import UnifiedStorage
# except ImportError as e:
#     logger.error(f"Error importing dependencies: {e}")
#     logger.error("Make sure LanceDB and codebase_analyser are installed")
#     sys.exit(1)

# class VectorSearch:
#     """Vector search for code chunks."""

#     def __init__(
#         self,
#         db_path: str = ".lancedb",
#         embedding_model: str = None
#     ):
#         """Initialize the vector search.

#         Args:
#             db_path: Path to the LanceDB database
#             embedding_model: Name of the embedding model to use
#         """
#         self.db_path = db_path
#         self.embedding_model = embedding_model
#         self.storage = None

#         try:
#             # Initialize the unified storage
#             self.storage = UnifiedStorage(db_path=db_path)
#             logger.info(f"Connected to LanceDB at {db_path}")
#         except Exception as e:
#             logger.error(f"Error connecting to LanceDB: {e}")
#             raise

#     def search(
#         self,
#         query: str,
#         project_id: str = None,
#         limit: int = 10,
#         threshold: float = 0.0
#     ) -> List[Dict[str, Any]]:
#         """Search for code chunks using a text query.

#         Args:
#             query: Text query
#             project_id: Project ID to filter results
#             limit: Maximum number of results to return
#             threshold: Minimum similarity score threshold

#         Returns:
#             List of search results
#         """
#         try:
#             if not self.storage:
#                 logger.error("Storage not initialized")
#                 return []

#             # Search for code chunks
#             results = self.storage.search_code_chunks(
#                 query=query,
#                 limit=limit,
#                 filters={"project_id": project_id} if project_id else None
#             )

#             # Filter results by threshold
#             if threshold > 0:
#                 results = [r for r in results if r.get("score", 0) >= threshold]

#             return results

#         except Exception as e:
#             logger.error(f"Error searching for code chunks: {e}")
#             return []

#     def search_with_embedding(
#         self,
#         embedding: List[float],
#         project_id: str = None,
#         limit: int = 10,
#         threshold: float = 0.0
#     ) -> List[Dict[str, Any]]:
#         """Search for code chunks using an embedding vector.

#         Args:
#             embedding: Embedding vector
#             project_id: Project ID to filter results
#             limit: Maximum number of results to return
#             threshold: Minimum similarity score threshold

#         Returns:
#             List of search results
#         """
#         try:
#             if not self.storage:
#                 logger.error("Storage not initialized")
#                 return []

#             # Search for code chunks
#             results = self.storage.search_code_chunks_by_vector(
#                 embedding=embedding,
#                 limit=limit,
#                 filters={"project_id": project_id} if project_id else None
#             )

#             # Filter results by threshold
#             if threshold > 0:
#                 results = [r for r in results if r.get("score", 0) >= threshold]

#             return results

#         except Exception as e:
#             logger.error(f"Error searching for code chunks: {e}")
#             return []

#     def multi_query_search(
#         self,
#         queries: List[str],
#         project_id: str = None,
#         limit_per_query: int = 5,
#         total_limit: int = 20,
#         threshold: float = 0.0
#     ) -> List[Dict[str, Any]]:
#         """Search for code chunks using multiple queries.

#         Args:
#             queries: List of text queries
#             project_id: Project ID to filter results
#             limit_per_query: Maximum number of results per query
#             total_limit: Maximum total number of results
#             threshold: Minimum similarity score threshold

#         Returns:
#             List of search results
#         """
#         try:
#             if not self.storage:
#                 logger.error("Storage not initialized")
#                 return []

#             all_results = []
#             seen_node_ids = set()

#             # Search for each query
#             for query in queries:
#                 # Search for code chunks
#                 results = self.search(
#                     query=query,
#                     project_id=project_id,
#                     limit=limit_per_query,
#                     threshold=threshold
#                 )

#                 # Add unique results
#                 for result in results:
#                     node_id = result.get("node_id")
#                     if node_id and node_id not in seen_node_ids:
#                         all_results.append(result)
#                         seen_node_ids.add(node_id)

#             # Sort by score and limit the total number of results
#             all_results.sort(key=lambda x: x.get("score", 0), reverse=True)
#             return all_results[:total_limit]

#         except Exception as e:
#             logger.error(f"Error performing multi-query search: {e}")
#             return []

#     def get_chunk_by_id(self, node_id: str) -> Dict[str, Any]:
#         """Get a code chunk by its ID.

#         Args:
#             node_id: Node ID

#         Returns:
#             Code chunk or empty dict if not found
#         """
#         try:
#             if not self.storage:
#                 logger.error("Storage not initialized")
#                 return {}

#             # Get the code chunk
#             chunk = self.storage.get_code_chunk(node_id)
#             return chunk or {}

#         except Exception as e:
#             logger.error(f"Error getting code chunk: {e}")
#             return {}

#     def get_related_chunks(
#         self,
#         node_id: str,
#         relationship_types: List[str] = None,
#         limit: int = 10
#     ) -> List[Dict[str, Any]]:
#         """Get related code chunks.

#         Args:
#             node_id: Node ID
#             relationship_types: Types of relationships to include
#             limit: Maximum number of results to return

#         Returns:
#             List of related code chunks
#         """
#         try:
#             if not self.storage:
#                 logger.error("Storage not initialized")
#                 return []

#             # Get related chunks
#             related_chunks = self.storage.get_related_chunks(
#                 node_id=node_id,
#                 relationship_types=relationship_types,
#                 limit=limit
#             )

#             return related_chunks

#         except Exception as e:
#             logger.error(f"Error getting related chunks: {e}")
#             return []

#     def close(self):
#         """Close the database connection."""
#         try:
#             if self.storage:
#                 self.storage.close()
#                 logger.info("Closed database connection")
#         except Exception as e:
#             logger.error(f"Error closing database connection: {e}")


# # Example usage
# if __name__ == "__main__":
#     import argparse

#     parser = argparse.ArgumentParser(description="Search for code chunks")
#     parser.add_argument("--query", required=True, help="Search query")
#     parser.add_argument("--project-id", help="Project ID to filter results")
#     parser.add_argument("--limit", type=int, default=10, help="Maximum number of results")
#     parser.add_argument("--db-path", default=".lancedb", help="Path to the LanceDB database")
#     args = parser.parse_args()

#     # Initialize vector search
#     search = VectorSearch(db_path=args.db_path)

#     # Search for code chunks
#     results = search.search(
#         query=args.query,
#         project_id=args.project_id,
#         limit=args.limit
#     )

#     # Print results
#     print(f"Found {len(results)} results for query: {args.query}")
#     for i, result in enumerate(results, 1):
#         print(f"\nResult {i}:")
#         print(f"  Score: {result.get('score', 0):.4f}")
#         print(f"  Node ID: {result.get('node_id', 'Unknown')}")
#         print(f"  Name: {result.get('name', 'Unknown')}")
#         print(f"  Type: {result.get('chunk_type', 'Unknown')}")
#         print(f"  File: {result.get('file_path', 'Unknown')}")
#         print(f"  Lines: {result.get('start_line', 0)}-{result.get('end_line', 0)}")

#         # Print a snippet of the content
#         content = result.get('content', '')
#         if len(content) > 100:
#             content = content[:100] + "..."
#         print(f"  Content: {content}")

#     # Close the connection
#     search.close()


# Edit the vector_search.py file to enhance its capabilities
"""
Vector Search module.

This module provides functionality for vector search with enhanced relevance scoring.
"""

import os
import sys
import logging
from typing import Dict, List, Any, Optional
import re
import math
from collections import Counter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Try to import LanceDB
try:
    import lancedb
    has_lancedb = True
except ImportError:
    has_lancedb = False
    logger.warning("LanceDB not installed. Vector search will not work.")

# Try to import tantivy for full text search
try:
    import tantivy
    has_tantivy = True
except ImportError:
    has_tantivy = False
    logger.warning("tantivy-py not installed. Full text search will not be available.")

class VectorSearch:
    """Enhanced vector search implementation."""

    def __init__(self, db_path="/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/.lancedb"):
        """Initialize the vector search.

        Args:
            db_path: Path to the LanceDB database
        """
        self.db_path = db_path
        self.db = None

        # Connect to the database
        if has_lancedb:
            try:
                self.db = lancedb.connect(db_path)
                logger.info(f"Connected to LanceDB at {db_path}")
            except Exception as e:
                logger.error(f"Error connecting to LanceDB: {e}")
                raise

    def preprocess_query(self, query: str) -> str:
        """Preprocess the query to improve search results.

        Args:
            query: Original query

        Returns:
            Preprocessed query
        """
        # Remove common words that don't add much meaning
        stopwords = {"a", "an", "the", "and", "or", "but", "is", "are", "was", "were",
                    "be", "been", "being", "in", "on", "at", "to", "for", "with", "by",
                    "about", "against", "between", "into", "through", "during", "before",
                    "after", "above", "below", "from", "up", "down", "of", "off", "over",
                    "under", "again", "further", "then", "once", "here", "there", "when",
                    "where", "why", "how", "all", "any", "both", "each", "few", "more",
                    "most", "other", "some", "such", "no", "nor", "not", "only", "own",
                    "same", "so", "than", "too", "very", "s", "t", "can", "will", "just",
                    "don", "should", "now"}

        # Split the query into words
        words = query.lower().split()

        # Remove stopwords
        filtered_words = [word for word in words if word not in stopwords]

        # If too many words were removed, keep some of the original words
        if len(filtered_words) < 3 and len(words) > 3:
            # Keep the first 3 words
            filtered_words = words[:3]

        # Join the words back into a string
        preprocessed_query = " ".join(filtered_words)

        return preprocessed_query

    def extract_key_terms(self, query: str) -> List[str]:
        """Extract key terms from the query.

        Args:
            query: Search query

        Returns:
            List of key terms
        """
        # Split the query into words
        words = query.lower().split()

        # Remove common words
        stopwords = {"a", "an", "the", "and", "or", "but", "is", "are", "was", "were",
                    "be", "been", "being", "in", "on", "at", "to", "for", "with", "by",
                    "about", "against", "between", "into", "through", "during", "before",
                    "after", "above", "below", "from", "up", "down", "of", "off", "over",
                    "under", "again", "further", "then", "once", "here", "there", "when",
                    "where", "why", "how", "all", "any", "both", "each", "few", "more",
                    "most", "other", "some", "such", "no", "nor", "not", "only", "own",
                    "same", "so", "than", "too", "very", "s", "t", "can", "will", "just",
                    "don", "should", "now"}

        # Filter out stopwords and short words
        key_terms = [word for word in words if word not in stopwords and len(word) > 2]

        # Extract potential code terms (camelCase, PascalCase, snake_case)
        code_term_pattern = r'\b([a-z]+[A-Z][a-zA-Z]*|[A-Z][a-z]+[A-Z][a-zA-Z]*|[a-z]+_[a-z]+)\b'
        code_terms = re.findall(code_term_pattern, query)

        # Add code terms to key terms
        key_terms.extend(code_terms)

        # Remove duplicates
        key_terms = list(set(key_terms))

        return key_terms

    def calculate_tf_idf_score(self, content: str, query_terms: List[str], all_contents: List[str]) -> float:
        """Calculate TF-IDF score for content based on query terms.

        Args:
            content: Content to score
            query_terms: List of query terms
            all_contents: List of all contents for IDF calculation

        Returns:
            TF-IDF score
        """
        # Convert content to lowercase for case-insensitive matching
        content_lower = content.lower()

        # Calculate term frequency (TF)
        content_words = content_lower.split()
        content_word_count = len(content_words)

        # Count occurrences of each query term
        term_counts = {}
        for term in query_terms:
            term_lower = term.lower()
            term_counts[term] = content_lower.count(term_lower)

        # Calculate TF for each term
        tf_scores = {}
        for term, count in term_counts.items():
            tf_scores[term] = count / max(1, content_word_count)

        # Calculate inverse document frequency (IDF)
        idf_scores = {}
        num_docs = len(all_contents)

        for term in query_terms:
            term_lower = term.lower()
            doc_count = sum(1 for doc in all_contents if term_lower in doc.lower())
            idf_scores[term] = math.log(num_docs / max(1, doc_count))

        # Calculate TF-IDF score
        tf_idf_score = sum(tf_scores[term] * idf_scores[term] for term in query_terms)

        return tf_idf_score

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for code chunks with enhanced relevance scoring.

        Args:
            query: Search query
            limit: Maximum number of results to return

        Returns:
            List of search results
        """
        try:
            # Check if LanceDB is available
            if not has_lancedb or not self.db:
                logger.error("LanceDB not available")
                return []

            # Get the table names
            tables = self.db.table_names()

            # If no tables, return empty results
            if not tables:
                logger.warning("No tables found in the database")
                return []

            # Use the first table (usually "code_chunks")
            table_name = tables[0]

            # Open the table
            table = self.db.open_table(table_name)

            # Preprocess the query
            preprocessed_query = self.preprocess_query(query)
            logger.info(f"Preprocessed query: '{preprocessed_query}'")

            # Extract key terms
            key_terms = self.extract_key_terms(query)
            logger.info(f"Key terms: {key_terms}")

            # Try different search approaches
            results = []

            # Approach 1: Try vector search
            try:
                # Try to use the vector search with explicit vector column name
                try:
                    # First try with 'embedding' as the vector column name
                    vector_results = table.search(preprocessed_query, vector_column_name="embedding").limit(limit * 2).to_list()
                    results.extend(vector_results)
                    logger.info(f"Vector search with 'embedding' column found {len(vector_results)} results")
                except Exception as e1:
                    logger.warning(f"Vector search with 'embedding' column failed: {e1}")
                    try:
                        # Then try with 'vector' as the vector column name
                        vector_results = table.search(preprocessed_query, vector_column_name="vector").limit(limit * 2).to_list()
                        results.extend(vector_results)
                        logger.info(f"Vector search with 'vector' column found {len(vector_results)} results")
                    except Exception as e2:
                        logger.warning(f"Vector search with 'vector' column failed: {e2}")
                        # Finally try the default column name
                        vector_results = table.search(preprocessed_query).limit(limit * 2).to_list()
                        results.extend(vector_results)
                        logger.info(f"Vector search with default column found {len(vector_results)} results")
            except Exception as e:
                logger.warning(f"All vector search attempts failed: {e}")

            # Approach 2: Try enhanced text search if vector search didn't work or returned few results
            if len(results) < limit:
                try:
                    # Get all rows
                    all_rows = table.to_pandas()

                    # Get all contents for IDF calculation
                    all_contents = all_rows['content'].tolist() if 'content' in all_rows.columns else []

                    # Score each row based on TF-IDF
                    scored_rows = []
                    for _, row in all_rows.iterrows():
                        content = str(row.get('content', ''))

                        # Calculate TF-IDF score
                        tf_idf_score = self.calculate_tf_idf_score(content, key_terms, all_contents)

                        # Only include rows with a positive score
                        if tf_idf_score > 0:
                            # Create a copy of the row as a dict
                            row_dict = row.to_dict()

                            # Add a score field
                            row_dict['score'] = tf_idf_score

                            scored_rows.append(row_dict)

                    # Sort by score (descending)
                    scored_rows.sort(key=lambda x: x.get('score', 0), reverse=True)

                    # Take the top results
                    text_search_results = scored_rows[:limit]

                    # Add to results if not already included
                    for result in text_search_results:
                        if result not in results:
                            results.append(result)

                    logger.info(f"Enhanced text search found {len(text_search_results)} results")
                except Exception as e:
                    logger.warning(f"Enhanced text search failed: {e}")

            # Limit the final results
            results = results[:limit]

            # If no results were found, try a more lenient search
            if not results:
                try:
                    # Get all rows
                    all_rows = table.to_pandas()

                    # Filter rows that contain any of the query terms
                    query_terms = query.lower().split()

                    # Score each row based on how many query terms it contains
                    scored_rows = []
                    for _, row in all_rows.iterrows():
                        content = str(row.get('content', '')).lower()

                        # Check if any query term is in the content
                        if any(term in content for term in query_terms):
                            # Create a copy of the row as a dict
                            row_dict = row.to_dict()

                            # Add a score field (simple count of matching terms)
                            row_dict['score'] = sum(1 for term in query_terms if term in content) / len(query_terms)

                            scored_rows.append(row_dict)

                    # Sort by score (descending)
                    scored_rows.sort(key=lambda x: x.get('score', 0), reverse=True)

                    # Take the top results
                    results.extend(scored_rows[:limit])

                    logger.info(f"Lenient text search found {len(scored_rows[:limit])} results")
                except Exception as e:
                    logger.warning(f"Lenient text search failed: {e}")

            return results

        except Exception as e:
            logger.error(f"Error searching for code chunks: {e}")
            return []

    def close(self):
        """Close the database connection."""
        # Nothing to do for LanceDB as it doesn't have an explicit close method
        logger.info("Closed database connection")
