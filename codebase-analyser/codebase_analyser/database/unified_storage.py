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

    def search_with_combined_scoring(
        self,
        query_embedding: List[float],
        query_node_id: str,
        alpha: float = 0.7,
        beta: float = 0.3,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for code chunks using combined semantic and graph-based scoring.

        This method combines vector similarity with graph proximity to provide more
        contextually relevant results. It takes into account:

        1. Semantic similarity (vector distance)
        2. Graph proximity (shortest path distance)
        3. Relationship attributes (strength, frequency, bidirectionality, etc.)

        Args:
            query_embedding: Query embedding vector
            query_node_id: Node ID to use as the starting point for graph proximity
            alpha: Weight for semantic similarity (0.0 to 1.0)
            beta: Weight for graph proximity (0.0 to 1.0)
            limit: Maximum number of results to return
            filters: Filters to apply to the search

        Returns:
            List of code chunks as dictionaries, sorted by combined score
        """
        import numpy as np
        import networkx as nx

        # Normalize weights
        total = alpha + beta
        alpha = alpha / total
        beta = beta / total

        # Get the code chunks table
        table = self.db_manager.get_code_chunks_table()

        # Create the search query
        search_query = table.search(query_embedding)

        # Apply filters if provided
        if filters:
            for key, value in filters.items():
                search_query = search_query.where(f"{key} = '{value}'")

        # Get more results than needed for reranking
        search_limit = min(limit * 3, 100)  # Get 3x results or max 100
        results = search_query.limit(search_limit).to_pandas()

        # Convert to list of dictionaries
        chunks = results.to_dict('records')

        # If no results or query_node_id is not provided, return semantic results only
        if not chunks or not query_node_id:
            return chunks[:limit]

        # Build the graph
        graph = self._build_graph_from_dependencies()

        # Calculate combined scores
        for chunk in chunks:
            # Get node ID
            node_id = chunk['node_id']

            # Calculate semantic score (already normalized by LanceDB)
            semantic_score = chunk.get('_distance', 0.0)
            # Convert distance to similarity (1.0 - distance)
            semantic_score = 1.0 - semantic_score

            # Calculate graph proximity
            graph_distance = float('inf')
            try:
                # Check if both nodes exist in the graph
                if query_node_id in graph and node_id in graph:
                    # Calculate shortest path length
                    try:
                        # Get all paths between the nodes
                        paths = list(nx.all_simple_paths(graph, query_node_id, node_id, cutoff=5))

                        if paths:
                            # Calculate path scores considering relationship attributes
                            path_scores = []
                            for path in paths:
                                path_score = 0.0

                                # Calculate score for each edge in the path
                                for i in range(len(path) - 1):
                                    source = path[i]
                                    target = path[i + 1]

                                    # Get edge attributes
                                    edge_attrs = graph.get_edge_data(source, target)

                                    # Base edge score is the strength
                                    edge_score = edge_attrs.get('strength', 0.5)

                                    # Adjust score based on relationship attributes

                                    # Frequency: More frequent relationships are more important
                                    frequency = edge_attrs.get('frequency', 1)
                                    frequency_factor = min(1.0, 0.5 + (0.1 * frequency))

                                    # Bidirectionality: Bidirectional relationships are stronger
                                    is_bidirectional = edge_attrs.get('is_bidirectional', False)
                                    bidirectional_factor = 1.2 if is_bidirectional else 1.0

                                    # Transitivity: Direct relationships are stronger than transitive ones
                                    is_transitive = edge_attrs.get('is_transitive', False)
                                    transitive_factor = 0.8 if is_transitive else 1.0

                                    # Inference confidence: Inferred relationships have lower confidence
                                    is_inferred = edge_attrs.get('is_inferred', False)
                                    inference_confidence = edge_attrs.get('inference_confidence', 1.0)
                                    inference_factor = inference_confidence if is_inferred else 1.0

                                    # Combine all factors
                                    edge_score *= frequency_factor * bidirectional_factor * transitive_factor * inference_factor

                                    # Add to path score
                                    path_score += edge_score

                                # Normalize by path length
                                if len(path) > 1:
                                    path_score /= (len(path) - 1)

                                path_scores.append(path_score)

                            # Use the highest path score
                            best_path_score = max(path_scores)

                            # Convert to distance (lower is better)
                            graph_distance = 1.0 / (1.0 + best_path_score)
                        else:
                            # No path found, use default distance
                            graph_distance = float('inf')
                    except nx.NetworkXNoPath:
                        # No path found, use default distance
                        graph_distance = float('inf')
            except Exception as e:
                # Error calculating graph distance
                print(f"Error calculating graph distance: {e}")
                graph_distance = float('inf')

            # Convert graph distance to proximity score (1.0 / (1.0 + distance))
            graph_proximity = 1.0 / (1.0 + graph_distance) if graph_distance != float('inf') else 0.0

            # Calculate combined score
            combined_score = (alpha * semantic_score) + (beta * graph_proximity)

            # Store scores in the chunk
            chunk['semantic_score'] = semantic_score
            chunk['graph_proximity'] = graph_proximity
            chunk['combined_score'] = combined_score

        # Sort by combined score (descending)
        chunks.sort(key=lambda x: x.get('combined_score', 0.0), reverse=True)

        # Return top results
        return chunks[:limit]

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

        # Check if dependencies table exists
        if "dependencies" in self.db.table_names():
            try:
                # Get dependencies from the dependencies table
                dependencies_table = self.db.open_table("dependencies")
                dependencies = dependencies_table.to_pandas()

                # Add edges from dependencies
                for _, dep in dependencies.iterrows():
                    # Get relationship attributes
                    source_id = dep.get('source_id')
                    target_id = dep.get('target_id')
                    rel_type = dep.get('type', 'REFERENCES')
                    description = dep.get('description', 'References')

                    # Determine relationship strength
                    rel_strength = 0.8  # Default strength
                    if rel_type == 'IMPORTS':
                        rel_strength = 0.7
                    elif rel_type == 'EXTENDS':
                        rel_strength = 1.0
                    elif rel_type == 'IMPLEMENTS':
                        rel_strength = 0.9
                    elif rel_type == 'USES':
                        rel_strength = 0.8
                    elif rel_type == 'HAS_FIELD':
                        rel_strength = 0.8

                    # Add the edge to the graph
                    graph.add_edge(
                        source_id,
                        target_id,
                        type=rel_type,
                        strength=rel_strength,
                        is_direct=True,
                        is_required=(rel_type in ['EXTENDS', 'IMPLEMENTS']),
                        description=description,
                        # Add new relationship attributes
                        frequency=dep.get('frequency', 1),
                        is_bidirectional=dep.get('is_bidirectional', False),
                        group_id=dep.get('group_id', None),
                        is_transitive=dep.get('is_transitive', False),
                        transitive_path_length=dep.get('transitive_path_length', 0),
                        is_inferred=dep.get('is_inferred', False),
                        inference_confidence=dep.get('inference_confidence', 1.0)
                    )

                print(f"Added {len(dependencies)} edges from dependencies table")
            except Exception as e:
                print(f"Error reading dependencies table: {e}")

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

    def get_dependency_graph(self, project_id: str):
        """Get the dependency graph for a project.

        Args:
            project_id: Project ID

        Returns:
            Dependency graph object or None if not found
        """
        from codebase_analyser.parsing.dependency_analyzer import DependencyGraph
        from codebase_analyser.parsing.dependency_types import DependencyType, Dependency

        # Create a new dependency graph
        dependency_graph = DependencyGraph()

        # Get all chunks for this project
        table = self.db_manager.get_code_chunks_table()
        chunks_df = table.search().where(f'project_id = \"{project_id}\"').to_pandas()

        # Get node IDs for this project
        project_nodes = chunks_df['node_id'].tolist()

        # Add nodes to the dependency graph
        for _, chunk in chunks_df.iterrows():
            node_id = chunk['node_id']
            dependency_graph.add_node(
                node_id=node_id,
                node_type=chunk['chunk_type'],
                name=chunk['name'],
                qualified_name=chunk['qualified_name']
            )

        # Check if dependencies table exists
        if "dependencies" in self.db.table_names():
            try:
                # Get dependencies for this project
                dependencies_table = self.db.open_table("dependencies")
                dependencies_df = dependencies_table.search().where(f'project_id = \"{project_id}\"').to_pandas()

                # Add edges from dependencies
                for _, dep in dependencies_df.iterrows():
                    source_id = dep['source_id']
                    target_id = dep['target_id']

                    # Skip if source or target is not in project nodes
                    if source_id not in project_nodes or target_id not in project_nodes:
                        continue

                    # Convert type string to DependencyType enum
                    try:
                        dep_type = DependencyType[dep['type']]
                    except (KeyError, ValueError):
                        dep_type = DependencyType.REFERENCES

                    # Create dependency object
                    dependency = Dependency(
                        source_id=source_id,
                        target_id=target_id,
                        dep_type=dep_type,
                        strength=0.8,  # Default strength
                        is_required=(dep['type'] in ['EXTENDS', 'IMPLEMENTS']),
                        description=dep['description']
                    )

                    # Add edge to dependency graph
                    dependency_graph.add_edge(dependency)

                print(f"Added {len(dependencies_df)} dependencies from dependencies table")
            except Exception as e:
                print(f"Error getting dependencies: {e}")

                # Fall back to building from the general graph
                graph = self._build_graph_from_dependencies()

                # Add edges to the dependency graph
                for u, v, attrs in graph.edges(data=True):
                    if u in project_nodes and v in project_nodes:
                        # Convert edge type string to DependencyType enum
                        try:
                            dep_type = DependencyType[attrs.get('type', 'REFERENCES')]
                        except (KeyError, ValueError):
                            dep_type = DependencyType.REFERENCES

                        # Create a dependency object
                        dependency = Dependency(
                            source_id=u,
                            target_id=v,
                            dep_type=dep_type,
                            strength=attrs.get('strength', 0.5),
                            is_required=attrs.get('is_required', False),
                            description=attrs.get('description', '')
                        )

                        # Add the edge to the dependency graph
                        dependency_graph.add_edge(dependency)
        else:
            print("No dependencies table found, using general graph")

            # Build the graph from the database
            graph = self._build_graph_from_dependencies()

            # Add edges to the dependency graph
            for u, v, attrs in graph.edges(data=True):
                if u in project_nodes and v in project_nodes:
                    # Convert edge type string to DependencyType enum
                    try:
                        dep_type = DependencyType[attrs.get('type', 'REFERENCES')]
                    except (KeyError, ValueError):
                        dep_type = DependencyType.REFERENCES

                    # Create a dependency object
                    dependency = Dependency(
                        source_id=u,
                        target_id=v,
                        dep_type=dep_type,
                        strength=attrs.get('strength', 0.5),
                        is_required=attrs.get('is_required', False),
                        description=attrs.get('description', '')
                    )

                    # Add the edge to the dependency graph
                    dependency_graph.add_edge(dependency)

        return dependency_graph

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
        # Open the table
        table = self.get_code_chunks_table()

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
