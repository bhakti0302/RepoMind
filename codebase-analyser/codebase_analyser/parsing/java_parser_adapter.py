"""
Adapter for Java parser to create CodeChunk objects.
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from ..chunking.code_chunk import CodeChunk


class JavaParserAdapter:
    """Adapter for Java parser to create CodeChunk objects."""

    @staticmethod
    def parse_file(file_path: Union[str, Path]) -> Dict[str, Any]:
        """Parse a Java file and return chunks.

        Args:
            file_path: Path to the Java file

        Returns:
            Dictionary with language, package, imports, and chunks
        """
        file_path = str(file_path)

        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract package
        package_name = JavaParserAdapter._extract_package(content)

        # Extract imports
        imports = JavaParserAdapter._extract_imports(content)

        # Create chunks
        chunks = JavaParserAdapter.create_chunks_from_file(file_path, content, package_name, imports)

        # Convert chunks to dictionaries
        chunk_dicts = []
        for chunk in chunks:
            chunk_dict = {
                'node_id': chunk.node_id,
                'chunk_type': chunk.chunk_type,
                'content': chunk.content,
                'file_path': chunk.file_path,
                'start_line': chunk.start_line,
                'end_line': chunk.end_line,
                'language': chunk.language,
                'name': chunk.name,
                'qualified_name': chunk.qualified_name
            }

            # Add metadata and context if present
            if hasattr(chunk, 'metadata') and chunk.metadata:
                chunk_dict['metadata'] = chunk.metadata
            if hasattr(chunk, 'context') and chunk.context:
                chunk_dict['context'] = chunk.context

            # Add parent_id if present
            if chunk.parent:
                chunk_dict['parent_id'] = chunk.parent.node_id

            # Add reference_ids if present
            if hasattr(chunk, 'references') and chunk.references:
                chunk_dict['reference_ids'] = [ref.node_id for ref in chunk.references]

            chunk_dicts.append(chunk_dict)

        return {
            'language': 'java',
            'package': {'name': package_name} if package_name else None,
            'imports': imports,
            'chunks': chunk_dicts
        }

    @staticmethod
    def create_chunks_from_file(file_path: Union[str, Path], content: str, package_name: Optional[str] = None, imports: Optional[List[str]] = None) -> List[CodeChunk]:
        """Create CodeChunk objects from a Java file.

        Args:
            file_path: Path to the Java file
            content: Content of the Java file
            package_name: Package name (optional)
            imports: List of imports (optional)

        Returns:
            List of CodeChunk objects
        """
        file_path = str(file_path)
        chunks = []
        import_chunks = []
        class_chunks = []

        # Create file chunk
        file_chunk = CodeChunk(
            node_id=f"file:{file_path}",
            chunk_type="file",
            content=content,
            file_path=file_path,
            start_line=1,
            end_line=content.count('\n') + 1,
            language="java",
            name=Path(file_path).stem
        )
        chunks.append(file_chunk)

        # Extract package if not provided
        if package_name is None:
            package_name = JavaParserAdapter._extract_package(content)

        # Create package chunk
        if package_name:
            package_chunk = CodeChunk(
                node_id=f"package:{package_name}",
                chunk_type="package_declaration",
                content=f"package {package_name};",
                file_path=file_path,
                start_line=1,  # Approximate
                end_line=1,    # Approximate
                language="java",
                name=package_name
            )
            file_chunk.add_child(package_chunk)
            chunks.append(package_chunk)

        # Extract imports if not provided
        if imports is None:
            imports = JavaParserAdapter._extract_imports(content)

        # Create import chunks
        for i, import_name in enumerate(imports):
            import_chunk = CodeChunk(
                node_id=f"import:{import_name}",
                chunk_type="import_declaration",
                content=f"import {import_name};",
                file_path=file_path,
                start_line=i + 2,  # Approximate
                end_line=i + 2,    # Approximate
                language="java",
                name=import_name
            )
            file_chunk.add_child(import_chunk)
            chunks.append(import_chunk)
            import_chunks.append(import_chunk)

        # Extract classes
        class_chunks = JavaParserAdapter._extract_classes(content, file_path, file_chunk)
        chunks.extend(class_chunks)

        # Extract methods from classes
        for class_chunk in class_chunks:
            method_chunks = JavaParserAdapter._extract_methods(class_chunk.content, file_path, class_chunk)
            chunks.extend(method_chunks)

        # Create a map of class name to chunk for establishing import relationships
        class_chunks_map = {chunk.name: chunk for chunk in class_chunks}

        # Establish dependencies based on imports
        for class_chunk in class_chunks:
            class_name = class_chunk.name
            qualified_name = class_chunk.qualified_name or class_name

            # Add references to imported classes
            for import_chunk in import_chunks:
                import_name = import_chunk.name

                # Check if the class uses this import
                if import_name.endswith("." + class_name):
                    # This is the import for this class
                    continue

                # Extract the simple class name from the import
                imported_class_name = import_name.split(".")[-1]

                # Check if the class content references the imported class
                if re.search(r'\b' + re.escape(imported_class_name) + r'\b', class_chunk.content):
                    # Add a reference from this class to the imported class
                    class_chunk.add_reference(import_chunk)

                    # Add metadata to indicate this is an IMPORTS relationship
                    if 'reference_types' not in class_chunk.metadata:
                        class_chunk.metadata['reference_types'] = {}

                    class_chunk.metadata['reference_types'][import_chunk.node_id] = 'IMPORTS'

        return chunks

    @staticmethod
    def _extract_package(content: str) -> Optional[str]:
        """Extract package name from Java content."""
        match = re.search(r'package\s+([\w.]+);', content)
        if match:
            return match.group(1)
        return None

    @staticmethod
    def _extract_imports(content: str) -> List[str]:
        """Extract import statements from Java content."""
        imports = []
        for match in re.finditer(r'import\s+([\w.]+);', content):
            imports.append(match.group(1))
        return imports

    @staticmethod
    def _extract_classes(content: str, file_path: str, parent_chunk: CodeChunk) -> List[CodeChunk]:
        """Extract class chunks from Java content."""
        chunks = []
        class_chunks_map = {}  # Map of class name to chunk for establishing relationships later

        # Find class declarations
        class_pattern = r'public\s+class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([\w,\s]+))?\s*\{'
        class_matches = re.finditer(class_pattern, content)

        for match in class_matches:
            class_name = match.group(1)
            superclass = match.group(2)
            interfaces = match.group(3)

            # Find the class body
            start_pos = match.start()

            # Find the matching closing brace
            open_braces = 1
            end_pos = start_pos + match.group(0).find('{') + 1

            while open_braces > 0 and end_pos < len(content):
                if content[end_pos] == '{':
                    open_braces += 1
                elif content[end_pos] == '}':
                    open_braces -= 1
                end_pos += 1

            # Extract the class content
            class_content = content[start_pos:end_pos]

            # Count lines
            start_line = content[:start_pos].count('\n') + 1
            end_line = content[:end_pos].count('\n') + 1

            # Create context
            context = {}
            if superclass:
                context['extends'] = superclass
            if interfaces:
                context['implements'] = [i.strip() for i in interfaces.split(',')]

            # Create the chunk
            chunk = CodeChunk(
                node_id=f"class:{class_name}",
                chunk_type="class_declaration",
                content=class_content,
                file_path=file_path,
                start_line=start_line,
                end_line=end_line,
                language="java",
                name=class_name,
                qualified_name=class_name
            )

            # Add context
            chunk.context = context

            # Add as child of parent
            parent_chunk.add_child(chunk)

            # Store in map for later relationship establishment
            class_chunks_map[class_name] = chunk

            chunks.append(chunk)

        # Extract field declarations to establish HAS_FIELD relationships
        for class_name, class_chunk in class_chunks_map.items():
            # Find field declarations
            field_pattern = r'(private|protected|public)\s+(\w+(?:<[\w\s,]+>)?)\s+(\w+)\s*[=;]'
            field_matches = re.finditer(field_pattern, class_chunk.content)

            for field_match in field_matches:
                field_type = field_match.group(2)
                field_name = field_match.group(3)

                # Add field type to context
                if 'fields' not in class_chunk.context:
                    class_chunk.context['fields'] = []

                class_chunk.context['fields'].append({
                    'name': field_name,
                    'type': field_type
                })

                # If the field type is one of our known classes, establish a HAS_FIELD relationship
                if field_type in class_chunks_map:
                    field_type_chunk = class_chunks_map[field_type]
                    class_chunk.add_reference(field_type_chunk)

                    # Add metadata to indicate this is a HAS_FIELD relationship
                    if 'reference_types' not in class_chunk.metadata:
                        class_chunk.metadata['reference_types'] = {}

                    class_chunk.metadata['reference_types'][field_type_chunk.node_id] = 'HAS_FIELD'

        # Establish inheritance relationships
        for class_name, class_chunk in class_chunks_map.items():
            # Check for extends relationship
            if 'extends' in class_chunk.context and class_chunk.context['extends'] in class_chunks_map:
                superclass_chunk = class_chunks_map[class_chunk.context['extends']]
                class_chunk.add_reference(superclass_chunk)

                # Add metadata to indicate this is an EXTENDS relationship
                if 'reference_types' not in class_chunk.metadata:
                    class_chunk.metadata['reference_types'] = {}

                class_chunk.metadata['reference_types'][superclass_chunk.node_id] = 'EXTENDS'

            # Check for implements relationships
            if 'implements' in class_chunk.context:
                for interface_name in class_chunk.context['implements']:
                    if interface_name in class_chunks_map:
                        interface_chunk = class_chunks_map[interface_name]
                        class_chunk.add_reference(interface_chunk)

                        # Add metadata to indicate this is an IMPLEMENTS relationship
                        if 'reference_types' not in class_chunk.metadata:
                            class_chunk.metadata['reference_types'] = {}

                        class_chunk.metadata['reference_types'][interface_chunk.node_id] = 'IMPLEMENTS'

        return chunks

    @staticmethod
    def _extract_methods(content: str, file_path: str, parent_chunk: CodeChunk) -> List[CodeChunk]:
        """Extract method chunks from Java content."""
        chunks = []

        # Find method declarations
        method_pattern = r'(public|private|protected)?\s+(?:static\s+)?(?:final\s+)?(?:(\w+(?:<[\w\s,]+>)?)\s+)?(\w+)\s*\((.*?)\)\s*(?:throws\s+[\w,\s]+)?\s*\{'
        method_matches = re.finditer(method_pattern, content)

        for match in method_matches:
            visibility = match.group(1) or "default"
            return_type = match.group(2) or "void"
            method_name = match.group(3)
            parameters = match.group(4)

            # Find the method body
            start_pos = match.start()

            # Find the matching closing brace
            open_braces = 1
            end_pos = start_pos + match.group(0).find('{') + 1

            while open_braces > 0 and end_pos < len(content):
                if content[end_pos] == '{':
                    open_braces += 1
                elif content[end_pos] == '}':
                    open_braces -= 1
                end_pos += 1

            # Extract the method content
            method_content = content[start_pos:end_pos]

            # Count lines
            start_line = content[:start_pos].count('\n') + 1
            end_line = content[:end_pos].count('\n') + 1

            # Create metadata
            metadata = {
                'visibility': visibility,
                'return_type': return_type,
                'parameters': parameters
            }

            # Create the chunk
            chunk = CodeChunk(
                node_id=f"method:{parent_chunk.name}.{method_name}",
                chunk_type="method_declaration",
                content=method_content,
                file_path=file_path,
                start_line=start_line,
                end_line=end_line,
                language="java",
                name=method_name,
                qualified_name=f"{parent_chunk.name}.{method_name}"
            )

            # Add metadata
            chunk.metadata = metadata

            # Add as child of parent
            parent_chunk.add_child(chunk)

            chunks.append(chunk)

        return chunks
