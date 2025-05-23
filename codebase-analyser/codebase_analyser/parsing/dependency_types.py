"""
Dependency types and constants for code chunk dependency analysis.
"""

from enum import Enum, auto
from typing import Dict, List, Set, Optional, Any


class DependencyType(Enum):
    """Types of dependencies between code chunks."""

    IMPORTS = auto()       # Import dependency
    EXTENDS = auto()       # Inheritance dependency
    IMPLEMENTS = auto()    # Interface implementation
    CALLS = auto()         # Method call dependency
    USES = auto()          # Variable/field usage
    CREATES = auto()       # Object creation
    THROWS = auto()        # Exception dependency
    CATCHES = auto()       # Exception handling
    OVERRIDES = auto()     # Method override
    ANNOTATES = auto()     # Annotation dependency
    CONTAINS = auto()      # Container relationship (class contains method)
    UNKNOWN = auto()       # Unknown dependency type

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        return self.name.lower().replace('_', ' ')

    @classmethod
    def get_description(cls, dep_type) -> str:
        """Get a human-readable description of a dependency type."""
        descriptions = {
            cls.IMPORTS: "Import dependency",
            cls.EXTENDS: "Inheritance dependency",
            cls.IMPLEMENTS: "Interface implementation",
            cls.CALLS: "Method call dependency",
            cls.USES: "Variable/field usage",
            cls.CREATES: "Object creation",
            cls.THROWS: "Exception dependency",
            cls.CATCHES: "Exception handling",
            cls.OVERRIDES: "Method override",
            cls.ANNOTATES: "Annotation dependency",
            cls.CONTAINS: "Container relationship",
            cls.UNKNOWN: "Unknown dependency type"
        }
        return descriptions.get(dep_type, "Unknown dependency type")


class DependencyLocation:
    """Represents a location of a dependency in code."""

    def __init__(
        self,
        line: int,
        column: Optional[int] = None,
        snippet: Optional[str] = None
    ):
        """Initialize a dependency location.

        Args:
            line: Line number (1-based)
            column: Column number (0-based)
            snippet: Code snippet containing the dependency
        """
        self.line = line
        self.column = column
        self.snippet = snippet

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {"line": self.line}
        if self.column is not None:
            result["column"] = self.column
        if self.snippet:
            result["snippet"] = self.snippet
        return result


class Dependency:
    """Represents a dependency between two code chunks."""

    def __init__(
        self,
        source_id: str,
        target_id: str,
        dep_type: DependencyType,
        strength: float = 1.0,
        locations: Optional[List[DependencyLocation]] = None,
        is_direct: bool = True,
        is_required: bool = True,
        description: Optional[str] = None,
        # New fields for enhanced relationship tracking
        frequency: int = 1,
        is_bidirectional: bool = False,
        group_id: Optional[str] = None,
        is_transitive: bool = False,
        transitive_path_length: int = 0,
        is_inferred: bool = False,
        inference_confidence: float = 1.0
    ):
        """Initialize a dependency.

        Args:
            source_id: ID of the source chunk
            target_id: ID of the target chunk
            dep_type: Type of dependency
            strength: Strength of the dependency (0.0 to 1.0)
            locations: Locations of the dependency in code
            is_direct: Whether this is a direct dependency
            is_required: Whether this dependency is required for compilation
            description: Human-readable description of the dependency
            frequency: How many times this relationship occurs
            is_bidirectional: Whether the relationship is bidirectional
            group_id: ID of the group/package/module this relationship belongs to
            is_transitive: Whether this is a transitive relationship
            transitive_path_length: Length of the transitive path (if transitive)
            is_inferred: Whether this relationship was inferred rather than explicit
            inference_confidence: Confidence score for inferred relationships (0.0 to 1.0)
        """
        self.source_id = source_id
        self.target_id = target_id
        self.type = dep_type
        self.strength = max(0.0, min(1.0, strength))  # Clamp to [0.0, 1.0]
        self.locations = locations or []
        self.is_direct = is_direct
        self.is_required = is_required
        self.description = description or DependencyType.get_description(dep_type)

        # Initialize new fields
        self.frequency = frequency
        self.is_bidirectional = is_bidirectional
        self.group_id = group_id
        self.is_transitive = is_transitive
        self.transitive_path_length = transitive_path_length
        self.is_inferred = is_inferred
        self.inference_confidence = max(0.0, min(1.0, inference_confidence))  # Clamp to [0.0, 1.0]

    def add_location(self, line: int, column: Optional[int] = None, snippet: Optional[str] = None) -> None:
        """Add a location to this dependency.

        Args:
            line: Line number (1-based)
            column: Column number (0-based)
            snippet: Code snippet containing the dependency
        """
        self.locations.append(DependencyLocation(line, column, snippet))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "type": self.type.name,
            "strength": self.strength,
            "locations": [loc.to_dict() for loc in self.locations],
            "is_direct": self.is_direct,
            "is_required": self.is_required,
            "description": self.description,
            # New fields
            "frequency": self.frequency,
            "is_bidirectional": self.is_bidirectional,
            "group_id": self.group_id,
            "is_transitive": self.is_transitive,
            "transitive_path_length": self.transitive_path_length,
            "is_inferred": self.is_inferred,
            "inference_confidence": self.inference_confidence
        }
