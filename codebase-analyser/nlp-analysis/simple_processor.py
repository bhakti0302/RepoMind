#!/usr/bin/env python3

"""
Simple Business Requirements Processor

This script processes business requirements without relying on complex dependencies.
It extracts key information from the requirements file and generates a simple response.
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def extract_requirements(file_path):
    """Extract requirements from a text file."""
    logger.info(f"Extracting requirements from {file_path}")

    try:
        with open(file_path, 'r') as f:
            content = f.read()

        # Simple extraction of key sections
        sections = {}

        if "Objective:" in content:
            objective_start = content.find("Objective:") + len("Objective:")
            objective_end = content.find("\n\n", objective_start)
            if objective_end == -1:
                objective_end = len(content)
            sections["objective"] = content[objective_start:objective_end].strip()

        if "Functional Requirements:" in content:
            req_start = content.find("Functional Requirements:") + len("Functional Requirements:")
            req_end = content.find("Suggested Code Enhancements:", req_start)
            if req_end == -1:
                req_end = len(content)
            sections["requirements"] = content[req_start:req_end].strip()

        if "Suggested Code Enhancements:" in content:
            enh_start = content.find("Suggested Code Enhancements:") + len("Suggested Code Enhancements:")
            enh_end = len(content)
            sections["enhancements"] = content[enh_start:enh_end].strip()

        return sections

    except Exception as e:
        logger.error(f"Error extracting requirements: {e}")
        return None

def generate_code(requirements, project_id):
    """Generate code based on the extracted requirements."""
    logger.info(f"Generating code for project {project_id}")

    # Extract key information
    objective = requirements.get("objective", "")
    functional_reqs = requirements.get("requirements", "")
    enhancements = requirements.get("enhancements", "")

    # Generate a simple implementation based on the requirements
    if "search" in objective.lower() and "employee" in objective.lower():
        code = """
package com.example.employee;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Employee Search Implementation
 * Generated based on business requirements
 */
public class EmployeeSearch {
    private EmployeeManager employeeManager;

    public EmployeeSearch(EmployeeManager employeeManager) {
        this.employeeManager = employeeManager;
    }

    /**
     * Search for employees based on various criteria
     * @param criteria The search criteria
     * @param type The type of search to perform
     * @return List of matching employees
     */
    public List<Employee> searchEmployees(String criteria, SearchType type) {
        List<Employee> allEmployees = employeeManager.getAllEmployees();
        List<Employee> results = new ArrayList<>();

        switch (type) {
            case NAME:
                results = searchByName(allEmployees, criteria);
                break;
            case DEPARTMENT:
                results = searchByDepartment(allEmployees, criteria);
                break;
            case SKILLS:
                results = searchBySkills(allEmployees, criteria);
                break;
            case ALL:
                results.addAll(searchByName(allEmployees, criteria));
                results.addAll(searchByDepartment(allEmployees, criteria));
                results.addAll(searchBySkills(allEmployees, criteria));
                // Remove duplicates
                results = results.stream().distinct().collect(Collectors.toList());
                break;
        }

        return results;
    }

    private List<Employee> searchByName(List<Employee> employees, String name) {
        String searchName = name.toLowerCase();
        return employees.stream()
            .filter(e -> e.getFirstName().toLowerCase().contains(searchName) ||
                   e.getLastName().toLowerCase().contains(searchName))
            .collect(Collectors.toList());
    }

    private List<Employee> searchByDepartment(List<Employee> employees, String department) {
        String searchDept = department.toLowerCase();
        return employees.stream()
            .filter(e -> e.getDepartment().toLowerCase().equals(searchDept))
            .collect(Collectors.toList());
    }

    private List<Employee> searchBySkills(List<Employee> employees, String skillsStr) {
        String[] skills = skillsStr.toLowerCase().split(",");

        return employees.stream()
            .filter(e -> hasMatchingSkills(e, skills))
            .sorted((e1, e2) -> countMatchingSkills(e2, skills) - countMatchingSkills(e1, skills))
            .collect(Collectors.toList());
    }

    private boolean hasMatchingSkills(Employee employee, String[] skills) {
        for (String skill : skills) {
            if (employee.hasSkill(skill.trim())) {
                return true;
            }
        }
        return false;
    }

    private int countMatchingSkills(Employee employee, String[] skills) {
        int count = 0;
        for (String skill : skills) {
            if (employee.hasSkill(skill.trim())) {
                count++;
            }
        }
        return count;
    }
}

/**
 * Search type enum
 */
enum SearchType {
    NAME,
    DEPARTMENT,
    SKILLS,
    ALL
}
"""
    else:
        code = """
// Generated code based on requirements
public class RequirementsImplementation {
    // TODO: Implement the requirements
    public void implementRequirements() {
        System.out.println("Implementing requirements...");
        // Add implementation here
    }
}
"""

    return code

def save_output(requirements, code, output_dir, project_id):
    """Save the processed requirements and generated code."""
    logger.info(f"Saving output to {output_dir}")

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Create project directory if it doesn't exist
    project_dir = os.path.join(output_dir, project_id)
    if not os.path.exists(project_dir):
        os.makedirs(project_dir)

    # Save requirements as JSON
    requirements_path = os.path.join(project_dir, "requirements.json")
    with open(requirements_path, 'w') as f:
        json.dump(requirements, f, indent=2)

    # Save generated code
    code_path = os.path.join(project_dir, "generated_code.java")
    with open(code_path, 'w') as f:
        f.write(code)

    # Save timestamp
    timestamp_path = os.path.join(project_dir, "timestamp.txt")
    with open(timestamp_path, 'w') as f:
        f.write(datetime.now().isoformat())

    # Create the llm-output.txt file that the extension expects
    llm_output_path = os.path.join(output_dir, "llm-output.txt")
    with open(llm_output_path, 'w') as f:
        f.write(code)

    # Create the llm-instructions.txt file that the extension expects
    llm_instructions_path = os.path.join(output_dir, "llm-instructions.txt")
    with open(llm_instructions_path, 'w') as f:
        f.write(f"""
Requirements:
{json.dumps(requirements, indent=2)}

Generated Code:
```java
{code}
```
""")

    return {
        "requirements_path": requirements_path,
        "code_path": code_path,
        "timestamp_path": timestamp_path,
        "llm_output_path": llm_output_path,
        "llm_instructions_path": llm_instructions_path
    }

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Process business requirements")
    parser.add_argument("--file", required=True, help="Path to the business requirements file")
    parser.add_argument("--project-id", required=True, help="Project ID")
    parser.add_argument("--output-dir", required=True, help="Output directory")
    parser.add_argument("--data-dir", required=False, help="Data directory")

    args = parser.parse_args()

    # Extract requirements
    requirements = extract_requirements(args.file)
    if not requirements:
        logger.error("Failed to extract requirements")
        sys.exit(1)

    # Generate code
    code = generate_code(requirements, args.project_id)

    # Save output
    output_paths = save_output(requirements, code, args.output_dir, args.project_id)

    # Print output paths
    print(f"Requirements saved to: {output_paths['requirements_path']}")
    print(f"Generated code saved to: {output_paths['code_path']}")
    print(f"Timestamp saved to: {output_paths['timestamp_path']}")
    print(f"LLM output saved to: {output_paths['llm_output_path']}")
    print(f"LLM instructions saved to: {output_paths['llm_instructions_path']}")

    # Return success
    return 0

if __name__ == "__main__":
    sys.exit(main())
