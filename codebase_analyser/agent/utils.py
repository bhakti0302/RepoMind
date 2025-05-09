"""
Utility functions for integrating the agent with the existing codebase.
"""
import logging
from typing import Dict, List, Any, Optional

from ..database import LanceDBManager
from ..graph import DependencyGraphBuilder
from ..parsing import CodebaseAnalyser

logger = logging.getLogger(__name__)

def get_database_manager(db_path: Optional[str] = None) -> LanceDBManager:
    """
    Get a database manager instance.
    
    Args:
        db_path: Optional path to the database
        
    Returns:
        LanceDBManager instance
    """
    from ..database import LanceDBManager
    return LanceDBManager(db_path=db_path)

def get_dependency_graph_builder(db_path: Optional[str] = None) -> DependencyGraphBuilder:
    """
    Get a dependency graph builder instance.
    
    Args:
        db_path: Optional path to the database
        
    Returns:
        DependencyGraphBuilder instance
    """
    from ..graph import DependencyGraphBuilder
    return DependencyGraphBuilder(db_path=db_path)

def get_codebase_analyser(repo_path: str) -> CodebaseAnalyser:
    """
    Get a codebase analyser instance.
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        CodebaseAnalyser instance
    """
    from ..parsing import CodebaseAnalyser
    return CodebaseAnalyser(repo_path=repo_path)