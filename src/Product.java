/**
 * Product entity that extends BaseEntity
 */
public class Product extends BaseEntity {
    private String name;
    private double price;
    
    public Product(String name, double price) {
        super();
        this.name = name;
        this.price = price;
    }
    
    public String getName() {
        return name;
    }
    
    public double getPrice() {
        return price;
    }
}
