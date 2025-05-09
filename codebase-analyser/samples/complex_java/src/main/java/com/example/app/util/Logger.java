package com.example.app.util;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

/**
 * Simple logger for logging messages.
 */
public class Logger {
    private final LogLevel level;
    private final DateTimeFormatter formatter;
    
    /**
     * Constructor for the Logger class.
     * 
     * @param level The log level
     */
    public Logger(LogLevel level) {
        this.level = level;
        this.formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
    }
    
    /**
     * Logs a message.
     * 
     * @param message The message to log
     */
    public void log(String message) {
        System.out.println(getTimestamp() + " [" + level + "] " + message);
    }
    
    /**
     * Logs a debug message.
     * 
     * @param message The message to log
     */
    public void debug(String message) {
        if (level == LogLevel.DEBUG) {
            System.out.println(getTimestamp() + " [DEBUG] " + message);
        }
    }
    
    /**
     * Logs an error message.
     * 
     * @param message The message to log
     */
    public void error(String message) {
        System.err.println(getTimestamp() + " [ERROR] " + message);
    }
    
    /**
     * Gets the current timestamp.
     * 
     * @return The current timestamp
     */
    private String getTimestamp() {
        return LocalDateTime.now().format(formatter);
    }
}
