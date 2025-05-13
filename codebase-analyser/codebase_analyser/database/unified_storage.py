"""
Unified storage for code chunks and dependency graph.
"""

import os
import json
import logging
import networkx as nx
from typing import Dict, List, Optional, Any, Union

import lancedb

logger = logging.getLogger(__name__)


class UnifiedStorage:
    """Unified storage for code chunks and dependency graph."""

    def __init__(
        self,
        db_path: str = ".lancedb",
        data_dir: str = "../data",
        use_minimal_schema: bool = False,
        create_if_not_exists: bool = True,
        read_only: bool = False
    ):
        """Initialize the unified storage.

        Args:
            db_path: Path to the LanceDB database
            data_dir: Path to the data directory for storing project-specific data
            use_minimal_schema: Whether to use a minimal schema
            create_if_not_exists: Whether to create the database if it doesn't exist
            read_only: Whether to open the database in read-only mode
        """
        self.db_path = db_path
        self.data_dir = data_dir
        self.use_minimal_schema = use_minimal_schema
        self.create_if_not_exists = create_if_not_exists
        self.read_only = read_only

        # Create database directory if it doesn't exist
        if create_if_not_exists and not os.path.exists(db_path):
            os.makedirs(db_path, exist_ok=True)

        # Create data directory if it doesn't exist
        if create_if_not_exists and not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
            # Create projects directory
            os.makedirs(os.path.join(data_dir, "projects"), exist_ok=True)

        # Connect to the database
        self.db = lancedb.connect(db_path)

        # Create the database manager
        self.db_manager = DatabaseManager(self.db, use_minimal_schema)

    def add_code_chunks_with_graph_metadata(self, chunks: List[Dict[str, Any]]) -> None:
        """Add code chunks with graph metadata to the database.

        Args:
            chunks: List of code chunks as dictionaries
        """
        if self.read_only:
            raise ValueError("Cannot add chunks in read-only mode")

        # Add chunks to the database
        self.db_manager.add_code_chunks(chunks)

    def search_code_chunks(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for code chunks in the database.

        Args:
            query: Query string
            limit: Maximum number of results to return
            filters: Filters to apply to the search

        Returns:
            List of code chunks as dictionaries
        """
        return self.db_manager.search_code_chunks(query, limit, filters)

    def _build_graph_from_dependencies(self) -> nx.DiGraph:
        """Build a NetworkX graph from the dependencies in the database.

        Returns:
            NetworkX directed graph
        """
        # Create a directed graph
        graph = nx.DiGraph()

        # Get all chunks from the database
        table = self.db_manager.get_code_chunks_table()
        chunks = table.to_pandas()

        # Add nodes to the graph
        for _, chunk in chunks.iterrows():
            graph.add_node(
                chunk['node_id'],
                type=chunk['chunk_type'],
                name=chunk['name'],
                qualified_name=chunk['qualified_name']
            )

        # Add edges based on parent-child relationships
        for _, chunk in chunks.iterrows():
            if 'parent_id' in chunk and chunk['parent_id']:
                graph.add_edge(
                    chunk['parent_id'],
                    chunk['node_id'],
                    type='CONTAINS',
                    strength=1.0,
                    is_direct=True,
                    is_required=True,
                    description='Contains'
                )

        # Add edges based on references
        for _, chunk in chunks.iterrows():
            if 'reference_ids' in chunk and chunk['reference_ids']:
                # Get reference types if available
                reference_types = {}
                if 'metadata' in chunk and chunk['metadata']:
                    try:
                        metadata = json.loads(chunk['metadata']) if isinstance(chunk['metadata'], str) else chunk['metadata']
                        if 'reference_types' in metadata:
                            reference_types = metadata['reference_types']
                    except (json.JSONDecodeError, TypeError):
                        pass

                for ref_id in chunk['reference_ids']:
                    # Determine the relationship type
                    rel_type = 'REFERENCES'
                    rel_strength = 0.8
                    rel_description = 'References'

                    if ref_id in reference_types:
                        rel_type = reference_types[ref_id]

                        # Set strength and description based on relationship type
                        if rel_type == 'IMPORTS':
                            rel_strength = 0.7
                            rel_description = 'Imports'
                        elif rel_type == 'EXTENDS':
                            rel_strength = 1.0
                            rel_description = 'Extends'
                        elif rel_type == 'IMPLEMENTS':
                            rel_strength = 0.9
                            rel_description = 'Implements'
                        elif rel_type == 'HAS_FIELD':
                            rel_strength = 0.8
                            rel_description = 'Has Field'

                    graph.add_edge(
                        chunk['node_id'],
                        ref_id,
                        type=rel_type,
                        strength=rel_strength,
                        is_direct=True,
                        is_required=(rel_type in ['EXTENDS', 'IMPLEMENTS']),
                        description=rel_description
                    )

        return graph

    def get_project_data_dir(self, project_id: str) -> str:
        """Get the data directory for a specific project.

        Args:
            project_id: Project ID

        Returns:
            Path to the project data directory
        """
        project_dir = os.path.join(self.data_dir, "projects", project_id)
        if self.create_if_not_exists and not os.path.exists(project_dir):
            os.makedirs(project_dir, exist_ok=True)
            # Create subdirectories for different types of data
            os.makedirs(os.path.join(project_dir, "visualizations"), exist_ok=True)
            os.makedirs(os.path.join(project_dir, "exports"), exist_ok=True)

        return project_dir

    def save_project_visualization(self, project_id: str, file_name: str, content: bytes) -> str:
        """Save a visualization for a specific project.

        Args:
            project_id: Project ID
            file_name: Name of the file
            content: Content of the file

        Returns:
            Path to the saved file
        """
        if self.read_only:
            raise ValueError("Cannot save visualization in read-only mode")

        project_dir = self.get_project_data_dir(project_id)
        vis_dir = os.path.join(project_dir, "visualizations")
        file_path = os.path.join(vis_dir, file_name)

        with open(file_path, "wb") as f:
            f.write(content)

        return file_path

    def export_project_chunks(self, project_id: str) -> str:
        """Export all chunks for a specific project to a JSON file.

        Args:
            project_id: Project ID

        Returns:
            Path to the exported file
        """
        if self.read_only:
            raise ValueError("Cannot export chunks in read-only mode")

        # Get all chunks for the project
        table = self.db_manager.get_code_chunks_table()
        chunks_df = table.to_pandas()
        project_chunks = chunks_df[chunks_df['project_id'] == project_id]

        # Convert to list of dictionaries
        chunks_list = project_chunks.to_dict('records')

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

            # Remove embedding to reduce file size
            if 'embedding' in chunk:
                del chunk['embedding']

        # Create the export directory
        project_dir = self.get_project_data_dir(project_id)
        export_dir = os.path.join(project_dir, "exports")
        os.makedirs(export_dir, exist_ok=True)

        # Save to file
        export_file = os.path.join(export_dir, f"{project_id}_chunks.json")
        with open(export_file, 'w') as f:
            json.dump(chunks_list, f, indent=2)

        return export_file

    def update_last_sync_time(self, project_id: str) -> str:
        """Update the last sync time for a project.

        Args:
            project_id: Project ID

        Returns:
            Timestamp string in ISO format
        """
        if self.read_only:
            raise ValueError("Cannot update last sync time in read-only mode")

        return self.db_manager.update_last_sync_time(project_id)

    def get_last_sync_time(self, project_id: str) -> Optional[str]:
        """Get the last sync time for a project.

        Args:
            project_id: Project ID

        Returns:
            Timestamp string in ISO format, or None if not found
        """
        return self.db_manager.get_last_sync_time(project_id)

    def close(self) -> None:
        """Close the database connection."""
        # LanceDB doesn't have an explicit close method
        self.db = None


class DatabaseManager:
    """Manager for the LanceDB database."""

    def __init__(self, db, use_minimal_schema: bool = False):
        """Initialize the database manager.

        Args:
            db: LanceDB database connection
            use_minimal_schema: Whether to use a minimal schema
        """
        self.db = db
        self.use_minimal_schema = use_minimal_schema

        # Define table names
        self.code_chunks_table_name = "code_chunks"
        self.metadata_table_name = "metadata"

    def clear_tables(self) -> None:
        """Clear all tables in the database."""
        # Drop the code chunks table if it exists
        if self.code_chunks_table_name in self.db.table_names():
            self.db.drop_table(self.code_chunks_table_name)

    def get_code_chunks_table(self):
        """Get the code chunks table.

        Returns:
            LanceDB table for code chunks
        """
        if self.code_chunks_table_name not in self.db.table_names():
            raise ValueError(f"Table {self.code_chunks_table_name} does not exist")

        return self.db.open_table(self.code_chunks_table_name)

    def add_code_chunks(self, chunks: List[Dict[str, Any]]) -> None:
        """Add code chunks to the database.

        Args:
            chunks: List of code chunks as dictionaries
        """
        # Convert JSON fields to strings
        for chunk in chunks:
            if 'metadata' in chunk and chunk['metadata']:
                chunk['metadata'] = json.dumps(chunk['metadata'])
            if 'context' in chunk and chunk['context']:
                chunk['context'] = json.dumps(chunk['context'])

        # Check if the table exists
        if self.code_chunks_table_name not in self.db.table_names():
            # Create the table with inferred schema
            self.db.create_table(self.code_chunks_table_name, data=chunks)
        else:
            # Open the table
            table = self.db.open_table(self.code_chunks_table_name)

            # Add the chunks
            table.add(chunks)

    def search_code_chunks(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for code chunks in the database.

        Args:
            query: Query string
            limit: Maximum number of results to return
            filters: Filters to apply to the search

        Returns:
            List of code chunks as dictionaries
        """
        try:
            # Open the table
            table = self.get_code_chunks_table()

            # Try to use the built-in search first
            try:
                # Create the search query
                search_query = table.search(query)

                # Apply filters if provided
                if filters:
                    for key, value in filters.items():
                        search_query = search_query.where(f"{key} = '{value}'")

                # Execute the search
                results = search_query.limit(limit).to_pandas()

                # Convert to list of dictionaries
                return results.to_dict('records')

            except Exception as e:
                # If the built-in search fails (e.g., due to missing tantivy),
                # fall back to a basic text search implementation
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Built-in search failed: {e}. Falling back to basic text search.")

                # Get all data from the table
                all_data = table.to_pandas()

                # Apply filters if provided
                if filters:
                    for key, value in filters.items():
                        all_data = all_data[all_data[key] == value]

                # Split query into keywords
                keywords = query.lower().split()

                # Score each row based on keyword matches
                scores = []
                for idx, row in all_data.iterrows():
                    score = 0

                    # Check for matches in content field
                    if 'content' in row:
                        content = str(row['content']).lower()
                        for keyword in keywords:
                            if keyword in content:
                                score += 1

                    # Check for matches in name field
                    if 'name' in row:
                        name = str(row['name']).lower()
                        for keyword in keywords:
                            if keyword in name:
                                score += 2  # Name matches are more important

                    # Check for matches in qualified_name field
                    if 'qualified_name' in row:
                        qualified_name = str(row['qualified_name']).lower()
                        for keyword in keywords:
                            if keyword in qualified_name:
                                score += 1.5

                    # Check for matches in file_path field
                    if 'file_path' in row:
                        file_path = str(row['file_path']).lower()
                        for keyword in keywords:
                            if keyword in file_path:
                                score += 0.5

                    # Add the score
                    scores.append((idx, score))

                # Sort by score (descending)
                scores.sort(key=lambda x: x[1], reverse=True)

                # Get the top results
                top_indices = [idx for idx, score in scores[:limit] if score > 0]

                # Get the corresponding rows
                results = all_data.loc[top_indices]

                # Add score to results
                results_with_scores = []
                for idx, row in results.iterrows():
                    row_dict = row.to_dict()
                    score = next(score for i, score in scores if i == idx)
                    row_dict['score'] = score / len(keywords) if keywords else 0
                    results_with_scores.append(row_dict)

                return results_with_scores

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in search_code_chunks: {e}")
            return []

    def update_last_sync_time(self, project_id: str) -> str:
        """Update the last sync time for a project.

        Args:
            project_id: Project ID

        Returns:
            Timestamp string in ISO format
        """
        import datetime

        # Get current timestamp in ISO format
        timestamp = datetime.datetime.now().isoformat()

        # Check if the metadata table exists
        if self.metadata_table_name not in self.db.table_names():
            # Create the metadata table
            self.db.create_table(
                self.metadata_table_name,
                data=[{
                    "project_id": project_id,
                    "last_sync_time": timestamp,
                    "embedding": [0.0] * 10  # Dummy embedding required by LanceDB
                }]
            )
        else:
            # Open the metadata table
            table = self.db.open_table(self.metadata_table_name)

            # Check if the project exists in the metadata table
            try:
                # Try to get the project's metadata
                result = table.search().where(f"project_id = '{project_id}'").to_pandas()

                if len(result) > 0:
                    # Update the existing record
                    table.update(
                        where=f"project_id = '{project_id}'",
                        values={"last_sync_time": timestamp}
                    )
                else:
                    # Add a new record
                    table.add([{
                        "project_id": project_id,
                        "last_sync_time": timestamp,
                        "embedding": [0.0] * 10  # Dummy embedding required by LanceDB
                    }])
            except Exception as e:
                # If there's an error, create a new record
                table.add([{
                    "project_id": project_id,
                    "last_sync_time": timestamp,
                    "embedding": [0.0] * 10  # Dummy embedding required by LanceDB
                }])

        return timestamp

    def get_last_sync_time(self, project_id: str) -> Optional[str]:
        """Get the last sync time for a project.

        Args:
            project_id: Project ID

        Returns:
            Timestamp string in ISO format, or None if not found
        """
        # Check if the metadata table exists
        if self.metadata_table_name not in self.db.table_names():
            return None

        # Open the metadata table
        table = self.db.open_table(self.metadata_table_name)

        try:
            # Try to get the project's metadata
            result = table.search().where(f"project_id = '{project_id}'").to_pandas()

            if len(result) > 0:
                # Return the last sync time
                return result.iloc[0]["last_sync_time"]
        except Exception as e:
            # If there's an error, return None
            pass

        return None
