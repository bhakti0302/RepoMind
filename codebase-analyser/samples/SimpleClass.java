package com.example.test;

import java.util.List;
import java.util.ArrayList;
import java.io.IOException;

/**
 * A simple Java class for testing the Tree-sitter parser
 */
public class SimpleClass extends BaseClass implements TestInterface {
    // Fields
    private String name;
    private int count;
    protected List<String> items;
    public static final String VERSION = "1.0.0";
    
    /**
     * Default constructor
     */
    public SimpleClass() {
        this.name = "Default";
        this.count = 0;
        this.items = new ArrayList<>();
    }
    
    /**
     * Constructor with parameters
     */
    public SimpleClass(String name, int count) {
        this.name = name;
        this.count = count;
        this.items = new ArrayList<>();
    }
    
    /**
     * Get the name
     */
    public String getName() {
        return name;
    }
    
    /**
     * Set the name
     */
    public void setName(String name) {
        this.name = name;
    }
    
    /**
     * Get the count
     */
    public int getCount() {
        return count;
    }
    
    /**
     * Set the count
     */
    public void setCount(int count) {
        this.count = count;
    }
    
    /**
     * Add an item to the list
     */
    public void addItem(String item) {
        items.add(item);
    }
    
    /**
     * Get all items
     */
    public List<String> getItems() {
        return items;
    }
    
    /**
     * Process items with exception handling
     */
    public void processItems() throws IOException {
        for (String item : items) {
            if (item == null) {
                throw new IOException("Null item found");
            }
            System.out.println("Processing: " + item);
        }
    }
    
    /**
     * Static utility method
     */
    public static int calculateSum(int a, int b) {
        return a + b;
    }
    
    /**
     * Main method for testing
     */
    public static void main(String[] args) {
        SimpleClass obj = new SimpleClass("Test", 5);
        obj.addItem("Item 1");
        obj.addItem("Item 2");
        
        System.out.println("Name: " + obj.getName());
        System.out.println("Count: " + obj.getCount());
        System.out.println("Items: " + obj.getItems());
        
        try {
            obj.processItems();
        } catch (IOException e) {
            System.err.println("Error: " + e.getMessage());
        }
        
        System.out.println("Sum: " + calculateSum(10, 20));
    }
}

/**
 * Base class for testing inheritance
 */
class BaseClass {
    protected String baseField;
    
    public BaseClass() {
        this.baseField = "Base";
    }
    
    public String getBaseField() {
        return baseField;
    }
}

/**
 * Interface for testing implementation
 */
interface TestInterface {
    void processItems() throws IOException;
}
