package com.example.complexproject;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;

/**
 * A complex Java project with multiple classes, interfaces, and dependencies
 * to demonstrate the codebase analysis capabilities.
 */
public class ComplexJavaProject {
    private final DataProcessor dataProcessor;
    private final ConfigManager configManager;
    private final Logger logger;
    private final Map<String, Module> modules;
    
    /**
     * Constructor for the ComplexJavaProject.
     * 
     * @param configPath Path to the configuration file
     */
    public ComplexJavaProject(String configPath) {
        this.configManager = new ConfigManager(configPath);
        this.logger = new Logger(configManager.getLogLevel());
        this.dataProcessor = new DataProcessor(logger);
        this.modules = new HashMap<>();
        
        logger.log(LogLevel.INFO, "ComplexJavaProject initialized");
    }
    
    /**
     * Initializes the project with the specified modules.
     * 
     * @param moduleNames List of module names to initialize
     * @return Number of successfully initialized modules
     */
    public int initializeModules(List<String> moduleNames) {
        logger.log(LogLevel.INFO, "Initializing modules: " + String.join(", ", moduleNames));
        
        int successCount = 0;
        for (String moduleName : moduleNames) {
            try {
                Module module = ModuleFactory.createModule(moduleName, configManager);
                modules.put(moduleName, module);
                module.initialize();
                successCount++;
                logger.log(LogLevel.INFO, "Module initialized: " + moduleName);
            } catch (ModuleInitializationException e) {
                logger.log(LogLevel.ERROR, "Failed to initialize module: " + moduleName + " - " + e.getMessage());
            }
        }
        
        return successCount;
    }
    
    /**
     * Processes data using the initialized modules.
     * 
     * @param inputData The input data to process
     * @return Processed data
     */
    public List<ProcessedData> processData(List<RawData> inputData) {
        logger.log(LogLevel.INFO, "Processing " + inputData.size() + " data items");
        
        // Pre-process data
        List<RawData> filteredData = dataProcessor.filterData(inputData);
        logger.log(LogLevel.DEBUG, "Filtered data: " + filteredData.size() + " items");
        
        // Process data through each module
        List<ProcessedData> results = new ArrayList<>();
        for (Module module : modules.values()) {
            if (module.isActive()) {
                List<ProcessedData> moduleResults = module.process(filteredData);
                results.addAll(moduleResults);
                logger.log(LogLevel.DEBUG, "Module " + module.getName() + " processed " + moduleResults.size() + " items");
            }
        }
        
        // Post-process results
        List<ProcessedData> finalResults = dataProcessor.aggregateResults(results);
        logger.log(LogLevel.INFO, "Processing complete, produced " + finalResults.size() + " results");
        
        return finalResults;
    }
    
    /**
     * Saves the processed data to the specified output path.
     * 
     * @param data The processed data to save
     * @param outputPath The path to save the data to
     * @return True if the data was saved successfully, false otherwise
     */
    public boolean saveResults(List<ProcessedData> data, String outputPath) {
        try {
            String serializedData = data.stream()
                .map(ProcessedData::serialize)
                .collect(Collectors.joining("\n"));
            
            Files.write(Paths.get(outputPath), serializedData.getBytes());
            logger.log(LogLevel.INFO, "Results saved to " + outputPath);
            return true;
        } catch (IOException e) {
            logger.log(LogLevel.ERROR, "Failed to save results: " + e.getMessage());
            return false;
        }
    }
    
    /**
     * Shuts down the project and releases resources.
     */
    public void shutdown() {
        logger.log(LogLevel.INFO, "Shutting down ComplexJavaProject");
        
        for (Module module : modules.values()) {
            try {
                module.shutdown();
                logger.log(LogLevel.DEBUG, "Module " + module.getName() + " shut down");
            } catch (Exception e) {
                logger.log(LogLevel.ERROR, "Error shutting down module " + module.getName() + ": " + e.getMessage());
            }
        }
        
        modules.clear();
        logger.log(LogLevel.INFO, "ComplexJavaProject shut down");
    }
    
    /**
     * Main method to demonstrate the usage of ComplexJavaProject.
     */
    public static void main(String[] args) {
        if (args.length < 2) {
            System.out.println("Usage: java ComplexJavaProject <configPath> <outputPath>");
            return;
        }
        
        String configPath = args[0];
        String outputPath = args[1];
        
        ComplexJavaProject project = new ComplexJavaProject(configPath);
        
        List<String> moduleNames = List.of("DataAnalyzer", "Visualizer", "Reporter");
        project.initializeModules(moduleNames);
        
        List<RawData> inputData = generateSampleData();
        List<ProcessedData> results = project.processData(inputData);
        
        project.saveResults(results, outputPath);
        project.shutdown();
    }
    
    /**
     * Generates sample data for demonstration purposes.
     */
    private static List<RawData> generateSampleData() {
        List<RawData> data = new ArrayList<>();
        for (int i = 0; i < 100; i++) {
            data.add(new RawData("Item" + i, Math.random() * 100));
        }
        return data;
    }
}

/**
 * Interface for modules that can process data.
 */
interface Module {
    /**
     * Gets the name of the module.
     */
    String getName();
    
    /**
     * Initializes the module.
     */
    void initialize() throws ModuleInitializationException;
    
    /**
     * Checks if the module is active.
     */
    boolean isActive();
    
    /**
     * Processes the input data.
     */
    List<ProcessedData> process(List<RawData> data);
    
    /**
     * Shuts down the module.
     */
    void shutdown();
}

/**
 * Factory for creating module instances.
 */
class ModuleFactory {
    /**
     * Creates a module instance based on the module name.
     */
    public static Module createModule(String moduleName, ConfigManager configManager) throws ModuleInitializationException {
        switch (moduleName) {
            case "DataAnalyzer":
                return new DataAnalyzerModule(configManager);
            case "Visualizer":
                return new VisualizerModule(configManager);
            case "Reporter":
                return new ReporterModule(configManager);
            default:
                throw new ModuleInitializationException("Unknown module: " + moduleName);
        }
    }
}

/**
 * Data analyzer module implementation.
 */
class DataAnalyzerModule implements Module {
    private final ConfigManager configManager;
    private boolean active;
    
    public DataAnalyzerModule(ConfigManager configManager) {
        this.configManager = configManager;
        this.active = false;
    }
    
    @Override
    public String getName() {
        return "DataAnalyzer";
    }
    
    @Override
    public void initialize() throws ModuleInitializationException {
        // Initialization logic
        this.active = true;
    }
    
    @Override
    public boolean isActive() {
        return active;
    }
    
    @Override
    public List<ProcessedData> process(List<RawData> data) {
        return data.stream()
            .map(raw -> new ProcessedData(raw.getName(), raw.getValue() * 2, "analyzed"))
            .collect(Collectors.toList());
    }
    
    @Override
    public void shutdown() {
        this.active = false;
    }
}

/**
 * Visualizer module implementation.
 */
class VisualizerModule implements Module {
    private final ConfigManager configManager;
    private boolean active;
    
    public VisualizerModule(ConfigManager configManager) {
        this.configManager = configManager;
        this.active = false;
    }
    
    @Override
    public String getName() {
        return "Visualizer";
    }
    
    @Override
    public void initialize() throws ModuleInitializationException {
        // Initialization logic
        this.active = true;
    }
    
    @Override
    public boolean isActive() {
        return active;
    }
    
    @Override
    public List<ProcessedData> process(List<RawData> data) {
        return data.stream()
            .map(raw -> new ProcessedData(raw.getName(), raw.getValue(), "visualized"))
            .collect(Collectors.toList());
    }
    
    @Override
    public void shutdown() {
        this.active = false;
    }
}

/**
 * Reporter module implementation.
 */
class ReporterModule implements Module {
    private final ConfigManager configManager;
    private boolean active;
    
    public ReporterModule(ConfigManager configManager) {
        this.configManager = configManager;
        this.active = false;
    }
    
    @Override
    public String getName() {
        return "Reporter";
    }
    
    @Override
    public void initialize() throws ModuleInitializationException {
        // Initialization logic
        this.active = true;
    }
    
    @Override
    public boolean isActive() {
        return active;
    }
    
    @Override
    public List<ProcessedData> process(List<RawData> data) {
        return data.stream()
            .map(raw -> new ProcessedData(raw.getName(), raw.getValue(), "reported"))
            .collect(Collectors.toList());
    }
    
    @Override
    public void shutdown() {
        this.active = false;
    }
}

/**
 * Exception thrown when a module fails to initialize.
 */
class ModuleInitializationException extends Exception {
    public ModuleInitializationException(String message) {
        super(message);
    }
}

/**
 * Configuration manager for the project.
 */
class ConfigManager {
    private final String configPath;
    private final Map<String, String> config;
    
    public ConfigManager(String configPath) {
        this.configPath = configPath;
        this.config = new HashMap<>();
        loadConfig();
    }
    
    private void loadConfig() {
        // Simulate loading configuration
        config.put("logLevel", "INFO");
        config.put("dataProcessor.filterThreshold", "10.0");
    }
    
    public LogLevel getLogLevel() {
        String level = config.getOrDefault("logLevel", "INFO");
        return LogLevel.valueOf(level);
    }
    
    public double getFilterThreshold() {
        String threshold = config.getOrDefault("dataProcessor.filterThreshold", "0.0");
        return Double.parseDouble(threshold);
    }
}

/**
 * Logger for the project.
 */
class Logger {
    private final LogLevel level;
    
    public Logger(LogLevel level) {
        this.level = level;
    }
    
    public void log(LogLevel messageLevel, String message) {
        if (messageLevel.ordinal() >= level.ordinal()) {
            System.out.println("[" + messageLevel + "] " + message);
        }
    }
}

/**
 * Log levels for the logger.
 */
enum LogLevel {
    DEBUG, INFO, WARNING, ERROR
}

/**
 * Data processor for filtering and aggregating data.
 */
class DataProcessor {
    private final Logger logger;
    
    public DataProcessor(Logger logger) {
        this.logger = logger;
    }
    
    public List<RawData> filterData(List<RawData> data) {
        return data.stream()
            .filter(item -> item.getValue() > 10.0)
            .collect(Collectors.toList());
    }
    
    public List<ProcessedData> aggregateResults(List<ProcessedData> results) {
        Map<String, List<ProcessedData>> groupedByType = results.stream()
            .collect(Collectors.groupingBy(ProcessedData::getType));
        
        List<ProcessedData> aggregated = new ArrayList<>();
        for (Map.Entry<String, List<ProcessedData>> entry : groupedByType.entrySet()) {
            String type = entry.getKey();
            List<ProcessedData> items = entry.getValue();
            
            double sum = items.stream().mapToDouble(ProcessedData::getValue).sum();
            aggregated.add(new ProcessedData("Aggregated_" + type, sum, type));
        }
        
        return aggregated;
    }
}

/**
 * Raw data class representing input data.
 */
class RawData {
    private final String name;
    private final double value;
    
    public RawData(String name, double value) {
        this.name = name;
        this.value = value;
    }
    
    public String getName() {
        return name;
    }
    
    public double getValue() {
        return value;
    }
}

/**
 * Processed data class representing output data.
 */
class ProcessedData {
    private final String name;
    private final double value;
    private final String type;
    
    public ProcessedData(String name, double value, String type) {
        this.name = name;
        this.value = value;
        this.type = type;
    }
    
    public String getName() {
        return name;
    }
    
    public double getValue() {
        return value;
    }
    
    public String getType() {
        return type;
    }
    
    public String serialize() {
        return name + "," + value + "," + type;
    }
}
