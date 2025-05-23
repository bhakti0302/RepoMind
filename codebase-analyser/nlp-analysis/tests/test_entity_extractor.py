# """
# Test script for the entity extractor component.
# """

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

# # Import the entity extractor
# from src.entity_extractor import EntityExtractor

# def test_entity_extractor():
#     """Test the entity extractor component."""
#     try:
#         # Create a sample text
#         sample_text = """
#         # Book Management System

#         Implement a system to manage books in a library.
#         Users should be able to search for books by author or title.
#         The system should display the availability status of each book.
#         """

#         # Initialize the entity extractor
#         entity_extractor = EntityExtractor()
#         logger.info("Initialized entity extractor")

#         # Extract entities
#         entities = entity_extractor.extract_entities(sample_text)
#         logger.info(f"Extracted {sum(len(entities[key]) for key in entities)} entities")

#         # Print the results
#         print("\nExtracted Entities:")
#         for entity_type, entity_list in entities.items():
#             print(f"\n{entity_type.capitalize()}:")
#             for entity in entity_list:
#                 print(f"  - {entity}")

#         return entities
    
#     except Exception as e:
#         logger.error(f"Error testing entity extractor: {e}")
#         return None

# if __name__ == "__main__":
#     test_entity_extractor()

#python3 test_entity_extractor.py /Users/bhaktichindhe/Desktop/Project/RepoMind/test-project-employee/EmployeeByDepartmentRequirement.txt
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

# Import the entity extractor
from src.entity_extractor import EntityExtractor

def test_entity_extraction(file_path):
    """Test entity extraction on a file."""
    try:
        # Read the file
        with open(file_path, 'r') as f:
            content = f.read()
        
        logger.info(f"Read file: {file_path}")
        
        # Initialize the entity extractor
        entity_extractor = EntityExtractor()
        logger.info("Initialized entity extractor")
        
        # Extract entities
        entities = entity_extractor.extract_entities(content)
        logger.info(f"Extracted {sum(len(entities[key]) for key in entities)} entities")
        
        # Print the results
        print("\nExtracted Entities:")
        for entity_type, entity_list in entities.items():
            print(f"\n{entity_type.capitalize()}:")
            for entity in entity_list:
                print(f"  - {entity}")
        
        return entities
    
    except Exception as e:
        logger.error(f"Error testing entity extraction: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "/Users/bhaktichindhe/Desktop/Project/RepoMind/test-project-employee/EmployeeByDepartmentRequirement.txt"
    
    test_entity_extraction(file_path)