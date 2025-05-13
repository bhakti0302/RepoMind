"""
Code Synthesis Workflow module.

This module provides functionality for the end-to-end code synthesis workflow.
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

# Import local modules

# Try different import paths to handle both direct and package imports
try:
    # Try direct imports first (when running from the same directory)
    from requirements_parser import RequirementsParser
    from entity_extractor import EntityExtractor
    from component_analyzer import ComponentAnalyzer
    from text_processor import TextProcessor
    from vector_search import VectorSearch
    from graph_enhancer import GraphEnhancer
    from context_builder import ContextBuilder
    from relevance_scorer import RelevanceScorer
    from context_combiner import ContextCombiner
    from multi_hop_rag import MultiHopRAG
    from llm_client import NVIDIALlamaClient
    from env_loader import get_env_var, load_env_vars
    from utils import save_json, load_json, ensure_dir, generate_search_queries
except ImportError:
    # Fall back to package imports (when imported as a module)
    from src.requirements_parser import RequirementsParser
    from src.entity_extractor import EntityExtractor
    from src.component_analyzer import ComponentAnalyzer
    from src.text_processor import TextProcessor
    from src.vector_search import VectorSearch
    from src.graph_enhancer import GraphEnhancer
    from src.context_builder import ContextBuilder
    from src.relevance_scorer import RelevanceScorer
    from src.context_combiner import ContextCombiner
    from src.multi_hop_rag import MultiHopRAG
    from src.llm_client import NVIDIALlamaClient
    from src.env_loader import get_env_var, load_env_vars
    from src.utils import save_json, load_json, ensure_dir, generate_search_queries

# Load environment variables
load_env_vars()

class CodeSynthesisWorkflow:
    """Workflow for end-to-end code synthesis."""

    def __init__(
        self,
        db_path: str = None,
        output_dir: str = None,
        model_name: str = None,
        max_context_length: int = None,
        llm_api_key: str = None,
        llm_model_name: str = None
    ):
        """Initialize the code synthesis workflow.

        Args:
            db_path: Path to the LanceDB database
            output_dir: Path to the output directory
            model_name: Name of the spaCy model to use
            max_context_length: Maximum length of the context in tokens
            llm_api_key: API key for the LLM service
            llm_model_name: Name of the LLM model to use
        """
        # Get values from environment variables if not provided
        self.db_path = db_path or os.environ.get("DB_PATH", ".lancedb")
        self.output_dir = output_dir or os.environ.get("OUTPUT_DIR")
        self.model_name = model_name or os.environ.get("SPACY_MODEL", "en_core_web_md")
        self.max_context_length = max_context_length or int(os.environ.get("MAX_CONTEXT_LENGTH", "4000"))
        self.llm_api_key = llm_api_key or os.environ.get("LLM_API_KEY")
        self.llm_model_name = llm_model_name or os.environ.get("LLM_MODEL_NAME", "nvidia/llama-3.3-nemotron-super-49b-v1:free")

        # Initialize components
        self.requirements_parser = None
        self.entity_extractor = None
        self.component_analyzer = None
        self.text_processor = None
        self.vector_search = None
        self.graph_enhancer = None
        self.context_builder = None
        self.relevance_scorer = None
        self.context_combiner = None
        self.multi_hop_rag = None
        self.llm_client = None

        try:
            # Create output directory if specified
            if output_dir:
                ensure_dir(output_dir)

            # Initialize NLP components
            self.requirements_parser = RequirementsParser(model_name=model_name)
            self.entity_extractor = EntityExtractor(nlp=self.requirements_parser.nlp)
            self.component_analyzer = ComponentAnalyzer(nlp=self.requirements_parser.nlp)
            self.text_processor = TextProcessor(nlp=self.requirements_parser.nlp)

            # Initialize RAG components
            self.vector_search = VectorSearch(db_path=db_path)
            self.graph_enhancer = GraphEnhancer(db_path=db_path)
            self.context_builder = ContextBuilder(max_context_length=max_context_length)
            self.relevance_scorer = RelevanceScorer()
            self.context_combiner = ContextCombiner(max_context_length=max_context_length)
            self.multi_hop_rag = MultiHopRAG(db_path=db_path, output_dir=output_dir)

            # Initialize LLM client if API key is provided
            if self.llm_api_key:
                # Get API base URL from environment
                api_base_url = os.environ.get("OPENAI_API_BASE_URL")
                if api_base_url:
                    self.llm_client = NVIDIALlamaClient(
                        api_key=self.llm_api_key,
                        model_name=self.llm_model_name,
                        api_url=api_base_url,
                        output_dir=output_dir
                    )
                    logger.info(f"Initialized LLM client for {self.llm_model_name} using OpenRouter API")
                else:
                    logger.warning("No API base URL found in environment variables. LLM functionality will be limited.")
                    self.llm_client = None
            else:
                logger.warning("No LLM API key provided. LLM functionality will be limited.")
                self.llm_client = None

            logger.info("Initialized code synthesis workflow")
        except Exception as e:
            logger.error(f"Error initializing code synthesis workflow: {e}")
            raise

    def process_requirements(
        self,
        input_file: str,
        project_id: str = None
    ) -> Dict[str, Any]:
        """Process business requirements.

        Args:
            input_file: Path to the input file
            project_id: Project ID to filter results

        Returns:
            Dictionary containing processed requirements
        """
        try:
            logger.info(f"Processing requirements file: {input_file}")

            # Process the file
            with open(input_file, 'r', encoding='utf-8') as f:
                text = f.read()

            # Preprocess the text
            preprocessed_text = self.text_processor.preprocess_text(text)

            # Parse the requirements
            parsed_data = self.requirements_parser.parse(preprocessed_text)

            # Extract entities
            entities = self.entity_extractor.extract_entities(preprocessed_text)

            # Analyze components
            components = self.component_analyzer.analyze_components(preprocessed_text)

            # Clean code references
            cleaned_text = self.text_processor.clean_code_references(preprocessed_text)

            # Generate search queries
            requirements_by_type = {
                "functional": [item["text"] for item in components["functional_requirements"]],
                "non_functional": [item["text"] for item in components["non_functional_requirements"]],
                "constraints": [constraint["text"] for constraint in components["constraints"]],
                "other": []
            }

            search_queries = generate_search_queries(requirements_by_type)

            # Combine all results
            result = {
                "original_text": text,
                "preprocessed_text": preprocessed_text,
                "cleaned_text": cleaned_text,
                "parsed_data": parsed_data,
                "entities": entities,
                "components": components,
                "search_queries": search_queries,
                "project_id": project_id
            }

            # Save the result if output directory is specified
            if self.output_dir:
                output_file = os.path.join(self.output_dir, "processed_requirements.json")
                save_json(result, output_file)
                logger.info(f"Saved processed requirements to {output_file}")

            return result

        except Exception as e:
            logger.error(f"Error processing requirements: {e}")
            return {"error": str(e)}

    def retrieve_context(
        self,
        processed_requirements: Dict[str, Any],
        rag_type: str = "multi_hop"
    ) -> Dict[str, Any]:
        """Retrieve context for code synthesis.

        Args:
            processed_requirements: Processed requirements
            rag_type: Type of RAG to use (basic, graph, multi_hop)

        Returns:
            Dictionary containing retrieved context
        """
        try:
            logger.info(f"Retrieving context using {rag_type} RAG")

            # Get search queries
            search_queries = processed_requirements.get("search_queries", [])
            if not search_queries:
                logger.warning("No search queries found in processed requirements")
                return {"error": "No search queries found"}

            # Get project ID
            project_id = processed_requirements.get("project_id")

            # Retrieve context based on RAG type
            if rag_type == "basic":
                # Use basic vector search
                results = []
                for query in search_queries:
                    query_results = self.vector_search.search(
                        query=query,
                        project_id=project_id,
                        limit=5
                    )
                    results.extend(query_results)

                # Remove duplicates
                unique_results = []
                seen_node_ids = set()
                for result in results:
                    node_id = result.get("node_id")
                    if node_id and node_id not in seen_node_ids:
                        unique_results.append(result)
                        seen_node_ids.add(node_id)

                # Build context
                context_result = self.context_builder.build_context(
                    chunks=unique_results,
                    query=processed_requirements.get("original_text")
                )

                return {
                    "rag_type": "basic",
                    "results": unique_results,
                    "context": context_result["context"],
                    "context_chunks": context_result["context_chunks"],
                    "total_tokens": context_result["total_tokens"]
                }

            elif rag_type == "graph":
                # Use graph-enhanced RAG
                results = []
                for query in search_queries:
                    query_results = self.vector_search.search(
                        query=query,
                        project_id=project_id,
                        limit=3
                    )
                    results.extend(query_results)

                # Enhance with graph context
                enhanced_results = self.graph_enhancer.enhance_search_results(
                    search_results=results,
                    max_neighbors_per_result=3
                )

                # Build context
                context_result = self.context_builder.build_context(
                    chunks=enhanced_results["enhanced_results"],
                    query=processed_requirements.get("original_text")
                )

                return {
                    "rag_type": "graph",
                    "original_results": enhanced_results["original_results"],
                    "enhanced_results": enhanced_results["enhanced_results"],
                    "context": context_result["context"],
                    "context_chunks": context_result["context_chunks"],
                    "total_tokens": context_result["total_tokens"]
                }

            elif rag_type == "multi_hop":
                # Use multi-hop RAG
                # Combine queries into a single query
                combined_query = " ".join(search_queries[:3])

                # Implement multi-hop RAG
                rag_result = self.multi_hop_rag.multi_hop_rag(
                    query=combined_query
                )

                return rag_result

            else:
                logger.error(f"Unknown RAG type: {rag_type}")
                return {"error": f"Unknown RAG type: {rag_type}"}

        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return {"error": str(e)}

    def generate_code_instructions(
        self,
        processed_requirements: Dict[str, Any],
        retrieved_context: Dict[str, Any],
        output_file: str = None,
        generate_code: bool = True,
        temperature: float = None,
        max_tokens: int = None
    ) -> Dict[str, Any]:
        """Generate code instructions and optionally generate code using LLM.

        Args:
            processed_requirements: Processed requirements
            retrieved_context: Retrieved context
            output_file: Path to the output file
            generate_code: Whether to generate code using LLM
            temperature: Temperature for LLM generation
            max_tokens: Maximum tokens for LLM generation

        Returns:
            Dictionary containing generated code instructions and code
        """
        # Get default values from environment variables if not provided
        temperature = temperature if temperature is not None else float(os.environ.get("LLM_TEMPERATURE", 0.7))
        max_tokens = max_tokens if max_tokens is not None else int(os.environ.get("LLM_MAX_TOKENS", 2000))
        try:
            logger.info("Generating code instructions")

            # Get the original requirements text
            requirements_text = processed_requirements.get("original_text", "")

            # Get the context
            context = retrieved_context.get("context", "")

            # Create the instructions
            instructions = {
                "requirements": requirements_text,
                "context": context,
                "instructions": "Based on the provided requirements and context, implement the necessary code changes."
            }

            # Create the prompt for LLM
            prompt = f"# Requirements\n\n{requirements_text}\n\n"
            prompt += f"# Context\n\n{context}\n\n"
            prompt += "# Instructions\n\n"
            prompt += "Based on the provided requirements and context, implement the necessary code changes.\n\n"
            prompt += "Please provide your implementation in the following format:\n\n"
            prompt += "## File: [file_path]\n\n"
            prompt += "```[language]\n// Your code here\n```\n\n"

            # Save the instructions to llm-instructions.txt
            if output_file:
                instructions_file = output_file
            elif self.output_dir:
                instructions_file = os.path.join(self.output_dir, "llm-instructions.txt")
            else:
                instructions_file = None

            if instructions_file:
                with open(instructions_file, 'w', encoding='utf-8') as f:
                    f.write(prompt)

                logger.info(f"Saved code instructions to {instructions_file}")

            # Generate code using LLM if requested and LLM client is available
            generated_code = None
            if generate_code and self.llm_client:
                try:
                    logger.info("Generating code using LLM")

                    # Generate code using LLM
                    generated_code = self.llm_client.generate(
                        prompt=prompt,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        save_output=True
                    )

                    # Save the generated code to llm-output.txt
                    if self.output_dir:
                        output_file = os.path.join(self.output_dir, "llm-output.txt")
                        with open(output_file, 'w', encoding='utf-8') as f:
                            f.write(generated_code)

                        logger.info(f"Saved generated code to {output_file}")

                    # Add generated code to instructions
                    instructions["generated_code"] = generated_code

                except Exception as e:
                    logger.error(f"Error generating code using LLM: {e}")
                    instructions["llm_error"] = str(e)

            elif generate_code and not self.llm_client:
                logger.warning("LLM client not available. Cannot generate code.")
                instructions["llm_error"] = "LLM client not available"

            return instructions

        except Exception as e:
            logger.error(f"Error generating code instructions: {e}")
            return {"error": str(e)}

    def run_workflow(
        self,
        input_file: str,
        project_id: str = None,
        rag_type: str = "multi_hop",
        output_file: str = None,
        generate_code: bool = True,
        temperature: float = None,
        max_tokens: int = None
    ) -> Dict[str, Any]:
        """Run the end-to-end code synthesis workflow.

        Args:
            input_file: Path to the input file
            project_id: Project ID to filter results
            rag_type: Type of RAG to use (basic, graph, multi_hop)
            output_file: Path to the output file
            generate_code: Whether to generate code using LLM
            temperature: Temperature for LLM generation
            max_tokens: Maximum tokens for LLM generation

        Returns:
            Dictionary containing workflow results
        """
        # Get default values from environment variables if not provided
        temperature = temperature if temperature is not None else float(os.environ.get("LLM_TEMPERATURE", 0.7))
        max_tokens = max_tokens if max_tokens is not None else int(os.environ.get("LLM_MAX_TOKENS", 2000))
        try:
            logger.info(f"Running code synthesis workflow for {input_file}")

            # Step 1: Process requirements
            processed_requirements = self.process_requirements(
                input_file=input_file,
                project_id=project_id
            )

            if "error" in processed_requirements:
                return processed_requirements

            # Step 2: Retrieve context
            retrieved_context = self.retrieve_context(
                processed_requirements=processed_requirements,
                rag_type=rag_type
            )

            if "error" in retrieved_context:
                return retrieved_context

            # Step 3: Generate code instructions and optionally generate code
            code_instructions = self.generate_code_instructions(
                processed_requirements=processed_requirements,
                retrieved_context=retrieved_context,
                output_file=output_file,
                generate_code=generate_code,
                temperature=temperature,
                max_tokens=max_tokens
            )

            if "error" in code_instructions:
                return code_instructions

            # Determine output files
            instructions_file = output_file or (os.path.join(self.output_dir, "llm-instructions.txt") if self.output_dir else None)
            output_file = os.path.join(self.output_dir, "llm-output.txt") if self.output_dir and generate_code else None

            # Return workflow results
            result = {
                "processed_requirements": processed_requirements,
                "retrieved_context": retrieved_context,
                "code_instructions": code_instructions,
                "instructions_file": instructions_file
            }

            # Add generated code information if available
            if "generated_code" in code_instructions:
                result["generated_code"] = code_instructions["generated_code"]
                result["output_file"] = output_file

            # Add LLM error if there was one
            if "llm_error" in code_instructions:
                result["llm_error"] = code_instructions["llm_error"]

            return result

        except Exception as e:
            logger.error(f"Error running code synthesis workflow: {e}")
            return {"error": str(e)}

    def close(self):
        """Close the database connections and LLM client."""
        try:
            if self.vector_search:
                self.vector_search.close()
            if self.graph_enhancer:
                self.graph_enhancer.close()
            if self.multi_hop_rag:
                self.multi_hop_rag.close()
            logger.info("Closed database connections")
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")


# Example usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run code synthesis workflow")
    parser.add_argument("--input-file", required=True, help="Path to the input file")
    parser.add_argument("--project-id", help="Project ID to filter results")
    parser.add_argument("--rag-type", choices=["basic", "graph", "multi_hop"], default="multi_hop",
                        help="Type of RAG to use")
    parser.add_argument("--output-file", help="Path to the output file")
    parser.add_argument("--db-path", help="Path to the LanceDB database")
    parser.add_argument("--output-dir", help="Path to the output directory")
    parser.add_argument("--llm-api-key", help="API key for the LLM service")
    parser.add_argument("--llm-model", help="Name of the LLM model to use")
    parser.add_argument("--generate-code", action="store_true", default=True,
                        help="Whether to generate code using LLM")
    parser.add_argument("--temperature", type=float, help="Temperature for LLM generation")
    parser.add_argument("--max-tokens", type=int, help="Maximum tokens for LLM generation")
    parser.add_argument("--env-file", help="Path to the .env file")
    args = parser.parse_args()

    # Load environment variables from specified file
    if args.env_file:
        load_env_vars(args.env_file)

    # Initialize workflow with values from command line or environment variables
    workflow = CodeSynthesisWorkflow(
        db_path=args.db_path,
        output_dir=args.output_dir,
        llm_api_key=args.llm_api_key,
        llm_model_name=args.llm_model
    )

    # Run workflow
    result = workflow.run_workflow(
        input_file=args.input_file,
        project_id=args.project_id,
        rag_type=args.rag_type,
        output_file=args.output_file,
        generate_code=args.generate_code,
        temperature=args.temperature,
        max_tokens=args.max_tokens
    )

    # Check for errors
    if "error" in result:
        logger.error(f"Workflow failed: {result['error']}")
        sys.exit(1)

    # Print success message
    print(f"\nCode synthesis workflow completed successfully!")

    # Print output files
    if "instructions_file" in result:
        print(f"Instructions file: {result['instructions_file']}")

    if "output_file" in result:
        print(f"Generated code file: {result['output_file']}")

    # Print LLM error if there was one
    if "llm_error" in result:
        print(f"LLM error: {result['llm_error']}")

    # Close connections
    workflow.close()
