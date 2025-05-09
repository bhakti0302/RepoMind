package com.example.javaproject;

import java.util.List;
import java.util.ArrayList;

/**
 * Main class that demonstrates dependencies between classes.
 */
public class Main {
    private final DataProcessor processor;
    private final Logger logger;
    
    public Main() {
        this.processor = new DataProcessor();
        this.logger = new Logger(LogLevel.INFO);
    }
    
    public void run() {
        logger.log("Starting application");
        
        List<String> data = new ArrayList<>();
        data.add("Item 1");
        data.add("Item 2");
        data.add("Item 3");
        
        List<ProcessedData> results = processor.processData(data);
        
        for (ProcessedData result : results) {
            logger.log("Processed: " + result.getValue());
        }
        
        logger.log("Application completed");
    }
    
    public static void main(String[] args) {
        Main app = new Main();
        app.run();
    }
}
