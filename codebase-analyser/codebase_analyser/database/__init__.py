"""
Database package for the codebase analyzer.
"""

from .unified_storage import UnifiedStorage

def open_unified_storage(
    db_path=None,
    embedding_dim=768,
    use_minimal_schema=True,
    create_if_not_exists=True,
    read_only=False
):
    """Open a unified storage connection."""
    return UnifiedStorage(
        db_path=db_path,
        embedding_dim=embedding_dim,
        use_minimal_schema=use_minimal_schema,
        create_if_not_exists=create_if_not_exists,
        read_only=read_only
    )

def close_unified_storage(storage):
    """Close a unified storage connection."""
    if storage:
        storage.close()

# For backward compatibility
def open_db_connection(*args, **kwargs):
    """Alias for open_unified_storage."""
    return open_unified_storage(*args, **kwargs)

def close_db_connection(connection):
    """Alias for close_unified_storage."""
    close_unified_storage(connection)
