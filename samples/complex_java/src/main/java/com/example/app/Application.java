package com.example.app;

import com.example.app.config.AppConfig;
import com.example.app.model.User;
import com.example.app.service.UserService;
import com.example.app.repository.UserRepository;
import com.example.app.util.Logger;
import com.example.app.util.LogLevel;

import java.util.List;

/**
 * Main application class that demonstrates a more complex Java application structure.
 */
public class Application {
    private final AppConfig config;
    private final UserService userService;
    private final Logger logger;
    
    /**
     * Constructor for the Application class.
     * 
     * @param config The application configuration
     */
    public Application(AppConfig config) {
        this.config = config;
        this.logger = new Logger(LogLevel.INFO);
        
        // Initialize repositories
        UserRepository userRepository = new UserRepository(config.getDatabaseUrl());
        
        // Initialize services
        this.userService = new UserService(userRepository);
        
        logger.log("Application initialized with config: " + config);
    }
    
    /**
     * Runs the application.
     */
    public void run() {
        logger.log("Starting application...");
        
        // Create some users
        userService.createUser(new User("user1", "John", "Doe", "john.doe@example.com"));
        userService.createUser(new User("user2", "Jane", "Smith", "jane.smith@example.com"));
        userService.createUser(new User("user3", "Bob", "Johnson", "bob.johnson@example.com"));
        
        // Get all users
        List<User> users = userService.getAllUsers();
        
        // Print users
        logger.log("Users:");
        for (User user : users) {
            logger.log("  - " + user);
        }
        
        // Find user by ID
        User user = userService.getUserById("user2");
        if (user != null) {
            logger.log("Found user: " + user);
            
            // Update user
            user.setEmail("jane.updated@example.com");
            userService.updateUser(user);
            logger.log("Updated user: " + user);
        }
        
        // Delete user
        userService.deleteUser("user3");
        
        // Get all users again
        users = userService.getAllUsers();
        
        // Print users
        logger.log("Users after deletion:");
        for (User user : users) {
            logger.log("  - " + user);
        }
        
        logger.log("Application completed");
    }
    
    /**
     * Main method to start the application.
     * 
     * @param args Command line arguments
     */
    public static void main(String[] args) {
        // Create configuration
        AppConfig config = new AppConfig("jdbc:mysql://localhost:3306/mydb", "username", "password");
        
        // Create and run application
        Application app = new Application(config);
        app.run();
    }
}
