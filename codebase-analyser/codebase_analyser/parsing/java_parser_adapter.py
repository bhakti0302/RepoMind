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
        
        # Create chunks
        chunks = JavaParserAdapter.create_chunks_from_file(file_path, content)
        
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
            
            chunk_dicts.append(chunk_dict)
        
        # Extract package
        package_name = JavaParserAdapter._extract_package(content)
        
        # Extract imports
        imports = JavaParserAdapter._extract_imports(content)
        
        return {
            'language': 'java',
            'package': {'name': package_name} if package_name else None,
            'imports': imports,
            'chunks': chunk_dicts
        }
    
    @staticmethod
    def create_chunks_from_file(file_path: Union[str, Path], content: str) -> List[CodeChunk]:
        """Create CodeChunk objects from a Java file.
        
        Args:
            file_path: Path to the Java file
            content: Content of the Java file
            
        Returns:
            List of CodeChunk objects
        """
        file_path = str(file_path)
        chunks = []
        
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
        
        # Extract package
        package_name = JavaParserAdapter._extract_package(content)
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
        
        # Extract imports
        imports = JavaParserAdapter._extract_imports(content)
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
        
        # Extract classes
        class_chunks = JavaParserAdapter._extract_classes(content, file_path, file_chunk)
        chunks.extend(class_chunks)
        
        # Extract methods from classes
        for class_chunk in class_chunks:
            method_chunks = JavaParserAdapter._extract_methods(class_chunk.content, file_path, class_chunk)
            chunks.extend(method_chunks)
        
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
            
            chunks.append(chunk)
        
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
