
import java.util.List;
import java.util.ArrayList;

/**
 * Processes data and returns results.
 */
public class DataProcessor {
    
    public List<ProcessedDataTest> processData(List<String> data) {
        List<ProcessedDataTest> results = new ArrayList<>();
        
        for (String item : data) {
            ProcessedDataTest processedItem = new ProcessedDataTest(item, item.length());
            results.add(processedItem);
        }
        
        return results;
    }
    
    public int calculateTotalLength(List<String> data) {
        int total = 0;
        for (String item : data) {
            total += item.length();
        }
        return total;
    }
}
