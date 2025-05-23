package com.example.javaproject;

/**
 * Represents processed data with a value and length.
 */
public class ProcessedData {
    private final String value;
    private final int length;
    
    public ProcessedData(String value, int length) {
        this.value = value;
        this.length = length;
    }
    
    public String getValue() {
        return value;
    }
    
    public int getLength() {
        return length;
    }
    
    @Override
    public String toString() {
        return "ProcessedData{value='" + value + "', length=" + length + '}';
    }
}
