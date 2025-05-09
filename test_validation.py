#!/usr/bin/env python3
"""
Test script for code validation functionality.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add parent directory to path to import codebase_analyser
sys.path.append(str(Path(__file__).parent))

from codebase_analyser.agent.state import AgentState
from codebase_analyser.agent.nodes.validation_nodes import validate_code

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Sample code with issues
SAMPLE_JAVA_CODE_WITH_ISSUES = """
public class Person {
    private String name;
    private int age;
    
    // Missing constructor
    
    public String getName() {
        return name;
    }
    
    public void setName(String name) {
        this.name = name;
    }
    
    public int getAge() {
        return age;
    }
    
    public void setAge(int age) {
        // Missing validation for negative age
        this.age = age;
    }
    
    // TODO: Add toString method
    
    public void processData() {
        try {
            // Some code that might throw an exception
            String data = fetchData();
            processDataInternal(data);
        } catch (Exception e) {
            // Empty catch block
        }
    }
    
    private String fetchData() {
        // Hardcoded credentials
        String apiKey = "1234567890abcdef";
        String password = "secretpassword";
        
        return "data";
    }
    
    private void processDataInternal(String data) {
        // Implementation
    }
}
"""

# Sample code without issues
SAMPLE_JAVA_CODE_CLEAN = """
public class Person {
    private String name;
    private int age;
    
    public Person(String name, int age) {
        this.name = name;
        setAge(age);  // Use setter for validation
    }
    
    public String getName() {
        return name;
    }
    
    public void setName(String name) {
        this.name = name;
    }
    
    public int getAge() {
        return age;
    }
    
    public void setAge(int age) {
        if (age < 0) {
            throw new IllegalArgumentException("Age cannot be negative");
        }
        this.age = age;
    }
    
    @Override
    public String toString() {
        return "Person{name='" + name + "', age=" + age + '}';
    }
    
    public void processData() {
        try {
            // Some code that might throw an exception
            String data = fetchData();
            processDataInternal(data);
        } catch (Exception e) {
            System.err.println("Error processing data: " + e.getMessage());
        }
    }
    
    private String fetchData() {
        // Using environment variables for credentials
        String apiKey = System.getenv("API_KEY");
        String password = System.getenv("PASSWORD");
        
        return "data";
    }
    
    private void processDataInternal(String data) {
        // Implementation
    }
}
"""

async def test_validation():
    """Test the code validation functionality."""
    # Test code with issues
    logger.info("\n\n=== Testing validation with code that has issues ===")
    state_with_issues = AgentState(
        requirements="Create a Person class with name and age properties",
        processed_requirements={
            "intent": "create_class",
            "language": "java",
            "entities": {
                "classes": ["Person"],
                "properties": ["name", "age"]
            },
            "original_text": "Create a Person class with name and age properties"
        },
        generated_code=SAMPLE_JAVA_CODE_WITH_ISSUES
    )
    
    result_with_issues = await validate_code(state_with_issues)
    
    # Print validation result
    validation_result = result_with_issues["validation_result"]
    logger.info(f"Validation result: valid={validation_result.get('valid', False)}")
    
    # Print