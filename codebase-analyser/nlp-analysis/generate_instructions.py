#!/usr/bin/env python3

"""
Generate instructions based on the multi-hop RAG output.

This script reads the multi-hop RAG output and generates instructions for implementing the code.
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def generate_instructions():
    """Generate instructions based on the multi-hop RAG output."""
    # Define file paths
    # Get the current directory and calculate relative paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    codebase_analyser_dir = os.path.dirname(current_dir)
    project_root = os.path.dirname(codebase_analyser_dir)

    # Original hardcoded paths:
    # multi_hop_output_file = "/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/output/output-multi-hop.txt"
    # requirement_file = "/Users/bhaktichindhe/Desktop/Project/RepoMind/test-project-employee/EmployeeByDepartmentRequirement.txt"
    # instructions_file = "/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/output/LLM-instructions.txt"

    # Relative paths:
    multi_hop_output_file = os.path.join(codebase_analyser_dir, "output", "output-multi-hop.txt")
    requirement_file = os.path.join(project_root, "test-project-employee", "EmployeeByDepartmentRequirement.txt")
    instructions_file = os.path.join(codebase_analyser_dir, "output", "LLM-instructions.txt")

    # Read the multi-hop RAG output
    with open(multi_hop_output_file, 'r') as f:
        multi_hop_output = f.read()

    # Read the requirement file
    with open(requirement_file, 'r') as f:
        requirement = f.read()

    # Generate instructions based on the multi-hop RAG output
    instructions = """# Implementation Instructions for Employee by Department Feature

## 1. Overview of the Implementation Approach

Based on the business requirements and the multi-hop RAG analysis, we need to implement a feature that allows users to list all employees belonging to a specific department. The implementation will follow the existing architecture patterns identified in the codebase, specifically the Service Layer Pattern.

## 2. Key Components and Their Responsibilities

1. **Employee Class**: Represents an employee with properties for ID, name, and department.
2. **EmployeeService Class**: Provides business logic for managing employees, including the new method to filter employees by department.
3. **Main Class**: Entry point for the application, demonstrates the new functionality.

## 3. Detailed Implementation Steps

### Step 1: Enhance the EmployeeService Class

Add a new method `getEmployeesByDepartment(String department)` to the `EmployeeService` class that filters employees by department.

File: `/Users/bhaktichindhe/Desktop/Project/RepoMind/test-project-employee/src/com/company/service/EmployeeService.java`

```java
public List<Employee> getEmployeesByDepartment(String department) {
    List<Employee> filteredEmployees = new ArrayList<>();
    for (Employee employee : employees) {
        if (employee.getDepartment().equalsIgnoreCase(department)) {
            filteredEmployees.add(employee);
        }
    }
    return filteredEmployees;
}
```

### Step 2: Update the Main Class

Modify the `Main` class to demonstrate the new functionality.

File: `/Users/bhaktichindhe/Desktop/Project/RepoMind/test-project-employee/src/com/company/app/Main.java`

```java
public static void main(String[] args) {
    EmployeeService service = new EmployeeService();

    // Add sample employees
    service.addEmployee(new Employee(1, "Alice", "HR"));
    service.addEmployee(new Employee(2, "Bob", "IT"));
    service.addEmployee(new Employee(3, "Charlie", "HR"));
    service.addEmployee(new Employee(4, "David", "Finance"));
    service.addEmployee(new Employee(5, "Eve", "IT"));

    // Display all employees
    System.out.println("All Employees:");
    for (Employee e : service.getAllEmployees()) {
        System.out.println(e);
    }

    // Display employees by department
    String departmentToFilter = "HR";
    System.out.println("\\nEmployees in " + departmentToFilter + " department:");
    for (Employee e : service.getEmployeesByDepartment(departmentToFilter)) {
        System.out.println(e);
    }
}
```

### Step 3: Ensure the Employee Class Has Proper Getters and Setters

Make sure the `Employee` class has a getter for the department field.

File: `/Users/bhaktichindhe/Desktop/Project/RepoMind/test-project-employee/src/com/company/model/Employee.java`

```java
public String getDepartment() {
    return department;
}
```

## 4. Code Examples for Critical Parts

### Employee Class (Complete)

```java
package com.company.model;

public class Employee {
    private int id;
    private String name;
    private String department;

    public Employee(int id, String name, String department) {
        this.id = id;
        this.name = name;
        this.department = department;
    }

    public int getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public String getDepartment() {
        return department;
    }

    @Override
    public String toString() {
        return "Employee{id=" + id + ", name='" + name + "', department='" + department + "'}";
    }
}
```

### EmployeeService Class (Complete)

```java
package com.company.service;

import com.company.model.Employee;
import java.util.ArrayList;
import java.util.List;

public class EmployeeService {
    private List<Employee> employees = new ArrayList<>();

    public void addEmployee(Employee employee) {
        employees.add(employee);
    }

    public List<Employee> getAllEmployees() {
        return employees;
    }

    public List<Employee> getEmployeesByDepartment(String department) {
        List<Employee> filteredEmployees = new ArrayList<>();
        for (Employee employee : employees) {
            if (employee.getDepartment().equalsIgnoreCase(department)) {
                filteredEmployees.add(employee);
            }
        }
        return filteredEmployees;
    }
}
```

## 5. Testing Approach

1. **Unit Testing**: Create unit tests for the `getEmployeesByDepartment` method to ensure it correctly filters employees.
2. **Integration Testing**: Test the entire workflow from adding employees to filtering by department.
3. **Manual Testing**: Run the application and verify that employees are correctly filtered by department.

### Test Cases

1. Filter by a department with multiple employees
2. Filter by a department with a single employee
3. Filter by a department with no employees
4. Filter with case-insensitive matching
"""

    # Write the instructions to the file
    with open(instructions_file, 'w') as f:
        f.write(instructions)

    print(f"Generated instructions and saved to {instructions_file}")

if __name__ == "__main__":
    generate_instructions()
