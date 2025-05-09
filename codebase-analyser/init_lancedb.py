"""
Initialize LanceDB with sample code chunks for testing.
"""
import logging
import os
import lancedb
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Sample code chunks for architecture
architecture_chunks = [
    {
        "id": "arch1",
        "content": """
        /**
         * Interface for data exporters.
         */
        public interface DataExporter {
            /**
             * Export data to a file.
             * 
             * @param filePath the path to the file
             * @param data the data to export
             * @throws IOException if an I/O error occurs
             */
            void exportData(String filePath, List<Object> data) throws IOException;
        }
        """,
        "file_path": "src/main/java/com/example/exporter/DataExporter.java",
        "language": "java",
        "type": "interface"
    },
    {
        "id": "arch2",
        "content": """
        /**
         * Factory for creating data exporters.
         */
        public class ExporterFactory {
            /**
             * Create an exporter for the specified format.
             * 
             * @param format the export format (e.g., "csv", "json", "xml")
             * @return the appropriate exporter
             * @throws IllegalArgumentException if the format is not supported
             */
            public static DataExporter createExporter(String format) {
                switch (format.toLowerCase()) {
                    case "csv":
                        return new CsvExporter();
                    case "json":
                        return new JsonExporter();
                    case "xml":
                        return new XmlExporter();
                    default:
                        throw new IllegalArgumentException("Unsupported format: " + format);
                }
            }
        }
        """,
        "file_path": "src/main/java/com/example/exporter/ExporterFactory.java",
        "language": "java",
        "type": "class"
    }
]

# Sample code chunks for implementation
code_chunks = [
    {
        "id": "impl1",
        "content": """
        /**
         * CSV exporter implementation.
         */
        public class CsvExporter implements DataExporter {
            @Override
            public void exportData(String filePath, List<Object> data) throws IOException {
                try (PrintWriter writer = new PrintWriter(new FileWriter(filePath))) {
                    for (Object item : data) {
                        writer.println(item.toString());
                    }
                }
            }
        }
        """,
        "file_path": "src/main/java/com/example/exporter/CsvExporter.java",
        "language": "java",
        "type": "class"
    },
    {
        "id": "impl2",
        "content": """
        /**
         * JSON exporter implementation.
         */
        public class JsonExporter implements DataExporter {
            private final ObjectMapper objectMapper = new ObjectMapper();
            
            @Override
            public void exportData(String filePath, List<Object> data) throws IOException {
                objectMapper.writeValue(new File(filePath), data);
            }
        }
        """,
        "file_path": "src/main/java/com/example/exporter/JsonExporter.java",
        "language": "java",
        "type": "class"
    },
    {
        "id": "impl3",
        "content": """
        /**
         * XML exporter implementation.
         */
        public class XmlExporter implements DataExporter {
            private final XmlMapper xmlMapper = new XmlMapper();
            
            @Override
            public void exportData(String filePath, List<Object> data) throws IOException {
                xmlMapper.writeValue(new File(filePath), data);
            }
        }
        """,
        "file_path": "src/main/java/com/example/exporter/XmlExporter.java",
        "language": "java",
        "type": "class"
    }
]

def main():
    """Initialize the LanceDB database with sample code chunks."""
    logger.info("Initializing LanceDB with sample code chunks")
    
    try:
        # Load the embedding model
        logger.info("Loading embedding model")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Connect to LanceDB
        logger.info("Connecting to LanceDB")
        db_path = "./lancedb"
        os.makedirs(db_path, exist_ok=True)
        db = lancedb.connect(db_path)
        
        # Process architecture chunks
        logger.info("Processing architecture chunks")
        arch_data = []
        for chunk in architecture_chunks:
            # Generate embedding
            embedding = model.encode(chunk["content"]).tolist()  # Convert to list
            
            # Create a dictionary with all fields
            item = {
                "id": chunk["id"],
                "content": chunk["content"],
                "file_path": chunk["file_path"],
                "language": chunk["language"],
                "type": chunk["type"],
                "vector": embedding
            }
            
            arch_data.append(item)
        
        # Create architecture_chunks table
        logger.info("Creating architecture_chunks table")
        try:
            # Try to get existing table names
            table_names = db.table_names()
            if "architecture_chunks" in table_names:
                logger.info("Dropping existing architecture_chunks table")
                db.drop_table("architecture_chunks")
        except (AttributeError, TypeError):
            # Older versions might not have table_names method
            try:
                db.drop_table("architecture_chunks")
                logger.info("Dropped existing architecture_chunks table")
            except:
                logger.info("No existing architecture_chunks table to drop")
        
        # Create the table
        arch_df = pd.DataFrame(arch_data)
        db.create_table("architecture_chunks", arch_df)
        logger.info(f"Added {len(arch_data)} architecture chunks to the database")
        
        # Process code chunks
        logger.info("Processing code chunks")
        code_data = []
        for chunk in code_chunks:
            # Generate embedding
            embedding = model.encode(chunk["content"]).tolist()  # Convert to list
            
            # Create a dictionary with all fields
            item = {
                "id": chunk["id"],
                "content": chunk["content"],
                "file_path": chunk["file_path"],
                "language": chunk["language"],
                "type": chunk["type"],
                "vector": embedding
            }
            
            code_data.append(item)
        
        # Create code_chunks table
        logger.info("Creating code_chunks table")
        try:
            # Try to get existing table names
            table_names = db.table_names()
            if "code_chunks" in table_names:
                logger.info("Dropping existing code_chunks table")
                db.drop_table("code_chunks")
        except (AttributeError, TypeError):
            # Older versions might not have table_names method
            try:
                db.drop_table("code_chunks")
                logger.info("Dropped existing code_chunks table")
            except:
                logger.info("No existing code_chunks table to drop")
        
        # Create the table
        code_df = pd.DataFrame(code_data)
        db.create_table("code_chunks", code_df)
        logger.info(f"Added {len(code_data)} code chunks to the database")
        
        logger.info("LanceDB initialization completed successfully")
    
    except Exception as e:
        logger.error(f"Error initializing LanceDB: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
