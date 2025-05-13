"""
Test script for the end-to-end pipeline.
"""

import sys
import os
import logging
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the code synthesis workflow
from src.code_synthesis_workflow import CodeSynthesisWorkflow
from src.env_loader import load_env_vars

def test_pipeline(input_file, db_path, output_dir, generate_code=False):
    """Test the end-to-end pipeline.
    
    Args:
        input_file: Path to the input file
        db_path: Path to the LanceDB database
        output_dir: Path to the output directory
        generate_code: Whether to generate code
    """
    try:
        # Load environment variables
        load_env_vars()
        logger.info("Loaded environment variables")

        # Initialize the workflow
        workflow = CodeSynthesisWorkflow(
            db_path=db_path,
            output_dir=output_dir
        )
        logger.info(f"Initialized code synthesis workflow with database at {db_path}")

        # Run the workflow
        result = workflow.run_workflow(
            input_file=input_file,
            rag_type="multi_hop",
            generate_code=generate_code
        )
        logger.info(f"Ran workflow for input file: {input_file}")

        # Print the results
        print(f"\nCode Synthesis Workflow Summary:")
        print(f"Input file: {input_file}")

        # Check for errors
        if "error" in result:
            print(f"Error: {result['error']}")
            logger.error(f"Workflow failed: {result['error']}")
        else:
            print("Workflow completed successfully!")
            logger.info("Workflow completed successfully")
            
            # Print the instructions file
            if "instructions_file" in result:
                print(f"Instructions file: {result['instructions_file']}")
                
                # Print a sample of the instructions
                with open(result['instructions_file'], 'r') as f:
                    instructions = f.read()
                    if len(instructions) > 200:
                        instructions = instructions[:200] + "..."
                    print(f"\nInstructions Sample:\n{instructions}")

        # Close connections
        workflow.close()
        logger.info("Closed workflow connections")

        return result
    
    except Exception as e:
        logger.error(f"Error testing pipeline: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test end-to-end pipeline")
    parser.add_argument("--input-file", default="../data/test/book_requirements.txt", help="Path to the input file")
    parser.add_argument("--db-path", default="../.lancedb", help="Path to the LanceDB database")
    parser.add_argument("--output-dir", default="../output", help="Path to the output directory")
    parser.add_argument("--generate-code", action="store_true", help="Whether to generate code")
    args = parser.parse_args()

    test_pipeline(
        input_file=args.input_file,
        db_path=args.db_path,
        output_dir=args.output_dir,
        generate_code=args.generate_code
    )