"""
LLM Client module.

This module provides functionality for interacting with LLM APIs for code generation.
"""

import os
import sys
import logging
import json
import time
import requests
from typing import Dict, List, Any, Optional, Union, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import local modules
from src.utils import ensure_dir, save_json, load_json
from src.env_loader import get_env_var, load_env_vars

# Load environment variables
load_env_vars()

class LLMClient:
    """Base client for LLM APIs."""

    def __init__(
        self,
        api_key: str = None,
        model_name: str = None,
        output_dir: str = None,
        max_retries: int = 3,
        retry_delay: int = 2
    ):
        """Initialize the LLM client.

        Args:
            api_key: API key for the LLM service
            model_name: Name of the model to use
            output_dir: Path to the output directory
            max_retries: Maximum number of retries for API calls
            retry_delay: Delay between retries in seconds
        """
        # Get values from environment variables if not provided
        self.api_key = api_key or os.environ.get("LLM_API_KEY")
        self.model_name = model_name or os.environ.get("LLM_MODEL_NAME")
        self.output_dir = output_dir or os.environ.get("OUTPUT_DIR")
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Create output directory if specified
        if self.output_dir:
            ensure_dir(self.output_dir)

    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stop_sequences: List[str] = None,
        save_output: bool = True
    ) -> str:
        """Generate text using the LLM.

        Args:
            prompt: Input prompt
            temperature: Temperature for generation
            max_tokens: Maximum number of tokens to generate
            stop_sequences: Sequences that stop generation
            save_output: Whether to save the output

        Returns:
            Generated text
        """
        raise NotImplementedError("Subclasses must implement this method")

    def save_conversation(
        self,
        prompt: str,
        response: str,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Save a conversation to a file.

        Args:
            prompt: Input prompt
            response: Generated response
            metadata: Additional metadata

        Returns:
            Path to the saved file
        """
        try:
            # Check if output directory is specified
            if not self.output_dir:
                return ""

            # Create a timestamp
            timestamp = int(time.time())

            # Create the conversation data
            conversation_data = {
                "timestamp": timestamp,
                "model": self.model_name,
                "prompt": prompt,
                "response": response,
                "metadata": metadata or {}
            }

            # Create the file path
            file_path = os.path.join(self.output_dir, f"conversation_{timestamp}.json")

            # Save the conversation data
            save_json(conversation_data, file_path)

            logger.info(f"Saved conversation to {file_path}")

            return file_path

        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
            return ""

    def save_output(
        self,
        output: str,
        file_name: str = "llm-output.txt"
    ) -> str:
        """Save output to a file.

        Args:
            output: Output text
            file_name: Name of the output file

        Returns:
            Path to the saved file
        """
        try:
            # Check if output directory is specified
            if not self.output_dir:
                return ""

            # Create the file path
            file_path = os.path.join(self.output_dir, file_name)

            # Write the output to the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(output)

            logger.info(f"Saved output to {file_path}")

            return file_path

        except Exception as e:
            logger.error(f"Error saving output: {e}")
            return ""


class NVIDIALlamaClient(LLMClient):
    """Client for NVIDIA's Llama 3.3 Nemotron Super 49B model via OpenRouter."""

    def __init__(
        self,
        api_key: str = None,
        model_name: str = None,
        api_url: str = None,
        output_dir: str = None,
        max_retries: int = 3,
        retry_delay: int = 2
    ):
        """Initialize the NVIDIA Llama client.

        Args:
            api_key: API key for the OpenRouter API
            model_name: Name of the model to use
            api_url: URL for the OpenRouter API
            output_dir: Path to the output directory
            max_retries: Maximum number of retries for API calls
            retry_delay: Delay between retries in seconds
        """
        # Get default values from environment if not provided
        model_name = model_name or os.environ.get("LLM_MODEL_NAME", "nvidia/llama-3.3-nemotron-super-49b-v1:free")
        api_url = api_url or os.environ.get("OPENAI_API_BASE_URL", "https://openrouter.ai/api/v1")

        super().__init__(
            api_key=api_key,
            model_name=model_name,
            output_dir=output_dir,
            max_retries=max_retries,
            retry_delay=retry_delay
        )
        self.api_url = f"{api_url}/chat/completions"

        # Check if API key is provided
        if not self.api_key:
            logger.warning("No API key provided for NVIDIA Llama client")

    def _prepare_headers(self) -> Dict[str, str]:
        """Prepare headers for API requests.

        Returns:
            Dictionary of headers
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/bhaktichindhe",  # Required by OpenRouter
            "X-Title": "RepoMind Codebase Analyzer"  # Optional but helpful for OpenRouter
        }

    def _prepare_payload(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stop_sequences: List[str] = None,
        system_prompt: str = None
    ) -> Dict[str, Any]:
        """Prepare payload for API requests.

        Args:
            prompt: Input prompt
            temperature: Temperature for generation
            max_tokens: Maximum number of tokens to generate
            stop_sequences: Sequences that stop generation
            system_prompt: System prompt to use (overrides default)

        Returns:
            Dictionary of payload
        """
        # Use default system prompt if none provided
        if system_prompt is None:
            system_prompt = "You are a helpful AI assistant that specializes in code generation and software development."

        # Prepare the payload for OpenRouter API (OpenAI-compatible format)
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        # Add stop sequences if provided
        if stop_sequences:
            payload["stop"] = stop_sequences

        return payload

    def generate(
        self,
        prompt: str,
        temperature: float = None,
        max_tokens: int = None,
        stop_sequences: List[str] = None,
        save_output: bool = True,
        system_prompt: str = None
    ) -> str:
        """Generate text using the NVIDIA Llama model.

        Args:
            prompt: Input prompt
            temperature: Temperature for generation
            max_tokens: Maximum number of tokens to generate
            stop_sequences: Sequences that stop generation
            save_output: Whether to save the output
            system_prompt: System prompt to use (overrides default)

        Returns:
            Generated text
        """
        # Get default values from environment variables if not provided
        temperature = temperature if temperature is not None else float(os.environ.get("LLM_TEMPERATURE", 0.7))
        max_tokens = max_tokens if max_tokens is not None else int(os.environ.get("LLM_MAX_TOKENS", 2000))
        try:
            # Check if API key is provided
            if not self.api_key:
                raise ValueError("No API key provided for NVIDIA Llama client")

            # Prepare headers and payload
            headers = self._prepare_headers()
            payload = self._prepare_payload(
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                stop_sequences=stop_sequences,
                system_prompt=system_prompt
            )

            # Initialize response
            response_text = ""

            # Make the API request with retries
            for attempt in range(self.max_retries):
                try:
                    logger.info(f"Making API request to {self.api_url} (attempt {attempt + 1}/{self.max_retries})")

                    # Make the API request
                    response = requests.post(
                        self.api_url,
                        headers=headers,
                        json=payload
                    )

                    # Check if the request was successful
                    response.raise_for_status()

                    # Parse the response from OpenRouter API
                    response_data = response.json()

                    # Extract the generated text from the OpenAI-compatible format
                    choices = response_data.get("choices", [])
                    if choices:
                        message = choices[0].get("message", {})
                        response_text = message.get("content", "")
                    else:
                        response_text = ""

                    # Break the retry loop if successful
                    break

                except requests.exceptions.RequestException as e:
                    logger.error(f"API request failed: {e}")

                    # Check if this is the last attempt
                    if attempt == self.max_retries - 1:
                        raise

                    # Wait before retrying
                    time.sleep(self.retry_delay)

            # Save the conversation if requested
            if save_output:
                # Save the conversation
                self.save_conversation(
                    prompt=prompt,
                    response=response_text,
                    metadata={
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "stop_sequences": stop_sequences
                    }
                )

                # Save the output
                self.save_output(response_text)

            return response_text

        except Exception as e:
            logger.error(f"Error generating text: {e}")
            # Return a fallback mock response instead of error message
            return self._generate_fallback_response(prompt)

    def _generate_fallback_response(self, prompt: str) -> str:
        """Generate a fallback response when API fails.

        Args:
            prompt: The original prompt

        Returns:
            Fallback response text
        """
        logger.info("Generating fallback response due to API failure")

        fallback_response = f"""
I apologize, but I'm currently unable to connect to the LLM service. Here's what I can tell you based on the codebase analysis:

## Analysis

Based on your question about the codebase, here are some general insights:

1. **Architecture**: The system follows a modular design pattern with clear separation of concerns
2. **Components**: Multiple interconnected components work together through well-defined interfaces
3. **Data Flow**: Information flows through the system using established patterns

## Recommendations

1. Review the existing code patterns when making changes
2. Ensure proper error handling is implemented
3. Add appropriate tests for new functionality
4. Follow the established coding conventions

## Next Steps

- Configure your API key in the .env file for full LLM integration
- Check the logs for more detailed error information
- Try your question again once the connection is restored

*Note: This is a fallback response. For detailed code analysis, please ensure your LLM API key is properly configured.*
"""

        return fallback_response.strip()


# Example usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate text using LLM")
    parser.add_argument("--prompt", required=True, help="Input prompt")
    parser.add_argument("--api-key", help="API key for the LLM service")
    parser.add_argument("--model", default="nvidia/llama-3.3-nemotron-super-49b-v1:free",
                        help="Name of the model to use")
    parser.add_argument("--temperature", type=float, default=0.7,
                        help="Temperature for generation")
    parser.add_argument("--max-tokens", type=int, default=2000,
                        help="Maximum number of tokens to generate")
    parser.add_argument("--output-dir", default="output", help="Path to the output directory")
    args = parser.parse_args()

    # Create an LLM client
    client = NVIDIALlamaClient(
        api_key=args.api_key,
        model_name=args.model,
        output_dir=args.output_dir
    )

    # Generate text
    response = client.generate(
        prompt=args.prompt,
        temperature=args.temperature,
        max_tokens=args.max_tokens
    )

    # Print the response
    print(response)
