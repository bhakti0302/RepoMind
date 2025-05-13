package com.example.testshreya;

import java.util.UUID;

/**
 * Abstract base class that implements the Entity interface
 */
public abstract class AbstractEntity implements Entity {
    private final String id;
    private boolean valid;
    
    public AbstractEntity() {
        this.id = UUID.randomUUID().toString();
        this.valid = true;
    }
    
    @Override
    public String getId() {
        return id;
    }
    
    @Override
    public boolean isValid() {
        return valid;
    }
    
    protected void invalidate() {
        this.valid = false;
    }
    
    protected void validate() {
        this.valid = true;
    }
}
