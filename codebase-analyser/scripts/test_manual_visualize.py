#!/usr/bin/env python3
"""
Test script for manual_visualize.py.

This script tests the functionality of manual_visualize.py by generating
visualizations for a test project and verifying that they are created correctly.
"""

import os
import sys
import unittest
import tempfile
import shutil
import json
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class TestManualVisualize(unittest.TestCase):
    """Test case for manual_visualize.py."""

    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory for test output
        self.test_dir = tempfile.mkdtemp()
        logger.info(f"Created temporary directory: {self.test_dir}")

        # Path to the manual_visualize.py script
        self.script_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "manual_visualize.py"
        )

        # Make sure the script exists
        self.assertTrue(os.path.exists(self.script_path), f"Script not found: {self.script_path}")

        # Default project ID for testing
        self.project_id = "testshreya"

        # Path to the database
        self.db_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            ".lancedb"
        )

        # Make sure the database exists
        self.assertTrue(os.path.exists(self.db_path), f"Database not found: {self.db_path}")

    def tearDown(self):
        """Clean up the test environment."""
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)
        logger.info(f"Removed temporary directory: {self.test_dir}")

    def test_script_execution(self):
        """Test that the script can be executed."""
        # Run the script with --help to check if it's executable
        result = subprocess.run(
            [sys.executable, self.script_path, "--help"],
            capture_output=True,
            text=True
        )

        # Check that the script executed successfully
        self.assertEqual(result.returncode, 0, f"Script execution failed: {result.stderr}")

        # Check that the help text contains expected arguments
        self.assertIn("--output-dir", result.stdout)
        self.assertIn("--project-id", result.stdout)
        self.assertIn("--db-path", result.stdout)
        self.assertIn("--test", result.stdout)

    def test_visualization_generation(self):
        """Test that visualizations can be generated."""
        # Run the script in test mode
        result = subprocess.run(
            [
                sys.executable,
                self.script_path,
                "--output-dir", self.test_dir,
                "--project-id", self.project_id,
                "--db-path", self.db_path,
                "--test"
            ],
            capture_output=True,
            text=True
        )

        # Check that the script executed successfully
        self.assertEqual(result.returncode, 0, f"Script execution failed: {result.stderr}")

        # Parse the JSON output
        try:
            # Try to extract JSON from the output
            json_match = result.stdout.strip().split('\n')[-1]
            output = json.loads(json_match)
            self.assertIn("status", output)

            # If the test failed, print the error message
            if output["status"] == "error":
                logger.error(f"Test failed: {output.get('message', 'Unknown error')}")
                logger.error(f"Stderr: {result.stderr}")
                self.fail(f"Test failed: {output.get('message', 'Unknown error')}")

            # Check that the test passed
            self.assertEqual(output["status"], "success")

        except (json.JSONDecodeError, IndexError) as e:
            # Try to find JSON in the output
            json_start = result.stdout.find('{')
            json_end = result.stdout.rfind('}')

            if json_start >= 0 and json_end >= 0:
                try:
                    json_str = result.stdout[json_start:json_end+1]
                    output = json.loads(json_str)

                    self.assertIn("status", output)

                    # If the test failed, print the error message
                    if output["status"] == "error":
                        logger.error(f"Test failed: {output.get('message', 'Unknown error')}")
                        logger.error(f"Stderr: {result.stderr}")
                        self.fail(f"Test failed: {output.get('message', 'Unknown error')}")

                    # Check that the test passed
                    self.assertEqual(output["status"], "success")
                    return
                except Exception as nested_e:
                    logger.error(f"Failed to parse JSON even after extraction: {nested_e}")

            logger.error(f"Failed to parse JSON output: {e}")
            logger.error(f"Stdout: {result.stdout}")
            logger.error(f"Stderr: {result.stderr}")
            self.fail(f"Failed to parse JSON output: {result.stdout}")

    def test_full_visualization_generation(self):
        """Test that all visualizations can be generated."""
        # Run the script to generate all visualizations
        result = subprocess.run(
            [
                sys.executable,
                self.script_path,
                "--output-dir", self.test_dir,
                "--project-id", self.project_id,
                "--db-path", self.db_path
            ],
            capture_output=True,
            text=True
        )

        # Check that the script executed successfully
        self.assertEqual(result.returncode, 0, f"Script execution failed: {result.stderr}")

        # Parse the JSON output
        try:
            # Try to extract JSON from the output
            json_match = result.stdout.strip().split('\n')[-1]
            output = json.loads(json_match)

            # Check that at least some visualizations were generated
            self.assertGreater(len(output), 0, "No visualizations were generated")

            # Check that the visualization files exist
            for viz_type, path in output.items():
                self.assertTrue(os.path.exists(path), f"{viz_type} visualization file does not exist: {path}")
                self.assertGreater(os.path.getsize(path), 0, f"{viz_type} visualization file is empty: {path}")

            logger.info(f"Generated {len(output)} visualizations: {', '.join(output.keys())}")

        except (json.JSONDecodeError, IndexError) as e:
            # Try to find JSON in the output
            json_start = result.stdout.find('{')
            json_end = result.stdout.rfind('}')

            if json_start >= 0 and json_end >= 0:
                try:
                    json_str = result.stdout[json_start:json_end+1]
                    output = json.loads(json_str)

                    # Check that at least some visualizations were generated
                    self.assertGreater(len(output), 0, "No visualizations were generated")

                    # Check that the visualization files exist
                    for viz_type, path in output.items():
                        self.assertTrue(os.path.exists(path), f"{viz_type} visualization file does not exist: {path}")
                        self.assertGreater(os.path.getsize(path), 0, f"{viz_type} visualization file is empty: {path}")

                    logger.info(f"Generated {len(output)} visualizations: {', '.join(output.keys())}")
                    return
                except Exception as nested_e:
                    logger.error(f"Failed to parse JSON even after extraction: {nested_e}")

            logger.error(f"Failed to parse JSON output: {e}")
            logger.error(f"Stdout: {result.stdout}")
            logger.error(f"Stderr: {result.stderr}")
            self.fail(f"Failed to parse JSON output: {result.stdout}")

def main():
    """Run the tests."""
    unittest.main()

if __name__ == "__main__":
    main()
