"""
Test script for the embedding generator.
"""
import logging
import numpy as np
from typing import List
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the embedding generator
from codebase_analyser.embeddings.embedding_generator import (
    EmbeddingGenerator, 
    generate_embedding, 
    cosine_similarity
)

def test_generate_embedding():
    """Test generating embeddings."""
    logger.info("Testing generate_embedding function")
    
    # Test with a simple text
    text = "public class DataExporter implements Exporter { ... }"
    
    # Measure time
    start_time = time.time()
    embedding = generate_embedding(text)
    elapsed_time = time.time() - start_time
    
    logger.info(f"Generated embedding with {len(embedding)} dimensions in {elapsed_time:.4f} seconds")
    
    # Test with empty text
    empty_embedding = generate_embedding("")
    logger.info(f"Empty text embedding has {len(empty_embedding)} dimensions")
    
    # Test with a longer text
    long_text = """
    /**
     * This class implements a data exporter that can export data to CSV format.
     * It supports various options like custom delimiters, headers, and quoting.
     */
    public class CsvExporterImpl implements DataExporter {
        private static final char DELIMITER = ',';
        private static final char QUOTE = '"';
        
        @Override
        public void export(Data data, OutputStream output) {
            // Implementation details...
        }
    }
    """
    
    long_embedding = generate_embedding(long_text)
    logger.info(f"Long text embedding has {len(long_embedding)} dimensions")
    
    return embedding, empty_embedding, long_embedding

def test_cosine_similarity(vec1: List[float], vec2: List[float]):
    """Test cosine similarity calculation."""
    logger.info("Testing cosine_similarity function")
    
    # Calculate similarity between the vectors
    similarity = cosine_similarity(vec1, vec2)
    logger.info(f"Cosine similarity: {similarity:.4f}")
    
    # Test with identical vectors
    identical_similarity = cosine_similarity(vec1, vec1)
    logger.info(f"Identical vectors similarity: {identical_similarity:.4f}")
    
    # Test with orthogonal vectors
    ortho_vec1 = [1.0, 0.0, 0.0]
    ortho_vec2 = [0.0, 1.0, 0.0]
    ortho_similarity = cosine_similarity(ortho_vec1, ortho_vec2)
    logger.info(f"Orthogonal vectors similarity: {ortho_similarity:.4f}")
    
    return similarity, identical_similarity, ortho_similarity

def test_embedding_generator():
    """Test the EmbeddingGenerator class."""
    logger.info("Testing EmbeddingGenerator class")
    
    # Create an instance
    generator = EmbeddingGenerator()
    
    # Test generate method
    text = "public interface DataExporter { void export(Data data, OutputStream output); }"
    embedding = generator.generate(text)
    logger.info(f"Generated embedding with {len(embedding)} dimensions")
    
    # Test batch_generate method
    texts = [
        "public class CsvExporter implements DataExporter { }",
        "public class JsonExporter implements DataExporter { }",
        "public class XmlExporter implements DataExporter { }"
    ]
    
    # Measure time
    start_time = time.time()
    embeddings = generator.batch_generate(texts)
    elapsed_time = time.time() - start_time
    
    logger.info(f"Generated {len(embeddings)} embeddings in batch in {elapsed_time:.4f} seconds")
    
    # Test compare method
    text1 = "public class CsvExporter implements DataExporter { }"
    text2 = "public class CsvExporterImpl implements DataExporter { }"
    similarity = generator.compare(text1, text2)
    logger.info(f"Similarity between similar texts: {similarity:.4f}")
    
    text3 = "public class XmlExporter implements DataExporter { }"
    similarity2 = generator.compare(text1, text3)
    logger.info(f"Similarity between different texts: {similarity2:.4f}")
    
    return generator, embeddings, similarity, similarity2

if __name__ == "__main__":
    logger.info("Starting embedding generator tests")
    
    # Run the tests
    embedding, empty_embedding, long_embedding = test_generate_embedding()
    similarity, identical_similarity, ortho_similarity = test_cosine_similarity(embedding, long_embedding)
    generator, embeddings, similarity, similarity2 = test_embedding_generator()
    
    logger.info("All tests completed successfully")