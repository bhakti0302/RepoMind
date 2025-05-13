"""
Output Display module.

This module provides functionality for displaying output in the VS Code extension.
"""

import os
import sys
import logging
import json
import difflib
from typing import Dict, List, Any, Optional, Union, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import local modules
from src.utils import ensure_dir, save_json, load_json

class OutputDisplay:
    """Display for output in the VS Code extension."""
    
    def __init__(
        self,
        output_dir: str = None,
        format_type: str = "markdown"
    ):
        """Initialize the output display.
        
        Args:
            output_dir: Path to the output directory
            format_type: Format type for the output (markdown, text)
        """
        self.output_dir = output_dir
        self.format_type = format_type
        
        # Create output directory if specified
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def format_processing_result(
        self,
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format a processing result for display.
        
        Args:
            result: Processing result
            
        Returns:
            Dictionary containing formatted result
        """
        try:
            # Check if result is valid
            if not result or "error" in result:
                return {
                    "status": "error",
                    "message": result.get("error", "Invalid result"),
                    "formatted_result": None
                }
            
            # Get the processed requirements
            processed_requirements = result.get("processed_requirements", {})
            
            # Get the retrieved context
            retrieved_context = result.get("retrieved_context", {})
            
            # Get the code instructions
            code_instructions = result.get("code_instructions", {})
            
            # Format the result
            formatted_result = {
                "requirements": {
                    "original_text": processed_requirements.get("original_text", ""),
                    "entities": processed_requirements.get("entities", []),
                    "components": processed_requirements.get("components", {}),
                    "search_queries": processed_requirements.get("search_queries", [])
                },
                "context": {
                    "rag_type": retrieved_context.get("rag_type", ""),
                    "context": retrieved_context.get("context", ""),
                    "total_tokens": retrieved_context.get("total_tokens", 0),
                    "truncated": retrieved_context.get("truncated", False)
                },
                "instructions": {
                    "requirements": code_instructions.get("requirements", ""),
                    "context": code_instructions.get("context", ""),
                    "instructions": code_instructions.get("instructions", "")
                },
                "output_file": result.get("output_file", "")
            }
            
            return {
                "status": "success",
                "message": "Result formatted successfully",
                "formatted_result": formatted_result
            }
        
        except Exception as e:
            logger.error(f"Error formatting processing result: {e}")
            return {
                "status": "error",
                "message": f"Error formatting processing result: {e}",
                "formatted_result": None
            }
    
    def format_for_chat(
        self,
        result: Dict[str, Any]
    ) -> str:
        """Format a processing result for chat display.
        
        Args:
            result: Processing result
            
        Returns:
            Formatted result for chat display
        """
        try:
            # Format the result
            formatted_result = self.format_processing_result(result)
            
            if formatted_result["status"] == "error":
                return f"Error: {formatted_result['message']}"
            
            # Get the formatted result
            result = formatted_result["formatted_result"]
            
            # Format for chat
            if self.format_type == "markdown":
                # Format as markdown
                chat_output = "## Processing Result\n\n"
                
                # Add requirements summary
                chat_output += "### Requirements Summary\n\n"
                
                # Add entities
                entities = result["requirements"]["entities"]
                if entities:
                    chat_output += "**Entities:**\n\n"
                    for entity_type, entity_list in entities.items():
                        if entity_list:
                            chat_output += f"- **{entity_type}**: {', '.join(entity_list)}\n"
                    chat_output += "\n"
                
                # Add search queries
                search_queries = result["requirements"]["search_queries"]
                if search_queries:
                    chat_output += "**Search Queries:**\n\n"
                    for query in search_queries:
                        chat_output += f"- {query}\n"
                    chat_output += "\n"
                
                # Add context summary
                chat_output += "### Context Summary\n\n"
                chat_output += f"**RAG Type:** {result['context']['rag_type']}\n"
                chat_output += f"**Total Tokens:** {result['context']['total_tokens']}\n"
                chat_output += f"**Truncated:** {result['context']['truncated']}\n\n"
                
                # Add output file
                if result["output_file"]:
                    chat_output += f"**Output File:** {result['output_file']}\n\n"
                
                # Add instructions to view the full result
                chat_output += "### Next Steps\n\n"
                chat_output += "To view the full result, open the output file or use the 'View Output' command.\n"
            
            else:  # text
                # Format as text
                chat_output = "PROCESSING RESULT\n==================\n\n"
                
                # Add requirements summary
                chat_output += "REQUIREMENTS SUMMARY\n-------------------\n\n"
                
                # Add entities
                entities = result["requirements"]["entities"]
                if entities:
                    chat_output += "Entities:\n\n"
                    for entity_type, entity_list in entities.items():
                        if entity_list:
                            chat_output += f"- {entity_type}: {', '.join(entity_list)}\n"
                    chat_output += "\n"
                
                # Add search queries
                search_queries = result["requirements"]["search_queries"]
                if search_queries:
                    chat_output += "Search Queries:\n\n"
                    for query in search_queries:
                        chat_output += f"- {query}\n"
                    chat_output += "\n"
                
                # Add context summary
                chat_output += "CONTEXT SUMMARY\n---------------\n\n"
                chat_output += f"RAG Type: {result['context']['rag_type']}\n"
                chat_output += f"Total Tokens: {result['context']['total_tokens']}\n"
                chat_output += f"Truncated: {result['context']['truncated']}\n\n"
                
                # Add output file
                if result["output_file"]:
                    chat_output += f"Output File: {result['output_file']}\n\n"
                
                # Add instructions to view the full result
                chat_output += "NEXT STEPS\n----------\n\n"
                chat_output += "To view the full result, open the output file or use the 'View Output' command.\n"
            
            return chat_output
        
        except Exception as e:
            logger.error(f"Error formatting for chat: {e}")
            return f"Error formatting for chat: {e}"
    
    def generate_diff(
        self,
        original_code: str,
        generated_code: str,
        file_name: str = "code.txt"
    ) -> str:
        """Generate a diff between original and generated code.
        
        Args:
            original_code: Original code
            generated_code: Generated code
            file_name: File name for the diff
            
        Returns:
            Diff between original and generated code
        """
        try:
            # Split the code into lines
            original_lines = original_code.splitlines()
            generated_lines = generated_code.splitlines()
            
            # Generate the diff
            diff = difflib.unified_diff(
                original_lines,
                generated_lines,
                fromfile=f"original/{file_name}",
                tofile=f"generated/{file_name}",
                lineterm=""
            )
            
            # Join the diff lines
            diff_text = "\n".join(diff)
            
            return diff_text
        
        except Exception as e:
            logger.error(f"Error generating diff: {e}")
            return f"Error generating diff: {e}"
    
    def save_formatted_output(
        self,
        result: Dict[str, Any],
        file_name: str = "formatted_output.md"
    ) -> Dict[str, Any]:
        """Save formatted output to a file.
        
        Args:
            result: Processing result
            file_name: Name of the output file
            
        Returns:
            Dictionary containing saving results
        """
        try:
            # Check if output directory is specified
            if not self.output_dir:
                return {
                    "status": "error",
                    "message": "Output directory not specified",
                    "file_path": None
                }
            
            # Format the result for chat
            formatted_output = self.format_for_chat(result)
            
            # Create the file path
            file_path = os.path.join(self.output_dir, file_name)
            
            # Write the formatted output to the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(formatted_output)
            
            logger.info(f"Saved formatted output to {file_path}")
            
            return {
                "status": "success",
                "message": f"Saved formatted output to {file_path}",
                "file_path": file_path
            }
        
        except Exception as e:
            logger.error(f"Error saving formatted output: {e}")
            return {
                "status": "error",
                "message": f"Error saving formatted output: {e}",
                "file_path": None
            }
    
    def create_html_view(
        self,
        result: Dict[str, Any],
        file_name: str = "output_view.html"
    ) -> Dict[str, Any]:
        """Create an HTML view of the processing result.
        
        Args:
            result: Processing result
            file_name: Name of the output file
            
        Returns:
            Dictionary containing creation results
        """
        try:
            # Check if output directory is specified
            if not self.output_dir:
                return {
                    "status": "error",
                    "message": "Output directory not specified",
                    "file_path": None
                }
            
            # Format the result
            formatted_result = self.format_processing_result(result)
            
            if formatted_result["status"] == "error":
                return {
                    "status": "error",
                    "message": formatted_result["message"],
                    "file_path": None
                }
            
            # Get the formatted result
            result = formatted_result["formatted_result"]
            
            # Create HTML content
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Processing Result</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        margin: 0;
                        padding: 20px;
                        color: #333;
                    }
                    h1, h2, h3 {
                        color: #0066cc;
                    }
                    .container {
                        max-width: 1200px;
                        margin: 0 auto;
                    }
                    .section {
                        margin-bottom: 30px;
                        padding: 20px;
                        background-color: #f9f9f9;
                        border-radius: 5px;
                    }
                    .code {
                        font-family: monospace;
                        background-color: #f5f5f5;
                        padding: 10px;
                        border-radius: 3px;
                        overflow-x: auto;
                        white-space: pre-wrap;
                    }
                    .entity-list {
                        list-style-type: none;
                        padding: 0;
                    }
                    .entity-type {
                        font-weight: bold;
                        margin-right: 10px;
                    }
                    .query-list {
                        list-style-type: disc;
                        padding-left: 20px;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Processing Result</h1>
                    
                    <div class="section">
                        <h2>Requirements</h2>
                        <h3>Original Text</h3>
                        <div class="code">
                            {requirements_text}
                        </div>
                        
                        <h3>Entities</h3>
                        <ul class="entity-list">
                            {entities_html}
                        </ul>
                        
                        <h3>Search Queries</h3>
                        <ul class="query-list">
                            {queries_html}
                        </ul>
                    </div>
                    
                    <div class="section">
                        <h2>Context</h2>
                        <p><strong>RAG Type:</strong> {rag_type}</p>
                        <p><strong>Total Tokens:</strong> {total_tokens}</p>
                        <p><strong>Truncated:</strong> {truncated}</p>
                        
                        <h3>Context Content</h3>
                        <div class="code">
                            {context_html}
                        </div>
                    </div>
                    
                    <div class="section">
                        <h2>Instructions</h2>
                        <div class="code">
                            {instructions_html}
                        </div>
                    </div>
                    
                    <div class="section">
                        <h2>Output File</h2>
                        <p>{output_file}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Format entities HTML
            entities_html = ""
            for entity_type, entity_list in result["requirements"]["entities"].items():
                if entity_list:
                    entities_html += f'<li><span class="entity-type">{entity_type}:</span> {", ".join(entity_list)}</li>\n'
            
            # Format queries HTML
            queries_html = ""
            for query in result["requirements"]["search_queries"]:
                queries_html += f"<li>{query}</li>\n"
            
            # Format context HTML
            context_html = result["context"]["context"].replace("<", "&lt;").replace(">", "&gt;")
            
            # Format instructions HTML
            instructions_html = result["instructions"]["instructions"].replace("<", "&lt;").replace(">", "&gt;")
            
            # Replace placeholders
            html_content = html_content.format(
                requirements_text=result["requirements"]["original_text"].replace("<", "&lt;").replace(">", "&gt;"),
                entities_html=entities_html,
                queries_html=queries_html,
                rag_type=result["context"]["rag_type"],
                total_tokens=result["context"]["total_tokens"],
                truncated=result["context"]["truncated"],
                context_html=context_html,
                instructions_html=instructions_html,
                output_file=result["output_file"]
            )
            
            # Create the file path
            file_path = os.path.join(self.output_dir, file_name)
            
            # Write the HTML content to the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Created HTML view at {file_path}")
            
            return {
                "status": "success",
                "message": f"Created HTML view at {file_path}",
                "file_path": file_path
            }
        
        except Exception as e:
            logger.error(f"Error creating HTML view: {e}")
            return {
                "status": "error",
                "message": f"Error creating HTML view: {e}",
                "file_path": None
            }


# Example usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Display output in VS Code extension")
    parser.add_argument("--result-file", required=True, help="Path to the result file")
    parser.add_argument("--output-dir", help="Path to the output directory")
    parser.add_argument("--format", choices=["markdown", "text"], default="markdown",
                        help="Format type for the output")
    args = parser.parse_args()
    
    # Create an output display
    display = OutputDisplay(
        output_dir=args.output_dir,
        format_type=args.format
    )
    
    # Load the result
    with open(args.result_file, 'r', encoding='utf-8') as f:
        result = json.load(f)
    
    # Format the result for chat
    chat_output = display.format_for_chat(result)
    
    # Print the chat output
    print(chat_output)
    
    # Save the formatted output
    save_result = display.save_formatted_output(result)
    
    if save_result["status"] == "success":
        print(f"\nSaved formatted output to {save_result['file_path']}")
    
    # Create an HTML view
    html_result = display.create_html_view(result)
    
    if html_result["status"] == "success":
        print(f"Created HTML view at {html_result['file_path']}")
