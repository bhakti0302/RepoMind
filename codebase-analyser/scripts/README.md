# Codebase Analyzer Scripts

This directory contains scripts for analyzing codebases, generating visualizations, and managing the database.

## Main Scripts

### Analysis Scripts

- **run_codebase_analysis.py**: Main script for running the complete codebase analysis pipeline.
- **run_codebase_analysis_enhanced.py**: Enhanced version that integrates all visualization capabilities.
- **analyze_java.py**: Script for analyzing Java projects specifically.
- **update_codebase.py**: Script for incremental updates to the codebase analysis.

## Visualization Scripts

### Core Visualization Scripts

These scripts are used directly by the main analysis pipeline:

- **visualize_all_relationships.py**: Comprehensive script that runs all visualization scripts.
- **generate_uml_diagrams.py**: Generates UML-style diagrams showing class hierarchies and relationships.
- **generate_colored_diagrams.py**: Generates colored diagrams showing different types of relationships.
- **create_dependencies_table.py**: Creates a table of dependencies for visualization.

### Specialized Visualization Scripts

These scripts provide additional visualization capabilities:

- **visualize_code_relationships.py**: Visualizes relationships between code elements with detailed information.
- **visualize_complex_relationships.py**: Visualizes more complex relationships with advanced layout options.
- **visualize_from_db.py**: Visualizes relationships directly from the database without re-analyzing the code.
- **visualize_testshreya.py**: Specialized visualization for the testshreya project.
- **create_uml_diagrams.py**: Creates UML diagrams with additional customization options.

### Utility Scripts

- **visualization_utils.py**: Utility functions for copying visualizations and enhancing graphs.

## Database Management Scripts

- **check_db.py**: Checks the database structure and contents.
- **check_dependencies.py**: Checks the dependencies stored in the database.
- **check_relationships.py**: Checks the relationships stored in the database.
- **add_dependencies_to_db.py**: Adds dependencies to the database.

## Testing and Analysis Scripts

- **analyze_enhanced_relationships.py**: Analyzes enhanced relationships between code elements.
- **analyze_relationships.py**: Analyzes basic relationships between code elements.
- **test_enhanced_relationships.py**: Tests the enhanced relationship analysis.
- **test_nlp_setup.py**: Tests the NLP setup for requirements parsing.
- **test_parser.py**: Tests the code parser.

## Usage Examples

### Running the Complete Analysis Pipeline

```bash
python run_codebase_analysis.py /path/to/repo --project-id my_project --visualize
```

### Generating All Visualizations

```bash
python visualize_all_relationships.py --repo-path /path/to/repo --output-dir /path/to/output --project-id my_project
```

### Analyzing a Java Project

```bash
python analyze_java.py /path/to/java/project --project-id java_project
```

### Updating an Existing Analysis

```bash
python update_codebase.py /path/to/repo --project-id my_project
```

### Generating Specific Visualizations

```bash
python visualize_code_relationships.py --db-path .lancedb --project-id my_project --output-file code_relationships.png
```

```bash
python visualize_complex_relationships.py --db-path .lancedb --project-id my_project --output-file complex_relationships.png
```

## Visualization Types

1. **UML Diagrams**: Show class hierarchies, inheritance, and implementation relationships.
2. **Multi-File Relationships**: Show relationships between different files in the codebase.
3. **Relationship Types**: Show different types of relationships (imports, extends, implements, etc.) with different colors.
4. **Code Relationships**: Show detailed relationships between code elements.
5. **Complex Relationships**: Show more complex relationships with advanced layout options.
6. **TestShreya Visualizations**: Specialized visualizations for the testshreya project.

## Best Practices

- Use `run_codebase_analysis_enhanced.py` for the most comprehensive analysis and visualization.
- Store visualizations in the `data/visualizations/{project_id}` directory.
- Use consistent naming conventions for visualization files.
- Include timestamps in visualization filenames to track changes over time.
