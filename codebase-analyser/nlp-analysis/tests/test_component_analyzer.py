# import sys
# import os
# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# # Import the component analyzer
# from src.component_analyzer import ComponentAnalyzer

# # Create a cleaner sample text with proper formatting
# sample_text = """# Book Management System

# ## Functional Requirements
# 1. Users should be able to search for books by author
# 2. Users should be able to search for books by title
# 3. The system should display the availability status of each book

# ## Non-Functional Requirements
# 1. The system should respond within 2 seconds
# 2. The system should handle up to 1000 concurrent users
# """

# # Initialize the component analyzer
# component_analyzer = ComponentAnalyzer()
# print("Initialized component analyzer")

# # Analyze components
# components = component_analyzer.analyze_components(sample_text)

# # Print the results
# print("\nAnalyzed Components:")
# print("\nFunctional Requirements:")
# for req in components["functional_requirements"]:
#     print(f"  - {req['text']}")

# print("\nNon-Functional Requirements:")
# for req in components["non_functional_requirements"]:
#     print(f"  - {req['text']}")

# print("\nConstraints:")
# for constraint in components["constraints"]:
#     print(f"  - {constraint['text']}")


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

# Import the component analyzer
from src.component_analyzer import ComponentAnalyzer

def test_component_analysis(file_path):
    """Test component analysis on a file."""
    try:
        # Read the file
        with open(file_path, 'r') as f:
            content = f.read()
        
        logger.info(f"Read file: {file_path}")
        
        # Initialize the component analyzer
        component_analyzer = ComponentAnalyzer()
        logger.info("Initialized component analyzer")
        
        # Analyze components
        components = component_analyzer.analyze_components(content)
        logger.info(f"Analyzed components: {len(components['functional_requirements'])} functional requirements, {len(components['non_functional_requirements'])} non-functional requirements")
        
        # Print the results
        print("\nAnalyzed Components:")
        print("\nFunctional Requirements:")
        for req in components["functional_requirements"]:
            print(f"  - {req['text']}")
        
        print("\nNon-Functional Requirements:")
        for req in components["non_functional_requirements"]:
            print(f"  - {req['text']}")
        
        print("\nConstraints:")
        for constraint in components["constraints"]:
            print(f"  - {constraint['text']}")
        
        return components
    
    except Exception as e:
        logger.error(f"Error testing component analysis: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "/Users/bhaktichindhe/Desktop/Project/RepoMind/test-project-employee/EmployeeByDepartmentRequirement.txt"
    
    test_component_analysis(file_path)


