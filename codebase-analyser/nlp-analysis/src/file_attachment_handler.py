"""
File Attachment Handler module.

This module provides functionality for handling file attachments in the VS Code extension.
"""

import os
import sys
import logging
import json
import shutil
import tempfile
import mimetypes
from typing import Dict, List, Any, Optional, Union, Tuple

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for more detailed logs
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("file_attachment_handler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import local modules
from src.utils import ensure_dir, save_json, load_json

class FileAttachmentHandler:
    """Handler for file attachments in the VS Code extension."""

    def __init__(
        self,
        upload_dir: str = None,
        requirements_dir: str = None,
        allowed_extensions: List[str] = None,
        max_file_size: int = 10 * 1024 * 1024  # 10 MB
    ):
        """Initialize the file attachment handler.

        Args:
            upload_dir: Path to the upload directory
            requirements_dir: Path to the Requirements directory
            allowed_extensions: List of allowed file extensions
            max_file_size: Maximum file size in bytes
        """
        self.upload_dir = upload_dir or os.path.join(tempfile.gettempdir(), "nlp-analysis-uploads")

        # Use the absolute path to the Requirements directory
        self.requirements_dir = requirements_dir or "/Users/bhaktichindhe/Desktop/Project/RepoMind/Requirements"

        self.allowed_extensions = allowed_extensions or [".txt", ".md", ".json", ".yaml", ".yml"]
        self.max_file_size = max_file_size

        # Create directories if they don't exist
        ensure_dir(self.upload_dir)
        ensure_dir(self.requirements_dir)

        logger.info(f"Upload directory: {self.upload_dir}")
        logger.info(f"Requirements directory: {self.requirements_dir}")

    def validate_file(
        self,
        file_path: str
    ) -> Dict[str, Any]:
        """Validate a file.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary containing validation results
        """
        try:
            # Check if the file exists
            if not os.path.exists(file_path):
                return {
                    "valid": False,
                    "error": f"File not found: {file_path}"
                }

            # Check if the file is a regular file
            if not os.path.isfile(file_path):
                return {
                    "valid": False,
                    "error": f"Not a regular file: {file_path}"
                }

            # Check file extension
            _, ext = os.path.splitext(file_path)
            if self.allowed_extensions and ext.lower() not in self.allowed_extensions:
                return {
                    "valid": False,
                    "error": f"File extension not allowed: {ext}. Allowed extensions: {', '.join(self.allowed_extensions)}"
                }

            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size > self.max_file_size:
                return {
                    "valid": False,
                    "error": f"File too large: {file_size} bytes. Maximum size: {self.max_file_size} bytes"
                }

            # Get file metadata
            file_name = os.path.basename(file_path)
            file_type, _ = mimetypes.guess_type(file_path)

            return {
                "valid": True,
                "file_name": file_name,
                "file_path": file_path,
                "file_size": file_size,
                "file_type": file_type or "application/octet-stream",
                "file_extension": ext.lower()
            }

        except Exception as e:
            logger.error(f"Error validating file: {e}")
            return {
                "valid": False,
                "error": f"Error validating file: {e}"
            }

    def process_file(
        self,
        file_path: str
    ) -> Dict[str, Any]:
        """Process a file.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary containing processing results
        """
        try:
            # Validate the file
            validation_result = self.validate_file(file_path)

            if not validation_result["valid"]:
                return validation_result

            # Create a unique file name
            file_name = validation_result["file_name"]
            file_extension = validation_result["file_extension"]
            timestamp = f"{os.path.getmtime(file_path):.0f}"
            unique_file_name = f"{os.path.splitext(file_name)[0]}_{timestamp}{file_extension}"

            # Create the destination paths
            upload_dest_path = os.path.join(self.upload_dir, unique_file_name)
            requirements_dest_path = os.path.join(self.requirements_dir, file_name)

            # Copy the file to both directories
            shutil.copy2(file_path, upload_dest_path)

            try:
                # Ensure the Requirements directory exists
                os.makedirs(self.requirements_dir, exist_ok=True)

                # Copy the file to the Requirements directory
                shutil.copy2(file_path, requirements_dest_path)
                logger.info(f"Copied file to requirements directory: {requirements_dest_path}")
            except Exception as e:
                logger.error(f"Error copying file to requirements directory: {e}")
                # Continue processing even if copying to Requirements directory fails

            logger.info(f"Copied file to upload directory: {upload_dest_path}")

            # Read the file content
            with open(upload_dest_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Create processing result
            result = {
                "valid": True,
                "file_name": file_name,
                "file_path": upload_dest_path,
                "requirements_path": requirements_dest_path,
                "file_size": validation_result["file_size"],
                "file_type": validation_result["file_type"],
                "file_extension": file_extension,
                "content": content
            }

            # Save metadata
            metadata_path = os.path.join(self.upload_dir, f"{os.path.splitext(unique_file_name)[0]}_metadata.json")
            save_json(result, metadata_path)

            logger.info(f"Processed file: {file_name} -> {upload_dest_path} and {requirements_dest_path}")

            return result

        except Exception as e:
            logger.error(f"Error processing file: {e}")
            return {
                "valid": False,
                "error": f"Error processing file: {e}"
            }

    def get_file_content(
        self,
        file_path: str
    ) -> Dict[str, Any]:
        """Get file content.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary containing file content
        """
        try:
            # Validate the file
            validation_result = self.validate_file(file_path)

            if not validation_result["valid"]:
                return validation_result

            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return {
                "valid": True,
                "file_name": validation_result["file_name"],
                "file_path": file_path,
                "file_size": validation_result["file_size"],
                "file_type": validation_result["file_type"],
                "file_extension": validation_result["file_extension"],
                "content": content
            }

        except Exception as e:
            logger.error(f"Error getting file content: {e}")
            return {
                "valid": False,
                "error": f"Error getting file content: {e}"
            }

    def list_uploaded_files(self) -> List[Dict[str, Any]]:
        """List uploaded files.

        Returns:
            List of uploaded files
        """
        try:
            # Get all files in the upload directory
            files = []

            for file_name in os.listdir(self.upload_dir):
                file_path = os.path.join(self.upload_dir, file_name)

                # Skip metadata files and directories
                if file_name.endswith("_metadata.json") or not os.path.isfile(file_path):
                    continue

                # Get file metadata
                metadata_path = os.path.join(self.upload_dir, f"{os.path.splitext(file_name)[0]}_metadata.json")

                if os.path.exists(metadata_path):
                    # Load metadata
                    metadata = load_json(metadata_path)
                    files.append(metadata)
                else:
                    # Create metadata
                    validation_result = self.validate_file(file_path)

                    if validation_result["valid"]:
                        files.append(validation_result)

            return files

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
            # Check if the file exists
            if not os.path.exists(file_path):
                return {
                    "valid": False,
                    "error": f"File not found: {file_path}"
                }

            # Check if the file is in the upload directory
            if not file_path.startswith(self.upload_dir):
                return {
                    "valid": False,
                    "error": f"File not in upload directory: {file_path}"
                }

            # Get file name
            file_name = os.path.basename(file_path)

            # Delete the file
            os.remove(file_path)

            # Delete metadata file if it exists
            metadata_path = os.path.join(self.upload_dir, f"{os.path.splitext(file_name)[0]}_metadata.json")

            if os.path.exists(metadata_path):
                os.remove(metadata_path)

            logger.info(f"Deleted file: {file_path}")

            return {
                "valid": True,
                "file_path": file_path,
                "file_name": file_name
            }

        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return {
                "valid": False,
                "error": f"Error deleting file: {e}"
            }

    def clear_upload_directory(self) -> Dict[str, Any]:
        """Clear the upload directory.

        Returns:
            Dictionary containing clearing results
        """
        try:
            # Get all files in the upload directory
            files = os.listdir(self.upload_dir)

            # Delete each file
            for file_name in files:
                file_path = os.path.join(self.upload_dir, file_name)

                if os.path.isfile(file_path):
                    os.remove(file_path)

            logger.info(f"Cleared upload directory: {self.upload_dir}")

            return {
                "valid": True,
                "upload_dir": self.upload_dir,
                "files_deleted": len(files)
            }

        except Exception as e:
            logger.error(f"Error clearing upload directory: {e}")
            return {
                "valid": False,
                "error": f"Error clearing upload directory: {e}"
            }


# Example usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Handle file attachments")
    parser.add_argument("--file", help="Path to the file")
    parser.add_argument("--upload-dir", help="Path to the upload directory")
    parser.add_argument("--list", action="store_true", help="List uploaded files")
    parser.add_argument("--delete", help="Delete a file")
    parser.add_argument("--clear", action="store_true", help="Clear the upload directory")
    args = parser.parse_args()

    # Create a file attachment handler
    handler = FileAttachmentHandler(
        upload_dir=args.upload_dir
    )

    if args.file:
        # Process the file
        result = handler.process_file(args.file)

        if result["valid"]:
            print(f"Processed file: {result['file_name']} -> {result['file_path']}")
        else:
            print(f"Error: {result['error']}")

    elif args.list:
        # List uploaded files
        files = handler.list_uploaded_files()

        print(f"Uploaded files ({len(files)}):")
        for file in files:
            print(f"- {file['file_name']} ({file['file_size']} bytes)")

    elif args.delete:
        # Delete a file
        result = handler.delete_file(args.delete)

        if result["valid"]:
            print(f"Deleted file: {result['file_name']}")
        else:
            print(f"Error: {result['error']}")

    elif args.clear:
        # Clear the upload directory
        result = handler.clear_upload_directory()

        if result["valid"]:
            print(f"Cleared upload directory: {result['upload_dir']} ({result['files_deleted']} files deleted)")
        else:
            print(f"Error: {result['error']}")

    else:
        parser.print_help()
