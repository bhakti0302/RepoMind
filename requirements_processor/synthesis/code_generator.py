
"""
Code generator for requirements-based code generation.

This module provides functionality to generate code based on requirements
and retrieved context from the codebase.
"""

import logging
import os
import json
from typing import Dict, List, Set, Optional, Any, Tuple, Union
from pathlib import Path
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Import LangChain's ChatOpenAI instead of OpenAI client
from langchain_openai import ChatOpenAI

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class CodeGenerator:
    """Generates code based on requirements and context."""
    
    def __init__(
        self,
        model: str = "nvidia/llama-3.3-nemotron-super-49b-v1:free",
        api_key: str = "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",#Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 4000,
        base_url: str = "https://openrouter.ai/api/v1"
    ):
        """Initialize the code generator.
        
        Args:
            model: Name of the model to use
            api_key: OpenRouter API key (defaults to environment variable)
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            base_url: Base URL for the API (defaults to OpenRouter)
        """
        # Use API key from environment variable if not provided
        if api_key is None:
            api_key = "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"#os.environ.get("OPENAI_API_KEY")
        
        if api_key is None:
            raise ValueError("API key not provided and not found in environment")
        
        # Store the API key
        self.api_key = "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"#api_key
        
        # Initialize LangChain's ChatOpenAI with OpenRouter base URL
        self.client = ChatOpenAI(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            base_url=base_url,
            api_key=api_key,
            # Add headers for OpenRouter
            default_headers={ 
                "X-Title": "RepoMind Code Generator"
            }
        )
        
        # Store parameters
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.base_url = base_url
        self.default_headers = { "X-Title": "RepoMind Code Generator" }
        
        logger.info(f"Initialized CodeGenerator with model: {model} using OpenRouter")
    
    # Add retry decorator to handle transient errors
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True
    )
    def _generate_with_retry(self, messages):
        """Generate code with retry logic for transient errors.
        
        Args:
            messages: List of messages for the model
        
        Returns:
            Generated response
        """
        return self.client.invoke(messages)

    def generate_code(
        self,
        requirements: Dict[str, Any],
        context_chunks: List[Dict[str, Any]],
        language: str = "java",
        file_type: str = "class"
    ) -> Dict[str, Any]:
        """Generate code based on requirements and context.
        
        Args:
            requirements: Parsed requirements
            context_chunks: Retrieved context chunks
            language: Target programming language
            file_type: Type of file to generate
        
        Returns:
            Dictionary with generated code and metadata
        """
        # Prepare the prompt
        prompt = self._prepare_prompt(requirements, context_chunks, language, file_type)
        
        try:
            # Convert to LangChain message format
            from langchain_core.messages import SystemMessage, HumanMessage
            
            # Try up to 3 times with different models if needed
            models_to_try = [
                self.model,
                "nvidia/llama-3.3-nemotron-super-49b-v1:free",
                "openai/gpt-3.5-turbo"
            ]
            
            generated_code = None
            last_error = None
            
            for model_to_try in models_to_try:
                try:
                    # Create a new client with the current model
                    current_client = ChatOpenAI(
                        model=model_to_try,
                        temperature=self.temperature,
                        max_tokens=self.max_tokens,
                        base_url=self.base_url,
                        api_key=self.api_key,
                        default_headers=self.default_headers
                    )
                    
                    # Create messages for this attempt
                    lc_messages = [
                        SystemMessage(content=self._get_system_prompt(language, file_type)),
                        HumanMessage(content=prompt)
                    ]
                    
                    # Generate response with the current client
                    response = current_client.invoke(lc_messages)
                    
                    # Extract generated code
                    generated_code = response.content
                    
                    # Print the response
                    logger.info("LLM Response:")
                    logger.info("-" * 40)
                    logger.info(generated_code)
                    logger.info("-" * 40)
                    
                    # If successful, break the loop
                    logger.info(f"Successfully generated code using model: {model_to_try}")
                    break
                except Exception as e:
                    last_error = e
                    logger.warning(f"Error with model {model_to_try}: {e}. Trying next model...")
                    time.sleep(2)  # Brief pause before trying next model
            
            # If all models failed, raise the last error
            if generated_code is None:
                raise last_error or Exception("All models failed to generate code")
                
        except Exception as e:
            logger.error(f"Error generating code: {e}")
            
            # Check if it's a 500 error
            error_str = str(e)
            if "500" in error_str or "Internal Server Error" in error_str:
                generated_code = f"""// Error: OpenRouter API internal server error
// This is likely a temporary issue with the OpenRouter service.
// Please try again in a few minutes or try a different model.
//
// Full error: {error_str}"""
            # Check if it's a 404 error related to data policy
            elif "404" in error_str and "data policy" in error_str:
                generated_code = f"""// Error: OpenRouter API data policy issue
// Please visit https://openrouter.ai/settings/privacy to enable prompt training
// or choose a different model that matches your data policy settings.
//
// Full error: {error_str}"""
            else:
                generated_code = f"// Error: {error_str}"
        
        # Parse the generated code
        code_blocks = self._extract_code_blocks(generated_code)
        
        # If no code blocks were extracted, create a default one
        if not code_blocks:
            code_blocks = [{
                "language": language,
                "content": generated_code
            }]
        
        # Prepare result
        result = {
            "requirements": requirements,
            "generated_code": code_blocks,
            "raw_response": generated_code,
            "language": language,
            "file_type": file_type,
            "model": self.model,
            "provider": "openrouter"
        }
        
        logger.info(f"Generated code for {language} {file_type} using OpenRouter")
        
        return result
    
    def _prepare_prompt(
        self,
        requirements: Dict[str, Any],
        context_chunks: List[Dict[str, Any]],
        language: str,
        file_type: str
    ) -> str:
        """Prepare the prompt for code generation.
        
        Args:
            requirements: Parsed requirements
            context_chunks: Retrieved context chunks
            language: Target programming language
            file_type: Type of file to generate
            
        Returns:
            Formatted prompt string
        """
        # Extract requirements text
        requirements_text = requirements.get("text", "")
        
        # Extract entities
        entities = requirements.get("entities", {})
        
        # Format context chunks
        context_text = self._format_context_chunks(context_chunks)
        
        # Build the prompt
        prompt = f"""
# Requirements
{requirements_text}

# Extracted Entities
Classes: {', '.join([e['name'] for e in entities.get('classes', [])])}
Methods: {', '.join([e['name'] for e in entities.get('methods', [])])}
Interfaces: {', '.join([e['name'] for e in entities.get('interfaces', [])])}

# Relevant Code Context
{context_text}

# Task
Generate a {language} {file_type} that implements the requirements above.
Use the provided code context as a reference for coding style, patterns, and existing functionality.
Ensure the generated code integrates well with the existing codebase.
"""
        
        return prompt
    
    def _get_system_prompt(self, language: str, file_type: str) -> str:
        """Get the system prompt for code generation.
        
        Args:
            language: Target programming language
            file_type: Type of file to generate
            
        Returns:
            System prompt string
        """
        return f"""
You are an expert {language} developer. Your task is to generate high-quality {language} code based on requirements and context from an existing codebase.

Follow these guidelines:
1. Generate complete, well-structured {language} code that implements the requirements
2. Follow best practices and coding standards for {language}
3. Ensure the code integrates well with the existing codebase
4. Include appropriate comments and documentation
5. Use the provided context to match the style and patterns of the existing code
6. Provide a brief explanation of your implementation choices

Format your response as follows:
```{language}
// Your generated code here
```

Then provide a brief explanation of your implementation.
"""
    
    def _format_context_chunks(self, context_chunks: List[Dict[str, Any]]) -> str:
        """Format context chunks for inclusion in the prompt.
        
        Args:
            context_chunks: Retrieved context chunks
            
        Returns:
            Formatted context string
        """
        # Group chunks by file
        chunks_by_file = {}
        for chunk in context_chunks:
            file_path = chunk.get("file_path", "unknown")
            if file_path not in chunks_by_file:
                chunks_by_file[file_path] = []
            chunks_by_file[file_path].append(chunk)
        
        # Format chunks
        formatted_chunks = []
        for file_path, chunks in chunks_by_file.items():
            # Sort chunks by position in file
            chunks.sort(key=lambda x: x.get("start_line", 0))
            
            # Add file header
            formatted_chunks.append(f"## File: {file_path}")
            
            # Add chunks
            for chunk in chunks:
                content = chunk.get("content", "")
                chunk_type = chunk.get("chunk_type", "unknown")
                
                formatted_chunks.append(f"### {chunk_type}")
                formatted_chunks.append("```")
                formatted_chunks.append(content)
                formatted_chunks.append("```")
                formatted_chunks.append("")
        
        return "\n".join(formatted_chunks)
    
    def _extract_code_blocks(self, text: str) -> List[Dict[str, str]]:
        """Extract code blocks from generated text.
        
        Args:
            text: Generated text
            
        Returns:
            List of code blocks with language and content
        """
        import re
        
        # Regular expression to match code blocks
        pattern = r"```(\w*)\n([\s\S]*?)```"
        
        # Find all code blocks
        matches = re.findall(pattern, text)
        
        # Format results
        code_blocks = []
        for language, content in matches:
            code_blocks.append({
                "language": language.strip() or "text",
                "content": content.strip()
            })
        
        return code_blocks

