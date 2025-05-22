# Create the end-to-end pipeline script
#!/usr/bin/env python3

import os
import sys
import logging
import argparse
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the components
from src.entity_extractor import EntityExtractor
from src.component_analyzer import ComponentAnalyzer
from src.vector_search import VectorSearch
from src.multi_hop_rag import MultiHopRAG

def run_pipeline(input_file: str, db_path: str, output_dir: str) -> Dict[str, Any]:
    """Run the complete NLP analysis pipeline.
    
    Args:
        input_file: Path to the input file
        db_path: Path to the LanceDB database
        output_dir: Path to the output directory
        
    Returns:
        Dictionary of pipeline results
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Step 1: Read the input file
        logger.info(f"Reading input file: {input_file}")
        with open(input_file, 'r') as f:
            content = f.read()
        
        # Save a copy of the input file to the output directory
        input_copy = os.path.join(output_dir, "input.txt")
        with open(input_copy, 'w') as f:
            f.write(content)
        logger.info(f"Saved copy of input file to {input_copy}")
        
        # Step 2: Entity Extraction
        logger.info("Step 2: Entity Extraction")
        entity_extractor = EntityExtractor()
        entities = entity_extractor.extract_entities(content)
        logger.info(f"Extracted {sum(len(entities[key]) for key in entities)} entities")
        
        # Save entities to file
        entities_file = os.path.join(output_dir, "entities.txt")
        with open(entities_file, 'w') as f:
            f.write("Extracted Entities\n")
            f.write("=================\n\n")
            for entity_type, entity_list in entities.items():
                f.write(f"{entity_type.capitalize()}:\n")
                for entity in entity_list:
                    f.write(f"  - {entity}\n")
                f.write("\n")
        logger.info(f"Saved entities to {entities_file}")
        
        # Step 3: Component Analysis
        logger.info("Step 3: Component Analysis")
        component_analyzer = ComponentAnalyzer()
        components = component_analyzer.analyze_components(content)
        logger.info(f"Analyzed components: {len(components['functional_requirements'])} functional requirements, {len(components['non_functional_requirements'])} non-functional requirements")
        
        # Save components to file
        components_file = os.path.join(output_dir, "components.txt")
        with open(components_file, 'w') as f:
            f.write("Analyzed Components\n")
            f.write("==================\n\n")
            
            f.write("Functional Requirements:\n")
            for req in components["functional_requirements"]:
                f.write(f"  - {req['text']}\n")
            f.write("\n")
            
            f.write("Non-Functional Requirements:\n")
            for req in components["non_functional_requirements"]:
                f.write(f"  - {req['text']}\n")
            f.write("\n")
            
            f.write("Constraints:\n")
            for constraint in components["constraints"]:
                f.write(f"  - {constraint['text']}\n")
            f.write("\n")
            
            f.write("Actions:\n")
            for action in components.get("actions", []):
                f.write(f"  - {action.get('text', '')}\n")
        logger.info(f"Saved components to {components_file}")
        
        # Step 4: Generate query from entities and components
        logger.info("Step 4: Generate query")
        query_parts = []
        
        # Add nouns
        if 'nouns' in entities:
            query_parts.extend(entities['nouns'][:5])
        
        # Add technical terms
        if 'technical_terms' in entities:
            query_parts.extend(entities['technical_terms'][:3])
        
        # Add functional requirements
        for req in components["functional_requirements"][:2]:
            query_parts.append(req['text'][:])
        
        # If no query parts, use the first 100 characters of the content
        if not query_parts:
            query = content[:].replace('\n', ' ').strip()
        else:
            # Create the query
            query = " ".join(query_parts)
        
        logger.info(f"Generated query: {query}")
        
        # Save query to file
        query_file = os.path.join(output_dir, "query.txt")
        with open(query_file, 'w') as f:
            f.write(f"Generated Query\n")
            f.write(f"===============\n\n")
            f.write(query)
        logger.info(f"Saved query to {query_file}")
        
        # Step 5: Vector Search
        logger.info("Step 5: Vector Search")
        vector_search = VectorSearch(db_path=db_path)
        search_results = vector_search.search(query=query, limit=5)
        logger.info(f"Found {len(search_results)} results for query")
        
        # Save search results to file
        search_results_file = os.path.join(output_dir, "search_results.txt")
        with open(search_results_file, 'w') as f:
            f.write(f"Vector Search Results\n")
            f.write(f"====================\n\n")
            f.write(f"Query: {query}\n\n")
            
            for i, result in enumerate(search_results, 1):
                f.write(f"Result {i}:\n")
                f.write(f"  Score: {result.get('score', 0):.4f}\n")
                f.write(f"  File: {result.get('file_path', 'Unknown')}\n")
                
                # Print a snippet of the content
                content = result.get('content', '')
                if len(content) > 200:
                    content = content[:200] + "..."
                f.write(f"  Content: {content}\n\n")
        logger.info(f"Saved search results to {search_results_file}")
        
        # Step 6: Multi-Hop RAG
        logger.info("Step 6: Multi-Hop RAG")
        rag = MultiHopRAG(db_path=db_path, output_dir=output_dir)
        rag_result = rag.multi_hop_rag(query=query)
        logger.info(f"Completed multi-hop RAG")
        
        # The multi-hop RAG already saves its output to output_dir/output-multi-hop.txt
        
        # Step 7: Clean up
        logger.info("Step 7: Clean up")
        vector_search.close()
        rag.close()
        
        logger.info("Pipeline completed successfully")
        
        return {
            "input_file": input_file,
            "entities": entities,
            "components": components,
            "query": query,
            "search_results": search_results,
            "rag_result": rag_result
        }
    
    except Exception as e:
        logger.error(f"Error running pipeline: {e}")
        return {"error": str(e)}

def main():
    parser = argparse.ArgumentParser(description="Run the complete NLP analysis pipeline")
    parser.add_argument("--input-file", required=True, help="Path to the input file")
    parser.add_argument("--db-path", default="/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/.lancedb", help="Path to the LanceDB database")
    parser.add_argument("--output-dir", default="/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/nlp-analysis/tests/output", help="Path to the output directory")
    
    args = parser.parse_args()
    
    run_pipeline(args.input_file, args.db_path, args.output_dir)

if __name__ == "__main__":
    main()


# Make the script executable
