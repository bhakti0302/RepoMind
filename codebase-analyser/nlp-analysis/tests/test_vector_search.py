# # """
# # Test script for the vector search component.
# # """

# # import sys
# # import os
# # import logging
# # import argparse

# # # Configure logging
# # logging.basicConfig(
# #     level=logging.INFO,
# #     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
# # )
# # logger = logging.getLogger(__name__)

# # # Add the parent directory to the Python path
# # sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# # # Import the vector search
# # from src.vector_search import VectorSearch

# # def test_vector_search(db_path, query, limit=5):
# #     """Test the vector search component.
    
# #     Args:
# #         db_path: Path to the LanceDB database
# #         query: Search query
# #         limit: Maximum number of results to return
# #     """
# #     try:
# #         # Initialize the vector search
# #         vector_search = VectorSearch(db_path=db_path)
# #         logger.info(f"Initialized vector search with database at {db_path}")

# #         # Search for code chunks
# #         results = vector_search.search(query=query, limit=limit)
# #         logger.info(f"Found {len(results)} results for query: '{query}'")

# #         # Print the results
# #         print(f"\nFound {len(results)} results for query: '{query}'")
# #         for i, result in enumerate(results, 1):
# #             print(f"\nResult {i}:")
# #             print(f"  Score: {result.get('score', 0):.4f}")
# #             print(f"  File: {result.get('file_path', 'Unknown')}")
            
# #             # Print a snippet of the content
# #             content = result.get('content', '')
# #             if len(content) > 100:
# #                 content = content[:100] + "..."
# #             print(f"  Content: {content}")

# #         # Close the connection
# #         vector_search.close()
# #         logger.info("Closed vector search connection")

# #         return results
    
# #     except Exception as e:
# #         logger.error(f"Error testing vector search: {e}")
# #         return None

# # if __name__ == "__main__":
# #     parser = argparse.ArgumentParser(description="Test vector search")
# #     parser.add_argument("--db-path", default="../.lancedb", help="Path to the LanceDB database")
# #     parser.add_argument("--query", default="book author availability library management system", help="Search query")
# #     parser.add_argument("--limit", type=int, default=5, help="Maximum number of results")
# #     args = parser.parse_args()

# #     test_vector_search(db_path=args.db_path, query=args.query, limit=args.limit)


# # Create a test script for vector search
# #cat > test_vector_search.py << 'EOF'
# #!/usr/bin/env python3

# import sys
# import os
# import logging

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
# )
# logger = logging.getLogger(__name__)

# # Add the parent directory to the Python path
# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# # Import the vector search
# from src.vector_search import VectorSearch

# def test_vector_search(file_path, db_path="../.lancedb"):
#     """Test vector search with queries derived from a file."""
#     try:
#         # Read the file
#         with open(file_path, 'r') as f:
#             content = f.read()
        
#         logger.info(f"Read file: {file_path}")
        
#         # Generate a simple query from the content
#         # Just take the first 100 characters and clean them up
#         query = content[:100].replace('\n', ' ').strip()
#         logger.info(f"Generated query: {query}")
        
#         # Initialize the vector search
#         vector_search = VectorSearch(db_path=db_path)
#         logger.info(f"Initialized vector search with database at {db_path}")
        
#         # Search for code chunks
#         results = vector_search.search(query=query, limit=5)
#         logger.info(f"Found {len(results)} results for query: '{query}'")
        
#         # Print the results
#         print(f"\nFound {len(results)} results for query: '{query}'")
#         for i, result in enumerate(results, 1):
#             print(f"\nResult {i}:")
#             print(f"  Score: {result.get('score', 0):.4f}")
#             print(f"  File: {result.get('file_path', 'Unknown')}")
            
#             # Print a snippet of the content
#             content = result.get('content', '')
#             if len(content) > 100:
#                 content = content[:100] + "..."
#             print(f"  Content: {content}")
        
#         # Close the connection
#         vector_search.close()
#         logger.info("Closed vector search connection")
        
#         return results
    
#     except Exception as e:
#         logger.error(f"Error testing vector search: {e}")
#         return None

# if __name__ == "__main__":
#     if len(sys.argv) > 1:
#         file_path = sys.argv[1]
#     else:
#         file_path = "/Users/bhaktichindhe/Desktop/Project/RepoMind/test-project-employee/EmployeeByDepartmentRequirement.txt"
    
#     db_path = "../.lancedb"
#     if len(sys.argv) > 2:
#         db_path = sys.argv[2]
    
#     test_vector_search(file_path, db_path)


# # Make the script executable
# #chmod +x test_vector_search.py

# # Run the vector search test
# #python3 test_vector_search.py /Users/bhaktichindhe/Desktop/Project/RepoMind/test-project-employee/EmployeeByDepartmentRequirement.txt ../../lancedb


# Create a backup of the original file

# Edit the test_vector_search.py file
#!/usr/bin/env python3
#python3 test_vector_search.py --file-path /Users/bhaktichindhe/Desktop/Project/RepoMind/test-project-employee/EmployeeByDepartmentRequirement.txt --db-path /Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/.lancedb
#/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/.lancedb

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

# Import the vector search
from src.vector_search import VectorSearch

def test_vector_search(file_path, db_path="../.lancedb", limit=5):
    """Test vector search with queries derived from a file."""
    try:
        # Read the file
        with open(file_path, 'r') as f:
            content = f.read()
        
        logger.info(f"Read file: {file_path}")
        
        # Generate a simple query from the content
        # Just take the first 100 characters and clean them up
        query = content[:100].replace('\n', ' ').strip()
        logger.info(f"Generated query: {query}")
        
        # Initialize the vector search
        vector_search = VectorSearch(db_path=db_path)
        logger.info(f"Initialized vector search with database at {db_path}")
        
        # Search for code chunks
        results = vector_search.search(query=query, limit=limit)
        logger.info(f"Found {len(results)} results for query: '{query}'")
        
        # Print the results
        print(f"\nFound {len(results)} results for query: '{query}'")
        for i, result in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"  Score: {result.get('score', 0):.4f}")
            print(f"  File: {result.get('file_path', 'Unknown')}")
            
            # Print a snippet of the content
            content = result.get('content', '')
            if len(content) > 100:
                content = content[:100] + "..."
            print(f"  Content: {content}")
        
        # Close the connection
        vector_search.close()
        logger.info("Closed vector search connection")
        
        return results
    
    except Exception as e:
        logger.error(f"Error testing vector search: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test vector search")
    parser.add_argument("--file-path", help="Path to the file to process")
    parser.add_argument("--db-path", default="../.lancedb", help="Path to the LanceDB database")
    parser.add_argument("--limit", type=int, default=5, help="Maximum number of results")
    
    # Handle both named and positional arguments
    args, unknown = parser.parse_known_args()
    
    # If file_path is not provided as a named argument but there are unknown arguments
    if not args.file_path and len(unknown) > 0:
        args.file_path = unknown[0]
    
    # If db_path is not provided as a named argument but there are at least 2 unknown arguments
    if len(unknown) > 1:
        args.db_path = unknown[1]
    
    # If no file path is provided, use a default
    if not args.file_path:
        args.file_path = "/Users/bhaktichindhe/Desktop/Project/RepoMind/test-project-employee/EmployeeByDepartmentRequirement.txt"
    
    # Run the test
    test_vector_search(args.file_path, args.db_path, args.limit)


# Make the script executable
