#!/usr/bin/env python3
"""
Test for the run_codebase_analysis.py script.

This test verifies that the codebase analysis service works correctly
by running it on a small test directory with mock embeddings.
"""

import os
import sys
import unittest
import tempfile
import shutil
import logging
from pathlib import Path

# Add parent directory to path to import run_codebase_analysis
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from run_codebase_analysis import analyze_codebase, parse_args

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestRunCodebaseAnalysis(unittest.TestCase):
    """Test cases for the run_codebase_analysis.py script."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()

        # Create a main Java file that imports and uses other classes
        self.main_java_path = os.path.join(self.test_dir, "Main.java")
        with open(self.main_java_path, "w") as f:
            f.write("""
import java.util.List;
import java.util.ArrayList;

public class Main {
    public static void main(String[] args) {
        // Use the SimpleClass
        SimpleClass simple = new SimpleClass();
        simple.sayHello("World");

        // Use the DataProcessor
        DataProcessor processor = new DataProcessor();
        List<String> data = new ArrayList<>();
        data.add("item1");
        data.add("item2");
        processor.process(data);
    }
}
            """)

        # Create a simple Java class that will be imported
        self.simple_class_path = os.path.join(self.test_dir, "SimpleClass.java")
        with open(self.simple_class_path, "w") as f:
            f.write("""
public class SimpleClass {
    public void sayHello(String name) {
        System.out.println("Hello, " + name + "!");
    }

    public String formatGreeting(String name) {
        return "Hello, " + name + "!";
    }
}
            """)

        # Create another Java class with dependencies
        self.data_processor_path = os.path.join(self.test_dir, "DataProcessor.java")
        with open(self.data_processor_path, "w") as f:
            f.write("""
import java.util.List;

public class DataProcessor {
    public void process(List<String> data) {
        for (String item : data) {
            System.out.println("Processing: " + item);
        }
    }
}
            """)

        # Create a Python module that imports another module
        self.main_py_path = os.path.join(self.test_dir, "main.py")
        with open(self.main_py_path, "w") as f:
            f.write("""
import utils
from data_processor import DataProcessor

def main():
    # Use the utils module
    message = utils.format_greeting("World")
    print(message)

    # Use the DataProcessor class
    processor = DataProcessor()
    processor.process(["item1", "item2"])

if __name__ == "__main__":
    main()
            """)

        # Create a Python utility module
        self.utils_py_path = os.path.join(self.test_dir, "utils.py")
        with open(self.utils_py_path, "w") as f:
            f.write("""
def format_greeting(name):
    return f"Hello, {name}!"

def hello_world():
    print("Hello, World!")
            """)

        # Create a Python data processor module
        self.data_processor_py_path = os.path.join(self.test_dir, "data_processor.py")
        with open(self.data_processor_py_path, "w") as f:
            f.write("""
class DataProcessor:
    def process(self, data):
        for item in data:
            print(f"Processing: {item}")

    def analyze(self, data):
        return len(data)
            """)

        # Create a temporary directory for the database
        self.db_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.db_dir, ".lancedb")

        # Create a temporary directory for output files
        self.output_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary directories
        shutil.rmtree(self.test_dir)
        shutil.rmtree(self.db_dir)
        shutil.rmtree(self.output_dir)

    def test_analyze_codebase_with_mock_embeddings(self):
        """Test analyzing a codebase with mock embeddings."""
        # Create a mock args object
        class MockArgs:
            repo_path = self.test_dir
            db_path = self.db_path
            clear_db = True
            minimal_schema = True
            embedding_model = "microsoft/codebert-base"
            embedding_batch_size = 8
            embedding_cache_dir = ".cache"
            mock_embeddings = True
            visualize = True
            output_dir = self.output_dir
            graph_format = "png"
            project_id = "test-project"
            max_files = 5
            skip_large_files = True

        args = MockArgs()

        # Run the analysis
        success = analyze_codebase(args)

        # Check that the analysis was successful
        self.assertTrue(success)

        # Check that the database was created
        self.assertTrue(os.path.exists(self.db_path))

        # Check that the visualization was created
        visualization_path = os.path.join(self.output_dir, "dependency_graph.png")
        self.assertTrue(os.path.exists(visualization_path))

    def test_parse_args(self):
        """Test argument parsing."""
        # Test with minimal required arguments
        sys.argv = ["run_codebase_analysis.py", "--repo-path", self.test_dir]
        args = parse_args()
        self.assertEqual(args.repo_path, self.test_dir)
        self.assertEqual(args.db_path, "codebase-analyser/.lancedb")  # Default value
        self.assertFalse(args.clear_db)  # Default value

        # Test with all arguments
        sys.argv = [
            "run_codebase_analysis.py",
            "--repo-path", self.test_dir,
            "--db-path", self.db_path,
            "--clear-db",
            "--minimal-schema",
            "--embedding-model", "custom-model",
            "--embedding-batch-size", "16",
            "--mock-embeddings",
            "--visualize",
            "--output-dir", self.output_dir,
            "--graph-format", "dot",
            "--project-id", "test-project",
            "--max-files", "10",
            "--skip-large-files"
        ]
        args = parse_args()
        self.assertEqual(args.repo_path, self.test_dir)
        self.assertEqual(args.db_path, self.db_path)
        self.assertTrue(args.clear_db)
        self.assertTrue(args.minimal_schema)
        self.assertEqual(args.embedding_model, "custom-model")
        self.assertEqual(args.embedding_batch_size, 16)
        self.assertTrue(args.mock_embeddings)
        self.assertTrue(args.visualize)
        self.assertEqual(args.output_dir, self.output_dir)
        self.assertEqual(args.graph_format, "dot")
        self.assertEqual(args.project_id, "test-project")
        self.assertEqual(args.max_files, 10)
        self.assertTrue(args.skip_large_files)


if __name__ == "__main__":
    unittest.main()
