"""
LLM provider for the codebase analyser.
"""
import os
import logging
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

class LLMProvider:
    """Base class for LLM providers."""
    
    async def generate(self, prompt: str) -> str:
        """Generate text from a prompt."""
        raise NotImplementedError("Subclasses must implement this method")

class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing."""
    
    async def generate(self, prompt: str) -> str:
        """Generate text from a prompt."""
        logger.info("Generating text with mock LLM provider")
        return f"This is a mock response for: {prompt[:50]}..."

class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """Initialize the OpenAI provider."""
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model = model or os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
        
        if not self.api_key:
            logger.warning("OpenAI API key not found, using mock provider")
            self.use_mock = True
            self.mock_provider = MockLLMProvider()
        else:
            self.use_mock = False
            try:
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
            except ImportError:
                logger.warning("OpenAI package not installed, using mock provider")
                self.use_mock = True
                self.mock_provider = MockLLMProvider()
    
    async def generate(self, prompt: str) -> str:
        """Generate text from a prompt."""
        if self.use_mock:
            return await self.mock_provider.generate(prompt)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates code based on requirements."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating text with OpenAI: {str(e)}")
            return f"Error: {str(e)}"

class OpenRouterProvider(LLMProvider):
    """OpenRouter LLM provider."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "openai/gpt-3.5-turbo"):
        """Initialize the OpenRouter provider."""
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        self.model = model or os.environ.get("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")
        
        if not self.api_key:
            logger.warning("OpenRouter API key not found, using mock provider")
            self.use_mock = True
            self.mock_provider = MockLLMProvider()
        else:
            self.use_mock = False
            try:
                import openai
                self.client = openai.OpenAI(
                    api_key=self.api_key,
                    base_url="https://openrouter.ai/api/v1"
                )
            except ImportError:
                logger.warning("OpenAI package not installed, using mock provider")
                self.use_mock = True
                self.mock_provider = MockLLMProvider()
    
    async def generate(self, prompt: str) -> str:
        """Generate text from a prompt."""
        if self.use_mock:
            return await self.mock_provider.generate(prompt)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates code based on requirements."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating text with OpenRouter: {str(e)}")
            return f"Error: {str(e)}"

def get_llm_provider() -> LLMProvider:
    """Get the appropriate LLM provider based on environment variables."""
    # Check if we should use mock implementations
    use_mock = os.environ.get("USE_MOCK_IMPLEMENTATIONS", "0") == "1"
    if use_mock:
        logger.info("Using mock LLM provider as requested by environment variable")
        return MockLLMProvider()
    
    # Check for OpenRouter API key
    if os.environ.get("OPENROUTER_API_KEY"):
        logger.info("Using OpenRouter LLM provider")
        return OpenRouterProvider()
    
    # Check for OpenAI API key
    if os.environ.get("OPENAI_API_KEY"):
        logger.info("Using OpenAI LLM provider")
        return OpenAIProvider()
    
    # Fall back to mock provider
    logger.warning("No API keys found, using mock LLM provider")
    return MockLLMProvider()