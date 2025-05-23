# NLP Analysis Scripts

This directory contains scripts for enhancing the RAG system and processing business requirements.

## Overview

The RAG system uses LanceDB to store code chunks and perform vector search. The current implementation falls back to text-based search when vector search fails, which is less effective than true vector search. These scripts add a vector column to the database, modify the vector search implementation, and provide tools for processing business requirements.

## Scripts

### 1. `add_vector_column.py`

This script adds a vector column to the LanceDB database for improved vector search. It processes existing code chunks, generates embeddings, and adds them to the database.

#### Usage

```bash
python add_vector_column.py --db-path ../path/to/db --model-name all-MiniLM-L6-v2 --batch-size 100 --vector-column-name vector
```

#### Parameters

- `--db-path`: Path to the LanceDB database (default: "../.lancedb")
- `--model-name`: Name of the embedding model to use (default: "all-MiniLM-L6-v2")
- `--batch-size`: Number of chunks to process at once (default: 100)
- `--vector-column-name`: Name of the vector column to add (default: "vector")

### 2. `test_vector_search.py`

This script tests the vector search functionality with the new vector column.

#### Usage

```bash
python test_vector_search.py --db-path ../path/to/db --query "employee management system" --limit 5 --output-file results.txt
```

#### Parameters

- `--db-path`: Path to the LanceDB database (default: "../.lancedb")
- `--query`: Search query (required)
- `--limit`: Maximum number of results to return (default: 5)
- `--output-file`: Path to the output file (optional)

### 3. `test_rag_system.py`

This script tests the entire RAG system, including vector search and multi-hop RAG.

#### Usage

```bash
python test_rag_system.py --db-path ../path/to/db --query "employee management system" --output-dir ./output
```

#### Parameters

- `--db-path`: Path to the LanceDB database (default: "../.lancedb")
- `--query`: Search query (default: "employee management system")
- `--output-dir`: Path to the output directory (default: "./output")
- `--test-type`: Type of test to run (choices: "vector", "multi-hop", "both"; default: "both")
- `--limit`: Maximum number of results to return (default: 5)
- `--max-hops`: Maximum number of hops for multi-hop RAG (default: 3)

## Implementation Details

### Vector Column

The vector column stores embeddings for each code chunk, which enables true vector search. The embeddings are generated using the Sentence Transformers library with the all-MiniLM-L6-v2 model, which is a good balance between performance and quality.

### Vector Search

The vector search implementation has been modified to use the vector column. It tries different column names ("embedding", "vector") to ensure compatibility with different database schemas. If vector search fails, it falls back to text-based search.

### Multi-Hop RAG

The multi-hop RAG implementation has been updated to use the vector column for improved search results. It performs multiple hops to find related code through vector search and graph relationships.

### Business Requirements Processing

The business requirements processor extracts entities and components from business requirements using NER and processes them using multi-hop RAG. It stores the processed requirements in the data directory and generates code using the LLM.

## Requirements

- Python 3.8+
- LanceDB
- Sentence Transformers
- NumPy
- Pandas
- tqdm
- spaCy (with en_core_web_sm model)

## Installation

```bash
pip install lancedb sentence-transformers numpy pandas tqdm spacy
python -m spacy download en_core_web_sm
```

## Workflow

1. Run `add_vector_column.py` to add a vector column to the database (optional)
2. Run `test_rag_system.py` to test the RAG system
3. Process business requirements using the VS Code extension's attach button
4. View the generated code in the output directory

## Notes

- The vector column significantly improves the relevance of search results
- The embedding model can be changed to balance performance and quality
- The batch size can be adjusted based on available memory
- The vector column name can be changed to match existing schemas
- Business requirements are stored in the data directory under the project ID
- The VS Code extension automatically detects business requirements files and processes them
