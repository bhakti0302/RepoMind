def _create_file(self, file_path: str, content: str) -> Tuple[bool, Optional[str]]:
    """
    Create a new file.

    Args:
        file_path: Path to the file
        content: File content (can be a string or a list)

    Returns:
        A tuple of (success, error_message)
    """
    try:
        # Direct file operation
        full_path = os.path.join(self.codebase_path, file_path)

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Check if file already exists
        if os.path.exists(full_path):
            return False, f"File already exists: {file_path}"

        # Convert content to string if it's a list
        if isinstance(content, list):
            content = '\n'.join(content)

        # Write the file
        with open(full_path, 'w') as f:
            f.write(content)

        # Display the created file
        print(f"\nCreated file: {file_path}")
        print("=" * 80)
        print(content)
        print("=" * 80)

        return True, None
    
    except Exception as e:
        return False, f"Error creating file: {str(e)}"
