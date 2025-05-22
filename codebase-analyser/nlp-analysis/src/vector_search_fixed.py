"""
Vector Search module (Fixed version).

This module provides functionality for vector search with enhanced relevance scoring,
without relying on tantivy for full-text search.
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

class VectorSearch:
    """Enhanced vector search implementation without tantivy dependency."""
    
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
                # This will use the vector search if the table has a vector column
                vector_results = table.search(preprocessed_query).limit(limit * 2).to_list()
                results.extend(vector_results)
                logger.info(f"Vector search found {len(vector_results)} results")
            except Exception as e:
                logger.warning(f"Vector search failed: {e}")
            
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
            
            return results
        
        except Exception as e:
            logger.error(f"Error searching for code chunks: {e}")
            return []
    
    def close(self):
        """Close the database connection."""
        # Nothing to do for LanceDB as it doesn't have an explicit close method
        logger.info("Closed database connection")
