/**
 * Base entity class that all domain entities will extend
 */
public abstract class BaseEntity {
    private String id;
    
    public BaseEntity() {
        this.id = java.util.UUID.randomUUID().toString();
    }
    
    public String getId() {
        return id;
    }
}
