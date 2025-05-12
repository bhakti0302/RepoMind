package com.example.testshreya;

/**
 * Base entity interface that defines common operations
 */
public interface Entity {
    /**
     * Get the unique identifier
     */
    String getId();
    
    /**
     * Check if the entity is valid
     */
    boolean isValid();
}
