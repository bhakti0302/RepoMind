
/**
 * CSV exporter implementation.
 */
public class CsvExporterImpl implements DataExporter {
    private static final char DELIMITER = ',';
    private static final char QUOTE = '"';
    
    @Override
    public void export(List<Map<String, Object>> data, OutputStream output) throws IOException {
        try (BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(output))) {
            // Write header if data is not empty
            if (!data.isEmpty()) {
                Map<String, Object> firstRow = data.get(0);
                writeRow(writer, new ArrayList<>(firstRow.keySet()));
            }
            
            // Write data rows
            for (Map<String, Object> row : data) {
                writeRow(writer, new ArrayList<>(row.values()));
            }
            
            writer.flush();
        }
    }
    
    private void writeRow(BufferedWriter writer, List<?> values) throws IOException {
        StringBuilder sb = new StringBuilder();
        
        for (int i = 0; i < values.size(); i++) {
            if (i > 0) {
                sb.append(DELIMITER);
            }
            
            String value = values.get(i) != null ? values.get(i).toString() : "";
            sb.append(escapeValue(value));
        }
        
        writer.write(sb.toString());
        writer.newLine();
    }
    
    private String escapeValue(String value) {
        // Check if value needs quoting
        boolean needsQuoting = value.indexOf(DELIMITER) >= 0 
                            || value.indexOf(QUOTE) >= 0
                            || value.indexOf('\n') >= 0
                            || value.indexOf('\r') >= 0;
        
        if (!needsQuoting) {
            return value;
        }
        
        // Escape quotes by doubling them
        String escaped = value.replace(String.valueOf(QUOTE), String.valueOf(QUOTE) + String.valueOf(QUOTE));
        
        // Wrap in quotes
        return QUOTE + escaped + QUOTE;
    }
}
