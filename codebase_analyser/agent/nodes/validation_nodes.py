"""
Validation nodes for the agent graph.
"""
import logging
import os
import json
import tempfile
import subprocess
from typing import Dict, Any, List, Optional
import re
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from ..state import AgentState
from .llm_nodes import llm

# Configure logging
logger = logging.getLogger(__name__)

# Validation prompt template
VALIDATION_PROMPT_TEMPLATE = """
You are an expert software developer tasked with validating code.

# Code to Validate
```{language}
{code}
```

# Requirements
{requirements}

Your task is to validate the code against the requirements and check for any errors or issues.
Please analyze the code for:
1. Syntax errors
2. Logical errors
3. Compliance with requirements
4. Best practices and code quality

Provide your analysis in the following JSON format:
```json
{
  "valid": true/false,
  "issues": [
    {
      "severity": "error/warning/info",
      "message": "Description of the issue",
      "line": line_number,
      "column": column_number
    }
  ],
  "summary": "Overall assessment of the code"
}
```

Only respond with the JSON. Do not include any other text.
"""

async def validate_code(state: AgentState) -> Dict[str, Any]:
    """
    Validate the generated code.
    
    Args:
        state: The current agent state
        
    Returns:
        Updated state with validation results
    """
    logger.info("Validating generated code")
    
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
    
    # Get language from processed requirements
    language = state.processed_requirements.get("language", "java") if state.processed_requirements else "java"
    
    # Perform static validation
    static_validation = perform_static_validation(state.generated_code, language)
    
    # If static validation failed with critical errors, return the result
    if static_validation and not static_validation.get("valid", True) and any(
        issue.get("severity") == "error" for issue in static_validation.get("issues", [])
    ):
        logger.info("Static validation failed with critical errors")
        return {
            "validation_result": static_validation
        }
    
    # Perform LLM-based validation
    llm_validation = await perform_llm_validation(state)
    
    # Combine validation results
    combined_validation = combine_validation_results(static_validation, llm_validation)
    
    logger.info(f"Validation result: valid={combined_validation.get('valid', False)}")
    
    return {
        "validation_result": combined_validation
    }

def perform_static_validation(code: str, language: str) -> Dict[str, Any]:
    """
    Perform static validation of the code.
    
    Args:
        code: The code to validate
        language: The programming language
        
    Returns:
        Validation result
    """
    try:
        # Initialize validation result
        validation_result = {
            "valid": True,
            "issues": [],
            "summary": "Static validation passed"
        }
        
        # Check for empty code
        if not code.strip():
            validation_result["valid"] = False
            validation_result["issues"].append({
                "severity": "error",
                "message": "Code is empty",
                "line": 1,
                "column": 1
            })
            validation_result["summary"] = "Code is empty"
            return validation_result
        
        # Check for syntax errors based on language
        if language.lower() in ["python", "py"]:
            syntax_validation = validate_python_syntax(code)
            if not syntax_validation.get("valid", True):
                validation_result["valid"] = False
                validation_result["issues"].extend(syntax_validation.get("issues", []))
                validation_result["summary"] = "Python syntax validation failed"
        elif language.lower() in ["java"]:
            syntax_validation = validate_java_syntax(code)
            if not syntax_validation.get("valid", True):
                validation_result["valid"] = False
                validation_result["issues"].extend(syntax_validation.get("issues", []))
                validation_result["summary"] = "Java syntax validation failed"
        elif language.lower() in ["javascript", "js"]:
            syntax_validation = validate_javascript_syntax(code)
            if not syntax_validation.get("valid", True):
                validation_result["valid"] = False
                validation_result["issues"].extend(syntax_validation.get("issues", []))
                validation_result["summary"] = "JavaScript syntax validation failed"
        
        # Check for common issues
        common_issues = check_common_issues(code, language)
        if common_issues:
            validation_result["issues"].extend(common_issues)
            
            # If there are error-level issues, mark as invalid
            if any(issue.get("severity") == "error" for issue in common_issues):
                validation_result["valid"] = False
                validation_result["summary"] = "Common issues validation failed"
        
        return validation_result
    except Exception as e:
        logger.error(f"Error performing static validation: {e}")
        return {
            "valid": False,
            "issues": [
                {
                    "severity": "error",
                    "message": f"Static validation error: {str(e)}",
                    "line": 1,
                    "column": 1
                }
            ],
            "summary": f"Static validation error: {str(e)}"
        }

def validate_python_syntax(code: str) -> Dict[str, Any]:
    """
    Validate Python syntax.
    
    Args:
        code: The Python code to validate
        
    Returns:
        Validation result
    """
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(code.encode("utf-8"))
        
        # Validate syntax using Python compiler
        result = subprocess.run(
            ["python", "-m", "py_compile", temp_file_path],
            capture_output=True,
            text=True
        )
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
        # Check if compilation was successful
        if result.returncode != 0:
            # Parse the error message
            error_message = result.stderr
            line_match = re.search(r"line (\d+)", error_message)
            line_number = int(line_match.group(1)) if line_match else 1
            
            return {
                "valid": False,
                "issues": [
                    {
                        "severity": "error",
                        "message": f"Python syntax error: {error_message}",
                        "line": line_number,
                        "column": 1
                    }
                ]
            }
        
        return {
            "valid": True,
            "issues": []
        }
    except Exception as e:
        logger.error(f"Error validating Python syntax: {e}")
        return {
            "valid": False,
            "issues": [
                {
                    "severity": "error",
                    "message": f"Python syntax validation error: {str(e)}",
                    "line": 1,
                    "column": 1
                }
            ]
        }

def validate_java_syntax(code: str) -> Dict[str, Any]:
    """
    Validate Java syntax.
    
    Args:
        code: The Java code to validate
        
    Returns:
        Validation result
    """
    # Check if javac is available
    try:
        subprocess.run(["javac", "-version"], capture_output=True, check=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        logger.warning("javac not available, skipping Java syntax validation")
        return {
            "valid": True,
            "issues": [
                {
                    "severity": "info",
                    "message": "Java syntax validation skipped (javac not available)",
                    "line": 1,
                    "column": 1
                }
            ]
        }
    
    try:
        # Extract class name from code
        class_match = re.search(r"public\s+class\s+(\w+)", code)
        class_name = class_match.group(1) if class_match else "Main"
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=f"{class_name}.java", delete=False) as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(code.encode("utf-8"))
        
        # Validate syntax using javac
        result = subprocess.run(
            ["javac", temp_file_path],
            capture_output=True,
            text=True
        )
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
        # Check if compilation was successful
        if result.returncode != 0:
            # Parse the error message
            error_message = result.stderr
            line_match = re.search(r":(\d+):", error_message)
            line_number = int(line_match.group(1)) if line_match else 1
            
            return {
                "valid": False,
                "issues": [
                    {
                        "severity": "error",
                        "message": f"Java syntax error: {error_message}",
                        "line": line_number,
                        "column": 1
                    }
                ]
            }
        
        return {
            "valid": True,
            "issues": []
        }
    except Exception as e:
        logger.error(f"Error validating Java syntax: {e}")
        return {
            "valid": False,
            "issues": [
                {
                    "severity": "error",
                    "message": f"Java syntax validation error: {str(e)}",
                    "line": 1,
                    "column": 1
                }
            ]
        }

def validate_javascript_syntax(code: str) -> Dict[str, Any]:
    """
    Validate JavaScript syntax.
    
    Args:
        code: The JavaScript code to validate
        
    Returns:
        Validation result
    """
    # Check if node is available
    try:
        subprocess.run(["node", "--version"], capture_output=True, check=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        logger.warning("node not available, skipping JavaScript syntax validation")
        return {
            "valid": True,
            "issues": [
                {
                    "severity": "info",
                    "message": "JavaScript syntax validation skipped (node not available)",
                    "line": 1,
                    "column": 1
                }
            ]
        }
    
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".js", delete=False) as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(code.encode("utf-8"))
        
        # Validate syntax using node
        result = subprocess.run(
            ["node", "--check", temp_file_path],
            capture_output=True,
            text=True
        )
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
        # Check if syntax check was successful
        if result.returncode != 0:
            # Parse the error message
            error_message = result.stderr
            line_match = re.search(r":(\d+)", error_message)
            line_number = int(line_match.group(1)) if line_match else 1
            
            return {
                "valid": False,
                "issues": [
                    {
                        "severity": "error",
                        "message": f"JavaScript syntax error: {error_message}",
                        "line": line_number,
                        "column": 1
                    }
                ]
            }
        
        return {
            "valid": True,
            "issues": []
        }
    except Exception as e:
        logger.error(f"Error validating JavaScript syntax: {e}")
        return {
            "valid": False,
            "issues": [
                {
                    "severity": "error",
                    "message": f"JavaScript syntax validation error: {str(e)}",
                    "line": 1,
                    "column": 1
                }
            ]
        }

def check_common_issues(code: str, language: str) -> List[Dict[str, Any]]:
    """
    Check for common issues in the code.
    
    Args:
        code: The code to check
        language: The programming language
        
    Returns:
        List of issues
    """
    issues = []
    
    # Check for TODO comments
    todo_pattern = r"(?i)TODO|FIXME"
    for i, line in enumerate(code.split("\n")):
        if re.search(todo_pattern, line):
            issues.append({
                "severity": "warning",
                "message": f"TODO or FIXME comment found: {line.strip()}",
                "line": i + 1,
                "column": 1
            })
    
    # Check for hardcoded credentials
    credential_patterns = [
        r"password\s*=\s*['\"](?!.*\$\{).*['\"]",
        r"api[_-]?key\s*=\s*['\"](?!.*\$\{).*['\"]",
        r"secret\s*=\s*['\"](?!.*\$\{).*['\"]",
        r"token\s*=\s*['\"](?!.*\$\{).*['\"]"
    ]
    
    for pattern in credential_patterns:
        for i, line in enumerate(code.split("\n")):
            if re.search(pattern, line, re.IGNORECASE):
                issues.append({
                    "severity": "error",
                    "message": f"Hardcoded credential found: {line.strip()}",
                    "line": i + 1,
                    "column": 1
                })
    
    # Language-specific checks
    if language.lower() in ["python", "py"]:
        # Check for bare except
        for i, line in enumerate(code.split("\n")):
            if re.search(r"except\s*:", line):
                issues.append({
                    "severity": "warning",
                    "message": "Bare except clause found. Specify exception types to catch.",
                    "line": i + 1,
                    "column": 1
                })
    
    elif language.lower() in ["java"]:
        # Check for empty catch blocks
        for i, line in enumerate(code.split("\n")):
            if re.search(r"catch\s*\([^)]+\)\s*\{\s*\}", line):
                issues.append({
                    "severity": "warning",
                    "message": "Empty catch block found. Consider logging or handling the exception.",
                    "line": i + 1,
                    "column": 1
                })
    
    elif language.lower() in ["javascript", "js"]:
        # Check for console.log statements
        for i, line in enumerate(code.split("\n")):
            if re.search(r"console\.log", line):
                issues.append({
                    "severity": "info",
                    "message": "console.log statement found. Consider removing in production code.",
                    "line": i + 1,
                    "column": 1
                })
    
    return issues

async def perform_llm_validation(state: AgentState) -> Dict[str, Any]:
    """
    Perform LLM-based validation of the code.
    
    Args:
        state: The current agent state
        
    Returns:
        Validation result
    """
    try:
        # If LLM is not available, return empty validation
        if not llm:
            logger.warning("LLM not available, skipping LLM-based validation")
            return {
                "valid": True,
                "issues": [
                    {
                        "severity": "info",
                        "message": "LLM-based validation skipped (LLM not available)",
                        "line": 1,
                        "column": 1
                    }
                ],
                "summary": "LLM-based validation skipped"
            }
        
        # Get language and requirements from processed requirements
        language = state.processed_requirements.get("language", "java") if state.processed_requirements else "java"
        requirements_text = state.processed_requirements.get("original_text", "") if state.processed_requirements else ""
        
        # Create the prompt
        prompt = PromptTemplate.from_template(VALIDATION_PROMPT_TEMPLATE)
        
        # Create the parser
        parser = JsonOutputParser()
        
        # Create the chain
        chain = prompt | llm | parser
        
        # Run the chain
        response = await chain.ainvoke({
            "language": language,
            "code": state.generated_code,
            "requirements": requirements_text
        })
        
        # Ensure the response has the expected format
        if not isinstance(response, dict):
            logger.warning(f"Unexpected LLM validation response format: {type(response)}")
            return {
                "valid": False,
                "issues": [
                    {
                        "severity": "error",
                        "message": "LLM validation failed: unexpected response format",
                        "line": 1,
                        "column": 1
                    }
                ],
                "summary": "LLM validation failed"
            }
        
        # Ensure the response has the required fields
        if "valid" not in response:
            response["valid"] = False
        
        if "issues" not in response:
            response["issues"] = []
        
        if "summary" not in response:
            response["summary"] = "LLM validation completed"
        
        logger.info(f"LLM validation result: valid={response.get('valid', False)}")
        
        return response
    except Exception as e:
        logger.error(f"Error performing LLM-based validation: {e}")
        return {
            "valid": False,
            "issues": [
                {
                    "severity": "error",
                    "message": f"LLM validation error: {str(e)}",
                    "line": 1,
                    "column": 1
                }
            ],
            "summary": f"LLM validation error: {str(e)}"
        }

def combine_validation_results(static_validation: Dict[str, Any], llm_validation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Combine static and LLM-based validation results.
    
    Args:
        static_validation: Static validation result
        llm_validation: LLM-based validation result
        
    Returns:
        Combined validation result
    """
    # Initialize combined result
    combined_result = {
        "valid": True,
        "issues": [],
        "summary": "Validation passed"
    }
    
    # Add static validation issues
    if static_validation and "issues" in static_validation:
        combined_result["issues"].extend(static_validation.get("issues", []))
        
        # If static validation failed, mark combined result as invalid
        if not static_validation.get("valid", True):
            combined_result["valid"] = False
    
    # Add LLM validation issues
    if llm_validation and "issues" in llm_validation:
        combined_result["issues"].extend(llm_validation.get("issues", []))
        
        # If LLM validation failed, mark combined result as invalid
        if not llm_validation.get("valid", True):
            combined_result["valid"] = False
    
    # Create summary
    if not combined_result["valid"]:
        error_count = len([i for i in combined_result["issues"] if i.get("severity") == "error"])
        warning_count = len([i for i in combined_result["issues"] if i.get("severity") == "warning"])
        info_count = len([i for i in combined_result["issues"] if i.get("severity") == "info"])
        
        combined_result["summary"] = f"Validation failed with {error_count} errors, {warning_count} warnings, and {info_count} info messages"
    else:
        combined_result["summary"] = "Validation passed successfully"
    
    return combined_result

def create_validation_report(validation_result: Dict[str, Any]) -> str:
    """
    Create a human-readable validation report.
    
    Args:
        validation_result: The validation result
        
    Returns:
        Human-readable report
    """
    if not validation_result:
        return "No validation results available"
    
    # Start with summary
    report = [f"# Validation Report\n"]
    report.append(f"**Status**: {'✅ Valid' if validation_result.get('valid', False) else '❌ Invalid'}\n")
    report.append(f"**Summary**: {validation_result.get('summary', 'No summary available')}\n")
    
    # Add issues
    issues = validation_result.get("issues", [])
    if issues:
        report.append("\n## Issues\n")
        
        # Group issues by severity
        errors = [i for i in issues if i.get("severity") == "error"]
        warnings = [i for i in issues if i.get("severity") == "warning"]
        infos = [i for i in issues if i.get("severity") == "info"]
        
        # Add errors
        if errors:
            report.append("\n### Errors\n")
            for issue in errors:
                report.append(f"- Line {issue.get('line', '?')}: {issue.get('message', 'Unknown error')}\n")
        
        # Add warnings
        if warnings:
            report.append("\n### Warnings\n")
            for issue in warnings:
                report.append(f"- Line {issue.get('line', '?')}: {issue.get('message', 'Unknown warning')}\n")
        
        # Add infos
        if infos:
            report.append("\n### Info\n")
            for issue in infos:
                report.append(f"- Line {issue.get('line', '?')}: {issue.get('message', 'Unknown info')}\n")
    else:
        report.append("\nNo issues found.\n")
    
    return "".join(report)

def validate_with_pydantic(code: str, schema_name: str) -> Dict[str, Any]:
    """
    Validate code against a Pydantic schema.
    
    Args:
        code: The code to validate
        schema_name: The name of the Pydantic schema
        
    Returns:
        Validation result
    """
    try:
        # This is a placeholder for future implementation
        # In a real implementation, we would:
        # 1. Import the schema dynamically
        # 2. Parse the code into a Python object
        # 3. Validate against the schema
        
        logger.warning(f"Pydantic validation not implemented for schema: {schema_name}")
        
        return {
            "valid": True,
            "issues": [
                {
                    "severity": "info",
                    "message": f"Pydantic validation not implemented for schema: {schema_name}",
                    "line": 1,
                    "column": 1
                }
            ],
            "summary": "Pydantic validation skipped"
        }
    except Exception as e:
        logger.error(f"Error performing Pydantic validation: {e}")
        return {
            "valid": False,
            "issues": [
                {
                    "severity": "error",
                    "message": f"Pydantic validation error: {str(e)}",
                    "line": 1,
                    "column": 1
                }
            ],
            "summary": f"Pydantic validation error: {str(e)}"
        }
