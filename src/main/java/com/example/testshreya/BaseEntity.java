package com.example.testshreya;

import java.util.UUID;

/**
 * Base entity class that all domain entities will extend
 */
public abstract class BaseEntity {
    private UUID id;
    
    public BaseEntity() {
        this.id = UUID.randomUUID();
    }
    
    public UUID getId() {
        return id;
    }
}
