package com.example.testshreya;

import java.util.ArrayList;
import java.util.List;

/**
 * User entity that extends BaseEntity
 */
public class User extends BaseEntity {
    private String username;
    private List<Order> orders;
    
    public User(String username) {
        super();
        this.username = username;
        this.orders = new ArrayList<>();
    }
    
    public String getUsername() {
        return username;
    }
    
    public List<Order> getOrders() {
        return orders;
    }
    
    public void addOrder(Order order) {
        this.orders.add(order);
    }
}
