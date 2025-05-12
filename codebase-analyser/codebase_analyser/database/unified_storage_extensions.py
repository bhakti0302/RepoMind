"""
Extensions to the UnifiedStorage class for incremental updates.

This module provides additional methods for the UnifiedStorage class
to support incremental updates to the database.
"""

import logging
import json
from typing import Dict, List, Any

from .unified_storage import UnifiedStorage

logger = logging.getLogger(__name__)


def get_chunks_by_file_paths(self, file_paths: List[str], project_id: str = None) -> List[Dict[str, Any]]:
    """Get all chunks for specific file paths.
    
    Args:
        file_paths: List of file paths
        project_id: Optional project ID to filter by
        
    Returns:
        List of chunks as dictionaries
    """
    # Open the table
    table = self.db_manager.get_code_chunks_table()
    
    # Get all chunks
    chunks_df = table.to_pandas()
    
    # Filter by file paths
    file_path_chunks = chunks_df[chunks_df['file_path'].isin(file_paths)]
    
    # Filter by project ID if provided
    if project_id:
        file_path_chunks = file_path_chunks[file_path_chunks['project_id'] == project_id]
    
    # Convert to list of dictionaries
    chunks_list = file_path_chunks.to_dict('records')
    
    # Process JSON fields
    for chunk in chunks_list:
        # Convert metadata and context back to dictionaries if they are strings
        if 'metadata' in chunk and isinstance(chunk['metadata'], str):
            try:
                chunk['metadata'] = json.loads(chunk['metadata'])
            except json.JSONDecodeError:
                pass
                
        if 'context' in chunk and isinstance(chunk['context'], str):
            try:
                chunk['context'] = json.loads(chunk['context'])
            except json.JSONDecodeError:
                pass
    
    return chunks_list
    
def delete_chunks(self, node_ids: List[str]) -> int:
    """Delete chunks from the database.
    
    Args:
        node_ids: List of node IDs to delete
        
    Returns:
        Number of chunks deleted
    """
    if self.read_only:
        raise ValueError("Cannot delete chunks in read-only mode")
        
    # Open the table
    table = self.db_manager.get_code_chunks_table()
    
    # Delete the chunks
    deleted_count = 0
    for node_id in node_ids:
        try:
            # Delete the chunk
            table.delete(f"node_id = '{node_id}'")
            deleted_count += 1
        except Exception as e:
            logger.error(f"Error deleting chunk {node_id}: {e}")
            
    return deleted_count


# Monkey patch the UnifiedStorage class
UnifiedStorage.get_chunks_by_file_paths = get_chunks_by_file_paths
UnifiedStorage.delete_chunks = delete_chunks
