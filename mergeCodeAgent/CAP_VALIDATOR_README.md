# CAP SAP Java Validator

A tool for validating and fixing Java files to ensure they comply with SAP Cloud Application Programming (CAP) standards.

## Features

- Validates Java classes to ensure they follow CAP SAP patterns
- Automatically fixes common issues:
  - Adds missing annotations (@Service, @Entity, @Repository)
  - Adds required imports
  - Fixes syntax errors (missing semicolons, braces, etc.)
  - Ensures proper class inheritance/implementation

## Usage

### Standalone Validation

To validate a single Java file:

```bash
python3 mergeCodeAgent/java_cap_validator.py /path/to/your/JavaFile.java
```

### Batch Validation

To validate all Java files in a directory:

```bash
python3 mergeCodeAgent/integrate_cap_validator.py --directory /path/to/your/project
```

To validate specific Java files:

```bash
python3 mergeCodeAgent/integrate_cap_validator.py --files /path/to/file1.java /path/to/file2.java
```

## Supported Class Types

1. **Service Classes**
   - Must have `@Service` annotation
   - Must have proper package structure (typically under `.service`)

2. **Entity Classes**
   - Must have `@Entity` annotation
   - Must include proper JPA imports
   - Typically contains fields with getters/setters

3. **Repository Interfaces**
   - Must have `@Repository` annotation
   - Must extend `JpaRepository<EntityType, IdType>`
   - Must include the proper import for JpaRepository

## Integration with Merge Code Agent

The validator is designed to work with the merge code agent to ensure that generated Java code follows CAP SAP standards before being committed.

## Testing

Run the test suite to verify the validator's functionality:

```bash
python3 mergeCodeAgent/test_cap_validator.py
``` 