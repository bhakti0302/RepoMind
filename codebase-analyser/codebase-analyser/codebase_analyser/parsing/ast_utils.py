"""
Utility functions for working with Tree-sitter ASTs.
"""
from typing import List, Optional, Callable, Any, Dict
from tree_sitter import Node

def traverse_ast(node: Node, callback: Callable[[Node, int], Any], depth: int = 0) -> None:
    """Traverse an AST and call a function on each node.
    
    Args:
        node: The node to start traversal from
        callback: Function to call on each node, receives (node, depth)
        depth: Current depth in the tree (used for recursion)
    """
    # Call the callback on this node
    callback(node, depth)
    
    # Recursively process children
    for child in node.children:
        traverse_ast(child, callback, depth + 1)

def find_nodes_by_type(root: Node, node_type: str) -> List[Node]:
    """Find all nodes of a specific type in the AST.
    
    Args:
        root: The root node to start searching from
        node_type: The type of node to find
        
    Returns:
        List of nodes matching the specified type
    """
    results = []
    
    def collect_nodes(node, _):
        if node.type == node_type:
            results.append(node)
    
    traverse_ast(root, collect_nodes)
    return results

def find_parent(node: Node, root: Node) -> Optional[Node]:
    """Find the parent of a node in the AST.
    
    Args:
        node: The node to find the parent of
        root: The root node of the AST
        
    Returns:
        The parent node or None if not found
    """
    for child in root.children:
        if child == node:
            return root
        
        parent = find_parent(node, child)
        if parent:
            return parent
    
    return None

def get_node_text(node: Node, source_code: bytes) -> str:
    """Get the text of a node from the source code.
    
    Args:
        node: The node to get text for
        source_code: The source code bytes
        
    Returns:
        The text of the node
    """
    return source_code[node.start_byte:node.end_byte].decode('utf-8', errors='replace')

def find_nodes_by_text(root: Node, text: str, source_code: bytes) -> List[Node]:
    """Find all nodes containing specific text.
    
    Args:
        root: The root node to start searching from
        text: The text to search for
        source_code: The source code bytes
        
    Returns:
        List of nodes containing the specified text
    """
    results = []
    
    def check_node(node, _):
        try:
            node_text = source_code[node.start_byte:node.end_byte].decode('utf-8', errors='replace')
            if text in node_text:
                results.append(node)
        except Exception:
            pass  # Skip nodes that can't be decoded
    
    traverse_ast(root, check_node)
    return results

def find_nodes_by_type_and_text(root: Node, node_type: str, text: str, source_code: bytes) -> List[Node]:
    """Find all nodes of a specific type containing specific text.
    
    Args:
        root: The root node to start searching from
        node_type: The type of node to find
        text: The text to search for
        source_code: The source code bytes
        
    Returns:
        List of nodes matching the criteria
    """
    results = []
    
    def check_node(node, _):
        if node.type == node_type:
            try:
                node_text = source_code[node.start_byte:node.end_byte].decode('utf-8', errors='replace')
                if text in node_text:
                    results.append(node)
            except Exception:
                pass  # Skip nodes that can't be decoded
    
    traverse_ast(root, check_node)
    return results

def get_node_children_by_type(node: Node, child_type: str) -> List[Node]:
    """Get all children of a node with a specific type.
    
    Args:
        node: The parent node
        child_type: The type of children to find
        
    Returns:
        List of child nodes matching the type
    """
    return [child for child in node.children if child.type == child_type]

def get_node_descendants(node: Node) -> List[Node]:
    """Get all descendants of a node.
    
    Args:
        node: The parent node
        
    Returns:
        List of all descendant nodes
    """
    descendants = []
    
    def collect_descendants(n, _):
        if n != node:  # Don't include the original node
            descendants.append(n)
    
    traverse_ast(node, collect_descendants)
    return descendants

def get_node_location(node: Node) -> Dict[str, int]:
    """Get the location information for a node.
    
    Args:
        node: The node to get location for
        
    Returns:
        Dictionary with start_line, end_line, start_col, end_col
    """
    return {
        'start_line': node.start_point[0],
        'start_col': node.start_point[1],
        'end_line': node.end_point[0],
        'end_col': node.end_point[1]
    }

def print_ast(node: Node, source_code: bytes, depth: int = 0, max_depth: Optional[int] = None):
    """Print the AST structure for debugging.
    
    Args:
        node: The node to print
        source_code: The source code bytes
        depth: Current depth in the tree (used for recursion)
        max_depth: Maximum depth to print (None for unlimited)
    """
    if max_depth is not None and depth > max_depth:
        return
        
    indent = "  " * depth
    try:
        node_text = source_code[node.start_byte:node.end_byte].decode('utf-8', errors='replace')
        # Truncate and clean the text for display
        if len(node_text) > 50:
            node_text = node_text[:47] + "..."
        node_text = node_text.replace("\n", "\\n")
    except Exception:
        node_text = "<binary data>"
        
    print(f"{indent}{node.type}: {node_text}")
    
    for child in node.children:
        print_ast(child, source_code, depth + 1, max_depth)
