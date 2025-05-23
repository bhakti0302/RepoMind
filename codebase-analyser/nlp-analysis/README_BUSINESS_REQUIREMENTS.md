# Business Requirements Processing

This document describes how to process business requirements using the RAG system.

## Overview

The business requirements processor extracts entities and components from business requirements using Named Entity Recognition (NER) and processes them using multi-hop RAG. It stores the processed requirements in the data directory and generates code using the LLM.

## Features

- **Entity Extraction**: Extracts entities such as domain objects, actions, and attributes from business requirements
- **Component Analysis**: Identifies functional requirements, non-functional requirements, and constraints
- **Multi-Hop RAG**: Uses multi-hop RAG to find relevant code for each requirement
- **Code Generation**: Generates code based on the requirements and the retrieved context
- **Data Storage**: Stores processed requirements in the data directory for future reference

## Usage

### Command-Line Interface

You can process business requirements using the command-line interface:

```bash
python process_business_requirements.py --file path/to/requirements.txt --project-id your-project-id --output-dir ./output
```

#### Parameters

- `--file`: Path to the business requirements file (required)
- `--project-id`: Project ID (optional, derived from file name if not provided)
- `--db-path`: Path to the LanceDB database (optional, default: "../.lancedb")
- `--output-dir`: Path to the output directory (optional, default: "./output")
- `--data-dir`: Path to the data directory (optional, default: "../data")
- `--rag-type`: Type of RAG to use (optional, choices: "basic", "graph", "multi_hop", default: "multi_hop")
- `--generate-code`: Whether to generate code using LLM (optional, default: True)
- `--env-file`: Path to the .env file (optional)

### VS Code Extension

You can also process business requirements using the VS Code extension:

1. Open the VS Code extension
2. Click the "Attach" button
3. Select a business requirements file
4. Wait for the processing to complete
5. View the generated code in the output directory

## Implementation Details

### Business Requirements Processor

The business requirements processor is implemented in `src/business_requirements_processor.py`. It:

1. Reads the business requirements file
2. Preprocesses the text
3. Parses the requirements
4. Extracts entities
5. Analyzes components
6. Cleans code references
7. Stores the processed requirements in the data directory
8. Generates code using the LLM

### Named Entity Recognition

The NER component is implemented in `src/entity_extractor.py`. It uses spaCy to extract entities from the text. The entities are categorized as:

- **Domain Objects**: Nouns that represent domain objects (e.g., "employee", "department")
- **Actions**: Verbs that represent actions (e.g., "create", "update")
- **Attributes**: Adjectives and nouns that represent attributes (e.g., "name", "salary")
- **Constraints**: Phrases that represent constraints (e.g., "must be", "should not")

### Multi-Hop RAG

The multi-hop RAG component is implemented in `src/multi_hop_rag.py`. It:

1. Extracts domain entities from the query
2. Performs vector search for each entity
3. Enhances the search results with graph context
4. Performs multiple hops to find related code
5. Combines the results to generate a comprehensive context

### Code Generation

The code generation component is implemented in `src/code_synthesis_workflow.py`. It:

1. Processes the requirements
2. Retrieves relevant code using multi-hop RAG
3. Generates instructions for the LLM
4. Generates code using the LLM
5. Saves the generated code to the output directory

## Data Flow

1. Business requirements file is read
2. Text is preprocessed
3. Requirements are parsed
4. Entities are extracted
5. Components are analyzed
6. Code references are cleaned
7. Processed requirements are stored in the data directory
8. Multi-hop RAG is used to find relevant code
9. LLM generates code based on the requirements and the retrieved context
10. Generated code is saved to the output directory

## Directory Structure

- `src/business_requirements_processor.py`: Business requirements processor
- `src/entity_extractor.py`: Entity extraction component
- `src/component_analyzer.py`: Component analysis component
- `src/text_processor.py`: Text processing component
- `src/multi_hop_rag.py`: Multi-hop RAG component
- `src/code_synthesis_workflow.py`: Code generation component
- `process_business_requirements.py`: Command-line interface
- `data/requirements/{project_id}/`: Processed requirements for each project
- `output/`: Generated code and instructions

## Requirements

- Python 3.8+
- LanceDB
- spaCy (with en_core_web_sm model)
- Sentence Transformers
- NumPy
- Pandas

## Installation

```bash
pip install lancedb spacy sentence-transformers numpy pandas
python -m spacy download en_core_web_sm
```

## Notes

- The business requirements processor works best with well-structured requirements
- The NER component can be improved by training a custom model
- The multi-hop RAG component can be enhanced with more sophisticated graph traversal algorithms
- The code generation component can be improved by fine-tuning the LLM
