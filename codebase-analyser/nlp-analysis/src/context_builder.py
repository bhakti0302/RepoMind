"""
Context Builder module.

This module provides functionality for building context windows from search results.
"""

import os
import sys
import logging
from typing import Dict, List, Any, Optional, Union, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class ContextBuilder:
    """Builder for context windows from search results."""
    
    def __init__(
        self,
        max_context_length: int = 4000,
        include_metadata: bool = True,
        format_type: str = "markdown"
    ):
        """Initialize the context builder.
        
        Args:
            max_context_length: Maximum length of the context in tokens
            include_metadata: Whether to include metadata in the context
            format_type: Format type for the context (markdown, text, code)
        """
        self.max_context_length = max_context_length
        self.include_metadata = include_metadata
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
    
    def _format_chunk_metadata(self, chunk: Dict[str, Any]) -> str:
        """Format metadata for a code chunk.
        
        Args:
            chunk: Code chunk
            
        Returns:
            Formatted metadata
        """
        chunk_type = chunk.get("chunk_type", "Unknown")
        name = chunk.get("name", "Unknown")
        file_path = chunk.get("file_path", "Unknown")
        start_line = chunk.get("start_line", 0)
        end_line = chunk.get("end_line", 0)
        
        if self.format_type == "markdown":
            return f"**{chunk_type.upper()}**: `{name}`  \n**File**: `{file_path}` (Lines {start_line}-{end_line})\n\n"
        elif self.format_type == "code":
            return f"// {chunk_type.upper()}: {name}\n// FILE: {file_path} (Lines {start_line}-{end_line})\n\n"
        else:  # text
            return f"{chunk_type.upper()}: {name}\nFILE: {file_path} (Lines {start_line}-{end_line})\n\n"
    
    def _format_chunk_content(self, chunk: Dict[str, Any]) -> str:
        """Format content for a code chunk.
        
        Args:
            chunk: Code chunk
            
        Returns:
            Formatted content
        """
        content = chunk.get("content", "")
        language = chunk.get("language", "").lower()
        
        if not content:
            return ""
        
        if self.format_type == "markdown":
            # Format as markdown code block
            return f"```{language}\n{content}\n```\n\n"
        elif self.format_type == "code":
            # Format as raw code
            return f"{content}\n\n"
        else:  # text
            # Format as plain text
            return f"{content}\n\n"
    
    def _format_chunk(self, chunk: Dict[str, Any]) -> str:
        """Format a code chunk for inclusion in the context.
        
        Args:
            chunk: Code chunk
            
        Returns:
            Formatted chunk text
        """
        formatted_text = ""
        
        # Add metadata if requested
        if self.include_metadata:
            formatted_text += self._format_chunk_metadata(chunk)
        
        # Add content
        formatted_text += self._format_chunk_content(chunk)
        
        return formatted_text
    
    def build_context(
        self,
        chunks: List[Dict[str, Any]],
        query: str = None
    ) -> Dict[str, Any]:
        """Build a context window from code chunks.
        
        Args:
            chunks: List of code chunks
            query: Original query (for context)
            
        Returns:
            Dictionary containing the context and metadata
        """
        try:
            # Initialize context
            context = ""
            context_chunks = []
            total_tokens = 0
            
            # Add query to context if provided
            if query:
                if self.format_type == "markdown":
                    context += f"## Query\n\n{query}\n\n## Relevant Code\n\n"
                elif self.format_type == "code":
                    context += f"// QUERY: {query}\n\n"
                else:  # text
                    context += f"QUERY: {query}\n\n"
                
                # Estimate tokens for the query
                query_tokens = self._estimate_tokens(context)
                total_tokens += query_tokens
            
            # Process each chunk
            for chunk in chunks:
                # Format the chunk
                chunk_text = self._format_chunk(chunk)
                chunk_tokens = self._estimate_tokens(chunk_text)
                
                # Check if adding this chunk would exceed the maximum context length
                if total_tokens + chunk_tokens > self.max_context_length:
                    # Add a note about truncation
                    if self.format_type == "markdown":
                        context += "\n\n*Note: Some content was truncated due to context length limitations.*"
                    elif self.format_type == "code":
                        context += "\n\n// Note: Some content was truncated due to context length limitations."
                    else:  # text
                        context += "\n\nNote: Some content was truncated due to context length limitations."
                    break
                
                # Add the chunk to the context
                context += chunk_text
                context_chunks.append(chunk)
                total_tokens += chunk_tokens
            
            return {
                "context": context,
                "context_chunks": context_chunks,
                "total_tokens": total_tokens,
                "format_type": self.format_type,
                "truncated": len(context_chunks) < len(chunks)
            }
        
        except Exception as e:
            logger.error(f"Error building context: {e}")
            return {
                "context": "",
                "context_chunks": [],
                "total_tokens": 0,
                "format_type": self.format_type,
                "truncated": False,
                "error": str(e)
            }
    
    def build_hierarchical_context(
        self,
        chunks: List[Dict[str, Any]],
        query: str = None
    ) -> Dict[str, Any]:
        """Build a hierarchical context window from code chunks.
        
        Args:
            chunks: List of code chunks
            query: Original query (for context)
            
        Returns:
            Dictionary containing the context and metadata
        """
        try:
            # Group chunks by type
            chunks_by_type = {}
            
            for chunk in chunks:
                chunk_type = chunk.get("chunk_type", "unknown")
                
                if chunk_type not in chunks_by_type:
                    chunks_by_type[chunk_type] = []
                
                chunks_by_type[chunk_type].append(chunk)
            
            # Define the order of chunk types
            type_order = [
                "package", "file", "class", "interface",
                "method", "field", "import", "comment"
            ]
            
            # Sort chunk types by the defined order
            sorted_types = sorted(
                chunks_by_type.keys(),
                key=lambda x: type_order.index(x) if x in type_order else len(type_order)
            )
            
            # Initialize context
            context = ""
            context_chunks = []
            total_tokens = 0
            
            # Add query to context if provided
            if query:
                if self.format_type == "markdown":
                    context += f"## Query\n\n{query}\n\n## Relevant Code\n\n"
                elif self.format_type == "code":
                    context += f"// QUERY: {query}\n\n"
                else:  # text
                    context += f"QUERY: {query}\n\n"
                
                # Estimate tokens for the query
                query_tokens = self._estimate_tokens(context)
                total_tokens += query_tokens
            
            # Process each chunk type
            for chunk_type in sorted_types:
                # Add section header
                if self.format_type == "markdown":
                    context += f"### {chunk_type.capitalize()}s\n\n"
                elif self.format_type == "code":
                    context += f"// {chunk_type.upper()}S\n\n"
                else:  # text
                    context += f"{chunk_type.upper()}S\n\n"
                
                # Process chunks of this type
                for chunk in chunks_by_type[chunk_type]:
                    # Format the chunk
                    chunk_text = self._format_chunk(chunk)
                    chunk_tokens = self._estimate_tokens(chunk_text)
                    
                    # Check if adding this chunk would exceed the maximum context length
                    if total_tokens + chunk_tokens > self.max_context_length:
                        # Add a note about truncation
                        if self.format_type == "markdown":
                            context += "\n\n*Note: Some content was truncated due to context length limitations.*"
                        elif self.format_type == "code":
                            context += "\n\n// Note: Some content was truncated due to context length limitations."
                        else:  # text
                            context += "\n\nNote: Some content was truncated due to context length limitations."
                        break
                    
                    # Add the chunk to the context
                    context += chunk_text
                    context_chunks.append(chunk)
                    total_tokens += chunk_tokens
                
                # Check if we've exceeded the maximum context length
                if total_tokens > self.max_context_length:
                    break
            
            return {
                "context": context,
                "context_chunks": context_chunks,
                "total_tokens": total_tokens,
                "format_type": self.format_type,
                "truncated": len(context_chunks) < len(chunks)
            }
        
        except Exception as e:
            logger.error(f"Error building hierarchical context: {e}")
            return {
                "context": "",
                "context_chunks": [],
                "total_tokens": 0,
                "format_type": self.format_type,
                "truncated": False,
                "error": str(e)
            }


# Example usage
if __name__ == "__main__":
    # Create a context builder
    builder = ContextBuilder(
        max_context_length=2000,
        include_metadata=True,
        format_type="markdown"
    )
    
    # Example chunks
    chunks = [
        {
            "node_id": "1",
            "chunk_type": "class",
            "name": "UserService",
            "file_path": "src/main/java/com/example/service/UserService.java",
            "start_line": 10,
            "end_line": 50,
            "language": "java",
            "content": "public class UserService {\n    private final UserRepository userRepository;\n\n    public UserService(UserRepository userRepository) {\n        this.userRepository = userRepository;\n    }\n\n    public User authenticate(String username, String password) {\n        // Implementation\n    }\n}"
        },
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
    
    # Build the context
    context_result = builder.build_context(chunks, query="How does user authentication work?")
    
    # Print the context
    print(context_result["context"])
    print(f"\nTotal tokens: {context_result['total_tokens']}")
    print(f"Truncated: {context_result['truncated']}")
    
    # Build a hierarchical context
    hierarchical_context = builder.build_hierarchical_context(chunks, query="How does user authentication work?")
    
    # Print the hierarchical context
    print("\n\nHierarchical Context:")
    print(hierarchical_context["context"])
