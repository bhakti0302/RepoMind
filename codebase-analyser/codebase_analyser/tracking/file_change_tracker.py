"""
File change tracking system for incremental updates.

This module provides functionality to track changes in files and determine
which files need to be reprocessed for database updates.
"""

import os
import json
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Set, Optional, Any, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class FileChangeTracker:
    """Tracks file changes for incremental updates to the database."""

    def __init__(self, data_dir: str, project_id: str):
        """Initialize the file change tracker.

        Args:
            data_dir: Path to the data directory
            project_id: Project ID
        """
        self.data_dir = Path(data_dir)
        self.project_id = project_id
        self.project_dir = self.data_dir / "projects" / project_id
        self.tracking_dir = self.project_dir / "tracking"
        self.file_hashes_path = self.tracking_dir / "file_hashes.json"
        
        # Create tracking directory if it doesn't exist
        os.makedirs(self.tracking_dir, exist_ok=True)
        
        # Load existing file hashes if available
        self.file_hashes = self._load_file_hashes()
        
    def _load_file_hashes(self) -> Dict[str, Dict[str, Any]]:
        """Load existing file hashes from disk.

        Returns:
            Dictionary mapping file paths to their hash information
        """
        if not self.file_hashes_path.exists():
            return {}
        
        try:
            with open(self.file_hashes_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading file hashes: {e}")
            return {}
    
    def _save_file_hashes(self) -> None:
        """Save file hashes to disk."""
        try:
            with open(self.file_hashes_path, 'w') as f:
                json.dump(self.file_hashes, f, indent=2)
        except IOError as e:
            logger.error(f"Error saving file hashes: {e}")
    
    def compute_file_hash(self, file_path: Path) -> str:
        """Compute the hash of a file.

        Args:
            file_path: Path to the file

        Returns:
            SHA-256 hash of the file content
        """
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.sha256(content).hexdigest()
        except IOError as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return ""
    
    def detect_changes(self, repo_path: Path, file_extensions: List[str] = None) -> Tuple[List[Path], List[Path], List[Path]]:
        """Detect changes in the repository.

        Args:
            repo_path: Path to the repository
            file_extensions: List of file extensions to consider (e.g., ['.java', '.py'])

        Returns:
            Tuple of (added_files, modified_files, deleted_files)
        """
        if file_extensions is None:
            file_extensions = ['.java']  # Default to Java files
        
        # Find all files with the specified extensions
        current_files = set()
        for ext in file_extensions:
            current_files.update(repo_path.glob(f'**/*{ext}'))
        
        # Convert to relative paths for storage
        current_files_rel = {str(f.relative_to(repo_path)) for f in current_files}
        
        # Get the set of previously tracked files
        previous_files_rel = set(self.file_hashes.keys())
        
        # Identify added, modified, and deleted files
        added_files_rel = current_files_rel - previous_files_rel
        deleted_files_rel = previous_files_rel - current_files_rel
        
        # Check for modifications in existing files
        modified_files_rel = set()
        for file_rel in current_files_rel & previous_files_rel:
            file_path = repo_path / file_rel
            current_hash = self.compute_file_hash(file_path)
            previous_hash = self.file_hashes[file_rel]['hash']
            
            if current_hash != previous_hash:
                modified_files_rel.add(file_rel)
        
        # Convert relative paths back to absolute paths
        added_files = [repo_path / f for f in added_files_rel]
        modified_files = [repo_path / f for f in modified_files_rel]
        deleted_files = [repo_path / f for f in deleted_files_rel]
        
        # Update file hashes for added and modified files
        timestamp = datetime.now().isoformat()
        for file_rel in added_files_rel | modified_files_rel:
            file_path = repo_path / file_rel
            self.file_hashes[file_rel] = {
                'hash': self.compute_file_hash(file_path),
                'last_updated': timestamp,
                'size': file_path.stat().st_size
            }
        
        # Remove deleted files from tracking
        for file_rel in deleted_files_rel:
            del self.file_hashes[file_rel]
        
        # Save updated file hashes
        self._save_file_hashes()
        
        return added_files, modified_files, deleted_files
    
    def get_affected_files(self, repo_path: Path, changed_files: List[Path], dependency_graph: Dict[str, Any]) -> Set[Path]:
        """Get all files affected by changes, including dependencies.

        Args:
            repo_path: Path to the repository
            changed_files: List of changed files
            dependency_graph: Dependency graph from the database

        Returns:
            Set of all affected files that need to be reprocessed
        """
        # Start with the directly changed files
        affected_files = set(changed_files)
        
        # TODO: Use the dependency graph to find files that depend on the changed files
        # This requires knowledge of the dependency graph structure
        
        return affected_files
    
    def clear_tracking_data(self) -> None:
        """Clear all tracking data."""
        self.file_hashes = {}
        self._save_file_hashes()
