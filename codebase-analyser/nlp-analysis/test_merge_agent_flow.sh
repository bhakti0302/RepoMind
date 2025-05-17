#!/bin/bash

# Test script to verify the Merge Agent flow

# Create a sample LLM instructions file
SAMPLE_INSTRUCTIONS_FILE="/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/output/LLM-instructions.txt"
TARGET_PROJECT="/Users/bhaktichindhe/Desktop/Project/EmployeeManagementSystem"

# Create logs directory if it doesn't exist
LOGS_DIR="/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/logs"
mkdir -p "$LOGS_DIR"

# Create a log file with timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$LOGS_DIR/test_merge_agent_$TIMESTAMP.log"
echo "Logging to: $LOG_FILE"

# Create the output directory if it doesn't exist
OUTPUT_DIR="/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/output"
mkdir -p "$OUTPUT_DIR"

# Create a sample LLM instructions file
echo "Creating sample LLM instructions file: $SAMPLE_INSTRUCTIONS_FILE" | tee -a "$LOG_FILE"
cat > "$SAMPLE_INSTRUCTIONS_FILE" << 'EOL'
Create a new file called Employee.java in the src directory with the following content:

```java
package com.employee;

import java.util.Date;

public class Employee {
    private int id;
    private String name;
    private String department;
    private double salary;
    private Date hireDate;

    public Employee(int id, String name, String department, double salary, Date hireDate) {
        this.id = id;
        this.name = name;
        this.department = department;
        this.salary = salary;
        this.hireDate = hireDate;
    }

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getDepartment() {
        return department;
    }

    public void setDepartment(String department) {
        this.department = department;
    }

    public double getSalary() {
        return salary;
    }

    public void setSalary(double salary) {
        this.salary = salary;
    }

    public Date getHireDate() {
        return hireDate;
    }

    public void setHireDate(Date hireDate) {
        this.hireDate = hireDate;
    }

    @Override
    public String toString() {
        return "Employee{" +
                "id=" + id +
                ", name='" + name + '\'' +
                ", department='" + department + '\'' +
                ", salary=" + salary +
                ", hireDate=" + hireDate +
                '}';
    }
}
```
EOL

# Create the target project directory if it doesn't exist
if [ ! -d "$TARGET_PROJECT" ]; then
    echo "Creating target project directory: $TARGET_PROJECT" | tee -a "$LOG_FILE"
    mkdir -p "$TARGET_PROJECT"
fi

# Create the src directory in the target project
mkdir -p "$TARGET_PROJECT/src"

# Run the Merge Agent
echo "Running Merge Agent with sample instructions..." | tee -a "$LOG_FILE"
cd /Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/nlp-analysis
./run_merge_agent.sh 2>&1 | tee -a "$LOG_FILE"

# Check if the Merge Agent ran successfully
if [ $? -eq 0 ]; then
    echo "Merge Agent completed successfully!" | tee -a "$LOG_FILE"

    # Check if the file was created
    if [ -f "$TARGET_PROJECT/src/Employee.java" ]; then
        echo "Test passed! Employee.java was created successfully." | tee -a "$LOG_FILE"
        echo "File content:" | tee -a "$LOG_FILE"
        cat "$TARGET_PROJECT/src/Employee.java" | tee -a "$LOG_FILE"
    else
        echo "Test failed! Employee.java was not created." | tee -a "$LOG_FILE"
    fi
else
    echo "Merge Agent failed! Check the log file for details: $LOG_FILE" | tee -a "$LOG_FILE"
fi
