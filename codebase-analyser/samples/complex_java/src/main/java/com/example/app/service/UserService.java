package com.example.app.service;

import com.example.app.model.User;
import com.example.app.repository.UserRepository;
import com.example.app.util.Logger;
import com.example.app.util.LogLevel;

import java.util.List;

/**
 * Service class for user operations.
 */
public class UserService {
    private final UserRepository userRepository;
    private final Logger logger;
    
    /**
     * Constructor for the UserService class.
     * 
     * @param userRepository The user repository
     */
    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
        this.logger = new Logger(LogLevel.DEBUG);
    }
    
    /**
     * Creates a new user.
     * 
     * @param user The user to create
     * @return The created user
     */
    public User createUser(User user) {
        logger.log("Creating user: " + user);
        return userRepository.save(user);
    }
    
    /**
     * Gets a user by ID.
     * 
     * @param id The user ID
     * @return The user, or null if not found
     */
    public User getUserById(String id) {
        logger.log("Getting user by ID: " + id);
        return userRepository.findById(id);
    }
    
    /**
     * Gets all users.
     * 
     * @return A list of all users
     */
    public List<User> getAllUsers() {
        logger.log("Getting all users");
        return userRepository.findAll();
    }
    
    /**
     * Updates a user.
     * 
     * @param user The user to update
     * @return The updated user
     */
    public User updateUser(User user) {
        logger.log("Updating user: " + user);
        return userRepository.update(user);
    }
    
    /**
     * Deletes a user by ID.
     * 
     * @param id The user ID
     */
    public void deleteUser(String id) {
        logger.log("Deleting user with ID: " + id);
        userRepository.delete(id);
    }
}
