"""
Context Combiner module.

This module provides functionality for combining context from multiple sources.
"""

import os
import sys
import logging
from typing import Dict, List, Any, Optional, Union, Tuple, Set

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class ContextCombiner:
    """Combiner for context from multiple sources."""
    
    def __init__(
        self,
        max_context_length: int = 4000,
        format_type: str = "markdown"
    ):
        """Initialize the context combiner.
        
        Args:
            max_context_length: Maximum length of the combined context in tokens
            format_type: Format type for the context (markdown, text, code)
        """
        self.max_context_length = max_context_length
        self.format_type = format_type
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate the number of tokens in a text.
        
        Args:
            text: Input text
            
        Returns:
            Estimated number of tokens
        """
        # Simple estimation: 1 token ≈ 4 characters
        return len(text) // 4
    
    def _format_section_header(self, title: str) -> str:
        """Format a section header.
        
        Args:
            title: Section title
            
        Returns:
            Formatted section header
        """
        if self.format_type == "markdown":
            return f"## {title}\n\n"
        elif self.format_type == "code":
            return f"// {title.upper()}\n// {'-' * len(title)}\n\n"
        else:  # text
            return f"{title.upper()}\n{'-' * len(title)}\n\n"
    
    def _format_subsection_header(self, title: str) -> str:
        """Format a subsection header.
        
        Args:
            title: Subsection title
            
        Returns:
            Formatted subsection header
        """
        if self.format_type == "markdown":
            return f"### {title}\n\n"
        elif self.format_type == "code":
            return f"// {title}\n\n"
        else:  # text
            return f"{title}\n{'-' * len(title)}\n\n"
    
    def deduplicate_chunks(
        self,
        chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Deduplicate chunks based on content similarity.
        
        Args:
            chunks: List of chunks
            
        Returns:
            Deduplicated list of chunks
        """
        try:
            # Initialize deduplicated chunks
            deduplicated_chunks = []
            
            # Track seen node IDs and content hashes
            seen_node_ids = set()
            seen_content_hashes = set()
            
            # Process each chunk
            for chunk in chunks:
                node_id = chunk.get("node_id")
                content = chunk.get("content", "")
                
                # Skip empty content
                if not content:
                    continue
                
                # Skip if node ID already seen
                if node_id and node_id in seen_node_ids:
                    continue
                
                # Create a simple hash of the content (first 100 chars + length)
                content_hash = f"{content[:100]}_{len(content)}"
                
                # Skip if content hash already seen
                if content_hash in seen_content_hashes:
                    continue
                
                # Add to deduplicated chunks
                deduplicated_chunks.append(chunk)
                
                # Mark as seen
                if node_id:
                    seen_node_ids.add(node_id)
                seen_content_hashes.add(content_hash)
            
            return deduplicated_chunks
        
        except Exception as e:
            logger.error(f"Error deduplicating chunks: {e}")
            return chunks
    
    def combine_contexts(
        self,
        contexts: Dict[str, List[Dict[str, Any]]],
        query: str = None
    ) -> Dict[str, Any]:
        """Combine contexts from multiple sources.
        
        Args:
            contexts: Dictionary mapping context type to list of chunks
            query: Original query (for context)
            
        Returns:
            Dictionary containing the combined context and metadata
        """
        try:
            # Initialize combined context
            combined_context = ""
            combined_chunks = []
            total_tokens = 0
            
            # Add query to context if provided
            if query:
                if self.format_type == "markdown":
                    combined_context += f"# Query\n\n{query}\n\n"
                elif self.format_type == "code":
                    combined_context += f"// QUERY: {query}\n\n"
                else:  # text
                    combined_context += f"QUERY: {query}\n\n"
                
                # Estimate tokens for the query
                query_tokens = self._estimate_tokens(combined_context)
                total_tokens += query_tokens
            
            # Process each context type
            for context_type, chunks in contexts.items():
                # Skip empty chunks
                if not chunks:
                    continue
                
                # Deduplicate chunks
                deduplicated_chunks = self.deduplicate_chunks(chunks)
                
                # Skip if no chunks after deduplication
                if not deduplicated_chunks:
                    continue
                
                # Format the section header
                section_header = self._format_section_header(context_type)
                section_tokens = self._estimate_tokens(section_header)
                
                # Check if adding this section would exceed the maximum context length
                if total_tokens + section_tokens > self.max_context_length:
                    # Add a note about truncation
                    if self.format_type == "markdown":
                        combined_context += "\n\n*Note: Some content was truncated due to context length limitations.*"
                    elif self.format_type == "code":
                        combined_context += "\n\n// Note: Some content was truncated due to context length limitations."
                    else:  # text
                        combined_context += "\n\nNote: Some content was truncated due to context length limitations."
                    break
                
                # Add the section header
                combined_context += section_header
                total_tokens += section_tokens
                
                # Group chunks by type
                chunks_by_type = {}
                for chunk in deduplicated_chunks:
                    chunk_type = chunk.get("chunk_type", "unknown")
                    if chunk_type not in chunks_by_type:
                        chunks_by_type[chunk_type] = []
                    chunks_by_type[chunk_type].append(chunk)
                
                # Process each chunk type
                for chunk_type, type_chunks in chunks_by_type.items():
                    # Format the subsection header
                    subsection_header = self._format_subsection_header(f"{chunk_type.capitalize()}s")
                    subsection_tokens = self._estimate_tokens(subsection_header)
                    
                    # Check if adding this subsection would exceed the maximum context length
                    if total_tokens + subsection_tokens > self.max_context_length:
                        break
                    
                    # Add the subsection header
                    combined_context += subsection_header
                    total_tokens += subsection_tokens
                    
                    # Process each chunk
                    for chunk in type_chunks:
                        # Format the chunk
                        chunk_text = self._format_chunk(chunk)
                        chunk_tokens = self._estimate_tokens(chunk_text)
                        
                        # Check if adding this chunk would exceed the maximum context length
                        if total_tokens + chunk_tokens > self.max_context_length:
                            break
                        
                        # Add the chunk to the context
                        combined_context += chunk_text
                        combined_chunks.append(chunk)
                        total_tokens += chunk_tokens
            
            return {
                "context": combined_context,
                "context_chunks": combined_chunks,
                "total_tokens": total_tokens,
                "format_type": self.format_type,
                "truncated": sum(len(chunks) for chunks in contexts.values()) > len(combined_chunks)
            }
        
        except Exception as e:
            logger.error(f"Error combining contexts: {e}")
            return {
                "context": "",
                "context_chunks": [],
                "total_tokens": 0,
                "format_type": self.format_type,
                "truncated": False,
                "error": str(e)
            }
    
    def _format_chunk(self, chunk: Dict[str, Any]) -> str:
        """Format a chunk for inclusion in the context.
        
        Args:
            chunk: Chunk data
            
        Returns:
            Formatted chunk text
        """
        chunk_type = chunk.get("chunk_type", "Unknown")
        name = chunk.get("name", "Unknown")
        file_path = chunk.get("file_path", "Unknown")
        start_line = chunk.get("start_line", 0)
        end_line = chunk.get("end_line", 0)
        content = chunk.get("content", "")
        language = chunk.get("language", "").lower()
        
        if self.format_type == "markdown":
            # Format metadata
            metadata = f"**{chunk_type.upper()}**: `{name}`  \n"
            metadata += f"**File**: `{file_path}` (Lines {start_line}-{end_line})\n\n"
            
            # Format content
            if content:
                content_text = f"```{language}\n{content}\n```\n\n"
            else:
                content_text = "*No content available*\n\n"
            
            return metadata + content_text
        
        elif self.format_type == "code":
            # Format metadata
            metadata = f"// {chunk_type.upper()}: {name}\n"
            metadata += f"// FILE: {file_path} (Lines {start_line}-{end_line})\n\n"
            
            # Format content
            if content:
                content_text = f"{content}\n\n"
            else:
                content_text = "// No content available\n\n"
            
            return metadata + content_text
        
        else:  # text
            # Format metadata
            metadata = f"{chunk_type.upper()}: {name}\n"
            metadata += f"FILE: {file_path} (Lines {start_line}-{end_line})\n\n"
            
            # Format content
            if content:
                content_text = f"{content}\n\n"
            else:
                content_text = "No content available\n\n"
            
            return metadata + content_text


# Example usage
if __name__ == "__main__":
    # Create a context combiner
    combiner = ContextCombiner(
        max_context_length=2000,
        format_type="markdown"
    )
    
    # Example contexts
    contexts = {
        "Architectural Components": [
            {
                "node_id": "1",
                "chunk_type": "class",
                "name": "UserService",
                "file_path": "src/main/java/com/example/service/UserService.java",
                "start_line": 10,
                "end_line": 50,
                "language": "java",
                "content": "public class UserService {\n    private final UserRepository userRepository;\n\n    public UserService(UserRepository userRepository) {\n        this.userRepository = userRepository;\n    }\n\n    public User authenticate(String username, String password) {\n        // Implementation\n    }\n}"
            }
        ],
        "Implementation Details": [
            {
                "node_id": "2",
                "chunk_type": "method",
                "name": "authenticate",
                "file_path": "src/main/java/com/example/service/UserService.java",
                "start_line": 15,
                "end_line": 20,
                "language": "java",
                "content": "public User authenticate(String username, String password) {\n    User user = userRepository.findByUsername(username);\n    if (user != null && passwordEncoder.matches(password, user.getPassword())) {\n        return user;\n    }\n    return null;\n}"
            }
        ]
    }
    
    # Combine contexts
    combined_context = combiner.combine_contexts(
        contexts=contexts,
        query="How does user authentication work?"
    )
    
    # Print the combined context
    print(combined_context["context"])
    print(f"\nTotal tokens: {combined_context['total_tokens']}")
    print(f"Truncated: {combined_context['truncated']}")
