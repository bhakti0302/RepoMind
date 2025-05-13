"""
VS Code Integration module.

This module provides the main integration with the VS Code extension.
"""

import os
import sys
import logging
import json
import argparse
import time
from typing import Dict, List, Any, Optional, Union, Tuple, Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("vscode_integration.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import local modules
#from src.file_attachment_handler import FileAttachmentHandler
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.file_attachment_handler import FileAttachmentHandler
#from codebase_analyser.nlp_analysis.src.file_attachment_handler import FileAttachmentHandler
from src.pipeline_integration import PipelineIntegration
from src.output_display import OutputDisplay
from src.utils import ensure_dir, save_json, load_json

class VSCodeIntegration:
    """Main integration with the VS Code extension."""

    def __init__(
        self,
        db_path: str = ".lancedb",
        output_dir: str = None,
        upload_dir: str = None,
        requirements_dir: str = None,
        model_name: str = "en_core_web_md",
        format_type: str = "markdown"
    ):
        """Initialize the VS Code integration.

        Args:
            db_path: Path to the LanceDB database
            output_dir: Path to the output directory
            upload_dir: Path to the upload directory
            requirements_dir: Path to the Requirements directory
            model_name: Name of the spaCy model to use
            format_type: Format type for the output (markdown, text)
        """
        self.db_path = db_path
        self.output_dir = output_dir
        self.upload_dir = upload_dir

        # Use the absolute path to the Requirements directory
        self.requirements_dir = requirements_dir or "/Users/bhaktichindhe/Desktop/Project/RepoMind/Requirements"

        self.model_name = model_name
        self.format_type = format_type

        # Create directories if they don't exist
        if output_dir:
            ensure_dir(output_dir)
        if upload_dir:
            ensure_dir(upload_dir)
        ensure_dir(self.requirements_dir)

        # Initialize components
        self.file_handler = None
        self.pipeline = None
        self.display = None

        try:
            # Initialize file handler
            self.file_handler = FileAttachmentHandler(
                upload_dir=upload_dir,
                requirements_dir=self.requirements_dir
            )

            # Initialize pipeline
            self.pipeline = PipelineIntegration(
                db_path=db_path,
                output_dir=output_dir,
                upload_dir=upload_dir,
                model_name=model_name
            )

            # Initialize display
            self.display = OutputDisplay(
                output_dir=output_dir,
                format_type=format_type
            )

            logger.info("Initialized VS Code integration")
        except Exception as e:
            logger.error(f"Error initializing VS Code integration: {e}")
            raise

    def handle_file_attachment(
        self,
        file_path: str
    ) -> Dict[str, Any]:
        """Handle a file attachment.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary containing handling results
        """
        try:
            # Process the file
            result = self.file_handler.process_file(file_path)

            if not result["valid"]:
                return {
                    "status": "error",
                    "message": result["error"],
                    "result": None
                }

            return {
                "status": "success",
                "message": f"Processed file: {result['file_name']}",
                "result": result
            }

        except Exception as e:
            logger.error(f"Error handling file attachment: {e}")
            return {
                "status": "error",
                "message": f"Error handling file attachment: {e}",
                "result": None
            }

    def process_requirements(
        self,
        file_path: str,
        project_id: str = None,
        rag_type: str = "multi_hop",
        callback: Callable[[Dict[str, Any]], None] = None
    ) -> Dict[str, Any]:
        """Process requirements.

        Args:
            file_path: Path to the file
            project_id: Project ID to filter results
            rag_type: Type of RAG to use (basic, graph, multi_hop)
            callback: Callback function to call when processing is complete

        Returns:
            Dictionary containing processing status
        """
        try:
            # Process the file
            result = self.pipeline.process_file(
                file_path=file_path,
                project_id=project_id,
                rag_type=rag_type,
                callback=self._process_callback(callback)
            )

            return result

        except Exception as e:
            logger.error(f"Error processing requirements: {e}")
            return {
                "status": "error",
                "message": f"Error processing requirements: {e}",
                "progress": self.pipeline.get_progress()
            }

    def _process_callback(
        self,
        callback: Callable[[Dict[str, Any]], None]
    ) -> Callable[[Dict[str, Any]], None]:
        """Create a callback function for processing.

        Args:
            callback: Original callback function

        Returns:
            Wrapped callback function
        """
        def wrapped_callback(result):
            try:
                # Format the result for chat
                if result["status"] == "completed" and "result" in result:
                    # Create an HTML view
                    html_result = self.display.create_html_view(result["result"])

                    if html_result["status"] == "success":
                        result["html_view"] = html_result["file_path"]

                    # Format for chat
                    chat_output = self.display.format_for_chat(result["result"])
                    result["chat_output"] = chat_output

                # Call the original callback
                if callback:
                    callback(result)

            except Exception as e:
                logger.error(f"Error in process callback: {e}")
                if callback:
                    callback({
                        "status": "error",
                        "message": f"Error in process callback: {e}",
                        "progress": self.pipeline.get_progress()
                    })

        return wrapped_callback

    def get_progress(self) -> Dict[str, Any]:
        """Get the current progress.

        Returns:
            Dictionary containing progress information
        """
        try:
            return self.pipeline.get_progress()

        except Exception as e:
            logger.error(f"Error getting progress: {e}")
            return {
                "status": "error",
                "message": f"Error getting progress: {e}",
                "progress": 0.0
            }

    def cancel_processing(self) -> Dict[str, Any]:
        """Cancel the current processing.

        Returns:
            Dictionary containing cancellation status
        """
        try:
            return self.pipeline.cancel_processing()

        except Exception as e:
            logger.error(f"Error cancelling processing: {e}")
            return {
                "status": "error",
                "message": f"Error cancelling processing: {e}",
                "progress": self.pipeline.get_progress()
            }

    def get_output_file(self) -> Dict[str, Any]:
        """Get the output file.

        Returns:
            Dictionary containing output file information
        """
        try:
            return self.pipeline.get_output_file()

        except Exception as e:
            logger.error(f"Error getting output file: {e}")
            return {
                "status": "error",
                "message": f"Error getting output file: {e}",
                "file_path": None
            }

    def list_uploaded_files(self) -> List[Dict[str, Any]]:
        """List uploaded files.

        Returns:
            List of uploaded files
        """
        try:
            return self.file_handler.list_uploaded_files()

        except Exception as e:
            logger.error(f"Error listing uploaded files: {e}")
            return []

    def delete_file(
        self,
        file_path: str
    ) -> Dict[str, Any]:
        """Delete a file.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary containing deletion results
        """
        try:
            return self.file_handler.delete_file(file_path)

        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return {
                "status": "error",
                "message": f"Error deleting file: {e}",
                "file_path": None
            }

    def clear_upload_directory(self) -> Dict[str, Any]:
        """Clear the upload directory.

        Returns:
            Dictionary containing clearing results
        """
        try:
            return self.file_handler.clear_upload_directory()

        except Exception as e:
            logger.error(f"Error clearing upload directory: {e}")
            return {
                "status": "error",
                "message": f"Error clearing upload directory: {e}",
                "upload_dir": None
            }

    def close(self):
        """Close the VS Code integration."""
        try:
            if self.pipeline:
                self.pipeline.close()

            logger.info("Closed VS Code integration")
        except Exception as e:
            logger.error(f"Error closing VS Code integration: {e}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Integrate with VS Code extension")

    # Command subparsers
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Process command
    process_parser = subparsers.add_parser("process", help="Process requirements")
    process_parser.add_argument("--file", required=True, help="Path to the file")
    process_parser.add_argument("--project-id", help="Project ID to filter results")
    process_parser.add_argument("--rag-type", choices=["basic", "graph", "multi_hop"], default="multi_hop",
                                help="Type of RAG to use")

    # Upload command
    upload_parser = subparsers.add_parser("upload", help="Upload a file")
    upload_parser.add_argument("--file", required=True, help="Path to the file")

    # List command
    list_parser = subparsers.add_parser("list", help="List uploaded files")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a file")
    delete_parser.add_argument("--file", required=True, help="Path to the file")

    # Clear command
    clear_parser = subparsers.add_parser("clear", help="Clear the upload directory")

    # Output command
    output_parser = subparsers.add_parser("output", help="Get the output file")

    # Progress command
    progress_parser = subparsers.add_parser("progress", help="Get the current progress")

    # Cancel command
    cancel_parser = subparsers.add_parser("cancel", help="Cancel the current processing")

    # Common arguments
    parser.add_argument("--db-path", default=".lancedb", help="Path to the LanceDB database")
    parser.add_argument("--output-dir", default="output", help="Path to the output directory")
    parser.add_argument("--upload-dir", default="uploads", help="Path to the upload directory")
    parser.add_argument("--requirements-dir", help="Path to the Requirements directory")
    parser.add_argument("--format", choices=["markdown", "text"], default="markdown",
                        help="Format type for the output")

    args = parser.parse_args()

    # Create the VS Code integration
    integration = VSCodeIntegration(
        db_path=args.db_path,
        output_dir=args.output_dir,
        upload_dir=args.upload_dir,
        requirements_dir=args.requirements_dir,
        format_type=args.format
    )

    try:
        # Execute the command
        if args.command == "process":
            # Define a callback function
            def callback(result):
                print(json.dumps(result, indent=2))
                sys.exit(0)

            # Process the file
            result = integration.process_requirements(
                file_path=args.file,
                project_id=args.project_id,
                rag_type=args.rag_type,
                callback=callback
            )

            print(json.dumps(result, indent=2))

            # Wait for the background thread to complete
            while True:
                progress = integration.get_progress()
                if progress["status"] in ["completed", "error", "cancelled"]:
                    break
                time.sleep(1)

        elif args.command == "upload":
            # Upload the file
            result = integration.handle_file_attachment(args.file)
            print(json.dumps(result, indent=2))

        elif args.command == "list":
            # List uploaded files
            files = integration.list_uploaded_files()
            print(json.dumps(files, indent=2))

        elif args.command == "delete":
            # Delete the file
            result = integration.delete_file(args.file)
            print(json.dumps(result, indent=2))

        elif args.command == "clear":
            # Clear the upload directory
            result = integration.clear_upload_directory()
            print(json.dumps(result, indent=2))

        elif args.command == "output":
            # Get the output file
            result = integration.get_output_file()
            print(json.dumps(result, indent=2))

        elif args.command == "progress":
            # Get the current progress
            progress = integration.get_progress()
            print(json.dumps(progress, indent=2))

        elif args.command == "cancel":
            # Cancel the current processing
            result = integration.cancel_processing()
            print(json.dumps(result, indent=2))

        else:
            parser.print_help()

    finally:
        # Close the integration
        integration.close()


if __name__ == "__main__":
    main()
