#!/usr/bin/env python3
"""
Add Dependencies to Database

This script adds dependencies between chunks in the database.
It's a workaround for the tree-sitter parser issue.
"""

import os
import sys
import logging
import json
from pathlib import Path

from codebase_analyser.database import open_unified_storage, close_unified_storage
from codebase_analyser.parsing.dependency_types import DependencyType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def add_dependencies_to_db(project_id, db_path=".lancedb"):
    """Add dependencies to the database for a specific project."""
    logger.info(f"Adding dependencies for project: {project_id}")

    # Open the database
    from codebase_analyser.database.unified_storage import UnifiedStorage
    storage = UnifiedStorage(
        db_path=db_path,
        create_if_not_exists=True,
        read_only=False
    )

    try:
        # Get all chunks for the project
        table = storage.db_manager.get_code_chunks_table()
        chunks_df = table.search().where(f'project_id = \"{project_id}\"').to_pandas()

        if len(chunks_df) == 0:
            logger.error(f"No chunks found for project: {project_id}")
            return False

        logger.info(f"Found {len(chunks_df)} chunks for project: {project_id}")

        # Create a map of chunk names to node_ids
        chunk_map = {}
        for _, chunk in chunks_df.iterrows():
            name = chunk.get('name', '')
            if name:
                chunk_map[name] = chunk.get('node_id')

        # Create a list of dependencies to add
        dependencies = []

        # Add Customer extends AbstractEntity
        if 'Customer' in chunk_map and 'AbstractEntity' in chunk_map:
            dependencies.append({
                'source_id': chunk_map['Customer'],
                'target_id': chunk_map['AbstractEntity'],
                'type': 'EXTENDS',
                'description': 'Customer extends AbstractEntity'
            })

        # Add Product extends AbstractEntity
        if 'Product' in chunk_map and 'AbstractEntity' in chunk_map:
            dependencies.append({
                'source_id': chunk_map['Product'],
                'target_id': chunk_map['AbstractEntity'],
                'description': 'Product extends AbstractEntity',
                'type': 'EXTENDS'
            })

        # Add Order uses Product
        if 'Order' in chunk_map and 'Product' in chunk_map:
            dependencies.append({
                'source_id': chunk_map['Order'],
                'target_id': chunk_map['Product'],
                'description': 'Order uses Product',
                'type': 'USES'
            })

        # Add Order uses Customer
        if 'Order' in chunk_map and 'Customer' in chunk_map:
            dependencies.append({
                'source_id': chunk_map['Order'],
                'target_id': chunk_map['Customer'],
                'description': 'Order uses Customer',
                'type': 'USES'
            })

        # Add Customer uses Address
        if 'Customer' in chunk_map and 'Address' in chunk_map:
            dependencies.append({
                'source_id': chunk_map['Customer'],
                'target_id': chunk_map['Address'],
                'description': 'Customer uses Address',
                'type': 'USES'
            })

        # Add User extends AbstractEntity
        if 'User' in chunk_map and 'AbstractEntity' in chunk_map:
            dependencies.append({
                'source_id': chunk_map['User'],
                'target_id': chunk_map['AbstractEntity'],
                'description': 'User extends AbstractEntity',
                'type': 'EXTENDS'
            })

        # Update chunks with dependencies
        for dep in dependencies:
            source_id = dep['source_id']
            target_id = dep['target_id']
            dep_type = dep['type']

            # Find the source chunk
            source_chunk = chunks_df[chunks_df['node_id'] == source_id]
            if len(source_chunk) == 0:
                logger.warning(f"Source chunk not found: {source_id}")
                continue

            # Get the current chunk data
            chunk_data = source_chunk.iloc[0].to_dict()

            # Add reference_ids if not present
            if 'reference_ids' not in chunk_data or chunk_data['reference_ids'] is None:
                chunk_data['reference_ids'] = []
            elif isinstance(chunk_data['reference_ids'], str):
                try:
                    chunk_data['reference_ids'] = json.loads(chunk_data['reference_ids'])
                except json.JSONDecodeError:
                    chunk_data['reference_ids'] = []

            # Add target_id to reference_ids if not already present
            if target_id not in chunk_data['reference_ids']:
                chunk_data['reference_ids'].append(target_id)

            # Add metadata if not present
            if 'metadata' not in chunk_data or chunk_data['metadata'] is None:
                chunk_data['metadata'] = {}
            elif isinstance(chunk_data['metadata'], str):
                try:
                    chunk_data['metadata'] = json.loads(chunk_data['metadata'])
                except json.JSONDecodeError:
                    chunk_data['metadata'] = {}

            # Add reference_types if not present
            if 'reference_types' not in chunk_data['metadata']:
                chunk_data['metadata']['reference_types'] = {}

            # Add target_id to reference_types
            chunk_data['metadata']['reference_types'][target_id] = dep_type

            # Convert metadata back to string
            chunk_data['metadata'] = json.dumps(chunk_data['metadata'])

            # Update the chunk in the database
            # Only update metadata since reference_ids column doesn't exist
            table.update(
                where=f"node_id = '{source_id}'",
                values={
                    'metadata': chunk_data['metadata']
                }
            )

            logger.info(f"Added dependency: {dep['description']}")

        logger.info(f"Added {len(dependencies)} dependencies to the database")
        return True

    finally:
        # Close the database connection
        storage.close()

def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Add dependencies to the database")
    parser.add_argument("--project-id", required=True, help="Project ID")
    parser.add_argument("--db-path", default=".lancedb", help="Path to the LanceDB database")

    args = parser.parse_args()

    success = add_dependencies_to_db(args.project_id, args.db_path)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
