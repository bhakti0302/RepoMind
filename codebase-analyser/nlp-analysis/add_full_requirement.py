#!/usr/bin/env python3

"""
Add the full business requirement to the output-multi-hop.txt file.
"""

import os
import sys

def add_full_requirement():
    """Add the full business requirement to the output-multi-hop.txt file."""
    # Define file paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))  # Go up two levels to reach project root

    output_file = os.path.join(os.path.dirname(current_dir), "output", "output-multi-hop.txt")
    requirement_file = os.path.join(project_root, "test-project-employee", "EmployeeByDepartmentRequirement.txt")

    # Read the output file
    with open(output_file, 'r') as f:
        content = f.read()

    # Read the requirement file
    with open(requirement_file, 'r') as f:
        requirement = f.read()

    # Find the position to insert the full requirement
    query_line = "Query: "
    query_pos = content.find(query_line)
    if query_pos == -1:
        print("Error: Could not find the query line in the output file.")
        return

    # Find the end of the query line
    query_end_pos = content.find("\n\n", query_pos)
    if query_end_pos == -1:
        print("Error: Could not find the end of the query line.")
        return

    # Insert the full requirement after the query line
    new_content = (
        content[:query_end_pos + 2] +
        "Full Business Requirement:\n" +
        requirement +
        "\n\n" +
        content[query_end_pos + 2:]
    )

    # Write the new content back to the output file
    with open(output_file, 'w') as f:
        f.write(new_content)

    print(f"Added full business requirement to {output_file}")

if __name__ == "__main__":
    add_full_requirement()
