"""
Pipeline Integration module.

This module provides functionality for integrating the NLP analysis pipeline with the VS Code extension.
"""

import os
import sys
import logging
import json
import time
import threading
from typing import Dict, List, Any, Optional, Union, Tuple, Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import local modules
from src.code_synthesis_workflow import CodeSynthesisWorkflow
from src.file_attachment_handler import FileAttachmentHandler
from src.utils import ensure_dir, save_json, load_json

class PipelineIntegration:
    """Integration of the NLP analysis pipeline with the VS Code extension."""

    def __init__(
        self,
        db_path: str = ".lancedb",
        output_dir: str = None,
        upload_dir: str = None,
        requirements_dir: str = None,
        model_name: str = "en_core_web_md"
    ):
        """Initialize the pipeline integration.

        Args:
            db_path: Path to the LanceDB database
            output_dir: Path to the output directory
            upload_dir: Path to the upload directory
            requirements_dir: Path to the Requirements directory
            model_name: Name of the spaCy model to use
        """
        self.db_path = db_path
        self.output_dir = output_dir
        self.upload_dir = upload_dir

        # Use the absolute path to the Requirements directory
        self.requirements_dir = requirements_dir or "/Users/bhaktichindhe/Desktop/Project/RepoMind/Requirements"

        self.model_name = model_name

        # Create directories if they don't exist
        if output_dir:
            ensure_dir(output_dir)
        if upload_dir:
            ensure_dir(upload_dir)
        ensure_dir(self.requirements_dir)

        # Initialize components
        self.workflow = None
        self.file_handler = None

        # Initialize progress tracking
        self.progress = {
            "status": "idle",
            "message": "",
            "progress": 0.0,
            "start_time": 0,
            "end_time": 0,
            "error": None
        }

        # Initialize background thread
        self.background_thread = None

        try:
            # Initialize file handler
            self.file_handler = FileAttachmentHandler(
                upload_dir=upload_dir,
                requirements_dir=self.requirements_dir
            )

            # Initialize workflow
            self.workflow = CodeSynthesisWorkflow(
                db_path=db_path,
                output_dir=output_dir,
                model_name=model_name
            )

            logger.info("Initialized pipeline integration")
        except Exception as e:
            logger.error(f"Error initializing pipeline integration: {e}")
            self.progress["status"] = "error"
            self.progress["message"] = f"Error initializing pipeline integration: {e}"
            self.progress["error"] = str(e)

    def get_progress(self) -> Dict[str, Any]:
        """Get the current progress.

        Returns:
            Dictionary containing progress information
        """
        return self.progress

    def _update_progress(
        self,
        status: str,
        message: str,
        progress: float = 0.0,
        error: str = None
    ):
        """Update the progress.

        Args:
            status: Status of the pipeline
            message: Progress message
            progress: Progress percentage (0.0 to 1.0)
            error: Error message
        """
        self.progress["status"] = status
        self.progress["message"] = message
        self.progress["progress"] = progress

        if status == "starting":
            self.progress["start_time"] = time.time()
            self.progress["end_time"] = 0
            self.progress["error"] = None
        elif status == "completed":
            self.progress["end_time"] = time.time()
            self.progress["progress"] = 1.0
        elif status == "error":
            self.progress["end_time"] = time.time()
            self.progress["error"] = error

        logger.info(f"Progress: {status} - {message} ({progress:.0%})")

    def process_file(
        self,
        file_path: str,
        project_id: str = None,
        rag_type: str = "multi_hop",
        callback: Callable[[Dict[str, Any]], None] = None
    ) -> Dict[str, Any]:
        """Process a file in the background.

        Args:
            file_path: Path to the file
            project_id: Project ID to filter results
            rag_type: Type of RAG to use (basic, graph, multi_hop)
            callback: Callback function to call when processing is complete

        Returns:
            Dictionary containing processing status
        """
        try:
            # Check if a background thread is already running
            if self.background_thread and self.background_thread.is_alive():
                return {
                    "status": "error",
                    "message": "A background process is already running",
                    "progress": self.progress
                }

            # Validate the file
            if not self.file_handler:
                return {
                    "status": "error",
                    "message": "File handler not initialized",
                    "progress": self.progress
                }

            validation_result = self.file_handler.validate_file(file_path)

            if not validation_result["valid"]:
                self._update_progress("error", validation_result["error"], 0.0, validation_result["error"])
                return {
                    "status": "error",
                    "message": validation_result["error"],
                    "progress": self.progress
                }

            # Update progress
            self._update_progress("starting", f"Processing file: {validation_result['file_name']}", 0.0)

            # Start background thread
            self.background_thread = threading.Thread(
                target=self._process_file_background,
                args=(file_path, project_id, rag_type, callback)
            )
            self.background_thread.daemon = True
            self.background_thread.start()

            return {
                "status": "started",
                "message": f"Started processing file: {validation_result['file_name']}",
                "progress": self.progress
            }

        except Exception as e:
            logger.error(f"Error starting file processing: {e}")
            self._update_progress("error", f"Error starting file processing: {e}", 0.0, str(e))
            return {
                "status": "error",
                "message": f"Error starting file processing: {e}",
                "progress": self.progress
            }

    def _process_file_background(
        self,
        file_path: str,
        project_id: str = None,
        rag_type: str = "multi_hop",
        callback: Callable[[Dict[str, Any]], None] = None
    ):
        """Process a file in the background.

        Args:
            file_path: Path to the file
            project_id: Project ID to filter results
            rag_type: Type of RAG to use (basic, graph, multi_hop)
            callback: Callback function to call when processing is complete
        """
        try:
            # Process the file
            self._update_progress("processing", "Processing requirements", 0.1)

            # Get file content
            file_content = self.file_handler.get_file_content(file_path)

            if not file_content["valid"]:
                self._update_progress("error", file_content["error"], 0.0, file_content["error"])
                if callback:
                    callback({
                        "status": "error",
                        "message": file_content["error"],
                        "progress": self.progress
                    })
                return

            # Create a temporary file with the content
            temp_file_path = os.path.join(self.file_handler.upload_dir, f"temp_{os.path.basename(file_path)}")

            with open(temp_file_path, 'w', encoding='utf-8') as f:
                f.write(file_content["content"])

            # Run the workflow
            self._update_progress("processing", "Running code synthesis workflow", 0.2)

            result = self.workflow.run_workflow(
                input_file=temp_file_path,
                project_id=project_id,
                rag_type=rag_type
            )

            # Check for errors
            if "error" in result:
                self._update_progress("error", result["error"], 0.0, result["error"])
                if callback:
                    callback({
                        "status": "error",
                        "message": result["error"],
                        "progress": self.progress
                    })
                return

            # Update progress
            self._update_progress("completed", "Processing completed", 1.0)

            # Call the callback
            if callback:
                callback({
                    "status": "completed",
                    "message": "Processing completed",
                    "progress": self.progress,
                    "result": result
                })

        except Exception as e:
            logger.error(f"Error processing file in background: {e}")
            self._update_progress("error", f"Error processing file: {e}", 0.0, str(e))

            if callback:
                callback({
                    "status": "error",
                    "message": f"Error processing file: {e}",
                    "progress": self.progress
                })

    def cancel_processing(self) -> Dict[str, Any]:
        """Cancel the current processing.

        Returns:
            Dictionary containing cancellation status
        """
        try:
            # Check if a background thread is running
            if not self.background_thread or not self.background_thread.is_alive():
                return {
                    "status": "error",
                    "message": "No background process is running",
                    "progress": self.progress
                }

            # Update progress
            self._update_progress("cancelled", "Processing cancelled", 0.0)

            # The thread will continue running, but the progress will be marked as cancelled
            return {
                "status": "cancelled",
                "message": "Processing cancelled",
                "progress": self.progress
            }

        except Exception as e:
            logger.error(f"Error cancelling processing: {e}")
            return {
                "status": "error",
                "message": f"Error cancelling processing: {e}",
                "progress": self.progress
            }

    def get_output_file(self) -> Dict[str, Any]:
        """Get the output file.

        Returns:
            Dictionary containing output file information
        """
        try:
            # Check if output directory is specified
            if not self.output_dir:
                return {
                    "status": "error",
                    "message": "Output directory not specified",
                    "file_path": None
                }

            # Check if output file exists
            output_file = os.path.join(self.output_dir, "llm-instructions.txt")

            if not os.path.exists(output_file):
                return {
                    "status": "error",
                    "message": "Output file not found",
                    "file_path": None
                }

            # Get file content
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()

            return {
                "status": "success",
                "message": "Output file found",
                "file_path": output_file,
                "content": content
            }

        except Exception as e:
            logger.error(f"Error getting output file: {e}")
            return {
                "status": "error",
                "message": f"Error getting output file: {e}",
                "file_path": None
            }

    def close(self):
        """Close the pipeline integration."""
        try:
            if self.workflow:
                self.workflow.close()

            logger.info("Closed pipeline integration")
        except Exception as e:
            logger.error(f"Error closing pipeline integration: {e}")


# Example usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Integrate NLP analysis pipeline with VS Code extension")
    parser.add_argument("--file", required=True, help="Path to the file")
    parser.add_argument("--project-id", help="Project ID to filter results")
    parser.add_argument("--rag-type", choices=["basic", "graph", "multi_hop"], default="multi_hop",
                        help="Type of RAG to use")
    parser.add_argument("--db-path", default=".lancedb", help="Path to the LanceDB database")
    parser.add_argument("--output-dir", help="Path to the output directory")
    parser.add_argument("--upload-dir", help="Path to the upload directory")
    parser.add_argument("--requirements-dir", help="Path to the Requirements directory")
    args = parser.parse_args()

    # Create a pipeline integration
    integration = PipelineIntegration(
        db_path=args.db_path,
        output_dir=args.output_dir,
        upload_dir=args.upload_dir,
        requirements_dir=args.requirements_dir
    )

    # Define a callback function
    def callback(result):
        print(f"\nProcessing completed with status: {result['status']}")
        print(f"Message: {result['message']}")

        if result['status'] == "completed":
            output_file = result['result'].get('output_file')
            if output_file:
                print(f"Output file: {output_file}")

    # Process the file
    result = integration.process_file(
        file_path=args.file,
        project_id=args.project_id,
        rag_type=args.rag_type,
        callback=callback
    )

    print(f"Started processing with status: {result['status']}")
    print(f"Message: {result['message']}")

    # Wait for the background thread to complete
    while integration.background_thread and integration.background_thread.is_alive():
        progress = integration.get_progress()
        print(f"\rProgress: {progress['status']} - {progress['message']} ({progress['progress']:.0%})", end="")
        time.sleep(1)

    # Close the integration
    integration.close()
