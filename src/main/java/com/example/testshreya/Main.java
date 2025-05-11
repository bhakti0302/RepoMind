package com.example.testshreya;

/**
 * Main class to demonstrate the relationships between entities
 */
public class Main {
    public static void main(String[] args) {
        // Create a user
        User user = new User("johndoe");
        
        // Create some products
        Product laptop = new Product("Laptop", 1299.99);
        Product tShirt = new Product("T-Shirt", 19.99);
        Product book = new Product("Java Programming", 49.99);
        
        // Create an order for the user
        Order order = new Order(user);
        
        // Add products to the order
        order.addProduct(laptop);
        order.addProduct(tShirt);
        order.addProduct(book);
        
        // Update order status
        order.setStatus(OrderStatus.PROCESSING);
        
        // Print user's orders
        System.out.println("User " + user.getUsername() + " has " + user.getOrders().size() + " orders.");
    }
}
