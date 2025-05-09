"""
Test script for the updated agent implementation.
"""
import logging
import json
import os
import sys
import argparse
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Try to import the real run_agent function
try:
    from codebase_analyser.agent.graph import run_agent
    logger.info("Using real agent implementation")
    using_real_agent = True
except ImportError:
    logger.warning("Could not import real agent implementation, using mock")
    using_real_agent = False
    
    # Define a mock run_agent function
    def run_agent(requirements):
        """
        Temporary implementation of run_agent for testing.
        
        Args:
            requirements: The requirements to process
            
        Returns:
            A mock result
        """
        logger.info(f"Mock agent running with requirements: {requirements}")
        
        # Create a mock result
        result = {
            "code": """
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
                            || value.indexOf('\\n') >= 0
                            || value.indexOf('\\r') >= 0;
        
        if (!needsQuoting) {
            return value;
        }
        
        // Escape quotes by doubling them
        String escaped = value.replace(String.valueOf(QUOTE), String.valueOf(QUOTE) + String.valueOf(QUOTE));
        
        // Wrap in quotes
        return QUOTE + escaped + QUOTE;
    }
}
""",
            "file_path": requirements.get("file_path", "generated_code/output.txt"),
            "language": requirements.get("language", "unknown"),
            "validation_status": True,
            "metadata": {
                "requirements": requirements,
                "context_used": {
                    "architectural": ["arch1"],
                    "implementation": ["impl1", "impl2"]
                },
                "errors": [],
                "attempts": 1
            }
        }
        
        return result

def load_requirements_from_file(file_path):
    """Load requirements from a JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def main():
    """Run the test."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Test the agent implementation')
    parser.add_argument('--requirements', type=str, help='Path to a JSON file containing requirements')
    parser.add_argument('--output-dir', type=str, default='generated_code', help='Directory to save generated code')
    parser.add_argument('--force-mock', action='store_true', help='Force using the mock implementation')
    args = parser.parse_args()
    
    # Use mock implementation if requested
    global run_agent, using_real_agent
    if args.force_mock and using_real_agent:
        logger.info("Forcing mock implementation as requested")
        from test_updated_agent import run_agent as mock_run_agent
        run_agent = mock_run_agent
        using_real_agent = False
    
    # Load requirements from file or use default
    if args.requirements and os.path.exists(args.requirements):
        requirements = load_requirements_from_file(args.requirements)
        logger.info(f"Loaded requirements from {args.requirements}")
    else:
        # Define sample requirements
        requirements = {
            "description": "Create a CSV exporter that implements the DataExporter interface",
            "language": "java",
            "file_path": os.path.join(args.output_dir, "CsvExporterImpl.java"),
            "additional_context": "The exporter should handle escaping commas and quotes in the data."
        }
    
    # Update file path if output directory is specified
    if args.output_dir and "file_path" in requirements:
        file_name = os.path.basename(requirements["file_path"])
        requirements["file_path"] = os.path.join(args.output_dir, file_name)
    
    # Create the output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Run the agent
    logger.info("Running agent with requirements...")
    result = run_agent(requirements)
    
    # Print the result
    logger.info("Agent execution completed")
    logger.info(f"Validation status: {result['validation_status']}")
    
    # Save the generated code to a file
    if result.get("code"):
        file_path = result.get("file_path", os.path.join(args.output_dir, "output.txt"))
        with open(file_path, "w") as f:
            f.write(result["code"])
        logger.info(f"Generated code saved to {file_path}")
    
    # Save metadata for analysis
    metadata_path = os.path.join(args.output_dir, "metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(result["metadata"], f, indent=2)
    logger.info(f"Metadata saved to {metadata_path}")
    
    # Print summary
    print("\n=== Agent Execution Summary ===")
    print(f"Implementation: {'Real' if using_real_agent else 'Mock'}")
    print(f"Validation Status: {result['validation_status']}")
    print(f"Code Length: {len(result.get('code', ''))}")
    print(f"File Path: {result.get('file_path')}")
    print(f"Attempts: {result['metadata'].get('attempts', 1)}")
    print(f"Architectural Context Used: {len(result['metadata']['context_used']['architectural'])}")
    print(f"Implementation Context Used: {len(result['metadata']['context_used']['implementation'])}")
    
    if not result['validation_status']:
        print("\nErrors:")
        for error in result['metadata'].get('errors', []):
            print(f"- {error}")

if __name__ == "__main__":
    main()
