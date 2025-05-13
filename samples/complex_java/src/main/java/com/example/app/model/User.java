package com.example.app.model;

import java.util.Objects;

/**
 * User model class.
 */
public class User {
    private final String id;
    private String firstName;
    private String lastName;
    private String email;
    
    /**
     * Constructor for the User class.
     * 
     * @param id The user ID
     * @param firstName The user's first name
     * @param lastName The user's last name
     * @param email The user's email
     */
    public User(String id, String firstName, String lastName, String email) {
        this.id = id;
        this.firstName = firstName;
        this.lastName = lastName;
        this.email = email;
    }
    
    /**
     * Gets the user ID.
     * 
     * @return The user ID
     */
    public String getId() {
        return id;
    }
    
    /**
     * Gets the user's first name.
     * 
     * @return The user's first name
     */
    public String getFirstName() {
        return firstName;
    }
    
    /**
     * Sets the user's first name.
     * 
     * @param firstName The user's first name
     */
    public void setFirstName(String firstName) {
        this.firstName = firstName;
    }
    
    /**
     * Gets the user's last name.
     * 
     * @return The user's last name
     */
    public String getLastName() {
        return lastName;
    }
    
    /**
     * Sets the user's last name.
     * 
     * @param lastName The user's last name
     */
    public void setLastName(String lastName) {
        this.lastName = lastName;
    }
    
    /**
     * Gets the user's email.
     * 
     * @return The user's email
     */
    public String getEmail() {
        return email;
    }
    
    /**
     * Sets the user's email.
     * 
     * @param email The user's email
     */
    public void setEmail(String email) {
        this.email = email;
    }
    
    /**
     * Gets the user's full name.
     * 
     * @return The user's full name
     */
    public String getFullName() {
        return firstName + " " + lastName;
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        User user = (User) o;
        return Objects.equals(id, user.id);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(id);
    }
    
    @Override
    public String toString() {
        return "User{" +
                "id='" + id + '\'' +
                ", firstName='" + firstName + '\'' +
                ", lastName='" + lastName + '\'' +
                ", email='" + email + '\'' +
                '}';
    }
}
