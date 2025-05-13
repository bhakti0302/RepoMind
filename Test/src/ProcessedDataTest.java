/**
 * Represents processed data with a value and length.
 */
public class ProcessedDataTest {
    private final String value;
    private final int length;
    
    /**
     * Creates a new ProcessedData instance.
     * 
     * @param value The string value
     * @param length The length of the value
     */
    public ProcessedDataTest(String value, int length) {
        this.value = value;
        this.length = length;
    }
    
    /**
     * Gets the value of this processed data.
     * 
     * @return The string value
     */
    public String getValue() {
        return value;
    }
    
    /**
     * Gets the length of this processed data.
     * 
     * @return The length
     */
    public int getLength() {
        return length;
    }
    
    @Override
    public String toString() {
        return "ProcessedData{value='" + value + "', length=" + length + '}';
    }
}