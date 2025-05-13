package com.example.javaproject;

/**
 * Simple logger for logging messages.
 */
public class Logger {
    private final LogLevel level;
    
    public Logger(LogLevel level) {
        this.level = level;
    }
    
    public void log(String message) {
        System.out.println("[" + level + "] " + message);
    }
    
    public void debug(String message) {
        if (level == LogLevel.DEBUG) {
            System.out.println("[DEBUG] " + message);
        }
    }
    
    public void error(String message) {
        System.err.println("[ERROR] " + message);
    }
}
