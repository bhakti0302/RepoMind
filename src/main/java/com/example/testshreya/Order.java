package com.example.testshreya;

import java.util.ArrayList;
import java.util.List;

/**
 * Order entity that extends BaseEntity
 */
public class Order extends BaseEntity {
    private User user;
    private OrderStatus status;
    private List<Product> products;
    
    public Order(User user) {
        super();
        this.user = user;
        this.status = OrderStatus.PENDING;
        this.products = new ArrayList<>();
        
        // Add this order to the user's orders
        user.addOrder(this);
    }
    
    public User getUser() {
        return user;
    }
    
    public OrderStatus getStatus() {
        return status;
    }
    
    public void setStatus(OrderStatus status) {
        this.status = status;
    }
    
    public List<Product> getProducts() {
        return products;
    }
    
    public void addProduct(Product product) {
        this.products.add(product);
    }
}
