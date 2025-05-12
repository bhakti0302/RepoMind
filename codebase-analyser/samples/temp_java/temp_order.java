package com.example.testshreya;

import java.util.Date;

/**
 * Order entity representing a user order
 */
public class Order extends AbstractEntity {
    private String orderNumber;
    private Date orderDate;
    private double totalAmount;
    private User user;
    
    public Order(String orderNumber, User user, double totalAmount) {
        super();
        this.orderNumber = orderNumber;
        this.orderDate = new Date();
        this.totalAmount = totalAmount;
        this.user = user;
        user.addOrder(this);
    }
    
    public String getOrderNumber() {
        return orderNumber;
    }
    
    public Date getOrderDate() {
        return orderDate;
    }
    
    public double getTotalAmount() {
        return totalAmount;
    }
    
    public User getUser() {
        return user;
    }
    
    @Override
    public boolean isValid() {
        return super.isValid() && totalAmount > 0;
    }
}
