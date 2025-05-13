"""
Prompt Builder module.

This module provides functionality for building prompts for code generation.
"""

import os
import sys
import logging
import json
from typing import Dict, List, Any, Optional, Union, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class PromptBuilder:
    """Builder for code generation prompts."""
    
    def __init__(
        self,
        template_dir: str = None,
        max_prompt_length: int = 8000
    ):
        """Initialize the prompt builder.
        
        Args:
            template_dir: Path to the directory containing prompt templates
            max_prompt_length: Maximum length of the prompt in tokens
        """
        self.template_dir = template_dir
        self.max_prompt_length = max_prompt_length
        self.templates = {}
        
        # Load templates if template directory is specified
        if template_dir and os.path.exists(template_dir):
            self._load_templates()
    
    def _load_templates(self):
        """Load prompt templates from the template directory."""
        try:
            # Get all JSON files in the template directory
            template_files = [f for f in os.listdir(self.template_dir) if f.endswith('.json')]
            
            # Load each template
            for template_file in template_files:
                template_path = os.path.join(self.template_dir, template_file)
                with open(template_path, 'r', encoding='utf-8') as f:
                    template = json.load(f)
                
                # Add to templates dictionary
                template_name = os.path.splitext(template_file)[0]
                self.templates[template_name] = template
            
            logger.info(f"Loaded {len(self.templates)} prompt templates")
        
        except Exception as e:
            logger.error(f"Error loading prompt templates: {e}")
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate the number of tokens in a text.
        
        Args:
            text: Input text
            
        Returns:
            Estimated number of tokens
        """
        # Simple estimation: 1 token ≈ 4 characters
        return len(text) // 4
    
    def build_code_generation_prompt(
        self,
        requirements: str,
        context: str,
        language: str = None,
        framework: str = None,
        examples: List[Dict[str, str]] = None
    ) -> str:
        """Build a prompt for code generation.
        
        Args:
            requirements: Business requirements
            context: Retrieved context
            language: Programming language
            framework: Framework or library
            examples: List of examples (each with 'input' and 'output' keys)
            
        Returns:
            Generated prompt
        """
        try:
            # Start with the system prompt
            prompt = "You are an expert software developer tasked with implementing code based on business requirements.\n\n"
            
            # Add language and framework information if provided
            if language:
                prompt += f"You will be writing code in {language}.\n"
            if framework:
                prompt += f"You will be using the {framework} framework.\n"
            
            prompt += "\n"
            
            # Add the requirements
            prompt += "# Business Requirements\n\n"
            prompt += requirements
            prompt += "\n\n"
            
            # Add the context
            prompt += "# Relevant Code Context\n\n"
            
            # Check if adding the context would exceed the maximum prompt length
            context_tokens = self._estimate_tokens(context)
            current_tokens = self._estimate_tokens(prompt)
            
            if current_tokens + context_tokens > self.max_prompt_length:
                # Truncate the context
                max_context_tokens = self.max_prompt_length - current_tokens - 100  # Leave some room for the rest of the prompt
                context_chars = max_context_tokens * 4
                context = context[:context_chars] + "\n\n... (context truncated due to length constraints)"
            
            prompt += context
            prompt += "\n\n"
            
            # Add examples if provided
            if examples:
                prompt += "# Examples\n\n"
                
                for i, example in enumerate(examples, 1):
                    prompt += f"## Example {i}\n\n"
                    prompt += f"### Input\n\n{example['input']}\n\n"
                    prompt += f"### Output\n\n{example['output']}\n\n"
            
            # Add the task
            prompt += "# Task\n\n"
            prompt += "Based on the business requirements and the provided code context, implement the necessary code changes.\n"
            prompt += "Please provide a complete implementation that satisfies the requirements.\n"
            
            # Add output format instructions
            prompt += "\n# Output Format\n\n"
            prompt += "Please provide your implementation in the following format:\n\n"
            prompt += "```[language]\n// Your code here\n```\n\n"
            prompt += "For each file that needs to be created or modified, specify the file path and the code:\n\n"
            prompt += "## File: [file_path]\n\n"
            prompt += "```[language]\n// Your code here\n```\n\n"
            
            return prompt
        
        except Exception as e:
            logger.error(f"Error building code generation prompt: {e}")
            return ""
    
    def build_code_refinement_prompt(
        self,
        requirements: str,
        context: str,
        initial_code: str,
        feedback: str = None
    ) -> str:
        """Build a prompt for code refinement.
        
        Args:
            requirements: Business requirements
            context: Retrieved context
            initial_code: Initial code implementation
            feedback: Feedback on the initial implementation
            
        Returns:
            Generated prompt
        """
        try:
            # Start with the system prompt
            prompt = "You are an expert software developer tasked with refining code based on feedback.\n\n"
            
            # Add the requirements
            prompt += "# Business Requirements\n\n"
            prompt += requirements
            prompt += "\n\n"
            
            # Add the initial code
            prompt += "# Initial Implementation\n\n"
            prompt += initial_code
            prompt += "\n\n"
            
            # Add feedback if provided
            if feedback:
                prompt += "# Feedback\n\n"
                prompt += feedback
                prompt += "\n\n"
            
            # Add the context (truncated if necessary)
            prompt += "# Relevant Code Context\n\n"
            
            # Check if adding the context would exceed the maximum prompt length
            context_tokens = self._estimate_tokens(context)
            current_tokens = self._estimate_tokens(prompt)
            
            if current_tokens + context_tokens > self.max_prompt_length:
                # Truncate the context
                max_context_tokens = self.max_prompt_length - current_tokens - 100  # Leave some room for the rest of the prompt
                context_chars = max_context_tokens * 4
                context = context[:context_chars] + "\n\n... (context truncated due to length constraints)"
            
            prompt += context
            prompt += "\n\n"
            
            # Add the task
            prompt += "# Task\n\n"
            prompt += "Based on the business requirements, the initial implementation, and the feedback, refine the code to better satisfy the requirements.\n"
            prompt += "Please provide a complete implementation that addresses the feedback and satisfies the requirements.\n"
            
            # Add output format instructions
            prompt += "\n# Output Format\n\n"
            prompt += "Please provide your implementation in the following format:\n\n"
            prompt += "```[language]\n// Your code here\n```\n\n"
            prompt += "For each file that needs to be created or modified, specify the file path and the code:\n\n"
            prompt += "## File: [file_path]\n\n"
            prompt += "```[language]\n// Your code here\n```\n\n"
            
            return prompt
        
        except Exception as e:
            logger.error(f"Error building code refinement prompt: {e}")
            return ""
    
    def build_from_template(
        self,
        template_name: str,
        variables: Dict[str, str]
    ) -> str:
        """Build a prompt from a template.
        
        Args:
            template_name: Name of the template
            variables: Dictionary of variables to substitute in the template
            
        Returns:
            Generated prompt
        """
        try:
            # Check if the template exists
            if template_name not in self.templates:
                logger.error(f"Template not found: {template_name}")
                return ""
            
            # Get the template
            template = self.templates[template_name]
            
            # Get the template text
            template_text = template.get("text", "")
            
            # Substitute variables
            for variable, value in variables.items():
                placeholder = f"{{{{{variable}}}}}"
                template_text = template_text.replace(placeholder, value)
            
            return template_text
        
        except Exception as e:
            logger.error(f"Error building prompt from template: {e}")
            return ""


# Example usage
if __name__ == "__main__":
    # Create a prompt builder
    builder = PromptBuilder()
    
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
    
    # Build a code generation prompt
    prompt = builder.build_code_generation_prompt(
        requirements=requirements,
        context=context,
        language="Java",
        framework="Spring Boot"
    )
    
    # Print the prompt
    print(prompt)
