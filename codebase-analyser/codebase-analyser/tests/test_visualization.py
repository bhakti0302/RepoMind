#!/usr/bin/env python3
"""
Test script for the visualization utility.
"""

import sys
import os
from pathlib import Path
import argparse
import tempfile
import webbrowser

from codebase_analyser import CodebaseAnalyser
from codebase_analyser.visualization import ChunkVisualizer


def test_visualization(file_path, output_dir=None, format="html"):
    """Test the visualization utility on a file.

    Args:
        file_path: Path to the file to visualize
        output_dir: Directory to save visualization outputs
        format: Output format (html, svg, png)
    """
    # If output_dir is not specified, use the samples folder
    if output_dir is None:
        output_dir = Path("samples")
    print(f"Testing visualization on {file_path}")

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
    visualizer = ChunkVisualizer(output_dir=output_dir or tempfile.gettempdir())

    # Generate visualizations based on format
    try:
        # Get the base name of the file without extension
        base_name = file_path.stem

        # Print output directory for debugging
        print(f"Output directory: {output_dir}")

        # Always generate the dependency visualization with Plotly (most reliable)
        try:
            dependency_file = visualizer.visualize_dependencies_plotly(
                chunks,
                output_file=os.path.join(output_dir, f"{base_name}_dependencies.html"),
                show=False
            )
            print(f"\nGenerated dependency visualization: {dependency_file}")
        except Exception as e:
            print(f"Error generating dependency visualization: {e}")

        if format == "html":
            # Generate HTML report
            report_file = os.path.join(output_dir, f"{base_name}_report.html")
            visualizer.generate_html_report(chunks, output_file=report_file, show=False)
            print(f"Generated HTML report: {report_file}")

            # Open the dependency visualization in the browser
            webbrowser.open(f"file://{os.path.abspath(dependency_file)}")

        elif format == "svg":
            try:
                # Try to generate SVG visualizations
                hierarchy_file = visualizer.visualize_hierarchy_graphviz(
                    chunks,
                    output_file=os.path.join(output_dir, f"{base_name}_hierarchy.svg"),
                    show=False,
                    format="svg"
                )
                print(f"Generated hierarchy visualization: {hierarchy_file}")
            except (ImportError, FileNotFoundError) as e:
                print(f"Could not generate hierarchy visualization: {e}")

        elif format == "png":
            try:
                # Try to generate PNG visualization
                output_file = visualizer.visualize_hierarchy_matplotlib(
                    chunks,
                    output_file=os.path.join(output_dir, f"{base_name}_hierarchy.png"),
                    show=False
                )
                print(f"Generated hierarchy visualization: {output_file}")
            except ImportError as e:
                print(f"Could not generate matplotlib visualization: {e}")

        else:
            print(f"Unsupported format: {format}")

    except Exception as e:
        print(f"Error generating visualization: {e}")

    print("Visualization test completed successfully")


def main():
    parser = argparse.ArgumentParser(description="Test the visualization utility")
    parser.add_argument("file_path", help="Path to the file to visualize")
    parser.add_argument("--output-dir", "-o", help="Directory to save visualization outputs")
    parser.add_argument("--format", "-f", choices=["html", "svg", "png"], default="html",
                        help="Output format (html, svg, png)")

    args = parser.parse_args()

    file_path = Path(args.file_path)
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return

    test_visualization(file_path, args.output_dir, args.format)


if __name__ == "__main__":
    main()
