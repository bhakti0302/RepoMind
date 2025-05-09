import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.List;

/**
 * CSVExporter class responsible for exporting data to a CSV file.
 */
public class CSVExporter {

    /**
     * Exports data to a CSV file.
     * 
     * @param filePath the path to the CSV file
     * @param data     the data to be exported (each sublist represents a row)
     * @throws IOException if an I/O error occurs
     */
    public void exportToCSV(String filePath, List<List<String>> data) throws IOException {
        try (PrintWriter writer = new PrintWriter(new FileWriter(filePath))) {
            // Write each row to the CSV file
            for (List<String> row : data) {
                // Join the row elements with a comma and write to the file
                writer.println(String.join(",", row));
            }
        }
    }

    /**
     * Exports a single row to a CSV file (appends if file already exists).
     * 
     * @param filePath the path to the CSV file
     * @param row     the row data to be exported
     * @throws IOException if an I/O error occurs
     */
    public void appendRowToCSV(String filePath, List<String> row) throws IOException {
        try (PrintWriter writer = new PrintWriter(new FileWriter(filePath, true))) {
            // Join the row elements with a comma and append to the file
            writer.println(String.join(",", row));
        }
    }

    /**
     * Example usage of the CSVExporter class.
     * 
     * @param args command line arguments (not used)
     * @throws IOException if an I/O error occurs
     */
    public static void main(String[] args) throws IOException {
        CSVExporter exporter = new CSVExporter();
        
        // Example data
        List<List<String>> data = List.of(
            List.of("Name", "Age", "Country"),
            List.of("John Doe", "25", "USA"),
            List.of("Jane Doe", "30", "Canada")
        );
        
        // Export data to a CSV file
        exporter.exportToCSV("example.csv", data);
        
        // Append a new row to the existing CSV file
        exporter.appendRowToCSV("example.csv", List.of("Bob Smith", "35", "Mexico"));
    }
}