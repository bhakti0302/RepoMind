"""
Code chunk module for representing code chunks.
"""

from typing import Dict, List, Set, Optional, Any, Tuple
from pathlib import Path


class CodeChunk:
    """Represents a chunk of code with metadata."""
    
    def __init__(
        self,
        node_id: str,
        chunk_type: str,
        content: str,
        file_path: str,
        start_line: int,
        end_line: int,
        language: str,
        name: Optional[str] = None,
        qualified_name: Optional[str] = None
    ):
        """Initialize a code chunk.
        
        Args:
            node_id: Unique identifier for the chunk
            chunk_type: Type of the chunk (file, class, method, etc.)
            content: Code content
            file_path: Path to the file containing the chunk
            start_line: Start line number (1-based)
            end_line: End line number (1-based)
            language: Programming language
            name: Name of the chunk
            qualified_name: Fully qualified name of the chunk
        """
        self.node_id = node_id
        self.chunk_type = chunk_type
        self.content = content
        self.file_path = file_path
        self.start_line = start_line
        self.end_line = end_line
        self.language = language
        self.name = name
        self.qualified_name = qualified_name
        
        # Additional properties
        self.parent = None
        self.children = []
        self.context = {}
        self.metadata = {}
    
    def add_child(self, child: 'CodeChunk') -> None:
        """Add a child chunk.
        
        Args:
            child: Child chunk to add
        """
        self.children.append(child)
        child.parent = self
    
    def get_descendants(self) -> List['CodeChunk']:
        """Get all descendants of this chunk.
        
        Returns:
            List of descendant chunks
        """
        descendants = []
        for child in self.children:
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation.
        
        Returns:
            Dictionary representation of the chunk
        """
        result = {
            "node_id": self.node_id,
            "chunk_type": self.chunk_type,
            "content": self.content,
            "file_path": self.file_path,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "language": self.language,
            "name": self.name,
            "qualified_name": self.qualified_name,
            "context": self.context,
            "metadata": self.metadata
        }
        
        if self.parent:
            result["parent_id"] = self.parent.node_id
        
        return result
