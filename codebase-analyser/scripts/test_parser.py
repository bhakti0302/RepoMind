#!/usr/bin/env python3
"""
Test the Java parser on the testshreya files.
"""

import os
from codebase_analyser.parsing.java_parser_adapter import JavaParserAdapter

def main():
    """Main entry point."""
    testshreya_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'testshreya')
    java_files = [
        'Entity.java',
        'AbstractEntity.java',
        'User.java',
        'Order.java',
        'Address.java'
    ]

    total_chunks = 0
    for file in java_files:
        path = os.path.join(testshreya_dir, file)
        result = JavaParserAdapter.parse_file(path)
        chunks = len(result['chunks'])
        print(f'{file}: {chunks} chunks')

        # Print the types of chunks
        chunk_types = {}
        for chunk in result['chunks']:
            chunk_type = chunk['chunk_type']
            if chunk_type not in chunk_types:
                chunk_types[chunk_type] = 0
            chunk_types[chunk_type] += 1

        for chunk_type, count in chunk_types.items():
            print(f'  - {chunk_type}: {count}')

        total_chunks += chunks

    print(f'Total: {total_chunks} chunks')

if __name__ == '__main__':
    main()
