# Add the parent directory to the Python path
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the component analyzer
from src.component_analyzer import ComponentAnalyzer

# Create a cleaner sample text with proper formatting
sample_text = """# Book Management System

## Functional Requirements
1. Users should be able to search for books by author
2. Users should be able to search for books by title
3. The system should display the availability status of each book

## Non-Functional Requirements
1. The system should respond within 2 seconds
2. The system should handle up to 1000 concurrent users
"""

# Initialize the component analyzer
component_analyzer = ComponentAnalyzer()
print("Initialized component analyzer")

# Analyze components
components = component_analyzer.analyze_components(sample_text)

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

# Print raw component data for debugging
print("\nRaw Component Data:")
for component_type, components_list in components.items():
    print(f"\n{component_type}:")
    for i, component in enumerate(components_list):
        print(f"  {i+1}. {component}")