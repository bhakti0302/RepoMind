import java.util.List;
import java.util.ArrayList;

/**
 * Processes data and returns results.
 */
public class DataProcessorTest {
    
    /**
     * Processes a list of string data and returns processed results.
     * 
     * @param data The list of strings to process
     * @return A list of processed data objects
     */
    public List<ProcessedDataTest> processData(List<String> data) {
        List<ProcessedDataTest> results = new ArrayList<>();
        
        for (String item : data) {
            ProcessedDataTest processedItem = new ProcessedDataTest(item, item.length());
            results.add(processedItem);
        }
        
        return results;
    }
    
    /**
     * Calculates the total length of all strings in the data list.
     * 
     * @param data The list of strings to calculate length for
     * @return The total length of all strings
     */
    public int calculateTotalLength(List<String> data) {
        int total = 0;
        for (String item : data) {
            total += item.length();
        }
        return total;
    }
    
    /**
     * Filters data items that are longer than the specified minimum length.
     * 
     * @param data The list of strings to filter
     * @param minLength The minimum length threshold
     * @return A filtered list of strings
     */
    public List<String> filterByLength(List<String> data, int minLength) {
        List<String> filtered = new ArrayList<>();
        
        for (String item : data) {
            if (item.length() >= minLength) {
                filtered.add(item);
            }
        }
        
        return filtered;
    }
}
