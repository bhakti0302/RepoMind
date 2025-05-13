#!/usr/bin/env python3
"""
Test script for the simple visualization utility.
"""

import sys
import os
from pathlib import Path
import argparse

from codebase_analyser import CodebaseAnalyser
from codebase_analyser.visualization import SimpleVisualizer


def test_visualization(file_path, output_dir=None, include_dependencies=True):
    """Test the simple visualization utility on a file.
    
    Args:
        file_path: Path to the file to visualize
        output_dir: Directory to save visualization outputs
        include_dependencies: Whether to include dependency relationships
    """
    print(f"Testing visualization on {file_path}")
    
    # If output_dir is not specified, use the samples folder
    if output_dir is None:
        output_dir = Path("samples")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create analyser with the parent directory as the repo path
    analyser = CodebaseAnalyser(file_path.parent)
    
    # Parse the file
    result = analyser.parse_file(file_path)
    
    if not result:
        print(f"Failed to parse {file_path}")
        return
    
    print(f"Successfully parsed {file_path}")
    print(f"Language: {result['language']}")
    
    # Get chunks for the file
    chunks = analyser.get_chunks(result)
    
    print(f"\nCreated {len(chunks)} top-level chunks")
    
    # Get all chunks including descendants
    all_chunks = []
    for chunk in chunks:
        all_chunks.append(chunk)
        all_chunks.extend(chunk.get_descendants())
    
    print(f"Total chunks (including children): {len(all_chunks)}")
    
    # Create visualizer
    visualizer = SimpleVisualizer(output_dir=output_dir)
    
    # Generate visualization
    try:
        # Get the base name of the file without extension
        base_name = file_path.stem
        
        # Generate visualization
        output_file = visualizer.visualize_hierarchy(
            chunks,
            output_file=os.path.join(output_dir, f"{base_name}_visualization.png"),
            show=False,
            include_dependencies=include_dependencies
        )
        
        print(f"\nGenerated visualization: {output_file}")
        print(f"Visualization saved to: {os.path.abspath(output_file)}")
        
    except Exception as e:
        print(f"Error generating visualization: {e}")
    
    print("Visualization test completed successfully")


def main():
    parser = argparse.ArgumentParser(description="Test the simple visualization utility")
    parser.add_argument("file_path", help="Path to the file to visualize")
    parser.add_argument("--output-dir", "-o", help="Directory to save visualization outputs")
    parser.add_argument("--no-dependencies", action="store_true", 
                        help="Exclude dependency relationships (show only hierarchy)")
    
    args = parser.parse_args()
    
    file_path = Path(args.file_path)
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return
    
    test_visualization(
        file_path, 
        args.output_dir, 
        include_dependencies=not args.no_dependencies
    )


if __name__ == "__main__":
    main()
