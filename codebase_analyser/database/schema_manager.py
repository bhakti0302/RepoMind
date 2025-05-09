"""
Schema management module for ensuring schema consistency.

This module provides functionality to ensure schema consistency across
different components and database operations.
"""

import os
import logging
import json
from typing import Dict, List, Any, Optional, Set
import pyarrow as pa

from .schema import SchemaDefinitions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SchemaManager:
    """Manager for ensuring schema consistency."""
    
    def __init__(
        self,
        embedding_dim: int = 768,
        use_minimal_schema: bool = True
    ):
        """Initialize the schema manager.
        
        Args:
            embedding_dim: Dimension of the embedding vectors
            use_minimal_schema: Whether to use the minimal schema
        """
        self.embedding_dim = embedding_dim
        self.use_minimal_schema = use_minimal_schema
        
        # Get the canonical schemas
        if use_minimal_schema:
            self.canonical_schemas = {
                "code_chunks": SchemaDefinitions.get_minimal_code_chunks_schema(embedding_dim),
                "dependencies": SchemaDefinitions.get_minimal_dependencies_schema()
            }
        else:
            self.canonical_schemas = {
                "code_chunks": SchemaDefinitions.get_code_chunks_schema(embedding_dim),
                "dependencies": SchemaDefinitions.get_dependencies_schema(),
                "embedding_metadata": SchemaDefinitions.get_embedding_metadata_schema()
            }
    
    def get_canonical_schema(self, table_name: str) -> Dict[str, pa.DataType]:
        """Get the canonical schema for a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Dictionary mapping field names to PyArrow data types
        """
        if table_name not in self.canonical_schemas:
            raise ValueError(f"Unknown table: {table_name}")
        
        return self.canonical_schemas[table_name]
    
    def get_canonical_field_names(self, table_name: str) -> Set[str]:
        """Get the canonical field names for a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Set of field names
        """
        return set(self.get_canonical_schema(table_name).keys())
    
    def validate_schema(self, table_name: str, actual_schema: pa.Schema) -> bool:
        """Validate that the actual schema matches the canonical schema.
        
        Args:
            table_name: Name of the table
            actual_schema: Actual schema of the table
            
        Returns:
            True if the schema is valid, False otherwise
        """
        canonical_schema = self.get_canonical_schema(table_name)
        canonical_field_names = set(canonical_schema.keys())
        actual_field_names = set(field.name for field in actual_schema)
        
        # Check if all canonical fields are present
        missing_fields = canonical_field_names - actual_field_names
        if missing_fields:
            logger.warning(f"Missing fields in {table_name}: {missing_fields}")
            return False
        
        # Check if there are extra fields
        extra_fields = actual_field_names - canonical_field_names
        if extra_fields:
            logger.warning(f"Extra fields in {table_name}: {extra_fields}")
            return False
        
        # Check field types
        for field_name, field_type in canonical_schema.items():
            actual_field = actual_schema.field(field_name)
            if str(actual_field.type) != str(field_type):
                logger.warning(f"Type mismatch for {field_name} in {table_name}: "
                              f"expected {field_type}, got {actual_field.type}")
                return False
        
        return True
    
    def filter_data_for_schema(
        self,
        table_name: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Filter data to match the canonical schema.
        
        Args:
            table_name: Name of the table
            data: Data to filter
            
        Returns:
            Filtered data
        """
        canonical_field_names = self.get_canonical_field_names(table_name)
        
        # Keep only fields that are in the canonical schema
        filtered_data = {k: v for k, v in data.items() if k in canonical_field_names}
        
        # Check if any fields are missing
        missing_fields = canonical_field_names - set(filtered_data.keys())
        if missing_fields:
            logger.warning(f"Missing fields in data for {table_name}: {missing_fields}")
        
        return filtered_data
    
    def filter_batch_for_schema(
        self,
        table_name: str,
        batch: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Filter a batch of data to match the canonical schema.
        
        Args:
            table_name: Name of the table
            batch: Batch of data to filter
            
        Returns:
            Filtered batch
        """
        return [self.filter_data_for_schema(table_name, item) for item in batch]
    
    def get_schema_summary(self) -> Dict[str, Any]:
        """Get a summary of the canonical schemas.
        
        Returns:
            Dictionary with schema information
        """
        summary = {
            "embedding_dim": self.embedding_dim,
            "use_minimal_schema": self.use_minimal_schema,
            "tables": {}
        }
        
        for table_name, schema in self.canonical_schemas.items():
            summary["tables"][table_name] = {
                "field_count": len(schema),
                "fields": {name: str(dtype) for name, dtype in schema.items()}
            }
        
        return summary
    
    def print_schema_summary(self) -> None:
        """Print a summary of the canonical schemas."""
        summary = self.get_schema_summary()
        
        print(f"Schema Summary (embedding_dim={summary['embedding_dim']}, "
              f"use_minimal_schema={summary['use_minimal_schema']})")
        
        for table_name, table_info in summary["tables"].items():
            print(f"\nTable: {table_name} ({table_info['field_count']} fields)")
            for field_name, field_type in table_info["fields"].items():
                print(f"  - {field_name}: {field_type}")


def get_schema_manager(
    embedding_dim: int = 768,
    use_minimal_schema: bool = True
) -> SchemaManager:
    """Get a schema manager instance.
    
    Args:
        embedding_dim: Dimension of the embedding vectors
        use_minimal_schema: Whether to use the minimal schema
        
    Returns:
        SchemaManager instance
    """
    return SchemaManager(
        embedding_dim=embedding_dim,
        use_minimal_schema=use_minimal_schema
    )
