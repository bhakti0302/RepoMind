"""
AST-aware code chunking implementation.

This module provides functionality to divide code into semantically meaningful chunks
based on the AST structure, ensuring that related code stays together.
"""

from typing import Dict, List, Optional, Set, Union, Any, Tuple
from pathlib import Path
import re

from tree_sitter import Node, Tree

from ..utils.ast_utils import (
    traverse_ast, find_nodes_by_type, get_node_text,
    get_node_location, find_parent
)
from .dependency_types import DependencyType, Dependency
from .dependency_analyzer import DependencyAnalyzer, DependencyGraph

class CodeChunk:
    """Represents a semantically meaningful chunk of code with hierarchical structure."""

    def __init__(
        self,
        content: str,
        start_line: int,
        end_line: int,
        language: str,
        file_path: str,
        chunk_type: str = "generic",
        metadata: Optional[Dict[str, Any]] = None,
        parent: Optional['CodeChunk'] = None,
        node_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        name: Optional[str] = None,
        qualified_name: Optional[str] = None
    ):
        """Initialize a code chunk.

        Args:
            content: The code content of the chunk
            start_line: The starting line number (1-based)
            end_line: The ending line number (1-based)
            language: The programming language of the code
            file_path: The path to the source file
            chunk_type: The type of chunk (e.g., "class", "method", "function")
            metadata: Additional metadata about the chunk
            parent: Parent chunk in the hierarchy (if any)
            node_id: Unique identifier for the chunk
            context: Context information (imports, package, etc.)
            name: Simple name of the code element (class name, method name, etc.)
            qualified_name: Fully qualified name (package.class.method)
        """
        self.content = content
        self.start_line = start_line
        self.end_line = end_line
        self.language = language
        self.file_path = file_path
        self.chunk_type = chunk_type
        self.metadata = metadata or {}
        self.parent = parent
        self.children = []
        self.name = name
        self.qualified_name = qualified_name
        self.context = context or {}
        self.references = []  # List of chunks this chunk references
        self.referenced_by = []  # List of chunks that reference this chunk
        self.node_id = node_id or f"{file_path}:{chunk_type}:{start_line}-{end_line}"

        # If parent is provided, add this chunk as a child of the parent
        if parent:
            parent.add_child(self)

        # If name is not provided but parent is, try to generate a qualified name
        if parent and not self.qualified_name and self.name:
            if parent.qualified_name:
                self.qualified_name = f"{parent.qualified_name}.{self.name}"
            elif 'package' in self.context:
                self.qualified_name = f"{self.context['package']}.{self.name}"

    def add_child(self, child: 'CodeChunk') -> None:
        """Add a child chunk to this chunk.

        Args:
            child: The child chunk to add
        """
        if child not in self.children:
            self.children.append(child)
            # Set the parent reference in the child if it's not already set
            if child.parent is None:
                child.parent = self

    def get_ancestors(self) -> List['CodeChunk']:
        """Get all ancestors of this chunk in order (parent, grandparent, etc.).

        Returns:
            List of ancestor chunks
        """
        ancestors = []
        current = self.parent
        while current:
            ancestors.append(current)
            current = current.parent
        return ancestors

    def get_descendants(self) -> List['CodeChunk']:
        """Get all descendants of this chunk (children, grandchildren, etc.).

        Returns:
            List of descendant chunks
        """
        descendants = []
        for child in self.children:
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants

    def get_siblings(self) -> List['CodeChunk']:
        """Get all siblings of this chunk (chunks with the same parent).

        Returns:
            List of sibling chunks
        """
        if not self.parent:
            return []
        return [child for child in self.parent.children if child != self]

    def __repr__(self) -> str:
        return f"CodeChunk({self.chunk_type}, {self.file_path}, lines {self.start_line}-{self.end_line}, children: {len(self.children)})"

    def add_reference(self, target_chunk: 'CodeChunk') -> None:
        """Add a reference from this chunk to another chunk.

        Args:
            target_chunk: The chunk being referenced
        """
        if target_chunk not in self.references:
            self.references.append(target_chunk)
            # Add the reverse reference
            if self not in target_chunk.referenced_by:
                target_chunk.referenced_by.append(self)

    def get_required_context(self) -> Dict[str, Any]:
        """Get all context required for this chunk to be semantically complete.

        This includes imports, package declarations, and any other context
        needed to understand the chunk in isolation.

        Returns:
            Dictionary of context information
        """
        # Start with this chunk's context
        required_context = self.context.copy()

        # Add context from ancestors
        for ancestor in self.get_ancestors():
            for key, value in ancestor.context.items():
                if key not in required_context:
                    required_context[key] = value
                elif isinstance(value, list) and isinstance(required_context[key], list):
                    # Merge lists (e.g., imports)
                    for item in value:
                        if item not in required_context[key]:
                            required_context[key].append(item)

        return required_context

    def get_standalone_content(self) -> str:
        """Get the content of this chunk with all required context.

        This creates a version of the chunk that can be understood in isolation,
        with all necessary imports, package declarations, etc.

        Returns:
            String containing the standalone content
        """
        context = self.get_required_context()
        standalone_content = []

        # Add package declaration if present
        if 'package' in context:
            standalone_content.append(f"package {context['package']};")
            standalone_content.append("")

        # Add imports if present
        if 'imports' in context and context['imports']:
            for imp in context['imports']:
                standalone_content.append(f"import {imp};")
            standalone_content.append("")

        # Add any other context (e.g., outer class declarations)
        if 'outer_classes' in context and context['outer_classes']:
            for cls in context['outer_classes']:
                standalone_content.append(cls)
                standalone_content.append("")

        # Add the chunk content
        standalone_content.append(self.content)

        return "\n".join(standalone_content)

    def validate_structural_integrity(self) -> bool:
        """Validate that this chunk maintains structural integrity.

        Checks that the chunk is semantically complete and can be understood
        in isolation with its context.

        Returns:
            True if the chunk is structurally sound, False otherwise
        """
        # Check if the chunk has a valid type
        if not self.chunk_type:
            return False

        # Check if the chunk has content
        if not self.content:
            return False

        # For method chunks, check if they have a parent class/interface
        if self.chunk_type in ['method_declaration', 'constructor_declaration'] and not self.parent:
            return False

        # For nested chunks, check if they have the necessary context
        if self.parent and self.parent.chunk_type in ['class_declaration', 'interface_declaration']:
            if 'container_type' not in self.metadata:
                return False

        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert the chunk to a dictionary representation."""
        return {
            "node_id": self.node_id,
            "name": self.name,
            "qualified_name": self.qualified_name,
            "content": self.content,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "language": self.language,
            "file_path": self.file_path,
            "chunk_type": self.chunk_type,
            "metadata": self.metadata,
            "context": self.context,
            "line_count": self.end_line - self.start_line + 1,
            "parent_id": self.parent.node_id if self.parent else None,
            "children_ids": [child.node_id for child in self.children],
            "references": [ref.node_id for ref in self.references],
            "referenced_by": [ref.node_id for ref in self.referenced_by]
        }

class CodeChunker:
    """AST-aware code chunking implementation."""

    def __init__(self, min_chunk_size: int = 50, max_chunk_size: int = 300):
        """Initialize the code chunker.

        Args:
            min_chunk_size: Minimum number of lines for a chunk
            max_chunk_size: Maximum number of lines for a chunk
        """
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.dependency_analyzer = DependencyAnalyzer()

        # Language-specific node types for chunking
        self.chunk_node_types = {
            "java": {
                "primary": ["class_declaration", "interface_declaration", "enum_declaration"],
                "secondary": ["method_declaration", "constructor_declaration"],
                "imports": ["import_declaration"],
                "package": ["package_declaration"]
            },
            "python": {
                "primary": ["class_definition"],
                "secondary": ["function_definition"],
                "imports": ["import_statement", "import_from_statement"],
                "package": []
            },
            "javascript": {
                "primary": ["class_declaration"],
                "secondary": ["function_declaration", "method_definition", "arrow_function"],
                "imports": ["import_statement"],
                "package": []
            },
            "typescript": {
                "primary": ["class_declaration", "interface_declaration"],
                "secondary": ["function_declaration", "method_definition", "arrow_function"],
                "imports": ["import_statement"],
                "package": []
            }
        }

    def chunk_file(self, parsed_file: Dict[str, Any]) -> List[CodeChunk]:
        """Chunk a parsed file into semantically meaningful chunks.

        Args:
            parsed_file: A parsed file dictionary from the analyser

        Returns:
            List of code chunks
        """
        language = parsed_file.get('language', 'unknown')
        file_path = parsed_file.get('path', 'unknown')
        content = parsed_file.get('content', '')
        ast = parsed_file.get('ast')

        if not ast or not content:
            print(f"Warning: Cannot chunk file {file_path} - missing AST or content")
            return []

        # Get language-specific node types
        node_types = self.chunk_node_types.get(language, {
            "primary": [],
            "secondary": [],
            "imports": [],
            "package": []
        })

        # Create chunks based on the AST structure
        chunks = self._create_chunks_from_ast(
            ast,
            content.encode('utf-8'),
            language,
            file_path,
            node_types
        )

        # Add file-level metadata to chunks
        for chunk in chunks:
            # Add imports and package info if available
            if 'imports' in parsed_file:
                chunk.metadata['imports'] = parsed_file['imports']
            if 'package' in parsed_file:
                chunk.metadata['package'] = parsed_file['package']

        return chunks

    def _create_chunks_from_ast(
        self,
        ast: Tree,
        content: bytes,
        language: str,
        file_path: str,
        node_types: Dict[str, List[str]]
    ) -> List[CodeChunk]:
        """Create hierarchical chunks from the AST structure.

        Args:
            ast: The Tree-sitter AST
            content: The file content as bytes
            language: The programming language
            file_path: The path to the source file
            node_types: Dictionary of node types to use for chunking

        Returns:
            List of code chunks (top-level chunks only)
        """
        # Extract context (imports, package declarations)
        context_nodes = []
        package_name = None
        imports = []

        for context_type in ['imports', 'package']:
            for node_type in node_types.get(context_type, []):
                context_nodes.extend(find_nodes_by_type(ast.root_node, node_type))

        # Process context nodes to extract package and imports
        if context_nodes:
            # Sort by position in file
            context_nodes.sort(key=lambda n: n.start_point[0])
            for node in context_nodes:
                node_text = get_node_text(node, content)

                # Extract package name
                if node.type == 'package_declaration':
                    # Extract package name from "package com.example.test;"
                    package_match = re.search(r'package\s+([^;]+);', node_text)
                    if package_match:
                        package_name = package_match.group(1).strip()

                # Extract import statements
                elif node.type == 'import_declaration':
                    # Extract import from "import java.util.List;"
                    import_match = re.search(r'import\s+([^;]+);', node_text)
                    if import_match:
                        imports.append(import_match.group(1).strip())

        # Create file context
        file_context = {}
        if package_name:
            file_context['package'] = package_name
        if imports:
            file_context['imports'] = imports

        # Create a file-level chunk as the root of the hierarchy
        file_chunk = CodeChunk(
            content=content.decode('utf-8', errors='replace'),
            start_line=1,
            end_line=content.count(b'\n') + 1,
            language=language,
            file_path=file_path,
            chunk_type="file",
            metadata={"level": "file"},
            context=file_context,
            name=Path(file_path).stem,
            qualified_name=f"{package_name}.{Path(file_path).stem}" if package_name else Path(file_path).stem
        )

        # Create context chunks
        context_text = ""
        if context_nodes:
            for node in context_nodes:
                node_text = get_node_text(node, content)
                context_text += node_text + "\n"

                # Create a context chunk for each import/package declaration
                context_chunk = CodeChunk(
                    content=node_text,
                    start_line=node.start_point[0] + 1,  # Convert to 1-based
                    end_line=node.end_point[0] + 1,      # Convert to 1-based
                    language=language,
                    file_path=file_path,
                    chunk_type=node.type,
                    metadata={
                        "level": "context",
                        "node_type": node.type
                    },
                    parent=file_chunk,
                    context=file_context
                )

        # Find primary chunk nodes (classes, interfaces, etc.)
        primary_nodes = []
        for node_type in node_types.get('primary', []):
            primary_nodes.extend(find_nodes_by_type(ast.root_node, node_type))

        # If no primary nodes, just return the file chunk
        if not primary_nodes:
            return [file_chunk]

        # Process primary nodes (container level)
        for node in primary_nodes:
            node_text = get_node_text(node, content)
            location = get_node_location(node)

            # Extract class/interface name
            container_name = None
            if node.type in ['class_declaration', 'interface_declaration', 'enum_declaration']:
                # Find the identifier node (class/interface name)
                for child in node.children:
                    if child.type == 'identifier':
                        container_name = get_node_text(child, content).strip()
                        break

            # Create qualified name
            qualified_name = None
            if container_name and package_name:
                qualified_name = f"{package_name}.{container_name}"
            elif container_name:
                qualified_name = container_name

            # Create container context
            container_context = file_context.copy()
            if container_name:
                container_context['container_name'] = container_name

            # Extract superclass and interfaces
            extends_clause = None
            implements_clause = None
            for child in node.children:
                if child.type == 'superclass':
                    extends_clause = get_node_text(child, content).strip()
                    container_context['extends'] = extends_clause
                elif child.type == 'interfaces':
                    implements_clause = get_node_text(child, content).strip()
                    container_context['implements'] = implements_clause

            # Create a chunk for the primary node (container level)
            container_chunk = CodeChunk(
                content=node_text,
                start_line=location['start_line'] + 1,  # Convert to 1-based
                end_line=location['end_line'] + 1,      # Convert to 1-based
                language=language,
                file_path=file_path,
                chunk_type=node.type,
                metadata={
                    "context": context_text,
                    "node_type": node.type,
                    "level": "container",
                    "extends": extends_clause,
                    "implements": implements_clause
                },
                parent=file_chunk,
                context=container_context,
                name=container_name,
                qualified_name=qualified_name
            )

            # Find secondary nodes (methods, functions, etc.) within this container
            secondary_nodes = []
            for node_type in node_types.get('secondary', []):
                secondary_nodes.extend(find_nodes_by_type(node, node_type))

            if secondary_nodes:
                # Sort secondary nodes by position
                secondary_nodes.sort(key=lambda n: n.start_point[0])

                # Extract the declaration part of the container (e.g., class declaration without methods)
                declaration_end = secondary_nodes[0].start_point[0]
                declaration_text = content[node.start_byte:secondary_nodes[0].start_byte].decode('utf-8', errors='replace')

                # Create a chunk for the declaration part
                declaration_chunk = CodeChunk(
                    content=declaration_text,
                    start_line=node.start_point[0] + 1,  # Convert to 1-based
                    end_line=declaration_end + 1,        # Convert to 1-based
                    language=language,
                    file_path=file_path,
                    chunk_type=f"{node.type}_declaration",
                    metadata={
                        "is_declaration": True,
                        "node_type": node.type,
                        "level": "declaration"
                    },
                    parent=container_chunk,
                    context=container_context,
                    name=f"{container_name}_declaration" if container_name else None
                )

                # Process each secondary node (fine-grained level)
                for i, sec_node in enumerate(secondary_nodes):
                    sec_text = get_node_text(sec_node, content)
                    sec_location = get_node_location(sec_node)

                    # Extract method name
                    method_name = None
                    for child in sec_node.children:
                        if child.type == 'identifier':
                            method_name = get_node_text(child, content).strip()
                            break

                    # Create method qualified name
                    method_qualified_name = None
                    if qualified_name and method_name:
                        method_qualified_name = f"{qualified_name}.{method_name}"

                    # Extract method parameters and return type
                    parameters = []
                    return_type = None

                    # For Java methods
                    if language == 'java':
                        # Find parameter list
                        for child in sec_node.children:
                            if child.type == 'formal_parameters':
                                for param_child in child.children:
                                    if param_child.type == 'formal_parameter':
                                        param_text = get_node_text(param_child, content).strip()
                                        parameters.append(param_text)
                            elif child.type == 'type_identifier' or child.type == 'primitive_type':
                                return_type = get_node_text(child, content).strip()

                    # Create method context
                    method_context = container_context.copy()
                    if method_name:
                        method_context['method_name'] = method_name
                    if parameters:
                        method_context['parameters'] = parameters
                    if return_type:
                        method_context['return_type'] = return_type

                    # Create a chunk for the secondary node
                    method_chunk = CodeChunk(
                        content=sec_text,
                        start_line=sec_location['start_line'] + 1,  # Convert to 1-based
                        end_line=sec_location['end_line'] + 1,      # Convert to 1-based
                        language=language,
                        file_path=file_path,
                        chunk_type=sec_node.type,
                        metadata={
                            "node_type": sec_node.type,
                            "container_type": node.type,
                            "level": "method",
                            "parameters": parameters,
                            "return_type": return_type
                        },
                        parent=container_chunk,
                        context=method_context,
                        name=method_name,
                        qualified_name=method_qualified_name
                    )

                # Add a closing chunk if there's code after the last secondary node
                if secondary_nodes[-1].end_point[0] < node.end_point[0]:
                    closing_text = content[secondary_nodes[-1].end_byte:node.end_byte].decode('utf-8', errors='replace')
                    closing_chunk = CodeChunk(
                        content=closing_text,
                        start_line=secondary_nodes[-1].end_point[0] + 1,  # Convert to 1-based
                        end_line=node.end_point[0] + 1,                  # Convert to 1-based
                        language=language,
                        file_path=file_path,
                        chunk_type=f"{node.type}_closing",
                        metadata={
                            "is_closing": True,
                            "node_type": node.type,
                            "level": "closing"
                        },
                        parent=container_chunk,
                        context=container_context,
                        name=f"{container_name}_closing" if container_name else None
                    )

        # Find any code outside of primary nodes (e.g., standalone functions)
        self._add_orphaned_chunks_hierarchical(file_chunk, ast.root_node, content, language, file_path, node_types)

        # Analyze references for all chunks
        self._analyze_all_references(file_chunk)

        # Validate structural integrity of all chunks
        self._validate_all_chunks(file_chunk)

        # Get all chunks (file chunk and all descendants)
        all_chunks = [file_chunk] + file_chunk.get_descendants()

        # Analyze dependencies between chunks
        dependency_graph = self.dependency_analyzer.analyze_dependencies(all_chunks)

        # Add dependency graph to file chunk metadata
        file_chunk.metadata["dependency_graph"] = dependency_graph.to_dict()

        # Return the top-level chunks (file chunk and any orphaned chunks not attached to the file)
        return [file_chunk]

    def _analyze_all_references(self, file_chunk: CodeChunk) -> None:
        """Analyze references for all chunks in the file.

        Args:
            file_chunk: The file-level chunk
        """
        # Get all chunks in the file
        all_chunks = file_chunk.get_descendants()

        # Analyze references for each chunk
        for chunk in all_chunks:
            if chunk.chunk_type in ['method_declaration', 'constructor_declaration', 'orphaned_method_declaration']:
                self._analyze_references(chunk, file_chunk)

    def _validate_all_chunks(self, file_chunk: CodeChunk) -> None:
        """Validate structural integrity of all chunks in the file.

        Args:
            file_chunk: The file-level chunk
        """
        # Get all chunks in the file
        all_chunks = [file_chunk] + file_chunk.get_descendants()

        # Validate each chunk
        for chunk in all_chunks:
            is_valid = chunk.validate_structural_integrity()
            chunk.metadata['is_valid'] = is_valid

    def _split_large_chunk(
        self,
        chunk: CodeChunk,
        node: Node,
        content: bytes,
        node_types: Dict[str, List[str]],
        language: str
    ) -> List[CodeChunk]:
        """Split a large chunk into smaller chunks based on secondary nodes.

        Args:
            chunk: The original large chunk
            node: The AST node for the chunk
            content: The file content as bytes
            node_types: Dictionary of node types to use for chunking
            language: The programming language

        Returns:
            List of smaller chunks
        """
        sub_chunks = []

        # Find secondary nodes (methods, functions, etc.)
        secondary_nodes = []
        for node_type in node_types.get('secondary', []):
            secondary_nodes.extend(find_nodes_by_type(node, node_type))

        # If no secondary nodes, just return the original chunk
        if not secondary_nodes:
            return [chunk]

        # Sort secondary nodes by position
        secondary_nodes.sort(key=lambda n: n.start_point[0])

        # Extract the declaration part of the primary node (e.g., class declaration without methods)
        declaration_end = secondary_nodes[0].start_point[0]
        declaration_text = content[node.start_byte:secondary_nodes[0].start_byte].decode('utf-8', errors='replace')

        # Create a chunk for the declaration
        declaration_chunk = CodeChunk(
            content=declaration_text,
            start_line=node.start_point[0] + 1,  # Convert to 1-based
            end_line=declaration_end + 1,        # Convert to 1-based
            language=language,
            file_path=chunk.file_path,
            chunk_type=f"{node.type}_declaration",
            metadata={
                **chunk.metadata,
                "is_declaration": True,
                "parent_node_type": node.type
            }
        )
        sub_chunks.append(declaration_chunk)

        # Process each secondary node
        for i, sec_node in enumerate(secondary_nodes):
            sec_text = get_node_text(sec_node, content)
            location = get_node_location(sec_node)

            # Create a chunk for the secondary node
            sec_chunk = CodeChunk(
                content=sec_text,
                start_line=location['start_line'] + 1,  # Convert to 1-based
                end_line=location['end_line'] + 1,      # Convert to 1-based
                language=language,
                file_path=chunk.file_path,
                chunk_type=sec_node.type,
                metadata={
                    **chunk.metadata,
                    "parent_node_type": node.type,
                    "node_type": sec_node.type
                }
            )
            sub_chunks.append(sec_chunk)

        # Add a closing chunk if there's code after the last secondary node
        if secondary_nodes[-1].end_point[0] < node.end_point[0]:
            closing_text = content[secondary_nodes[-1].end_byte:node.end_byte].decode('utf-8', errors='replace')
            closing_chunk = CodeChunk(
                content=closing_text,
                start_line=secondary_nodes[-1].end_point[0] + 1,  # Convert to 1-based
                end_line=node.end_point[0] + 1,                  # Convert to 1-based
                language=language,
                file_path=chunk.file_path,
                chunk_type=f"{node.type}_closing",
                metadata={
                    **chunk.metadata,
                    "is_closing": True,
                    "parent_node_type": node.type
                }
            )
            sub_chunks.append(closing_chunk)

        return sub_chunks

    def _analyze_references(self, chunk: CodeChunk, file_chunk: CodeChunk) -> None:
        """Analyze a chunk for references to other chunks.

        Args:
            chunk: The chunk to analyze
            file_chunk: The file-level chunk containing all chunks
        """
        # Skip if the chunk has no content
        if not chunk.content:
            return

        # Get all chunks in the file
        all_chunks = [file_chunk] + file_chunk.get_descendants()

        # For each chunk with a name, check if it's referenced in the current chunk
        for target_chunk in all_chunks:
            # Skip self-references and chunks without names
            if target_chunk == chunk or not target_chunk.name:
                continue

            # Check for references to the target chunk's name
            if target_chunk.name in chunk.content:
                # Simple heuristic: check if the name is used as an identifier
                # This could be improved with more sophisticated analysis
                pattern = r'\b' + re.escape(target_chunk.name) + r'\b'
                if re.search(pattern, chunk.content):
                    chunk.add_reference(target_chunk)

    def _add_orphaned_chunks_hierarchical(
        self,
        file_chunk: CodeChunk,
        root_node: Node,
        content: bytes,
        language: str,
        file_path: str,
        node_types: Dict[str, List[str]]
    ) -> None:
        """Add chunks for code that's not part of primary nodes, maintaining hierarchy.

        Args:
            file_chunk: The file-level chunk to attach orphaned chunks to
            root_node: The root AST node
            content: The file content as bytes
            language: The programming language
            file_path: The path to the source file
            node_types: Dictionary of node types to use for chunking
        """
        # Find all secondary nodes
        all_secondary_nodes = []
        for node_type in node_types.get('secondary', []):
            all_secondary_nodes.extend(find_nodes_by_type(root_node, node_type))

        # Get all container chunks (descendants of file_chunk that are containers)
        container_chunks = [c for c in file_chunk.get_descendants()
                           if c.metadata.get('level') == 'container']

        # Filter out secondary nodes that are children of container chunks
        orphaned_nodes = []
        for node in all_secondary_nodes:
            # Check if this node is already part of a container chunk
            is_orphaned = True
            for chunk in container_chunks:
                if (node.start_point[0] + 1 >= chunk.start_line and
                    node.end_point[0] + 1 <= chunk.end_line):
                    is_orphaned = False
                    break

            if is_orphaned:
                orphaned_nodes.append(node)

        # Create chunks for orphaned nodes
        for node in orphaned_nodes:
            node_text = get_node_text(node, content)
            location = get_node_location(node)

            # Extract function/method name
            function_name = None
            for child in node.children:
                if child.type == 'identifier':
                    function_name = get_node_text(child, content).strip()
                    break

            # Create qualified name
            qualified_name = None
            if function_name and file_chunk.context.get('package'):
                qualified_name = f"{file_chunk.context['package']}.{function_name}"
            elif function_name:
                qualified_name = function_name

            # Extract parameters and return type
            parameters = []
            return_type = None

            # For Java methods
            if language == 'java':
                # Find parameter list
                for child in node.children:
                    if child.type == 'formal_parameters':
                        for param_child in child.children:
                            if param_child.type == 'formal_parameter':
                                param_text = get_node_text(param_child, content).strip()
                                parameters.append(param_text)
                    elif child.type == 'type_identifier' or child.type == 'primitive_type':
                        return_type = get_node_text(child, content).strip()

            # Create function context
            function_context = file_chunk.context.copy()
            if function_name:
                function_context['function_name'] = function_name
            if parameters:
                function_context['parameters'] = parameters
            if return_type:
                function_context['return_type'] = return_type

            # Create a chunk for the orphaned node
            orphan_chunk = CodeChunk(
                content=node_text,
                start_line=location['start_line'] + 1,  # Convert to 1-based
                end_line=location['end_line'] + 1,      # Convert to 1-based
                language=language,
                file_path=file_path,
                chunk_type=f"orphaned_{node.type}",
                metadata={
                    "node_type": node.type,
                    "is_orphaned": True,
                    "level": "orphaned",
                    "parameters": parameters,
                    "return_type": return_type
                },
                parent=file_chunk,  # Attach directly to the file chunk
                context=function_context,
                name=function_name,
                qualified_name=qualified_name
            )

            # Analyze the function body for references to other chunks
            self._analyze_references(orphan_chunk, file_chunk)

    def _add_orphaned_chunks(
        self,
        chunks: List[CodeChunk],
        root_node: Node,
        content: bytes,
        language: str,
        file_path: str,
        node_types: Dict[str, List[str]]
    ) -> None:
        """Add chunks for code that's not part of primary nodes.

        Args:
            chunks: The existing chunks list to append to
            root_node: The root AST node
            content: The file content as bytes
            language: The programming language
            file_path: The path to the source file
            node_types: Dictionary of node types to use for chunking
        """
        # Find all secondary nodes
        all_secondary_nodes = []
        for node_type in node_types.get('secondary', []):
            all_secondary_nodes.extend(find_nodes_by_type(root_node, node_type))

        # Filter out secondary nodes that are children of primary nodes
        orphaned_nodes = []
        for node in all_secondary_nodes:
            # Check if this node is already part of a primary node
            is_orphaned = True
            for chunk in chunks:
                if (node.start_point[0] + 1 >= chunk.start_line and
                    node.end_point[0] + 1 <= chunk.end_line):
                    is_orphaned = False
                    break

            if is_orphaned:
                orphaned_nodes.append(node)

        # Create chunks for orphaned nodes
        for node in orphaned_nodes:
            node_text = get_node_text(node, content)
            location = get_node_location(node)

            # Create a chunk for the orphaned node
            orphan_chunk = CodeChunk(
                content=node_text,
                start_line=location['start_line'] + 1,  # Convert to 1-based
                end_line=location['end_line'] + 1,      # Convert to 1-based
                language=language,
                file_path=file_path,
                chunk_type=f"orphaned_{node.type}",
                metadata={
                    "node_type": node.type,
                    "is_orphaned": True
                }
            )
            chunks.append(orphan_chunk)