package com.example.app.repository;

import com.example.app.model.User;
import com.example.app.util.Logger;
import com.example.app.util.LogLevel;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Repository class for user data.
 */
public class UserRepository {
    private final String databaseUrl;
    private final Map<String, User> users;
    private final Logger logger;
    
    /**
     * Constructor for the UserRepository class.
     * 
     * @param databaseUrl The database URL
     */
    public UserRepository(String databaseUrl) {
        this.databaseUrl = databaseUrl;
        this.users = new HashMap<>();
        this.logger = new Logger(LogLevel.DEBUG);
        
        logger.log("Initialized UserRepository with database URL: " + databaseUrl);
    }
    
    /**
     * Saves a user.
     * 
     * @param user The user to save
     * @return The saved user
     */
    public User save(User user) {
        logger.log("Saving user: " + user);
        users.put(user.getId(), user);
        return user;
    }
    
    /**
     * Finds a user by ID.
     * 
     * @param id The user ID
     * @return The user, or null if not found
     */
    public User findById(String id) {
        logger.log("Finding user by ID: " + id);
        return users.get(id);
    }
    
    /**
     * Finds all users.
     * 
     * @return A list of all users
     */
    public List<User> findAll() {
        logger.log("Finding all users");
        return new ArrayList<>(users.values());
    }
    
    /**
     * Updates a user.
     * 
     * @param user The user to update
     * @return The updated user
     */
    public User update(User user) {
        logger.log("Updating user: " + user);
        if (users.containsKey(user.getId())) {
            users.put(user.getId(), user);
            return user;
        }
        return null;
    }
    
    /**
     * Deletes a user by ID.
     * 
     * @param id The user ID
     */
    public void delete(String id) {
        logger.log("Deleting user with ID: " + id);
        users.remove(id);
    }
}
