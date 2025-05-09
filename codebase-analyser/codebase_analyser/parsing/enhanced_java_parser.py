"""
Enhanced Java parser that extracts more granular chunks from Java files.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Union, Any
from tree_sitter import Language, Parser, Tree, Node

class EnhancedJavaParser:
    """Enhanced parser for Java source code using Tree-sitter with granular chunking."""

    def __init__(self, language: Language):
        """Initialize the enhanced Java parser.

        Args:
            language: Tree-sitter Java language
        """
        self.parser = Parser()
        self.parser.set_language(language)
        self.language = language  # Store the language separately for queries

        # Define queries for different Java elements
        self.class_query = """
        (class_declaration
          name: (_) @class_name
          body: (_) @class_body) @class
        """

        self.interface_query = """
        (interface_declaration
          name: (_) @interface_name
          body: (_) @interface_body) @interface
        """

        self.method_query = """
        (method_declaration
          name: (_) @method_name
          parameters: (_) @method_params
          body: (block)? @method_body) @method
        """

        self.field_query = """
        (field_declaration
          type: (_) @field_type
          declarator: (variable_declarator
            name: (_) @field_name)) @field
        """

        self.import_query = """
        (import_declaration) @import
        """

        self.package_query = """
        (package_declaration) @package
        """

        self.extends_query = """
        (class_declaration
          superclass: (type_identifier) @superclass) @class
        """

        self.implements_query = """
        (class_declaration
          interfaces: (implements_clause
            (type_list
              (type_identifier) @interface))) @class
        """

        self.method_call_query = """
        (method_invocation
          name: (_) @method_name) @method_call
        """

    def parse_file(self, file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """Parse a Java file and extract its structure with granular chunks.

        Args:
            file_path: Path to the Java file

        Returns:
            Dictionary containing the parsed information or None if parsing failed
        """
        file_path = Path(file_path)

        # Check if file exists
        if not file_path.exists():
            print(f"Error: Java file does not exist: {file_path}")
            return None

        # Check if file is a Java file
        if file_path.suffix.lower() != '.java':
            print(f"Error: Not a Java file: {file_path}")
            return None

        try:
            with open(file_path, 'rb') as f:
                content_bytes = f.read()
                content = content_bytes.decode('utf-8', errors='replace')

            # Parse the file
            tree = self.parser.parse(content_bytes)

            # Check if parsing was successful
            if not tree or not tree.root_node:
                print(f"Error: Failed to parse Java file {file_path}: Empty AST")
                return None

            # Extract Java-specific information
            try:
                package_info = self._extract_package(tree.root_node, content)
            except Exception as e:
                print(f"Warning: Failed to extract package from {file_path}: {e}")
                package_info = None

            try:
                imports = self._extract_imports(tree.root_node, content)
            except Exception as e:
                print(f"Warning: Failed to extract imports from {file_path}: {e}")
                imports = []

            try:
                classes = self._extract_classes(tree.root_node, content, str(file_path))
            except Exception as e:
                print(f"Warning: Failed to extract classes from {file_path}: {e}")
                classes = []

            try:
                interfaces = self._extract_interfaces(tree.root_node, content, str(file_path))
            except Exception as e:
                print(f"Warning: Failed to extract interfaces from {file_path}: {e}")
                interfaces = []

            # Create chunks for the file and its components
            chunks = []

            # File chunk
            file_chunk = {
                "node_id": f"file:{file_path}",
                "chunk_type": "file",
                "name": file_path.name,
                "qualified_name": str(file_path),
                "content": content,
                "file_path": str(file_path),
                "start_line": 1,
                "end_line": content.count('\n') + 1,
                "language": "java",
                "metadata": {
                    "package": package_info["name"] if package_info else None,
                    "imports": [imp["name"] for imp in imports]
                },
                "context": {},
                "parent_id": None
            }
            chunks.append(file_chunk)

            # Add package chunk if present
            if package_info:
                package_chunk = {
                    "node_id": f"package:{package_info['name']}",
                    "chunk_type": "package_declaration",
                    "name": package_info["name"],
                    "qualified_name": package_info["name"],
                    "content": package_info["content"],
                    "file_path": str(file_path),
                    "start_line": package_info["start_line"],
                    "end_line": package_info["end_line"],
                    "language": "java",
                    "metadata": {},
                    "context": {},
                    "parent_id": file_chunk["node_id"]
                }
                chunks.append(package_chunk)

            # Add import chunks
            for imp in imports:
                import_chunk = {
                    "node_id": f"import:{imp['name']}",
                    "chunk_type": "import_declaration",
                    "name": imp["name"],
                    "qualified_name": imp["name"],
                    "content": imp["content"],
                    "file_path": str(file_path),
                    "start_line": imp["start_line"],
                    "end_line": imp["end_line"],
                    "language": "java",
                    "metadata": {},
                    "context": {},
                    "parent_id": file_chunk["node_id"]
                }
                chunks.append(import_chunk)

            # Add class chunks and their methods/fields
            for cls in classes:
                class_chunk = {
                    "node_id": f"class:{cls['name']}",
                    "chunk_type": "class_declaration",
                    "name": cls["name"],
                    "qualified_name": f"{package_info['name']}.{cls['name']}" if package_info else cls["name"],
                    "content": cls["content"],
                    "file_path": str(file_path),
                    "start_line": cls["start_line"],
                    "end_line": cls["end_line"],
                    "language": "java",
                    "metadata": {},
                    "context": {
                        "extends": cls.get("superclass"),
                        "implements": cls.get("interfaces", [])
                    },
                    "parent_id": file_chunk["node_id"]
                }
                chunks.append(class_chunk)

                # Add method chunks
                for method in cls.get("methods", []):
                    method_chunk = {
                        "node_id": f"method:{cls['name']}.{method['name']}",
                        "chunk_type": "method_declaration",
                        "name": method["name"],
                        "qualified_name": f"{class_chunk['qualified_name']}.{method['name']}",
                        "content": method["content"],
                        "file_path": str(file_path),
                        "start_line": method["start_line"],
                        "end_line": method["end_line"],
                        "language": "java",
                        "metadata": {
                            "return_type": method.get("return_type", "void"),
                            "parameters": method.get("parameters", [])
                        },
                        "context": {},
                        "parent_id": class_chunk["node_id"]
                    }
                    chunks.append(method_chunk)

                # Add field chunks
                for field in cls.get("fields", []):
                    field_chunk = {
                        "node_id": f"field:{cls['name']}.{field['name']}",
                        "chunk_type": "field_declaration",
                        "name": field["name"],
                        "qualified_name": f"{class_chunk['qualified_name']}.{field['name']}",
                        "content": field["content"],
                        "file_path": str(file_path),
                        "start_line": field["start_line"],
                        "end_line": field["end_line"],
                        "language": "java",
                        "metadata": {
                            "type": field.get("type", "")
                        },
                        "context": {},
                        "parent_id": class_chunk["node_id"]
                    }
                    chunks.append(field_chunk)

            # Add interface chunks and their methods
            for interface in interfaces:
                interface_chunk = {
                    "node_id": f"interface:{interface['name']}",
                    "chunk_type": "interface_declaration",
                    "name": interface["name"],
                    "qualified_name": f"{package_info['name']}.{interface['name']}" if package_info else interface["name"],
                    "content": interface["content"],
                    "file_path": str(file_path),
                    "start_line": interface["start_line"],
                    "end_line": interface["end_line"],
                    "language": "java",
                    "metadata": {},
                    "context": {},
                    # Parent will be set later
                }
                chunks.append(interface_chunk)

                # Add method chunks
                for method in interface.get("methods", []):
                    method_chunk = {
                        "node_id": f"method:{interface['name']}.{method['name']}",
                        "chunk_type": "method_declaration",
                        "name": method["name"],
                        "qualified_name": f"{interface_chunk['qualified_name']}.{method['name']}",
                        "content": method["content"],
                        "file_path": str(file_path),
                        "start_line": method["start_line"],
                        "end_line": method["end_line"],
                        "language": "java",
                        "metadata": {
                            "return_type": method.get("return_type", "void"),
                            "parameters": method.get("parameters", [])
                        },
                        "context": {},
                        "parent_id": interface_chunk["node_id"]
                    }
                    chunks.append(method_chunk)

            # Extract dependencies between chunks
            dependencies = self._extract_dependencies(chunks, tree.root_node, content)

            return {
                'path': str(file_path),
                'language': 'java',
                'ast': tree,
                'content': content,
                'package': package_info,
                'imports': imports,
                'classes': classes,
                'interfaces': interfaces,
                'chunks': chunks,
                'dependencies': dependencies
            }
        except Exception as e:
            print(f"Error parsing Java file {file_path}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _extract_package(self, root_node: Node, content: str) -> Optional[Dict[str, Any]]:
        """Extract package declaration from a Java file."""
        query = self.language.query(self.package_query)
        captures = query.captures(root_node)

        for node, type_name in captures:
            if type_name == "package":
                return {
                    "name": self._get_package_name(node, content),
                    "content": self._get_node_text(node, content),
                    "start_line": node.start_point[0] + 1,  # Convert to 1-based
                    "end_line": node.end_point[0] + 1       # Convert to 1-based
                }

        return None

    def _get_package_name(self, package_node: Node, content: str) -> str:
        """Extract the package name from a package declaration node."""
        # Find the identifier node within the package declaration
        for child in package_node.children:
            if child.type == "scoped_identifier":
                return self._get_node_text(child, content)

        # If no scoped_identifier is found, look for any text after "package"
        text = self._get_node_text(package_node, content)
        parts = text.split("package")
        if len(parts) > 1:
            return parts[1].strip().rstrip(';').strip()

        return ""

    def _extract_imports(self, root_node: Node, content: str) -> List[Dict[str, Any]]:
        """Extract import declarations from a Java file."""
        imports = []
        query = self.language.query(self.import_query)
        captures = query.captures(root_node)

        for node, type_name in captures:
            if type_name == "import":
                import_text = self._get_node_text(node, content)
                import_name = self._get_import_name(node, content)

                imports.append({
                    "name": import_name,
                    "content": import_text,
                    "start_line": node.start_point[0] + 1,  # Convert to 1-based
                    "end_line": node.end_point[0] + 1       # Convert to 1-based
                })

        return imports

    def _get_import_name(self, import_node: Node, content: str) -> str:
        """Extract the import name from an import declaration node."""
        # Find the identifier node within the import declaration
        for child in import_node.children:
            if child.type == "scoped_identifier":
                return self._get_node_text(child, content)

        # If no scoped_identifier is found, look for any text after "import"
        text = self._get_node_text(import_node, content)
        parts = text.split("import")
        if len(parts) > 1:
            return parts[1].strip().rstrip(';').strip()

        return ""

    def _extract_classes(self, root_node: Node, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Extract class declarations from a Java file."""
        classes = []
        query = self.language.query(self.class_query)
        captures = query.captures(root_node)

        class_nodes = {}
        class_names = {}
        class_bodies = {}

        # First pass: collect all class nodes, names, and bodies
        for node, type_name in captures:
            if type_name == "class":
                class_nodes[node.id] = node
            elif type_name == "class_name":
                class_names[node.parent.id] = self._get_node_text(node, content)
            elif type_name == "class_body":
                class_bodies[node.parent.id] = node

        # Second pass: process each class
        for node_id, node in class_nodes.items():
            if node_id not in class_names:
                continue

            class_name = class_names[node_id]
            class_body_node = class_bodies.get(node_id)

            # Extract superclass
            superclass = self._extract_superclass(node, content)

            # Extract interfaces
            interfaces = self._extract_interfaces_implemented(node, content)

            # Extract methods
            methods = []
            if class_body_node:
                methods = self._extract_methods_from_node(class_body_node, content, class_name)

            # Extract fields
            fields = []
            if class_body_node:
                fields = self._extract_fields_from_node(class_body_node, content, class_name)

            classes.append({
                "name": class_name,
                "content": self._get_node_text(node, content),
                "start_line": node.start_point[0] + 1,  # Convert to 1-based
                "end_line": node.end_point[0] + 1,      # Convert to 1-based
                "superclass": superclass,
                "interfaces": interfaces,
                "methods": methods,
                "fields": fields,
                "file_path": file_path
            })

        return classes

    def _extract_superclass(self, class_node: Node, content: str) -> Optional[str]:
        """Extract the superclass of a class."""
        query = self.language.query(self.extends_query)
        captures = query.captures(class_node)

        for node, type_name in captures:
            if type_name == "superclass":
                return self._get_node_text(node, content)

        return None

    def _extract_interfaces_implemented(self, class_node: Node, content: str) -> List[str]:
        """Extract the interfaces implemented by a class."""
        interfaces = []
        query = self.language.query(self.implements_query)
        captures = query.captures(class_node)

        for node, type_name in captures:
            if type_name == "interface":
                interfaces.append(self._get_node_text(node, content))

        return interfaces

    def _extract_interfaces(self, root_node: Node, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Extract interface declarations from a Java file."""
        interfaces = []
        query = self.language.query(self.interface_query)
        captures = query.captures(root_node)

        interface_nodes = {}
        interface_names = {}
        interface_bodies = {}

        # First pass: collect all interface nodes, names, and bodies
        for node, type_name in captures:
            if type_name == "interface":
                interface_nodes[node.id] = node
            elif type_name == "interface_name":
                interface_names[node.parent.id] = self._get_node_text(node, content)
            elif type_name == "interface_body":
                interface_bodies[node.parent.id] = node

        # Second pass: process each interface
        for node_id, node in interface_nodes.items():
            if node_id not in interface_names:
                continue

            interface_name = interface_names[node_id]
            interface_body_node = interface_bodies.get(node_id)

            # Extract methods
            methods = []
            if interface_body_node:
                methods = self._extract_methods_from_node(interface_body_node, content, interface_name)

            interfaces.append({
                "name": interface_name,
                "content": self._get_node_text(node, content),
                "start_line": node.start_point[0] + 1,  # Convert to 1-based
                "end_line": node.end_point[0] + 1,      # Convert to 1-based
                "methods": methods,
                "file_path": file_path
            })

        return interfaces

    def _extract_methods_from_node(self, parent_node: Node, content: str, parent_name: str) -> List[Dict[str, Any]]:
        """Extract method declarations from a class or interface body node."""
        methods = []
        query = self.language.query(self.method_query)
        captures = query.captures(parent_node)

        method_nodes = {}
        method_names = {}
        method_params = {}
        method_bodies = {}

        # First pass: collect all method nodes, names, params, and bodies
        for node, type_name in captures:
            if type_name == "method":
                method_nodes[node.id] = node
            elif type_name == "method_name":
                method_names[node.parent.id] = self._get_node_text(node, content)
            elif type_name == "method_params":
                method_params[node.parent.id] = node
            elif type_name == "method_body":
                method_bodies[node.parent.id] = node

        # Second pass: process each method
        for node_id, node in method_nodes.items():
            if node_id not in method_names:
                continue

            method_name = method_names[node_id]
            params_node = method_params.get(node_id)
            body_node = method_bodies.get(node_id)

            # Extract return type
            return_type = self._extract_method_return_type(node, content)

            # Extract parameters
            parameters = []
            if params_node:
                parameters = self._extract_method_parameters(params_node, content)

            methods.append({
                "name": method_name,
                "content": self._get_node_text(node, content),
                "start_line": node.start_point[0] + 1,  # Convert to 1-based
                "end_line": node.end_point[0] + 1,      # Convert to 1-based
                "return_type": return_type,
                "parameters": parameters,
                "parent": parent_name
            })

        return methods

    def _extract_method_return_type(self, method_node: Node, content: str) -> str:
        """Extract the return type of a method."""
        # Look for the return type node
        for child in method_node.children:
            if child.type in ["type_identifier", "primitive_type", "void_type"]:
                return self._get_node_text(child, content)

        return "void"  # Default return type

    def _extract_method_parameters(self, params_node: Node, content: str) -> List[Dict[str, str]]:
        """Extract parameters from a method's formal_parameters node."""
        parameters = []

        for child in params_node.children:
            if child.type == "formal_parameter":
                param_type = ""
                param_name = ""

                # Extract parameter type and name
                for param_child in child.children:
                    if param_child.type in ["type_identifier", "primitive_type", "array_type"]:
                        param_type = self._get_node_text(param_child, content)
                    elif param_child.type == "identifier":
                        param_name = self._get_node_text(param_child, content)

                if param_name:
                    parameters.append({
                        "type": param_type,
                        "name": param_name
                    })

        return parameters

    def _extract_fields_from_node(self, parent_node: Node, content: str, parent_name: str) -> List[Dict[str, Any]]:
        """Extract field declarations from a class body node."""
        fields = []
        query = self.language.query(self.field_query)
        captures = query.captures(parent_node)

        field_nodes = {}
        field_types = {}
        field_names = {}

        # First pass: collect all field nodes, types, and names
        for node, type_name in captures:
            if type_name == "field":
                field_nodes[node.id] = node
            elif type_name == "field_type":
                field_types[node.parent.id] = self._get_node_text(node, content)
            elif type_name == "field_name":
                field_names[node.parent.parent.id] = self._get_node_text(node, content)

        # Second pass: process each field
        for node_id, node in field_nodes.items():
            if node_id not in field_names:
                continue

            field_name = field_names[node_id]
            field_type = field_types.get(node_id, "")

            fields.append({
                "name": field_name,
                "content": self._get_node_text(node, content),
                "start_line": node.start_point[0] + 1,  # Convert to 1-based
                "end_line": node.end_point[0] + 1,      # Convert to 1-based
                "type": field_type,
                "parent": parent_name
            })

        return fields

    def _extract_dependencies(self, chunks: List[Dict[str, Any]], root_node: Node, content: str) -> List[Dict[str, Any]]:
        """Extract dependencies between chunks."""
        dependencies = []

        # Create a map of chunk names to node_ids for quick lookup
        chunk_map = {}
        for chunk in chunks:
            chunk_map[chunk["name"]] = chunk["node_id"]
            if "qualified_name" in chunk:
                chunk_map[chunk["qualified_name"]] = chunk["node_id"]

        # Extract import dependencies
        for chunk in chunks:
            if chunk["chunk_type"] == "import_declaration":
                import_name = chunk["name"]
                # Find the target class or interface
                for target_chunk in chunks:
                    if target_chunk["chunk_type"] in ["class_declaration", "interface_declaration"]:
                        if target_chunk["qualified_name"] == import_name or target_chunk["name"] == import_name.split(".")[-1]:
                            dependencies.append({
                                "source_id": chunk["parent_id"],  # File imports the class
                                "target_id": target_chunk["node_id"],
                                "type": "IMPORTS",
                                "description": f"File imports {target_chunk['name']}",
                                "strength": 0.5,
                                "is_direct": True,
                                "is_required": True
                            })

        # Extract inheritance dependencies
        for chunk in chunks:
            if chunk["chunk_type"] == "class_declaration" and "context" in chunk:
                # Extends relationship
                if chunk["context"].get("extends"):
                    superclass_name = chunk["context"]["extends"]
                    for target_chunk in chunks:
                        if target_chunk["chunk_type"] == "class_declaration" and target_chunk["name"] == superclass_name:
                            dependencies.append({
                                "source_id": chunk["node_id"],
                                "target_id": target_chunk["node_id"],
                                "type": "EXTENDS",
                                "description": f"{chunk['name']} extends {target_chunk['name']}",
                                "strength": 1.0,
                                "is_direct": True,
                                "is_required": True
                            })

                # Implements relationship
                for interface_name in chunk["context"].get("implements", []):
                    for target_chunk in chunks:
                        if target_chunk["chunk_type"] == "interface_declaration" and target_chunk["name"] == interface_name:
                            dependencies.append({
                                "source_id": chunk["node_id"],
                                "target_id": target_chunk["node_id"],
                                "type": "IMPLEMENTS",
                                "description": f"{chunk['name']} implements {target_chunk['name']}",
                                "strength": 0.9,
                                "is_direct": True,
                                "is_required": True
                            })

        # Extract method call dependencies
        query = self.language.query(self.method_call_query)
        captures = query.captures(root_node)

        for node, type_name in captures:
            if type_name == "method_name":
                method_name = self._get_node_text(node, content)

                # Find the containing method
                containing_method = None
                for chunk in chunks:
                    if chunk["chunk_type"] == "method_declaration":
                        if node.start_point[0] + 1 >= chunk["start_line"] and node.end_point[0] + 1 <= chunk["end_line"]:
                            containing_method = chunk
                            break

                if containing_method:
                    # Find the target method
                    for target_chunk in chunks:
                        if target_chunk["chunk_type"] == "method_declaration" and target_chunk["name"] == method_name:
                            # Don't create self-dependencies
                            if target_chunk["node_id"] != containing_method["node_id"]:
                                dependencies.append({
                                    "source_id": containing_method["node_id"],
                                    "target_id": target_chunk["node_id"],
                                    "type": "CALLS",
                                    "description": f"{containing_method['name']} calls {target_chunk['name']}",
                                    "strength": 0.8,
                                    "is_direct": True,
                                    "is_required": True
                                })

        # Extract field usage dependencies
        for chunk in chunks:
            if chunk["chunk_type"] == "method_declaration":
                method_content = chunk["content"]

                # Check for field usage
                for field_chunk in chunks:
                    if field_chunk["chunk_type"] == "field_declaration":
                        field_name = field_chunk["name"]

                        # Simple check for field name in method content
                        if field_name in method_content:
                            dependencies.append({
                                "source_id": chunk["node_id"],
                                "target_id": field_chunk["node_id"],
                                "type": "USES",
                                "description": f"{chunk['name']} uses field {field_chunk['name']}",
                                "strength": 0.7,
                                "is_direct": True,
                                "is_required": False
                            })

        return dependencies

    def _get_node_text(self, node: Node, content: str) -> str:
        """Get the text of a node from the content."""
        if isinstance(content, str):
            return content[node.start_byte:node.end_byte]
        else:
            return content[node.start_byte:node.end_byte].decode('utf-8', errors='replace')