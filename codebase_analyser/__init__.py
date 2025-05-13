from .analyser import CodebaseAnalyser
from . import database
from . import embeddings
from . import graph

# Import key components for easier access
from .database import (
    open_unified_storage,
    close_unified_storage
)

# Aliases for backward compatibility
open_db_connection = open_unified_storage
close_db_connection = close_unified_storage

__version__ = "0.1.0"