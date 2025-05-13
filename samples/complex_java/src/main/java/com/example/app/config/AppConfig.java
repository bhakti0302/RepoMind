package com.example.app.config;

/**
 * Configuration class for the application.
 */
public class AppConfig {
    private final String databaseUrl;
    private final String username;
    private final String password;
    private final int connectionPoolSize;
    private final int timeout;
    
    /**
     * Constructor with default connection pool size and timeout.
     * 
     * @param databaseUrl The database URL
     * @param username The database username
     * @param password The database password
     */
    public AppConfig(String databaseUrl, String username, String password) {
        this(databaseUrl, username, password, 10, 30000);
    }
    
    /**
     * Constructor with all parameters.
     * 
     * @param databaseUrl The database URL
     * @param username The database username
     * @param password The database password
     * @param connectionPoolSize The connection pool size
     * @param timeout The timeout in milliseconds
     */
    public AppConfig(String databaseUrl, String username, String password, int connectionPoolSize, int timeout) {
        this.databaseUrl = databaseUrl;
        this.username = username;
        this.password = password;
        this.connectionPoolSize = connectionPoolSize;
        this.timeout = timeout;
    }
    
    /**
     * Gets the database URL.
     * 
     * @return The database URL
     */
    public String getDatabaseUrl() {
        return databaseUrl;
    }
    
    /**
     * Gets the database username.
     * 
     * @return The database username
     */
    public String getUsername() {
        return username;
    }
    
    /**
     * Gets the database password.
     * 
     * @return The database password
     */
    public String getPassword() {
        return password;
    }
    
    /**
     * Gets the connection pool size.
     * 
     * @return The connection pool size
     */
    public int getConnectionPoolSize() {
        return connectionPoolSize;
    }
    
    /**
     * Gets the timeout.
     * 
     * @return The timeout in milliseconds
     */
    public int getTimeout() {
        return timeout;
    }
    
    @Override
    public String toString() {
        return "AppConfig{" +
                "databaseUrl='" + databaseUrl + '\'' +
                ", username='" + username + '\'' +
                ", password='********'" +
                ", connectionPoolSize=" + connectionPoolSize +
                ", timeout=" + timeout +
                '}';
    }
}
