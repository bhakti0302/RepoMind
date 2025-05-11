"""
LLM-based nodes for the agent graph.
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional

# Import AgentState
from ..state import AgentState

# Configure logging
logger = logging.getLogger(__name__)

# Try to import LangChain LLM
try:
    from langchain_openai import ChatOpenAI
    from langchain.prompts import PromptTemplate
    from langchain.schema.output_parser import StrOutputParser
    # Check if OpenRouter API key is available
    openrouter_api_key = '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'
    if not openrouter_api_key:
        logger.warning("OPENROUTER_API_KEY not found in environment variables")
        llm = None
        LLM_AVAILABLE = False
    else:
        # Use OpenRouter with NVIDIA Llama model
        llm = ChatOpenAI(
            model="nvidia/llama-3.3-nemotron-super-49b-v1:free",
            temperature=0.2,
            base_url="https://openrouter.ai/api/v1",
            api_key=openrouter_api_key
        )
        LLM_AVAILABLE = True
        logger.info("LangChain OpenRouter LLM (NVIDIA Llama) is available")
except ImportError:
    llm = None
    LLM_AVAILABLE = False
    logger.warning("LangChain LLM is not available, using mock implementation")
except Exception as e:
    llm = None
    LLM_AVAILABLE = False
    logger.warning(f"Error initializing LLM: {str(e)}, using mock implementation")

# Code generation prompt template
CODE_GENERATION_PROMPT_TEMPLATE = """
You are an expert software developer tasked with generating code based on requirements.

# Requirements
{requirements}

# Context
{context}

# Task
Generate {language} code that implements the requirements.
The code should be complete, well-documented, and follow best practices for {language}.

Only respond with the code. Do not include any explanations or comments outside the code.
"""

# Custom prompt template (if provided)
CUSTOM_PROMPT_TEMPLATE = "{prompt_template}"

async def generate_code(state: AgentState) -> Dict[str, Any]:
    """
    Generate code based on requirements and context.
    
    Args:
        state: The current agent state
        
    Returns:
        Updated state with generated code
    """
    try:
        logger.info("Generating code")
        
        # If LLM is not available, return mock code
        if not LLM_AVAILABLE or not llm:
            logger.warning("LLM not available, returning mock code")
            return {
                "generated_code": f"// Mock code for: {state.requirements.get('description', 'Unknown requirements')}"
            }
        
        # Get requirements and context
        requirements_text = json.dumps(state.requirements, indent=2)
        context = state.combined_context
        
        # Get language from processed requirements
        language = state.processed_requirements.get("language", "java") if state.processed_requirements else "java"
        
        # Determine which prompt template to use
        if state.prompt_template:
            # Use custom prompt template
            prompt = PromptTemplate.from_template(CUSTOM_PROMPT_TEMPLATE)
            prompt_variables = {
                "prompt_template": state.prompt_template,
                "requirements": requirements_text,
                "context": context,
                "language": language
            }
        else:
            # Use default prompt template
            prompt = PromptTemplate.from_template(CODE_GENERATION_PROMPT_TEMPLATE)
            prompt_variables = {
                "requirements": requirements_text,
                "context": context,
                "language": language
            }
        
        # Create the parser
        parser = StrOutputParser()
        
        # Create the chain
        chain = prompt | llm | parser
        
        # Run the chain
        generated_code = await chain.ainvoke(prompt_variables)
        
        logger.info(f"Generated code with {len(generated_code)} characters")
        
        return {
            "generated_code": generated_code
        }
    except Exception as e:
        logger.error(f"Error generating code: {e}")
        return {
            "errors": state.errors + [{"stage": "code_generation", "message": str(e)}],
            "generated_code": f"// Error generating code: {str(e)}"
        }

async def validate_code(state: AgentState) -> Dict[str, Any]:
    """
    Validate the generated code using LLM.
    
    Args:
        state: The current agent state
        
    Returns:
        Updated state with validation results
    """
    try:
        logger.info("Validating code with LLM")
        
        # If LLM is not available, return mock validation
        if not LLM_AVAILABLE or not llm:
            logger.warning("LLM not available, returning mock validation")
            return {
                "validation_result": {
                    "valid": True,
                    "issues": [],
                    "summary": "Mock validation passed"
                }
            }
        
        # If no code is generated, return error
        if not state.generated_code:
            logger.error("No code to validate")
            return {
                "validation_result": {
                    "valid": False,
                    "issues": [
                        {
                            "severity": "error",
                            "message": "No code was generated",
                            "line": 1,
                            "column": 1
                        }
                    ],
                    "summary": "No code was generated to validate"
                }
            }
        
        # Get requirements and code
        requirements_text = json.dumps(state.requirements, indent=2)
        code = state.generated_code
        
        # Get language from processed requirements
        language = state.processed_requirements.get("language", "java") if state.processed_requirements else "java"
        
        # Create the prompt
        prompt = PromptTemplate.from_template(
            """
            You are an expert software developer tasked with validating code.
            
            # Requirements
            {requirements}
            
            # Code to Validate
            ```{language}
            {code}
            ```
            
            Validate the code against the requirements and check for any errors or issues.
            Provide your analysis in the following JSON format:
            ```json
            {{
              "valid": true/false,
              "issues": [
                {{
                  "severity": "error/warning/info",
                  "message": "Description of the issue",
                  "line": line_number,
                  "column": column_number
                }}
              ],
              "summary": "Brief summary of validation results"
            }}
            ```
            
            Only respond with the JSON. Do not include any explanations or comments outside the JSON.
            """
        )
        
        # Create the chain
        chain = prompt | llm | StrOutputParser()
        
        # Run the chain
        validation_result_str = await chain.ainvoke({
            "requirements": requirements_text,
            "code": code,
            "language": language
        })
        
        # Parse the validation result
        try:
            validation_result = json.loads(validation_result_str)
            logger.info(f"Validation result: {validation_result['valid']}")
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing validation result: {e}")
            validation_result = {
                "valid": False,
                "issues": [
                    {
                        "severity": "error",
                        "message": f"Error parsing validation result: {str(e)}",
                        "line": 1,
                        "column": 1
                    }
                ],
                "summary": "Error parsing validation result"
            }
        
        return {
            "validation_result": validation_result
        }
    except Exception as e:
        logger.error(f"Error validating code: {e}")
        return {
            "errors": state.errors + [{"stage": "code_validation", "message": str(e)}],
            "validation_result": {
                "valid": False,
                "issues": [
                    {
                        "severity": "error",
                        "message": f"Error validating code: {str(e)}",
                        "line": 1,
                        "column": 1
                    }
                ],
                "summary": f"Error validating code: {str(e)}"
            }
        }

async def generate_documentation(state: AgentState) -> Dict[str, Any]:
    """
    Generate documentation for the code.
    
    Args:
        state: The current agent state
        
    Returns:
        Updated state with documentation
    """
    try:
        logger.info("Generating documentation")
        
        # If LLM is not available, return mock documentation
        if not LLM_AVAILABLE or not llm:
            logger.warning("LLM not available, returning mock documentation")
            return {
                "documentation": f"# Mock Documentation\n\nThis is mock documentation for the generated code."
            }
        
        # If no code is generated, return error
        if not state.generated_code:
            logger.error("No code to document")
            return {
                "errors": state.errors + [{"stage": "documentation_generation", "message": "No code was generated"}],
                "documentation": "# Error\n\nNo code was generated to document."
            }
        
        # Get requirements and code
        requirements_text = json.dumps(state.requirements, indent=2)
        code = state.generated_code
        
        # Get language from processed requirements
        language = state.processed_requirements.get("language", "java") if state.processed_requirements else "java"
        
        # Create the prompt
        prompt = PromptTemplate.from_template(
            """
            You are an expert technical writer tasked with documenting code.
            
            # Requirements
            {requirements}
            
            # Code to Document
            ```{language}
            {code}
            ```
            
            Generate comprehensive documentation for this code in Markdown format.
            Include:
            1. Overview of what the code does
            2. Installation instructions (if applicable)
            3. Usage examples
            4. API documentation for functions/classes
            5. Any important notes or caveats
            
            Format your response as clean Markdown.
            """
        )
        
        # Create the chain
        chain = prompt | llm | StrOutputParser()
        
        # Run the chain
        documentation = await chain.ainvoke({
            "requirements": requirements_text,
            "code": code,
            "language": language
        })
        
        logger.info(f"Generated documentation with {len(documentation)} characters")
        
        return {
            "documentation": documentation
        }
    except Exception as e:
        logger.error(f"Error generating documentation: {e}")
        return {
            "errors": state.errors + [{"stage": "documentation_generation", "message": str(e)}],
            "documentation": f"# Error\n\nError generating documentation: {str(e)}"
        }

async def generate_tests(state: AgentState) -> Dict[str, Any]:
    """
    Generate tests for the code.
    
    Args:
        state: The current agent state
        
    Returns:
        Updated state with tests
    """
    try:
        logger.info("Generating tests")
        
        # If LLM is not available, return mock tests
        if not LLM_AVAILABLE or not llm:
            logger.warning("LLM not available, returning mock tests")
            return {
                "tests": f"// Mock tests for the generated code"
            }
        
        # If no code is generated, return error
        if not state.generated_code:
            logger.error("No code to test")
            return {
                "errors": state.errors + [{"stage": "test_generation", "message": "No code was generated"}],
                "tests": "// Error: No code was generated to test"
            }
        
        # Get requirements and code
        requirements_text = json.dumps(state.requirements, indent=2)
        code = state.generated_code
        
        # Get language from processed requirements
        language = state.processed_requirements.get("language", "java") if state.processed_requirements else "java"
        
        # Determine test framework based on language
        test_framework = "pytest"
        if language.lower() in ["java"]:
            test_framework = "JUnit"
        elif language.lower() in ["javascript", "js", "typescript", "ts"]:
            test_framework = "Jest"
        
        # Create the prompt
        prompt = PromptTemplate.from_template(
            """
            You are an expert software developer tasked with writing tests.
            
            # Requirements
            {requirements}
            
            # Code to Test
            ```{language}
            {code}
            ```
            
            # Task
            Generate comprehensive tests for this code using {test_framework}.
            The tests should:
            1. Cover all functionality
            2. Include edge cases
            3. Be well-documented
            4. Follow best practices for {test_framework}
            
            Only respond with the test code. Do not include any explanations or comments outside the code.
            """
        )
        
        # Create the chain
        chain = prompt | llm | StrOutputParser()
        
        # Run the chain
        tests = await chain.ainvoke({
            "requirements": requirements_text,
            "code": code,
            "language": language,
            "test_framework": test_framework
        })
        
        logger.info(f"Generated tests with {len(tests)} characters")
        
        return {
            "tests": tests
        }
    except Exception as e:
        logger.error(f"Error generating tests: {e}")
        return {
            "errors": state.errors + [{"stage": "test_generation", "message": str(e)}],
            "tests": f"// Error generating tests: {str(e)}"
        }
