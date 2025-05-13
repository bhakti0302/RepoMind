#!/usr/bin/env python3
"""
Test Dependency Storage

This script tests the dependency storage functionality.
"""

import os
import sys
import unittest
import tempfile
import shutil
from pathlib import Path

import lancedb
import pandas as pd
import numpy as np

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from codebase_analyser.database.unified_storage import UnifiedStorage
from codebase_analyser.parsing.dependency_types import DependencyType
from scripts.create_dependencies_table import create_dependencies_table


class TestDependencyStorage(unittest.TestCase):
    """Test dependency storage functionality."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for the database
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_db")

        # Create a test project ID
        self.project_id = "test_project"

        # Create a storage instance
        self.storage = UnifiedStorage(
            db_path=self.db_path,
            create_if_not_exists=True,
            read_only=False
        )

        # Create test chunks
        self.chunks = [
            {
                "node_id": "class:Customer",
                "chunk_type": "class_declaration",
                "name": "Customer",
                "qualified_name": "com.example.Customer",
                "content": "public class Customer extends AbstractEntity { ... }",
                "file_path": f"{self.project_id}/src/Customer.java",
                "start_line": 1,
                "end_line": 15,
                "language": "java",
                "project_id": self.project_id,
                "embedding": [0.0] * 10  # Dummy embedding
            },
            {
                "node_id": "class:AbstractEntity",
                "chunk_type": "class_declaration",
                "name": "AbstractEntity",
                "qualified_name": "com.example.AbstractEntity",
                "content": "public abstract class AbstractEntity { ... }",
                "file_path": f"{self.project_id}/src/AbstractEntity.java",
                "start_line": 1,
                "end_line": 10,
                "language": "java",
                "project_id": self.project_id,
                "embedding": [0.0] * 10  # Dummy embedding
            },
            {
                "node_id": "class:Product",
                "chunk_type": "class_declaration",
                "name": "Product",
                "qualified_name": "com.example.Product",
                "content": "public class Product extends AbstractEntity { ... }",
                "file_path": f"{self.project_id}/src/Product.java",
                "start_line": 1,
                "end_line": 15,
                "language": "java",
                "project_id": self.project_id,
                "embedding": [0.0] * 10  # Dummy embedding
            }
        ]

        # Store chunks in the database
        self.storage.add_code_chunks_with_graph_metadata(self.chunks)

    def tearDown(self):
        """Clean up after tests."""
        # Close the database connection
        self.storage.close()

        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)

    def test_create_dependencies_table(self):
        """Test creating the dependencies table."""
        # Create the dependencies table
        result = create_dependencies_table(self.project_id, self.db_path)

        # Check that the table was created
        self.assertTrue(result)

        # Connect to the database
        db = lancedb.connect(self.db_path)

        # Check that the dependencies table exists
        self.assertIn("dependencies", db.table_names())

        # Get the dependencies
        dependencies_table = db.open_table("dependencies")
        dependencies = dependencies_table.to_pandas()

        # Check that we have dependencies
        self.assertGreater(len(dependencies), 0)

        # Check that the dependencies have the correct project ID
        for _, dep in dependencies.iterrows():
            self.assertEqual(dep["project_id"], self.project_id)

    def test_get_dependency_graph(self):
        """Test getting the dependency graph."""
        # Create the dependencies table
        create_dependencies_table(self.project_id, self.db_path)

        # Get the dependency graph
        dependency_graph = self.storage.get_dependency_graph(self.project_id)

        # Check that the graph has nodes
        self.assertGreater(len(dependency_graph.nodes), 0)

        # Check that the graph has edges
        self.assertGreater(len(dependency_graph.edges), 0)

        # Check that Customer extends AbstractEntity
        customer_extends_abstract = False
        for edge in dependency_graph.edges:
            if (edge.source_id == "class:Customer" and
                edge.target_id == "class:AbstractEntity" and
                edge.type == DependencyType.EXTENDS):
                customer_extends_abstract = True
                break

        self.assertTrue(customer_extends_abstract)

        # Check that Product extends AbstractEntity
        product_extends_abstract = False
        for edge in dependency_graph.edges:
            if (edge.source_id == "class:Product" and
                edge.target_id == "class:AbstractEntity" and
                edge.type == DependencyType.EXTENDS):
                product_extends_abstract = True
                break

        self.assertTrue(product_extends_abstract)


if __name__ == "__main__":
    unittest.main()
