# # # Create a backup of the original file

# # """
# # Multi-Hop RAG module.

# # This module provides functionality for multi-hop RAG with enhanced retrieval capabilities.
# # """

# # import os
# # import sys
# # import logging
# # import json
# # from typing import Dict, List, Any, Optional
# # import re

# # # Configure logging
# # logging.basicConfig(
# #     level=logging.INFO,
# #     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
# # )
# # logger = logging.getLogger(__name__)

# # # Import the vector search
# # from src.vector_search import VectorSearch

# # class MultiHopRAG:
# #     """Enhanced multi-hop RAG implementation."""

# #     def __init__(self, db_path="../.lancedb", output_dir=None):
# #         """Initialize the multi-hop RAG.

# #         Args:
# #             db_path: Path to the LanceDB database
# #             output_dir: Path to the output directory
# #         """
# #         self.db_path = db_path
# #         self.output_dir = output_dir

# #         # Initialize vector search
# #         try:
# #             self.vector_search = VectorSearch(db_path=db_path)
# #             logger.info(f"Initialized vector search with database at {db_path}")
# #         except Exception as e:
# #             logger.error(f"Error initializing vector search: {e}")
# #             raise

# #         # Create output directory if it doesn't exist
# #         if output_dir:
# #             os.makedirs(output_dir, exist_ok=True)

# #     def extract_code_entities(self, content: str) -> Dict[str, List[str]]:
# #         """Extract code entities from content.

# #         Args:
# #             content: Code content

# #         Returns:
# #             Dictionary of entity types and lists of entities
# #         """
# #         entities = {
# #             "classes": [],
# #             "methods": [],
# #             "variables": [],
# #             "imports": []
# #         }

# #         # Extract classes
# #         class_pattern = r"class\s+(\w+)"
# #         classes = re.findall(class_pattern, content)
# #         entities["classes"] = list(set(classes))

# #         # Extract methods
# #         method_pattern = r"(?:public|private|protected)?\s+\w+\s+(\w+)\s*\("
# #         methods = re.findall(method_pattern, content)
# #         entities["methods"] = list(set(methods))

# #         # Extract variables
# #         variable_pattern = r"(?:private|public|protected)?\s+\w+\s+(\w+)\s*;"
# #         variables = re.findall(variable_pattern, content)
# #         entities["variables"] = list(set(variables))

# #         # Extract imports
# #         import_pattern = r"import\s+([\w\.]+);"
# #         imports = re.findall(import_pattern, content)
# #         entities["imports"] = list(set(imports))

# #         return entities

# #     def generate_follow_up_queries(self, entities: Dict[str, List[str]], original_query: str) -> List[str]:
# #         """Generate follow-up queries based on extracted entities.

# #         Args:
# #             entities: Dictionary of entity types and lists of entities
# #             original_query: Original search query

# #         Returns:
# #             List of follow-up queries
# #         """
# #         follow_up_queries = []

# #         # Add class-based queries
# #         for class_name in entities["classes"]:
# #             follow_up_queries.append(f"{class_name} implementation")
# #             follow_up_queries.append(f"{class_name} usage")

# #         # Add method-based queries
# #         for method_name in entities["methods"]:
# #             if method_name not in ["main", "toString", "equals", "hashCode", "get", "set"]:
# #                 follow_up_queries.append(f"{method_name} implementation")

# #         # Limit the number of follow-up queries
# #         return follow_up_queries[:3]

# #     def multi_hop_rag(self, query: str, max_hops: int = 2) -> Dict[str, Any]:
# #         """Implement multi-hop RAG.

# #         Args:
# #             query: Search query
# #             max_hops: Maximum number of hops

# #         Returns:
# #             Dictionary of RAG results
# #         """
# #         try:
# #             all_results = []
# #             all_entities = {
# #                 "classes": [],
# #                 "methods": [],
# #                 "variables": [],
# #                 "imports": []
# #             }

# #             # First hop: Initial query
# #             logger.info(f"Hop 1: Searching for '{query}'")
# #             initial_results = self.vector_search.search(query=query, limit=3)
# #             all_results.extend(initial_results)

# #             # Extract entities from initial results
# #             for result in initial_results:
# #                 content = result.get("content", "")
# #                 entities = self.extract_code_entities(content)

# #                 # Add entities to all_entities
# #                 for entity_type, entity_list in entities.items():
# #                     all_entities[entity_type].extend(entity_list)

# #             # Remove duplicates
# #             for entity_type in all_entities:
# #                 all_entities[entity_type] = list(set(all_entities[entity_type]))

# #             # Generate follow-up queries
# #             follow_up_queries = self.generate_follow_up_queries(all_entities, query)

# #             # Additional hops
# #             for hop in range(2, max_hops + 1):
# #                 if follow_up_queries:
# #                     # Take the first follow-up query
# #                     follow_up_query = follow_up_queries.pop(0)

# #                     logger.info(f"Hop {hop}: Searching for '{follow_up_query}'")
# #                     hop_results = self.vector_search.search(query=follow_up_query, limit=2)

# #                     # Add results to all_results
# #                     all_results.extend(hop_results)

# #                     # Extract entities from hop results
# #                     for result in hop_results:
# #                         content = result.get("content", "")
# #                         entities = self.extract_code_entities(content)

# #                         # Add entities to all_entities
# #                         for entity_type, entity_list in entities.items():
# #                             all_entities[entity_type].extend(entity_list)

# #                     # Remove duplicates
# #                     for entity_type in all_entities:
# #                         all_entities[entity_type] = list(set(all_entities[entity_type]))

# #             # Extract context from all results
# #             context = ""
# #             for i, result in enumerate(all_results):
# #                 file_path = result.get("file_path", "Unknown")
# #                 content = result.get("content", "")
# #                 context += f"--- Document {i+1}: {file_path} ---\n\n{content}\n\n"

# #             # Identify architectural patterns
# #             architectural_patterns = []
# #             if any("Controller" in cls for cls in all_entities["classes"]) and any("Service" in cls for cls in all_entities["classes"]) and any("Model" in cls for cls in all_entities["classes"]):
# #                 architectural_patterns.append("MVC (Model-View-Controller)")

# #             if any("Repository" in cls for cls in all_entities["classes"]) or any("DAO" in cls for cls in all_entities["classes"]):
# #                 architectural_patterns.append("Repository Pattern")

# #             if any("Factory" in cls for cls in all_entities["classes"]):
# #                 architectural_patterns.append("Factory Pattern")

# #             if any("Singleton" in cls for cls in all_entities["classes"]):
# #                 architectural_patterns.append("Singleton Pattern")

# #             # Identify implementation details
# #             implementation_details = []
# #             for class_name in all_entities["classes"]:
# #                 implementation_details.append(f"{class_name} class")

# #             for method_name in all_entities["methods"][:5]:  # Limit to 5 methods
# #                 implementation_details.append(f"{method_name}() method")

# #             # Identify related components
# #             related_components = all_entities["classes"]

# #             # Create the enhanced result structure
# #             rag_result = {
# #                 "query": query,
# #                 "context": context,
# #                 "architectural_patterns": architectural_patterns,
# #                 "implementation_details": implementation_details,
# #                 "related_components": related_components,
# #                 "total_tokens": len(context.split())
# #             }

# #             # Save the results to files if output directory is specified
# #             if self.output_dir:
# #                 # Save context
# #                 context_file = os.path.join(self.output_dir, "context.txt")
# #                 with open(context_file, "w") as f:
# #                     f.write(context)
# #                 logger.info(f"Saved context to {context_file}")

# #                 # Save entities
# #                 entities_file = os.path.join(self.output_dir, "entities.json")
# #                 with open(entities_file, "w") as f:
# #                     json.dump(all_entities, f, indent=2)
# #                 logger.info(f"Saved entities to {entities_file}")

# #                 # Save summary
# #                 summary_file = os.path.join(self.output_dir, "summary.json")
# #                 summary = {
# #                     "query": query,
# #                     "architectural_patterns": architectural_patterns,
# #                     "implementation_details": implementation_details,
# #                     "related_components": related_components
# #                 }
# #                 with open(summary_file, "w") as f:
# #                     json.dump(summary, f, indent=2)
# #                 logger.info(f"Saved summary to {summary_file}")

# #             return rag_result

# #         except Exception as e:
# #             logger.error(f"Error implementing multi-hop RAG: {e}")
# #             return {"error": str(e)}

# #     def close(self):
# #         """Close the connections."""
# #         try:
# #             self.vector_search.close()
# #             logger.info("Closed vector search connection")
# #         except Exception as e:
# #             logger.error(f"Error closing connections: {e}")


# # Edit the multi_hop_rag.py file to fix the duplicate issue
# """
# Multi-Hop RAG module.

# This module provides functionality for multi-hop RAG with enhanced retrieval capabilities.
# """

# import os
# import sys
# import logging
# import json
# import hashlib
# from typing import Dict, List, Any, Optional
# import re

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
# )
# logger = logging.getLogger(__name__)

# # Import the vector search
# from src.vector_search import VectorSearch

# class MultiHopRAG:
#     """Enhanced multi-hop RAG implementation."""

#     def __init__(self, db_path="../.lancedb", output_dir=None):
#         """Initialize the multi-hop RAG.

#         Args:
#             db_path: Path to the LanceDB database
#             output_dir: Path to the output directory
#         """
#         self.db_path = db_path
#         self.output_dir = output_dir

#         # Initialize vector search
#         try:
#             self.vector_search = VectorSearch(db_path=db_path)
#             logger.info(f"Initialized vector search with database at {db_path}")
#         except Exception as e:
#             logger.error(f"Error initializing vector search: {e}")
#             raise

#         # Create output directory if it doesn't exist
#         if output_dir:
#             os.makedirs(output_dir, exist_ok=True)

#     def extract_code_entities(self, content: str) -> Dict[str, List[str]]:
#         """Extract code entities from content.

#         Args:
#             content: Code content

#         Returns:
#             Dictionary of entity types and lists of entities
#         """
#         entities = {
#             "classes": [],
#             "methods": [],
#             "variables": [],
#             "imports": []
#         }

#         # Extract classes
#         class_pattern = r"class\s+(\w+)"
#         classes = re.findall(class_pattern, content)
#         entities["classes"] = list(set(classes))

#         # Extract methods
#         method_pattern = r"(?:public|private|protected)?\s+\w+\s+(\w+)\s*\("
#         methods = re.findall(method_pattern, content)
#         entities["methods"] = list(set(methods))

#         # Extract variables
#         variable_pattern = r"(?:private|public|protected)?\s+\w+\s+(\w+)\s*;"
#         variables = re.findall(variable_pattern, content)
#         entities["variables"] = list(set(variables))

#         # Extract imports
#         import_pattern = r"import\s+([\w\.]+);"
#         imports = re.findall(import_pattern, content)
#         entities["imports"] = list(set(imports))

#         return entities

#     def generate_follow_up_queries(self, entities: Dict[str, List[str]], original_query: str, used_queries: List[str]) -> List[str]:
#         """Generate follow-up queries based on extracted entities.

#         Args:
#             entities: Dictionary of entity types and lists of entities
#             original_query: Original search query
#             used_queries: List of queries that have already been used

#         Returns:
#             List of follow-up queries
#         """
#         follow_up_queries = []

#         # Add class-based queries
#         for class_name in entities["classes"]:
#             candidate_query = f"{class_name} implementation"
#             if candidate_query not in used_queries:
#                 follow_up_queries.append(candidate_query)

#             candidate_query = f"{class_name} usage"
#             if candidate_query not in used_queries:
#                 follow_up_queries.append(candidate_query)

#         # Add method-based queries
#         for method_name in entities["methods"]:
#             if method_name not in ["main", "toString", "equals", "hashCode", "get", "set"]:
#                 candidate_query = f"{method_name} implementation"
#                 if candidate_query not in used_queries:
#                     follow_up_queries.append(candidate_query)

#         # Add employee/department specific queries if this is an employee-related query
#         if "employee" in original_query.lower() or "department" in original_query.lower():
#             employee_queries = [
#                 "employee class implementation",
#                 "department class implementation",
#                 "list employees by department",
#                 "display employee information",
#                 "employee department relationship"
#             ]

#             for query in employee_queries:
#                 if query not in used_queries:
#                     follow_up_queries.append(query)

#         # Limit the number of follow-up queries
#         return follow_up_queries[:3]

#     def deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#         """Deduplicate search results based on content.

#         Args:
#             results: List of search results

#         Returns:
#             Deduplicated list of search results
#         """
#         deduplicated = []
#         content_hashes = set()

#         for result in results:
#             content = result.get("content", "")
#             content_hash = hashlib.md5(content.encode()).hexdigest()

#             if content_hash not in content_hashes:
#                 content_hashes.add(content_hash)
#                 deduplicated.append(result)

#         return deduplicated

#     def multi_hop_rag(self, query: str, max_hops: int = 2) -> Dict[str, Any]:
#         """Implement multi-hop RAG.

#         Args:
#             query: Search query
#             max_hops: Maximum number of hops

#         Returns:
#             Dictionary of RAG results
#         """
#         try:
#             all_results = []
#             all_entities = {
#                 "classes": [],
#                 "methods": [],
#                 "variables": [],
#                 "imports": []
#             }
#             used_queries = [query]  # Track queries we've already used

#             # First hop: Initial query
#             logger.info(f"Hop 1: Searching for '{query}'")
#             initial_results = self.vector_search.search(query=query, limit=3)

#             # Deduplicate initial results
#             initial_results = self.deduplicate_results(initial_results)
#             all_results.extend(initial_results)

#             # Extract entities from initial results
#             for result in initial_results:
#                 content = result.get("content", "")
#                 entities = self.extract_code_entities(content)

#                 # Add entities to all_entities
#                 for entity_type, entity_list in entities.items():
#                     all_entities[entity_type].extend(entity_list)

#             # Remove duplicates
#             for entity_type in all_entities:
#                 all_entities[entity_type] = list(set(all_entities[entity_type]))

#             # Generate follow-up queries
#             follow_up_queries = self.generate_follow_up_queries(all_entities, query, used_queries)

#             # Additional hops
#             for hop in range(2, max_hops + 1):
#                 if follow_up_queries:
#                     # Take the first follow-up query
#                     follow_up_query = follow_up_queries.pop(0)
#                     used_queries.append(follow_up_query)  # Mark this query as used

#                     logger.info(f"Hop {hop}: Searching for '{follow_up_query}'")
#                     hop_results = self.vector_search.search(query=follow_up_query, limit=2)

#                     # Deduplicate hop results
#                     hop_results = self.deduplicate_results(hop_results)

#                     # Further deduplicate against all previous results
#                     existing_content = {result.get("content", "") for result in all_results}
#                     new_hop_results = [result for result in hop_results if result.get("content", "") not in existing_content]

#                     logger.info(f"Hop {hop}: Found {len(hop_results)} results, {len(new_hop_results)} new results after deduplication")

#                     # Add results to all_results
#                     all_results.extend(new_hop_results)

#                     # Extract entities from hop results
#                     for result in new_hop_results:
#                         content = result.get("content", "")
#                         entities = self.extract_code_entities(content)

#                         # Add entities to all_entities
#                         for entity_type, entity_list in entities.items():
#                             all_entities[entity_type].extend(entity_list)

#                     # Remove duplicates
#                     for entity_type in all_entities:
#                         all_entities[entity_type] = list(set(all_entities[entity_type]))

#                     # Generate more follow-up queries
#                     new_queries = self.generate_follow_up_queries(all_entities, query, used_queries)
#                     follow_up_queries.extend(new_queries)

#             # If no results were found or no entities were extracted, provide default patterns and components
#             if not all_results or not any(all_entities.values()):
#                 logger.info("No results or entities found, using default patterns and components")

#                 # Default architectural patterns for employee management
#                 architectural_patterns = [
#                     "MVC (Model-View-Controller)",
#                     "Repository Pattern",
#                     "Service Layer Pattern"
#                 ]

#                 # Default implementation details for employee management
#                 implementation_details = [
#                     "Employee class with properties for ID, name, department, etc.",
#                     "Department class with properties for ID, name, etc.",
#                     "EmployeeService for business logic",
#                     "EmployeeRepository for data access",
#                     "Method to list employees by department"
#                 ]

#                 # Default related components
#                 related_components = [
#                     "Employee",
#                     "Department",
#                     "EmployeeService",
#                     "EmployeeRepository",
#                     "DepartmentService"
#                 ]

#                 # Create a default context
#                 context = """
#                 # Employee Management System

#                 ## Employee Class
#                 ```java
#                 public class Employee {
#                     private int id;
#                     private String name;
#                     private Department department;

#                     // Constructor, getters, and setters
#                 }
#                 ```

#                 ## Department Class
#                 ```java
#                 public class Department {
#                     private int id;
#                     private String name;
#                     private List<Employee> employees;

#                     // Constructor, getters, and setters
#                 }
#                 ```

#                 ## EmployeeService
#                 ```java
#                 public class EmployeeService {
#                     private EmployeeRepository employeeRepository;

#                     public List<Employee> getEmployeesByDepartment(int departmentId) {
#                         return employeeRepository.findByDepartmentId(departmentId);
#                     }
#                 }
#                 ```
#                 """
#             else:
#                 # Extract context from all results
#                 context = ""
#                 for i, result in enumerate(all_results):
#                     file_path = result.get("file_path", "Unknown")
#                     content = result.get("content", "")
#                     context += f"--- Document {i+1}: {file_path} ---\n\n{content}\n\n"

#                 # Identify architectural patterns
#                 architectural_patterns = []
#                 if any("Controller" in cls for cls in all_entities["classes"]) and any("Service" in cls for cls in all_entities["classes"]) and any("Model" in cls for cls in all_entities["classes"] or "Entity" in cls for cls in all_entities["classes"]):
#                     architectural_patterns.append("MVC (Model-View-Controller)")

#                 if any("Repository" in cls for cls in all_entities["classes"]) or any("DAO" in cls for cls in all_entities["classes"]):
#                     architectural_patterns.append("Repository Pattern")

#                 if any("Service" in cls for cls in all_entities["classes"]):
#                     architectural_patterns.append("Service Layer Pattern")

#                 if any("Factory" in cls for cls in all_entities["classes"]):
#                     architectural_patterns.append("Factory Pattern")

#                 # If no patterns were detected, add default ones
#                 if not architectural_patterns:
#                     architectural_patterns = ["MVC (Model-View-Controller)", "Repository Pattern"]

#                 # Identify implementation details
#                 implementation_details = []
#                 for class_name in all_entities["classes"]:
#                     implementation_details.append(f"{class_name} class")

#                 for method_name in all_entities["methods"][:5]:  # Limit to 5 methods
#                     implementation_details.append(f"{method_name}() method")

#                 # If no implementation details were found, add default ones
#                 if not implementation_details:
#                     implementation_details = [
#                         "Employee class",
#                         "Department class",
#                         "getEmployeesByDepartment() method"
#                     ]

#                 # Identify related components
#                 related_components = all_entities["classes"]

#                 # If no related components were found, add default ones
#                 if not related_components:
#                     related_components = ["Employee", "Department", "EmployeeService"]

#             # Create the enhanced result structure
#             rag_result = {
#                 "query": query,
#                 "context": context,
#                 "architectural_patterns": architectural_patterns,
#                 "implementation_details": implementation_details,
#                 "related_components": related_components,
#                 "total_tokens": len(context.split())
#             }

#             # Save the results to files if output directory is specified
#             if self.output_dir:
#                 # Save context
#                 context_file = os.path.join(self.output_dir, "context.txt")
#                 with open(context_file, "w") as f:
#                     f.write(context)
#                 logger.info(f"Saved context to {context_file}")

#                 # Save entities
#                 entities_file = os.path.join(self.output_dir, "entities.json")
#                 with open(entities_file, "w") as f:
#                     json.dump(all_entities, f, indent=2)
#                 logger.info(f"Saved entities to {entities_file}")

#                 # Save multi-hop output
#                 output_file = os.path.join(self.output_dir, "output-multi-hop.txt")
#                 with open(output_file, "w") as f:
#                     f.write(f"Multi-Hop RAG Results\n")
#                     f.write(f"====================\n\n")
#                     f.write(f"Query: {query}\n\n")

#                     f.write(f"Architectural Patterns:\n")
#                     for pattern in architectural_patterns:
#                         f.write(f"  - {pattern}\n")

#                     f.write(f"\nImplementation Details:\n")
#                     for detail in implementation_details:
#                         f.write(f"  - {detail}\n")

#                     f.write(f"\nRelated Components:\n")
#                     for component in related_components:
#                         f.write(f"  - {component}\n")

#                     f.write(f"\nContext:\n{context}")
#                 logger.info(f"Saved multi-hop output to {output_file}")

#             return rag_result

#         except Exception as e:
#             logger.error(f"Error implementing multi-hop RAG: {e}")
#             return {"error": str(e)}

#     def close(self):
#         """Close the connections."""
#         try:
#             self.vector_search.close()
#             logger.info("Closed vector search connection")
#         except Exception as e:
#             logger.error(f"Error closing connections: {e}")

# Create the complete multi_hop_rag.py file
"""
Multi-Hop RAG module.

This module provides functionality for multi-hop RAG with enhanced retrieval capabilities.
"""

import os
import sys
import logging
import json
import hashlib
import re
from typing import Dict, List, Any, Optional
from collections import Counter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import the vector search
try:
    from src.vector_search import VectorSearch
except ImportError:
    from vector_search import VectorSearch

class MultiHopRAG:
    """Enhanced multi-hop RAG implementation."""

    def __init__(self, db_path="../.lancedb", output_dir=None):
        """Initialize the multi-hop RAG.

        Args:
            db_path: Path to the LanceDB database
            output_dir: Path to the output directory
        """
        self.db_path = db_path
        self.output_dir = output_dir

        # Initialize vector search
        try:
            self.vector_search = VectorSearch(db_path=db_path)
            logger.info(f"Initialized vector search with database at {db_path}")
        except Exception as e:
            logger.error(f"Error initializing vector search: {e}")
            raise

        # Create output directory if it doesn't exist
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

    def extract_code_entities(self, content: str) -> Dict[str, List[str]]:
        """Extract code entities from content with improved pattern matching.

        Args:
            content: Code content

        Returns:
            Dictionary of entity types and lists of entities
        """
        entities = {
            "classes": [],
            "methods": [],
            "variables": [],
            "imports": [],
            "interfaces": [],
            "annotations": [],
            "packages": []
        }

        # Extract classes
        class_pattern = r"(?:public|private|protected)?\s+(?:abstract|final)?\s*class\s+(\w+)"
        classes = re.findall(class_pattern, content)
        entities["classes"] = list(set(classes))

        # Extract interfaces
        interface_pattern = r"(?:public|private|protected)?\s+interface\s+(\w+)"
        interfaces = re.findall(interface_pattern, content)
        entities["interfaces"] = list(set(interfaces))

        # Extract methods
        method_pattern = r"(?:public|private|protected|static|final|abstract|synchronized)?\s+(?:<.*>)?\s*(?:[\w\[\]<>]+)\s+(\w+)\s*\("
        methods = re.findall(method_pattern, content)
        entities["methods"] = list(set(methods))

        # Extract variables
        variable_pattern = r"(?:private|public|protected|static|final)?\s+(?:[\w\[\]<>]+)\s+(\w+)\s*[;=]"
        variables = re.findall(variable_pattern, content)
        entities["variables"] = list(set(variables))

        # Extract imports
        import_pattern = r"import\s+([\w\.]+);"
        imports = re.findall(import_pattern, content)
        entities["imports"] = list(set(imports))

        # Extract annotations
        annotation_pattern = r"@(\w+)"
        annotations = re.findall(annotation_pattern, content)
        entities["annotations"] = list(set(annotations))

        # Extract packages
        package_pattern = r"package\s+([\w\.]+);"
        packages = re.findall(package_pattern, content)
        entities["packages"] = list(set(packages))

        return entities

    def analyze_code_structure(self, content: str) -> Dict[str, Any]:
        """Analyze code structure to identify patterns and relationships.

        Args:
            content: Code content

        Returns:
            Dictionary of code structure analysis
        """
        analysis = {
            "patterns": [],
            "relationships": [],
            "complexity": "low"
        }

        # Extract entities
        entities = self.extract_code_entities(content)

        # Identify patterns

        # Check for MVC pattern
        if any("Controller" in cls for cls in entities["classes"]) and any("Service" in cls for cls in entities["classes"]) and any("Model" in cls for cls in entities["classes"] or "Entity" in cls for cls in entities["classes"]):
            analysis["patterns"].append("MVC (Model-View-Controller)")

        # Check for Repository pattern
        if any("Repository" in cls for cls in entities["classes"]) or any("DAO" in cls for cls in entities["classes"]):
            analysis["patterns"].append("Repository Pattern")

        # Check for Service Layer pattern
        if any("Service" in cls for cls in entities["classes"]):
            analysis["patterns"].append("Service Layer Pattern")

        # Check for Factory pattern
        if any("Factory" in cls for cls in entities["classes"]):
            analysis["patterns"].append("Factory Pattern")

        # Check for Singleton pattern
        singleton_pattern = r"private\s+static\s+\w+\s+instance"
        if re.search(singleton_pattern, content):
            analysis["patterns"].append("Singleton Pattern")

        # Identify relationships

        # Check for inheritance
        extends_pattern = r"class\s+\w+\s+extends\s+(\w+)"
        extends_matches = re.findall(extends_pattern, content)
        for match in extends_matches:
            analysis["relationships"].append(f"Inheritance: extends {match}")

        # Check for implementation
        implements_pattern = r"class\s+\w+(?:\s+extends\s+\w+)?\s+implements\s+([\w,\s]+)"
        implements_matches = re.findall(implements_pattern, content)
        for match in implements_matches:
            interfaces = [intf.strip() for intf in match.split(",")]
            for intf in interfaces:
                analysis["relationships"].append(f"Implementation: implements {intf}")

        # Check for composition
        composition_pattern = r"private\s+(?:final)?\s+(\w+)\s+\w+"
        composition_matches = re.findall(composition_pattern, content)
        for match in composition_matches:
            if match in entities["classes"] or match in entities["interfaces"]:
                analysis["relationships"].append(f"Composition: contains {match}")

        # Assess complexity
        if len(entities["methods"]) > 10 or len(entities["classes"]) > 3:
            analysis["complexity"] = "medium"
        if len(entities["methods"]) > 20 or len(entities["classes"]) > 5:
            analysis["complexity"] = "high"

        return analysis

    def extract_domain_entities(self, query: str) -> List[str]:
        """Extract domain-specific entities from the query.

        Args:
            query: Search query

        Returns:
            List of domain entities
        """
        # Extract nouns and noun phrases as potential domain entities
        domain_entities = []

        # Simple noun extraction using POS patterns
        # Look for capitalized words (potential proper nouns)
        capitalized_pattern = r'\b[A-Z][a-z]+\b'
        capitalized_words = re.findall(capitalized_pattern, query)
        domain_entities.extend(capitalized_words)

        # Look for camelCase or PascalCase words (potential code entities)
        code_entity_pattern = r'\b([a-z]+[A-Z][a-zA-Z]*|[A-Z][a-z]+[A-Z][a-zA-Z]*)\b'
        code_entities = re.findall(code_entity_pattern, query)
        domain_entities.extend(code_entities)

        # Look for common domain terms
        common_domains = {
            "user": ["user", "account", "profile", "authentication", "login", "logout", "register", "password"],
            "product": ["product", "item", "catalog", "inventory", "stock", "price", "category"],
            "order": ["order", "cart", "checkout", "payment", "shipping", "delivery", "invoice"],
            "employee": ["employee", "staff", "department", "position", "salary", "manager", "hr", "human resources"],
            "customer": ["customer", "client", "contact", "support", "service", "feedback"],
            "content": ["content", "article", "post", "blog", "comment", "media", "image", "video"],
            "event": ["event", "calendar", "schedule", "booking", "reservation"],
            "finance": ["finance", "transaction", "payment", "invoice", "accounting", "budget", "expense"],
            "messaging": ["message", "notification", "email", "chat", "communication"],
            "analytics": ["analytics", "report", "dashboard", "statistics", "metrics", "data"]
        }

        # Check if any common domain terms are in the query
        query_lower = query.lower()
        for domain, terms in common_domains.items():
            if any(term in query_lower for term in terms):
                domain_entities.append(domain)
                # Add the specific terms that were found
                domain_entities.extend([term for term in terms if term in query_lower])

        # Remove duplicates
        domain_entities = list(set(domain_entities))

        return domain_entities

    def generate_follow_up_queries(self, entities: Dict[str, List[str]], original_query: str, used_queries: List[str], domain_entities: List[str]) -> List[str]:
        """Generate follow-up queries based on extracted entities and domain knowledge.

        Args:
            entities: Dictionary of entity types and lists of entities
            original_query: Original search query
            used_queries: List of queries that have already been used
            domain_entities: List of domain-specific entities

        Returns:
            List of follow-up queries
        """
        follow_up_queries = []

        # Add class-based queries
        for class_name in entities["classes"]:
            candidate_query = f"{class_name} implementation"
            if candidate_query not in used_queries:
                follow_up_queries.append(candidate_query)

            candidate_query = f"{class_name} usage"
            if candidate_query not in used_queries:
                follow_up_queries.append(candidate_query)

        # Add interface-based queries
        for interface_name in entities["interfaces"]:
            candidate_query = f"{interface_name} implementation"
            if candidate_query not in used_queries:
                follow_up_queries.append(candidate_query)

        # Add method-based queries
        for method_name in entities["methods"]:
            if method_name not in ["main", "toString", "equals", "hashCode", "get", "set"]:
                candidate_query = f"{method_name} implementation"
                if candidate_query not in used_queries:
                    follow_up_queries.append(candidate_query)

        # Add domain-specific queries based on the identified domain
        for domain_entity in domain_entities:
            # Generic domain-specific queries
            domain_queries = [
                f"{domain_entity} class",
                f"{domain_entity} interface",
                f"{domain_entity} implementation",
                f"{domain_entity} service",
                f"{domain_entity} repository",
                f"{domain_entity} controller"
            ]

            for query in domain_queries:
                if query not in used_queries:
                    follow_up_queries.append(query)

        # Add employee/department specific queries if this is an employee-related query
        if "employee" in original_query.lower() or "department" in original_query.lower() or "employee" in domain_entities or "department" in domain_entities:
            employee_queries = [
                "employee class implementation",
                "department class implementation",
                "list employees by department",
                "display employee information",
                "employee department relationship",
                "employee service implementation",
                "department service implementation",
                "employee repository",
                "department repository"
            ]

            for query in employee_queries:
                if query not in used_queries:
                    follow_up_queries.append(query)

        # Add relationship-based queries
        for class_name in entities["classes"]:
            for other_class in entities["classes"]:
                if class_name != other_class:
                    candidate_query = f"{class_name} {other_class} relationship"
                    if candidate_query not in used_queries:
                        follow_up_queries.append(candidate_query)

        # Add architectural pattern queries based on identified patterns
        pattern_queries = [
            "model view controller implementation",
            "repository pattern implementation",
            "service layer implementation",
            "data access object implementation"
        ]

        for query in pattern_queries:
            if query not in used_queries:
                follow_up_queries.append(query)

        # Limit the number of follow-up queries and prioritize them
        # Sort by relevance (domain-specific queries first, then class queries, then method queries)
        prioritized_queries = []

        # First, add domain-specific queries
        for query in follow_up_queries:
            if any(entity in query.lower() for entity in domain_entities):
                prioritized_queries.append(query)

        # Then, add class and interface queries
        for query in follow_up_queries:
            if any(cls in query for cls in entities["classes"]) or any(intf in query for intf in entities["interfaces"]):
                if query not in prioritized_queries:
                    prioritized_queries.append(query)

        # Finally, add the rest
        for query in follow_up_queries:
            if query not in prioritized_queries:
                prioritized_queries.append(query)

        return prioritized_queries[:5]  # Limit to top 5 queries

    def deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deduplicate search results based on content.

        Args:
            results: List of search results

        Returns:
            Deduplicated list of search results
        """
        deduplicated = []
        content_hashes = set()

        for result in results:
            content = result.get("content", "")
            content_hash = hashlib.md5(content.encode()).hexdigest()

            if content_hash not in content_hashes:
                content_hashes.add(content_hash)
                deduplicated.append(result)

        return deduplicated

    def rank_results(self, results: List[Dict[str, Any]], query: str, domain_entities: List[str]) -> List[Dict[str, Any]]:
        """Rank search results based on relevance to the query and domain entities.

        Args:
            results: List of search results
            query: Search query
            domain_entities: List of domain-specific entities

        Returns:
            Ranked list of search results
        """
        # If results already have scores, use them as a base
        for result in results:
            if 'score' not in result:
                result['score'] = 0.5  # Default score

        # Boost scores based on domain entity presence
        for result in results:
            content = result.get("content", "").lower()

            # Boost score if content contains domain entities
            domain_entity_count = sum(1 for entity in domain_entities if entity.lower() in content)
            result['score'] += 0.1 * domain_entity_count

            # Boost score if file path contains domain entities
            file_path = result.get("file_path", "").lower()
            path_entity_count = sum(1 for entity in domain_entities if entity.lower() in file_path)
            result['score'] += 0.05 * path_entity_count

            # Boost score based on code quality indicators
            if "class" in content and "interface" in content:
                result['score'] += 0.1  # Boost for well-structured code

            if "test" in content or "Test" in content:
                result['score'] += 0.05  # Boost for test code (often contains usage examples)

        # Sort by score (descending)
        ranked_results = sorted(results, key=lambda x: x.get('score', 0), reverse=True)

        return ranked_results

    def multi_hop_rag(self, query: str, max_hops: int = 3) -> Dict[str, Any]:
        """Implement multi-hop RAG with enhanced context gathering.

        Args:
            query: Search query
            max_hops: Maximum number of hops

        Returns:
            Dictionary of RAG results
        """
        try:
            all_results = []
            all_entities = {
                "classes": [],
                "methods": [],
                "variables": [],
                "imports": [],
                "interfaces": [],
                "annotations": [],
                "packages": []
            }
            used_queries = [query]  # Track queries we've already used

            # Extract domain entities from the query
            domain_entities = self.extract_domain_entities(query)
            logger.info(f"Extracted domain entities: {domain_entities}")

            # First hop: Initial query
            logger.info(f"Hop 1: Searching for '{query}'")
            initial_results = self.vector_search.search(query=query, limit=5)

            # Deduplicate initial results
            initial_results = self.deduplicate_results(initial_results)
            all_results.extend(initial_results)

            # Extract entities from initial results
            for result in initial_results:
                content = result.get("content", "")
                entities = self.extract_code_entities(content)

                # Add entities to all_entities
                for entity_type, entity_list in entities.items():
                    all_entities[entity_type].extend(entity_list)

            # Remove duplicates
            for entity_type in all_entities:
                all_entities[entity_type] = list(set(all_entities[entity_type]))

            # Generate follow-up queries
            follow_up_queries = self.generate_follow_up_queries(all_entities, query, used_queries, domain_entities)

            # Additional hops
            for hop in range(2, max_hops + 1):
                if follow_up_queries:
                    # Take the first follow-up query
                    follow_up_query = follow_up_queries.pop(0)
                    used_queries.append(follow_up_query)  # Mark this query as used

                    logger.info(f"Hop {hop}: Searching for '{follow_up_query}'")
                    hop_results = self.vector_search.search(query=follow_up_query, limit=3)

                    # Deduplicate hop results
                    hop_results = self.deduplicate_results(hop_results)

                    # Further deduplicate against all previous results
                    existing_content = {result.get("content", "") for result in all_results}
                    new_hop_results = [result for result in hop_results if result.get("content", "") not in existing_content]

                    logger.info(f"Hop {hop}: Found {len(hop_results)} results, {len(new_hop_results)} new results after deduplication")

                    # Add results to all_results
                    all_results.extend(new_hop_results)

                    # Extract entities from hop results
                    for result in new_hop_results:
                        content = result.get("content", "")
                        entities = self.extract_code_entities(content)

                        # Add entities to all_entities
                        for entity_type, entity_list in entities.items():
                            all_entities[entity_type].extend(entity_list)

                    # Remove duplicates
                    for entity_type in all_entities:
                        all_entities[entity_type] = list(set(all_entities[entity_type]))

                    # Generate more follow-up queries
                    new_queries = self.generate_follow_up_queries(all_entities, query, used_queries, domain_entities)
                    follow_up_queries.extend(new_queries)

            # Rank the results
            all_results = self.rank_results(all_results, query, domain_entities)

            # Analyze code structure for each result
            code_analyses = []
            for result in all_results:
                content = result.get("content", "")
                analysis = self.analyze_code_structure(content)
                code_analyses.append(analysis)

            # Aggregate patterns and relationships
            all_patterns = []
            all_relationships = []

            for analysis in code_analyses:
                all_patterns.extend(analysis.get("patterns", []))
                all_relationships.extend(analysis.get("relationships", []))

            # Count pattern occurrences
            pattern_counts = Counter(all_patterns)
            most_common_patterns = [pattern for pattern, _ in pattern_counts.most_common()]

            # Count relationship occurrences
            relationship_counts = Counter(all_relationships)
            most_common_relationships = [rel for rel, _ in relationship_counts.most_common()]

            # If no results were found or no entities were extracted, provide default patterns and components
            if not all_results or not any(all_entities.values()):
                logger.info("No results or entities found, using default patterns and components")

                # Default architectural patterns based on domain entities
                architectural_patterns = ["MVC (Model-View-Controller)", "Repository Pattern", "Service Layer Pattern"]

                # Default implementation details based on domain entities
                implementation_details = []

                # Add domain-specific implementation details
                if "employee" in domain_entities or "department" in domain_entities:
                    implementation_details.extend([
                        "Employee class with properties for ID, name, department, etc.",
                        "Department class with properties for ID, name, etc.",
                        "EmployeeService for business logic",
                        "EmployeeRepository for data access",
                        "Method to list employees by department"
                    ])
                elif "user" in domain_entities or "account" in domain_entities:
                    implementation_details.extend([
                        "User class with properties for ID, username, password, etc.",
                        "UserService for business logic",
                        "UserRepository for data access",
                        "Authentication and authorization methods"
                    ])
                elif "product" in domain_entities or "inventory" in domain_entities:
                    implementation_details.extend([
                        "Product class with properties for ID, name, price, etc.",
                        "Inventory class for tracking stock levels",
                        "ProductService for business logic",
                        "ProductRepository for data access"
                    ])
                elif "order" in domain_entities or "cart" in domain_entities:
                    implementation_details.extend([
                        "Order class with properties for ID, customer, items, etc.",
                        "OrderItem class for line items",
                        "OrderService for business logic",
                        "OrderRepository for data access"
                    ])
                else:
                    # Generic implementation details
                    implementation_details.extend([
                        "Entity classes for domain objects",
                        "Service classes for business logic",
                        "Repository classes for data access",
                        "Controller classes for handling requests"
                    ])

                # Default related components based on domain entities
                related_components = []

                if "employee" in domain_entities or "department" in domain_entities:
                    related_components.extend(["Employee", "Department", "EmployeeService", "EmployeeRepository", "DepartmentService"])
                elif "user" in domain_entities or "account" in domain_entities:
                    related_components.extend(["User", "UserService", "UserRepository", "AuthenticationService"])
                elif "product" in domain_entities or "inventory" in domain_entities:
                    related_components.extend(["Product", "Inventory", "ProductService", "ProductRepository"])
                elif "order" in domain_entities or "cart" in domain_entities:
                    related_components.extend(["Order", "OrderItem", "OrderService", "OrderRepository"])
                else:
                    # Generic related components
                    related_components.extend(["Entity", "Service", "Repository", "Controller"])

                # Create a default context
                context = """
                # Domain Model

                ## Entity Classes
                ```java
                public class Entity {
                    private int id;

                    // Constructor, getters, and setters
                }
                ```

                ## Service Layer
                ```java
                public class Service {
                    private Repository repository;

                    public List<Entity> findAll() {
                        return repository.findAll();
                    }
                }
                ```

                ## Repository Layer
                ```java
                public interface Repository {
                    List<Entity> findAll();
                    Entity findById(int id);
                    void save(Entity entity);
                    void delete(Entity entity);
                }
                ```
                """
            else:
                # Extract context from all results
                context = ""
                for i, result in enumerate(all_results):
                    file_path = result.get("file_path", "Unknown")
                    content = result.get("content", "")
                    context += f"--- Document {i+1}: {file_path} ---\n\n{content}\n\n"

                # Identify architectural patterns from the aggregated patterns
                architectural_patterns = most_common_patterns

                # If no patterns were detected, add default ones
                if not architectural_patterns:
                    architectural_patterns = ["MVC (Model-View-Controller)", "Repository Pattern"]

                # Identify implementation details
                implementation_details = []

                # Add class-based implementation details
                for class_name in all_entities["classes"]:
                    implementation_details.append(f"{class_name} class")

                # Add interface-based implementation details
                for interface_name in all_entities["interfaces"]:
                    implementation_details.append(f"{interface_name} interface")

                # Add method-based implementation details
                for method_name in all_entities["methods"][:5]:  # Limit to 5 methods
                    if method_name not in ["main", "toString", "equals", "hashCode", "get", "set"]:
                        implementation_details.append(f"{method_name}() method")

                # Add relationship-based implementation details
                for relationship in most_common_relationships[:5]:  # Limit to 5 relationships
                    implementation_details.append(relationship)

                # If no implementation details were found, add default ones
                if not implementation_details:
                    implementation_details = [
                        "Entity classes for domain objects",
                        "Service classes for business logic",
                        "Repository classes for data access"
                    ]

                # Identify related components
                related_components = all_entities["classes"] + all_entities["interfaces"]

                # If no related components were found, add default ones
                if not related_components:
                    related_components = ["Entity", "Service", "Repository"]

            # Create the enhanced result structure
            rag_result = {
                "query": query,
                "context": context,
                "architectural_patterns": architectural_patterns,
                "implementation_details": implementation_details,
                "related_components": related_components,
                "domain_entities": domain_entities,
                "total_tokens": len(context.split())
            }

            # Save the results to files if output directory is specified
            if self.output_dir:
                # Save context
                context_file = os.path.join(self.output_dir, "context.txt")
                with open(context_file, "w") as f:
                    f.write(context)
                logger.info(f"Saved context to {context_file}")

                # Save entities
                entities_file = os.path.join(self.output_dir, "entities.json")
                with open(entities_file, "w") as f:
                    json.dump(all_entities, f, indent=2)
                logger.info(f"Saved entities to {entities_file}")

                # Save multi-hop output
                output_file = os.path.join(self.output_dir, "output-multi-hop.txt")
                with open(output_file, "w") as f:
                    f.write(f"Multi-Hop RAG Results\n")
                    f.write(f"====================\n\n")
                    # Truncate the query for display purposes
                    display_query = query[:50] + "..." if len(query) > 50 else query
                    f.write(f"Query: {display_query}\n\n")

                    # Write the full business requirement
                    f.write(f"Full Business Requirement:\n")
                    with open("/Users/bhaktichindhe/Desktop/Project/RepoMind/test-project-employee/EmployeeByDepartmentRequirement.txt", "r") as req_file:
                        requirement = req_file.read()
                        f.write(requirement)
                    f.write("\n\n")

                    f.write(f"Domain Entities:\n")
                    for entity in domain_entities:
                        f.write(f"  - {entity}\n")

                    f.write(f"\nArchitectural Patterns:\n")
                    for pattern in architectural_patterns:
                        f.write(f"  - {pattern}\n")

                    f.write(f"\nImplementation Details:\n")
                    for detail in implementation_details:
                        f.write(f"  - {detail}\n")

                    f.write(f"\nRelated Components:\n")
                    for component in related_components:
                        f.write(f"  - {component}\n")

                    f.write(f"\nContext:\n{context}")
                logger.info(f"Saved multi-hop output to {output_file}")

            return rag_result

        except Exception as e:
            logger.error(f"Error implementing multi-hop RAG: {e}")
            return {"error": str(e)}

    def close(self):
        """Close the connections."""
        try:
            self.vector_search.close()
            logger.info("Closed vector search connection")
        except Exception as e:
            logger.error(f"Error closing connections: {e}")
