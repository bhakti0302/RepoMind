# Import the fixed entity extractor

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.entity_extractor import EntityExtractor

# Create a sample text
sample_text = """
# Book Management System

Implement a system to manage books in a library.
Users should be able to search for books by author or title.
The system should display the availability status of each book.
"""

# Initialize the entity extractor
entity_extractor = EntityExtractor()
print("Initialized entity extractor")

# Extract entities
entities = entity_extractor.extract_entities(sample_text)

# Print the results
print("\nExtracted Entities:")
for entity_type, entity_list in entities.items():
    print(f"\n{entity_type.capitalize()}:")
    for entity in entity_list:
        print(f"  - {entity}")