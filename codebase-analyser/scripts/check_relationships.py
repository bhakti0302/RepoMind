#!/usr/bin/env python3
"""
Check relationships in the testshreya project.
"""

import lancedb
import json
import sys

def main():
    """Main entry point."""
    # Connect to the database
    print("Connecting to the database...")
    db = lancedb.connect("./.lancedb")

    # Check if the code_chunks table exists
    if "code_chunks" not in db.table_names():
        print("Code chunks table does not exist")
        return

    # Open the table
    table = db.open_table("code_chunks")

    # Get all chunks for the testshreya project
    df = table.to_pandas()
    testshreya_chunks = df[df["project_id"] == "testshreya"]

    print(f"Found {len(testshreya_chunks)} chunks for project 'testshreya'")

    # Count chunks by type
    type_counts = testshreya_chunks.groupby("chunk_type").size()
    print("Chunks by type:")
    for chunk_type, count in type_counts.items():
        print(f"  - {chunk_type}: {count}")

    # Check for parent-child relationships
    parent_child_relationships = []
    for _, chunk in testshreya_chunks.iterrows():
        if "children_ids" in chunk and isinstance(chunk["children_ids"], list) and len(chunk["children_ids"]) > 0:
            for child_id in chunk["children_ids"]:
                parent_child_relationships.append((chunk["node_id"], child_id, "CONTAINS"))

    print(f"Found {len(parent_child_relationships)} parent-child relationships")

    # Print some examples of parent-child relationships
    print("Examples of parent-child relationships:")
    for i, (parent, child, rel_type) in enumerate(parent_child_relationships[:5]):
        parent_name = testshreya_chunks[testshreya_chunks["node_id"] == parent]["name"].values[0] if len(testshreya_chunks[testshreya_chunks["node_id"] == parent]) > 0 else parent
        child_name = testshreya_chunks[testshreya_chunks["node_id"] == child]["name"].values[0] if len(testshreya_chunks[testshreya_chunks["node_id"] == child]) > 0 else child
        print(f"  {i+1}. {parent_name} {rel_type} {child_name}")

    # Check for class inheritance relationships
    class_chunks = testshreya_chunks[testshreya_chunks["chunk_type"] == "class_declaration"]

    # Look for "extends" and "implements" in the content
    inheritance_relationships = []
    for _, chunk in class_chunks.iterrows():
        content = chunk["content"].lower()
        if "extends" in content:
            # Find the class being extended
            lines = content.split("\n")
            for line in lines:
                if "extends" in line:
                    # Extract the class name
                    parts = line.split("extends")
                    if len(parts) > 1:
                        extended_class = parts[1].strip().split()[0].strip()
                        inheritance_relationships.append((chunk["name"], extended_class, "EXTENDS"))

        if "implements" in content:
            # Find the interface being implemented
            lines = content.split("\n")
            for line in lines:
                if "implements" in line:
                    # Extract the interface name
                    parts = line.split("implements")
                    if len(parts) > 1:
                        implemented_interface = parts[1].strip().split()[0].strip()
                        inheritance_relationships.append((chunk["name"], implemented_interface, "IMPLEMENTS"))

    print(f"Found {len(inheritance_relationships)} inheritance relationships")

    # Print inheritance relationships
    print("Inheritance relationships:")
    for i, (child, parent, rel_type) in enumerate(inheritance_relationships):
        print(f"  {i+1}. {child} {rel_type} {parent}")

    # Check for field type relationships
    field_type_relationships = []
    for _, chunk in class_chunks.iterrows():
        content = chunk["content"].lower()
        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            # Look for field declarations
            if "private" in line or "protected" in line or "public" in line:
                # Skip method declarations
                if "(" in line:
                    continue

                # Skip constructors
                if chunk["name"].lower() in line and "(" in line:
                    continue

                # Check for field declarations with known types
                for type_name in ["user", "order", "address", "entity", "abstractentity"]:
                    if type_name in line.lower():
                        field_type_relationships.append((chunk["name"], type_name.capitalize(), "FIELD_TYPE"))

    print(f"Found {len(field_type_relationships)} field type relationships")

    # Print field type relationships
    print("Field type relationships:")
    for i, (class_name, field_type, rel_type) in enumerate(field_type_relationships):
        print(f"  {i+1}. {class_name} {rel_type} {field_type}")

    # Check for method call relationships
    method_call_relationships = []
    for _, chunk in testshreya_chunks.iterrows():
        if chunk["chunk_type"] == "method_declaration":
            content = chunk["content"].lower()
            # Look for method calls to other classes
            for class_name in ["user", "order", "address"]:
                if class_name in content and "." in content:
                    method_call_relationships.append((chunk["name"], class_name.capitalize(), "CALLS"))

    print(f"Found {len(method_call_relationships)} method call relationships")

    # Print method call relationships
    print("Method call relationships:")
    for i, (method_name, class_name, rel_type) in enumerate(method_call_relationships):
        print(f"  {i+1}. {method_name} {rel_type} {class_name}")

    # Check for import relationships
    import_relationships = []
    for _, chunk in testshreya_chunks.iterrows():
        if chunk["chunk_type"] == "import_declaration":
            content = chunk["content"].lower()
            # Extract the imported class or package
            imported = content.replace("import", "").strip().rstrip(";")
            # Get the file that contains this import
            file_chunks = testshreya_chunks[testshreya_chunks["chunk_type"] == "file"]
            for _, file_chunk in file_chunks.iterrows():
                if chunk["file_path"] == file_chunk["file_path"]:
                    import_relationships.append((file_chunk["name"], imported, "IMPORTS"))

    print(f"Found {len(import_relationships)} import relationships")

    # Print import relationships
    print("Import relationships:")
    for i, (file_name, imported, rel_type) in enumerate(import_relationships[:5]):
        print(f"  {i+1}. {file_name} {rel_type} {imported}")

    # Total relationships
    total_relationships = len(parent_child_relationships) + len(inheritance_relationships) + len(field_type_relationships) + len(method_call_relationships) + len(import_relationships)
    print(f"Total relationships found: {total_relationships}")

if __name__ == "__main__":
    main()
