from codebase_analyser.parsing.java_parser_adapter import JavaParserAdapter

parser = JavaParserAdapter()
files = [
    "samples/java_test_project/Main.java",
    "samples/java_test_project/DataProcessor.java"
]

print("Testing sample Java files...")
for file in files:
    print(f"\nParsing {file}...")
    try:
        chunks = parser.parse_file(file)
        print(f"Generated {len(chunks)} chunks")
        for i, chunk in enumerate(chunks):
            if hasattr(chunk, "node_id"):
                print(f"  - {chunk.node_id}: {chunk.name}")
            else:
                print(f"  - Chunk {i}: {type(chunk)}")
    except Exception as e:
        print(f"Error: {e}")
