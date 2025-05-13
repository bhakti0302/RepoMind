import sys
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the multi-hop RAG
from src.multi_hop_rag import MultiHopRAG

def test_multi_hop_rag(file_path, db_path="/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/.lancedb", output_dir="../output"):
    """Test multi-hop RAG with a file."""
    try:
        # Read the file
        with open(file_path, 'r') as f:
            content = f.read()
        
        logger.info(f"Read file: {file_path}")
        
        # Generate a query from the content
        # Just take the first 100 characters and clean them up
        query = content[:].replace('\n', ' ').strip()
        #logger.info(f"Generated query: {query}")
        
        # Initialize the multi-hop RAG
        rag = MultiHopRAG(db_path=db_path, output_dir=output_dir)
        logger.info(f"Initialized multi-hop RAG with database at {db_path}")
        
        # Implement multi-hop RAG
        result = rag.multi_hop_rag(query=query)
        logger.info(f"Implemented multi-hop RAG for query: '{query}'")
        
        # Print the results
        print(f"\nMulti-Hop RAG Results:")
        print(f"Query: {query}")
        
        print(f"\nArchitectural Patterns:")
        for pattern in result.get('architectural_patterns', []):
            print(f"  - {pattern}")
        
        print(f"\nImplementation Details:")
        for detail in result.get('implementation_details', []):
            print(f"  - {detail}")
        
        print(f"\nRelated Components:")
        for component in result.get('related_components', []):
            print(f"  - {component}")
        
        # Print a sample of the context
        context = result.get('context', '')
        if len(context) > 200:
            context = context[:200] + "..."
        print(f"\nContext Sample:\n{context}")
        
        # Save the results to a file
        output_file = os.path.join(output_dir, "multi-hop-test-output.txt")
        with open(output_file, 'w') as f:
            f.write(f"Multi-Hop RAG Results\n")
            f.write(f"====================\n\n")
            f.write(f"Query: {query}\n\n")
            
            f.write(f"Architectural Patterns:\n")
            for pattern in result.get('architectural_patterns', []):
                f.write(f"  - {pattern}\n")
            
            f.write(f"\nImplementation Details:\n")
            for detail in result.get('implementation_details', []):
                f.write(f"  - {detail}\n")
            
            f.write(f"\nRelated Components:\n")
            for component in result.get('related_components', []):
                f.write(f"  - {component}\n")
            
            f.write(f"\nContext:\n{result.get('context', '')}")
        
        logger.info(f"Saved results to {output_file}")
        
        # Close the connection
        rag.close()
        logger.info("Closed RAG connection")
        logger.info("db path: {db_path}")
        
        return result
    
    except Exception as e:
        logger.error(f"Error testing multi-hop RAG: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "/Users/bhaktichindhe/Desktop/Project/RepoMind/test-project-employee/EmployeeByDepartmentRequirement.txt"
    
    db_path = "/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/.lancedb"
    if len(sys.argv) > 2:
        db_path = sys.argv[2]
    
    output_dir = "../output"
    if len(sys.argv) > 3:
        output_dir = sys.argv[3]
    
    test_multi_hop_rag(file_path, db_path, output_dir)