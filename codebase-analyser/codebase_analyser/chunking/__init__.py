"""
Code chunking module for dividing code into semantically meaningful chunks.
"""

from .code_chunk import CodeChunk
from .dependency_types import DependencyType, Dependency, DependencyLocation
from .dependency_analyzer import DependencyAnalyzer, DependencyGraph

__all__ = [
    'CodeChunk',
    'DependencyType',
    'Dependency',
    'DependencyLocation',
    'DependencyAnalyzer',
    'DependencyGraph'
]
