"""
Output Formatter module.

This module provides functionality for formatting output for llm-instructions.txt.
"""

import os
import sys
import logging
import json
import re
from typing import Dict, List, Any, Optional, Union, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class OutputFormatter:
    """Formatter for llm-instructions.txt output."""
    
    def __init__(
        self,
        output_dir: str = None,
        format_type: str = "markdown"
    ):
        """Initialize the output formatter.
        
        Args:
            output_dir: Path to the output directory
            format_type: Format type for the output (markdown, text)
        """
        self.output_dir = output_dir
        self.format_type = format_type
        
        # Create output directory if specified and it doesn't exist
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def _format_requirements(self, requirements: str) -> str:
        """Format business requirements.
        
        Args:
            requirements: Business requirements
            
        Returns:
            Formatted requirements
        """
        if self.format_type == "markdown":
            return f"# Business Requirements\n\n{requirements}\n\n"
        else:  # text
            return f"BUSINESS REQUIREMENTS\n{'=' * 20}\n\n{requirements}\n\n"
    
    def _format_context(self, context: str) -> str:
        """Format retrieved context.
        
        Args:
            context: Retrieved context
            
        Returns:
            Formatted context
        """
        if self.format_type == "markdown":
            return f"# Relevant Code Context\n\n{context}\n\n"
        else:  # text
            return f"RELEVANT CODE CONTEXT\n{'=' * 20}\n\n{context}\n\n"
    
    def _format_instructions(self, instructions: str) -> str:
        """Format instructions.
        
        Args:
            instructions: Instructions
            
        Returns:
            Formatted instructions
        """
        if self.format_type == "markdown":
            return f"# Instructions\n\n{instructions}\n\n"
        else:  # text
            return f"INSTRUCTIONS\n{'=' * 20}\n\n{instructions}\n\n"
    
    def _format_examples(self, examples: List[Dict[str, str]]) -> str:
        """Format examples.
        
        Args:
            examples: List of examples (each with 'input' and 'output' keys)
            
        Returns:
            Formatted examples
        """
        if not examples:
            return ""
        
        if self.format_type == "markdown":
            formatted_examples = "# Examples\n\n"
            
            for i, example in enumerate(examples, 1):
                formatted_examples += f"## Example {i}\n\n"
                formatted_examples += f"### Input\n\n{example['input']}\n\n"
                formatted_examples += f"### Output\n\n{example['output']}\n\n"
        
        else:  # text
            formatted_examples = f"EXAMPLES\n{'=' * 20}\n\n"
            
            for i, example in enumerate(examples, 1):
                formatted_examples += f"Example {i}\n{'-' * 10}\n\n"
                formatted_examples += f"Input:\n{example['input']}\n\n"
                formatted_examples += f"Output:\n{example['output']}\n\n"
        
        return formatted_examples
    
    def _format_metadata(self, metadata: Dict[str, Any]) -> str:
        """Format metadata.
        
        Args:
            metadata: Metadata
            
        Returns:
            Formatted metadata
        """
        if not metadata:
            return ""
        
        if self.format_type == "markdown":
            formatted_metadata = "# Metadata\n\n"
            
            for key, value in metadata.items():
                formatted_metadata += f"- **{key}**: {value}\n"
        
        else:  # text
            formatted_metadata = f"METADATA\n{'=' * 20}\n\n"
            
            for key, value in metadata.items():
                formatted_metadata += f"{key}: {value}\n"
        
        return formatted_metadata + "\n\n"
    
    def format_output(
        self,
        requirements: str,
        context: str,
        instructions: str = None,
        examples: List[Dict[str, str]] = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Format output for llm-instructions.txt.
        
        Args:
            requirements: Business requirements
            context: Retrieved context
            instructions: Instructions
            examples: List of examples (each with 'input' and 'output' keys)
            metadata: Metadata
            
        Returns:
            Formatted output
        """
        try:
            # Initialize output
            output = ""
            
            # Add metadata if provided
            if metadata:
                output += self._format_metadata(metadata)
            
            # Add requirements
            output += self._format_requirements(requirements)
            
            # Add context
            output += self._format_context(context)
            
            # Add examples if provided
            if examples:
                output += self._format_examples(examples)
            
            # Add instructions
            if instructions:
                output += self._format_instructions(instructions)
            else:
                # Default instructions
                default_instructions = "Based on the provided business requirements and code context, implement the necessary code changes."
                output += self._format_instructions(default_instructions)
            
            return output
        
        except Exception as e:
            logger.error(f"Error formatting output: {e}")
            return f"Error formatting output: {e}"
    
    def save_output(
        self,
        output: str,
        file_name: str = "llm-instructions.txt"
    ) -> str:
        """Save formatted output to a file.
        
        Args:
            output: Formatted output
            file_name: Name of the output file
            
        Returns:
            Path to the saved file
        """
        try:
            # Create the file path
            file_path = os.path.join(self.output_dir, file_name) if self.output_dir else file_name
            
            # Write the output to the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(output)
            
            logger.info(f"Saved output to {file_path}")
            
            return file_path
        
        except Exception as e:
            logger.error(f"Error saving output: {e}")
            return ""
    
    def extract_code_from_llm_response(self, response: str) -> Dict[str, str]:
        """Extract code from LLM response.
        
        Args:
            response: LLM response
            
        Returns:
            Dictionary mapping file paths to code
        """
        try:
            # Initialize result
            code_blocks = {}
            
            # Extract file paths and code blocks
            file_pattern = r"##\s*File:\s*([^\n]+)\s*\n\s*```[^\n]*\n(.*?)```"
            matches = re.finditer(file_pattern, response, re.DOTALL)
            
            for match in matches:
                file_path = match.group(1).strip()
                code = match.group(2).strip()
                code_blocks[file_path] = code
            
            # If no file paths were found, look for standalone code blocks
            if not code_blocks:
                code_pattern = r"```[^\n]*\n(.*?)```"
                matches = re.finditer(code_pattern, response, re.DOTALL)
                
                for i, match in enumerate(matches):
                    code = match.group(1).strip()
                    code_blocks[f"code_block_{i+1}.txt"] = code
            
            return code_blocks
        
        except Exception as e:
            logger.error(f"Error extracting code from LLM response: {e}")
            return {}
    
    def save_extracted_code(
        self,
        code_blocks: Dict[str, str],
        base_dir: str = None
    ) -> List[str]:
        """Save extracted code to files.
        
        Args:
            code_blocks: Dictionary mapping file paths to code
            base_dir: Base directory for saving files
            
        Returns:
            List of saved file paths
        """
        try:
            # Initialize result
            saved_files = []
            
            # Use output directory if base directory is not specified
            base_dir = base_dir or self.output_dir or os.getcwd()
            
            # Save each code block to a file
            for file_path, code in code_blocks.items():
                # Create the full file path
                full_path = os.path.join(base_dir, file_path)
                
                # Create the directory if it doesn't exist
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                # Write the code to the file
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(code)
                
                saved_files.append(full_path)
                logger.info(f"Saved code to {full_path}")
            
            return saved_files
        
        except Exception as e:
            logger.error(f"Error saving extracted code: {e}")
            return []


# Example usage
if __name__ == "__main__":
    # Create an output formatter
    formatter = OutputFormatter(output_dir="output")
    
    # Example requirements
    requirements = """
    The system should implement a UserService class that handles authentication.
    The login method should verify user credentials against the database.
    The system should return JWT tokens for authenticated users.
    """
    
    # Example context
    context = """
    public class UserService {
        private final UserRepository userRepository;
        
        public UserService(UserRepository userRepository) {
            this.userRepository = userRepository;
        }
        
        // Other methods...
    }
    """
    
    # Format the output
    output = formatter.format_output(
        requirements=requirements,
        context=context,
        metadata={
            "project": "AuthenticationSystem",
            "language": "Java",
            "framework": "Spring Boot"
        }
    )
    
    # Save the output
    file_path = formatter.save_output(output)
    
    # Print the file path
    print(f"Output saved to: {file_path}")
    
    # Example LLM response
    llm_response = """
    Based on the requirements, here's the implementation:
    
    ## File: UserService.java
    ```java
    public class UserService {
        private final UserRepository userRepository;
        private final JwtTokenProvider tokenProvider;
        
        public UserService(UserRepository userRepository, JwtTokenProvider tokenProvider) {
            this.userRepository = userRepository;
            this.tokenProvider = tokenProvider;
        }
        
        public String login(String username, String password) {
            User user = userRepository.findByUsername(username);
            if (user != null && passwordEncoder.matches(password, user.getPassword())) {
                return tokenProvider.generateToken(user);
            }
            throw new AuthenticationException("Invalid credentials");
        }
    }
    ```
    
    ## File: JwtTokenProvider.java
    ```java
    public class JwtTokenProvider {
        private final String secretKey;
        private final long validityInMilliseconds;
        
        public JwtTokenProvider(String secretKey, long validityInMilliseconds) {
            this.secretKey = secretKey;
            this.validityInMilliseconds = validityInMilliseconds;
        }
        
        public String generateToken(User user) {
            Claims claims = Jwts.claims().setSubject(user.getUsername());
            claims.put("roles", user.getRoles());
            
            Date now = new Date();
            Date validity = new Date(now.getTime() + validityInMilliseconds);
            
            return Jwts.builder()
                .setClaims(claims)
                .setIssuedAt(now)
                .setExpiration(validity)
                .signWith(SignatureAlgorithm.HS256, secretKey)
                .compact();
        }
    }
    ```
    """
    
    # Extract code from LLM response
    code_blocks = formatter.extract_code_from_llm_response(llm_response)
    
    # Save extracted code
    saved_files = formatter.save_extracted_code(code_blocks)
    
    # Print saved files
    print("\nSaved code files:")
    for file in saved_files:
        print(f"- {file}")
