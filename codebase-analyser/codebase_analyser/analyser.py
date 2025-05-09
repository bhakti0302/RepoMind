from pathlib import Path
from typing import Dict, List, Optional, Set, Union, Any

from tree_sitter import Language, Parser
from .parsers.java_parser import JavaParser
from .parsing.enhanced_java_parser import EnhancedJavaParser
from .chunking.chunker import CodeChunker, CodeChunk

class CodebaseAnalyser:
    """Main class for analysing a codebase using Tree-sitter."""

    def __init__(self, repo_path: Union[str, Path], min_chunk_size: int = 50, max_chunk_size: int = 300):
        """Initialize the analyser with a repository path.

        Args:
            repo_path: Path to the repository to analyze
            min_chunk_size: Minimum number of lines for a chunk
            max_chunk_size: Maximum number of lines for a chunk
        """
        self.repo_path = Path(repo_path)
        self.parser = None
        self.languages = {}
        self.java_parser = None
        self.enhanced_java_parser = None
        self.chunker = CodeChunker(min_chunk_size=min_chunk_size, max_chunk_size=max_chunk_size)
        self._setup_parser()

    def _setup_parser(self):
        """Set up the Tree-sitter parser with supported languages."""
        # Initialize the parser
        self.parser = Parser()

        # Load language libraries
        try:
            from tree_sitter_languages import get_language

            # Define supported languages
            supported_languages = ['java', 'python', 'javascript', 'typescript', 'c', 'cpp', 'go', 'ruby', 'php', 'rust']

            # Load all available languages
            for lang_name in supported_languages:
                try:
                    self.languages[lang_name] = get_language(lang_name)
                    print(f"Loaded language: {lang_name}")
                except Exception as e:
                    print(f"Failed to load language {lang_name}: {e}")

            # Ensure Java is loaded
            if 'java' in self.languages:
                self.java_parser = JavaParser(self.languages['java'])
                self.enhanced_java_parser = EnhancedJavaParser(self.languages['java'])
                print("Java parsers initialized successfully")
            else:
                print("WARNING: Java grammar not found in tree-sitter-languages")

            print(f"Loaded {len(self.languages)} language grammars")
        except ImportError:
            print("tree-sitter-languages not found. Please install it or build languages manually.")

    def parse_file(self, file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """Parse a single file and return its AST.

        Args:
            file_path: Path to the file to parse

        Returns:
            Parsed AST or None if parsing failed
        """
        file_path = Path(file_path)

        # Check if file exists
        if not file_path.exists():
            print(f"Error: File does not exist: {file_path}")
            return None

        # Determine language from file extension
        extension = file_path.suffix.lower()

        # Special handling for Java files
        if extension == '.java':
            if self.enhanced_java_parser:
                # Use the enhanced Java parser for better chunking
                return self.enhanced_java_parser.parse_file(file_path)
            elif self.java_parser:
                # Fall back to the original Java parser if enhanced parser fails
                return self.java_parser.parse_file(file_path)

        # For other languages, use the generic parser
        language = self._get_language_for_extension(extension)

        if not language:
            print(f"Unsupported file type: {extension}")
            return None

        # Set the language for the parser
        self.parser.set_language(language)

        # Read the file content
        try:
            with open(file_path, 'rb') as f:
                content = f.read()

            # Parse the file
            tree = self.parser.parse(content)

            # Check if parsing was successful
            if not tree or not tree.root_node:
                print(f"Error: Failed to parse {file_path}: Empty AST")
                return None

            # Return the AST (simplified for now)
            return {
                'path': str(file_path),
                'language': self._get_language_name(language),
                'ast': tree,
                'content': content.decode('utf-8', errors='replace')
            }
        except UnicodeDecodeError:
            print(f"Error parsing {file_path}: Invalid encoding")
            return None
        except FileNotFoundError:
            print(f"Error parsing {file_path}: File not found")
            return None
        except PermissionError:
            print(f"Error parsing {file_path}: Permission denied")
            return None
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None

    def _get_language_for_extension(self, extension: str) -> Optional[Language]:
        """Get the Tree-sitter language for a file extension."""
        # This is a simplified mapping - you'd want a more complete one
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.c': 'c',
            '.cpp': 'cpp',
            '.go': 'go',
            '.rb': 'ruby',
            '.php': 'php',
            '.rs': 'rust',
        }

        lang_name = extension_map.get(extension)
        return self.languages.get(lang_name) if lang_name else None

    def _get_language_name(self, language: Language) -> str:
        """Get the name of a language from its Language object."""
        for name, lang in self.languages.items():
            if lang == language:
                return name
        return "unknown"

    def parse(self):
        """Parse all supported files in the repository."""
        # This is a placeholder - you'd implement the full parsing logic here
        print(f"Parsing repository at {self.repo_path}")
        # Actual implementation would scan the repo and parse each file

    def parse_java_files(self) -> List[Dict[str, Any]]:
        """Parse all Java files in the repository.

        Returns:
            List of parsed Java files with their structure
        """
        if not self.enhanced_java_parser and not self.java_parser:
            print("Java parsers not initialized. Make sure tree-sitter-languages is installed with Java support.")
            return []

        results = []
        errors = 0

        # Find all Java files in the repository
        try:
            java_files = list(self.repo_path.glob('**/*.java'))
            print(f"Found {len(java_files)} Java files")
        except Exception as e:
            print(f"Error finding Java files: {e}")
            return []

        # Parse each Java file
        for file_path in java_files:
            try:
                # Try enhanced parser first
                if self.enhanced_java_parser:
                    result = self.enhanced_java_parser.parse_file(file_path)
                    if result:
                        results.append(result)
                        continue

                # Fall back to original parser if enhanced parser fails
                if self.java_parser:
                    result = self.java_parser.parse_file(file_path)
                    if result:
                        results.append(result)
                        continue

                # If both parsers fail
                errors += 1
            except Exception as e:
                print(f"Unexpected error parsing {file_path}: {e}")
                errors += 1

        print(f"Successfully parsed {len(results)} Java files. Failed to parse {errors} files.")
        return results

    def get_chunks(self, parsed_file: Optional[Dict[str, Any]] = None) -> List[CodeChunk]:
        """Get code chunks from a parsed file or all parsed files in the repository.

        Args:
            parsed_file: A parsed file dictionary from the analyser. If None, chunks all files.

        Returns:
            List of code chunks
        """
        if parsed_file:
            # Check if this is from the enhanced Java parser
            if parsed_file.get('chunks') and isinstance(parsed_file.get('chunks'), list):
                # Convert the enhanced parser's chunks to CodeChunk objects
                chunks = []
                chunk_map = {}  # Map of node_id to CodeChunk objects

                # First pass: create all chunks
                for chunk_data in parsed_file['chunks']:
                    # Remove parent_id if present (we'll set parent relationships later)
                    if 'parent_id' in chunk_data:
                        parent_id = chunk_data.pop('parent_id')
                    else:
                        parent_id = None

                    # Create the chunk
                    chunk = CodeChunk(
                        node_id=chunk_data['node_id'],
                        chunk_type=chunk_data['chunk_type'],
                        content=chunk_data['content'],
                        file_path=chunk_data['file_path'],
                        start_line=chunk_data['start_line'],
                        end_line=chunk_data['end_line'],
                        language=chunk_data['language'],
                        name=chunk_data.get('name'),
                        qualified_name=chunk_data.get('qualified_name')
                    )

                    # Add metadata and context
                    if 'metadata' in chunk_data:
                        chunk.metadata = chunk_data['metadata']
                    if 'context' in chunk_data:
                        chunk.context = chunk_data['context']

                    # Store in map and list
                    chunk_map[chunk.node_id] = chunk
                    chunks.append(chunk)

                # Second pass: set parent-child relationships
                for chunk_data in parsed_file['chunks']:
                    if 'parent_id' in chunk_data and chunk_data['parent_id'] is not None:
                        child = chunk_map.get(chunk_data['node_id'])
                        parent = chunk_map.get(chunk_data['parent_id'])
                        if child and parent:
                            parent.add_child(child)

                # Third pass: add dependencies if available
                if 'dependencies' in parsed_file and parsed_file['dependencies']:
                    for dep in parsed_file['dependencies']:
                        source = chunk_map.get(dep['source_id'])
                        target = chunk_map.get(dep['target_id'])
                        if source and target:
                            # Add reference relationship
                            source.references.append(target)
                            target.referenced_by.append(source)

                            # Add dependency information to context
                            if 'dependencies' not in source.context:
                                source.context['dependencies'] = []
                            source.context['dependencies'].append({
                                'target': target.node_id,
                                'type': dep.get('type', 'UNKNOWN'),
                                'description': dep.get('description', ''),
                                'strength': dep.get('strength', 0.5)
                            })

                return chunks
            else:
                # Use the regular chunker for other parsers
                return self.chunker.chunk_file(parsed_file)

        # Chunk all files in the repository
        all_chunks = []

        # Find all supported files
        for extension, lang_name in self._get_language_for_extension.__defaults__[0].items():
            if lang_name in self.languages:
                try:
                    files = list(self.repo_path.glob(f'**/*{extension}'))
                    print(f"Found {len(files)} {lang_name} files")

                    for file_path in files:
                        try:
                            parsed = self.parse_file(file_path)
                            if parsed:
                                file_chunks = self.chunker.chunk_file(parsed)
                                all_chunks.extend(file_chunks)
                                print(f"Created {len(file_chunks)} chunks for {file_path}")
                        except Exception as e:
                            print(f"Error chunking {file_path}: {e}")
                except Exception as e:
                    print(f"Error finding {lang_name} files: {e}")

        print(f"Created a total of {len(all_chunks)} chunks from the repository")
        return all_chunks
