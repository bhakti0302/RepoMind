#!/usr/bin/env python3
"""
Analyze enhanced relationships in a Java project.

This script analyzes a Java project using the enhanced dependency analyzer
and generates a visualization of the code relationships.

Usage:
    python analyze_enhanced_relationships.py --repo-path <path_to_repo> --output-file <path_to_output.png>
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from codebase_analyser import CodebaseAnalyser
from codebase_analyser.parsing.enhanced_dependency_analyzer import EnhancedDependencyAnalyzer
from codebase_analyser.visualization.graph_visualizer import GraphVisualizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Analyze Enhanced Relationships")
    parser.add_argument("--repo-path", required=True, help="Path to the Java repository")
    parser.add_argument("--output-file", default="samples/enhanced_graph.png", help="Path to save the visualization")
    parser.add_argument("--graph-file", default="samples/enhanced_dependency_graph.json", help="Path to save the dependency graph JSON")
    parser.add_argument("--project-id", default=None, help="Project ID (defaults to folder name)")
    parser.add_argument("--show-details", action="store_true", help="Show detailed information about the relationships")
    
    args = parser.parse_args()
    
    # Validate repo path
    repo_path = Path(args.repo_path)
    if not repo_path.exists() or not repo_path.is_dir():
        logger.error(f"Repository path does not exist or is not a directory: {repo_path}")
        sys.exit(1)
    
    # Set project ID if not provided
    project_id = args.project_id or repo_path.name
    
    # Create output directory if it doesn't exist
    output_dir = Path(args.output_file).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Parse the repository
    logger.info(f"Parsing repository: {repo_path}")
    analyser = CodebaseAnalyser(repo_path=repo_path)
    chunks = analyser.parse()
    
    if not chunks:
        logger.error("No chunks found in the repository")
        sys.exit(1)
    
    logger.info(f"Found {len(chunks)} chunks in the repository")
    
    # Print information about the chunks if requested
    if args.show_details:
        class_chunks = [c for c in chunks if c.chunk_type == 'class_declaration']
        interface_chunks = [c for c in chunks if c.chunk_type == 'interface_declaration']
        method_chunks = [c for c in chunks if c.chunk_type == 'method_declaration']
        
        logger.info(f"Found {len(class_chunks)} classes, {len(interface_chunks)} interfaces, {len(method_chunks)} methods")
        
        # Print information about the classes
        logger.info("\nClasses:")
        for chunk in class_chunks:
            logger.info(f"  - {chunk.name} ({chunk.node_id})")
            
            # Print parent class if available
            if 'extends' in chunk.context:
                logger.info(f"    Extends: {chunk.context['extends']}")
            
            # Print implemented interfaces if available
            if 'implements' in chunk.context:
                logger.info(f"    Implements: {', '.join(chunk.context['implements'])}")
            
            # Print fields if available
            if 'fields' in chunk.context:
                logger.info(f"    Fields:")
                for field in chunk.context['fields']:
                    logger.info(f"      - {field.get('name', 'unknown')} ({field.get('type', 'unknown')})")
        
        # Print information about the interfaces
        logger.info("\nInterfaces:")
        for chunk in interface_chunks:
            logger.info(f"  - {chunk.name} ({chunk.node_id})")
    
    # Analyze dependencies with the enhanced analyzer
    logger.info("Analyzing dependencies with enhanced analyzer")
    dependency_analyzer = EnhancedDependencyAnalyzer()
    dependency_graph = dependency_analyzer.analyze_dependencies(chunks)
    
    # Print information about the dependencies if requested
    if args.show_details:
        logger.info("\nDependencies:")
        edges = dependency_graph.edges
        
        # Group edges by type
        edge_types = {}
        for edge in edges:
            edge_type = edge.type
            if edge_type not in edge_types:
                edge_types[edge_type] = []
            edge_types[edge_type].append(edge)
        
        # Print edges by type
        for edge_type, edges in edge_types.items():
            logger.info(f"\n  {edge_type} ({len(edges)}):")
            for edge in edges:
                source_id = edge.source_id
                target_id = edge.target_id
                
                # Find the source and target chunks
                source_chunk = next((c for c in chunks if c.node_id == source_id), None)
                target_chunk = next((c for c in chunks if c.node_id == target_id), None)
                
                source_name = source_chunk.name if source_chunk else source_id
                target_name = target_chunk.name if target_chunk else target_id
                
                logger.info(f"    - {source_name} -> {target_name} ({edge.description})")
    
    # Convert to dictionary and save
    graph_dict = dependency_graph.to_dict()
    with open(args.graph_file, 'w') as f:
        json.dump(graph_dict, f, indent=2)
    
    logger.info(f"Generated dependency graph with {len(graph_dict['nodes'])} nodes and {len(graph_dict['edges'])} edges")
    logger.info(f"Saved dependency graph to {args.graph_file}")
    
    # Visualize the graph
    logger.info(f"Visualizing dependency graph to {args.output_file}")
    visualizer = GraphVisualizer()
    visualizer.visualize(dependency_graph, args.output_file, title=f"Enhanced Code Relationships - {project_id}")
    
    logger.info(f"Saved visualization to {args.output_file}")
    logger.info("Enhanced relationship analysis completed successfully")

if __name__ == "__main__":
    main()
