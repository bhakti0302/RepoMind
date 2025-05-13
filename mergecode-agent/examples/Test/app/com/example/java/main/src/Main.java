import java.util.List;
import java.util.ArrayList;

/**
 * Main class that demonstrates the usage of DataProcessor.
 */
public class Main {
    
    public static void main(String[] args) {
        // Create sample data
        List<String> data = new ArrayList<>();
        data.add("Hello");
        data.add("World");
        data.add("Java");
        data.add("Programming");
        
        // Create processor
        DataProcessorTest processor = new DataProcessorTest();
        
        // Process data
        List<ProcessedDataTest> results = processor.processData(data);
        
        // Print results
        System.out.println("Processed Results:");
        for (ProcessedDataTest result : results) {
            System.out.println(result);
        }
        
        // Calculate total length
        int totalLength = processor.calculateTotalLength(data);
        System.out.println("\nTotal length: " + totalLength);
        
        // Filter by length
        List<String> filtered = processor.filterByLength(data, 5);
        System.out.println("\nFiltered items (length >= 5):");
        for (String item : filtered) {
            System.out.println(item);
        }
    }
}