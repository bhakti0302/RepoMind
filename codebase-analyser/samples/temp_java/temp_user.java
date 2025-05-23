package com.example.testshreya;

import java.util.ArrayList;
import java.util.List;

/**
 * User entity representing a system user
 */
public class User extends AbstractEntity {
    private String username;
    private String email;
    private List<Order> orders;
    private Address address;
    
    public User(String username, String email) {
        super();
        this.username = username;
        this.email = email;
        this.orders = new ArrayList<>();
    }
    
    public String getUsername() {
        return username;
    }
    
    public String getEmail() {
        return email;
    }
    
    public void addOrder(Order order) {
        this.orders.add(order);
    }
    
    public List<Order> getOrders() {
        return orders;
    }
    
    public void setAddress(Address address) {
        this.address = address;
    }
    
    public Address getAddress() {
        return address;
    }
}
