"""
CodeChunk class for representing code chunks.
"""

from typing import Dict, List, Optional, Any, Union
from pathlib import Path


class CodeChunk:
    """Class for representing code chunks."""
    
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
        """Initialize a CodeChunk.
        
        Args:
            node_id: Unique identifier for the chunk
            chunk_type: Type of the chunk (file, class, method, etc.)
            content: Content of the chunk
            file_path: Path to the file containing the chunk
            start_line: Start line of the chunk
            end_line: End line of the chunk
            language: Programming language of the chunk
            name: Name of the chunk
            qualified_name: Fully qualified name of the chunk
        """
        self.node_id = node_id
        self.chunk_type = chunk_type
        self.content = content
        self.file_path = str(file_path)
        self.start_line = start_line
        self.end_line = end_line
        self.language = language
        self.name = name or node_id
        self.qualified_name = qualified_name or name or node_id
        
        # Relationships
        self.parent = None
        self.children = []
        self.references = []
        
        # Additional data
        self.metadata = {}
        self.context = {}
    
    def add_child(self, child: 'CodeChunk') -> None:
        """Add a child chunk.
        
        Args:
            child: Child chunk to add
        """
        self.children.append(child)
        child.parent = self
    
    def add_reference(self, reference: 'CodeChunk') -> None:
        """Add a reference to another chunk.
        
        Args:
            reference: Chunk being referenced
        """
        self.references.append(reference)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the chunk to a dictionary.
        
        Returns:
            Dictionary representation of the chunk
        """
        result = {
            'node_id': self.node_id,
            'chunk_type': self.chunk_type,
            'content': self.content,
            'file_path': self.file_path,
            'start_line': self.start_line,
            'end_line': self.end_line,
            'language': self.language,
            'name': self.name,
            'qualified_name': self.qualified_name
        }
        
        # Add metadata and context if present
        if self.metadata:
            result['metadata'] = self.metadata
        if self.context:
            result['context'] = self.context
        
        # Add parent_id if present
        if self.parent:
            result['parent_id'] = self.parent.node_id
        
        # Add children_ids if present
        if self.children:
            result['children_ids'] = [child.node_id for child in self.children]
        
        # Add reference_ids if present
        if self.references:
            result['reference_ids'] = [ref.node_id for ref in self.references]
        
        return result
    
    def __repr__(self) -> str:
        """Return a string representation of the chunk."""
        return f"CodeChunk(node_id={self.node_id}, chunk_type={self.chunk_type}, name={self.name})"
