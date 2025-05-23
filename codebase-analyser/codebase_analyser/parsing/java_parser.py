from pathlib import Path
from typing import Dict, List, Optional, Set, Union, Any
from tree_sitter import Language, Parser, Tree, Node

class JavaParser:
    """Parser for Java source code using Tree-sitter."""
    
    def __init__(self, language: Language):
        """Initialize the Java parser.
        
        Args:
            language: Tree-sitter Java language
        """
        self.parser = Parser()
        self.parser.set_language(language)
    
    def parse_file(self, file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """Parse a Java file and extract its structure.
        
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
                content = f.read()
            
            # Parse the file
            tree = self.parser.parse(content)
            
            # Check if parsing was successful
            if not tree or not tree.root_node:
                print(f"Error: Failed to parse Java file {file_path}: Empty AST")
                return None
            
            # Extract Java-specific information
            try:
                package_name = self._extract_package_name(tree.root_node, content)
            except Exception as e:
                print(f"Warning: Failed to extract package name from {file_path}: {e}")
                package_name = None
                
            try:
                imports = self._extract_imports(tree.root_node, content)
            except Exception as e:
                print(f"Warning: Failed to extract imports from {file_path}: {e}")
                imports = []
                
            try:
                classes = self._extract_classes(tree.root_node, content)
            except Exception as e:
                print(f"Warning: Failed to extract classes from {file_path}: {e}")
                classes = []
                
            try:
                methods = self._extract_methods(tree.root_node, content)
            except Exception as e:
                print(f"Warning: Failed to extract methods from {file_path}: {e}")
                methods = []
            
            return {
                'path': str(file_path),
                'language': 'java',
                'ast': tree,
                'content': content.decode('utf-8', errors='replace'),
                'package': package_name,
                'imports': imports,
                'classes': classes,
                'methods': methods
            }
        except UnicodeDecodeError:
            print(f"Error parsing Java file {file_path}: Invalid encoding")
            return None
        except FileNotFoundError:
            print(f"Error parsing Java file {file_path}: File not found")
            return None
        except PermissionError:
            print(f"Error parsing Java file {file_path}: Permission denied")
            return None
        except Exception as e:
            print(f"Error parsing Java file {file_path}: {e}")
            return None
    
    def _extract_package_name(self, root_node: Node, content: bytes) -> Optional[str]:
        """Extract the package name from a Java file."""
        package_decl = self._find_node(root_node, "package_declaration")
        if package_decl:
            name_node = self._find_node(package_decl, "scoped_identifier")
            if name_node:
                return self._get_node_text(name_node, content)
        return None
    
    def _extract_imports(self, root_node: Node, content: bytes) -> List[str]:
        """Extract import statements from a Java file."""
        imports = []
        import_nodes = self._find_nodes(root_node, "import_declaration")
        
        for node in import_nodes:
            name_node = self._find_node(node, "scoped_identifier")
            if name_node:
                import_name = self._get_node_text(name_node, content)
                imports.append(import_name)
        
        return imports
    
    def _extract_classes(self, root_node: Node, content: bytes) -> List[Dict[str, Any]]:
        """Extract class declarations from a Java file."""
        classes = []
        class_nodes = self._find_nodes(root_node, "class_declaration")
        
        for node in class_nodes:
            name_node = self._find_node(node, "identifier")
            if name_node:
                class_name = self._get_node_text(name_node, content)
                
                # Extract superclass if any
                superclass = None
                superclass_node = self._find_node(node, "superclass")
                if superclass_node:
                    type_node = self._find_node(superclass_node, "type_identifier")
                    if type_node:
                        superclass = self._get_node_text(type_node, content)
                
                # Extract interfaces if any
                interfaces = []
                interfaces_node = self._find_node(node, "super_interfaces")
                if interfaces_node:
                    interface_nodes = self._find_nodes(interfaces_node, "type_identifier")
                    for iface_node in interface_nodes:
                        interfaces.append(self._get_node_text(iface_node, content))
                
                # Extract fields
                fields = self._extract_fields(node, content)
                
                # Extract methods
                methods = self._extract_methods(node, content)
                
                classes.append({
                    'name': class_name,
                    'superclass': superclass,
                    'interfaces': interfaces,
                    'fields': fields,
                    'methods': methods,
                    'start_line': node.start_point[0],
                    'end_line': node.end_point[0],
                    'code': self._get_node_text(node, content)
                })
        
        return classes
    
    def _extract_fields(self, class_node: Node, content: bytes) -> List[Dict[str, Any]]:
        """Extract field declarations from a class."""
        fields = []
        field_nodes = self._find_nodes(class_node, "field_declaration")
        
        for node in field_nodes:
            type_node = self._find_node(node, "type_identifier")
            var_nodes = self._find_nodes(node, "variable_declarator")
            
            field_type = self._get_node_text(type_node, content) if type_node else "unknown"
            
            for var_node in var_nodes:
                name_node = self._find_node(var_node, "identifier")
                if name_node:
                    field_name = self._get_node_text(name_node, content)
                    fields.append({
                        'name': field_name,
                        'type': field_type,
                        'start_line': node.start_point[0],
                        'end_line': node.end_point[0],
                        'code': self._get_node_text(node, content)
                    })
        
        return fields
    
    def _extract_methods(self, root_node: Node, content: bytes) -> List[Dict[str, Any]]:
        """Extract method declarations from a Java file or class."""
        methods = []
        method_nodes = self._find_nodes(root_node, "method_declaration")
        
        for node in method_nodes:
            name_node = self._find_node(node, "identifier")
            if name_node:
                method_name = self._get_node_text(name_node, content)
                
                # Extract return type
                return_type = "void"  # Default
                type_node = self._find_node(node, "type_identifier")
                if type_node:
                    return_type = self._get_node_text(type_node, content)
                
                # Extract parameters
                parameters = []
                params_node = self._find_node(node, "formal_parameters")
                if params_node:
                    param_nodes = self._find_nodes(params_node, "formal_parameter")
                    for param_node in param_nodes:
                        param_type_node = self._find_node(param_node, "type_identifier")
                        param_name_node = self._find_node(param_node, "identifier")
                        
                        if param_type_node and param_name_node:
                            param_type = self._get_node_text(param_type_node, content)
                            param_name = self._get_node_text(param_name_node, content)
                            
                            parameters.append({
                                'name': param_name,
                                'type': param_type
                            })
                
                methods.append({
                    'name': method_name,
                    'return_type': return_type,
                    'parameters': parameters,
                    'start_line': node.start_point[0],
                    'end_line': node.end_point[0],
                    'code': self._get_node_text(node, content)
                })
        
        return methods
    
    def _find_node(self, node: Node, type_name: str) -> Optional[Node]:
        """Find the first child node of a specific type."""
        if node.type == type_name:
            return node
        
        for child in node.children:
            result = self._find_node(child, type_name)
            if result:
                return result
        
        return None
    
    def _find_nodes(self, node: Node, type_name: str) -> List[Node]:
        """Find all child nodes of a specific type."""
        results = []
        
        if node.type == type_name:
            results.append(node)
        
        for child in node.children:
            results.extend(self._find_nodes(child, type_name))
        
        return results
    
    def _get_node_text(self, node: Node, content: bytes) -> str:
        """Get the text content of a node."""
        return content[node.start_byte:node.end_byte].decode('utf-8', errors='replace')
