#!/usr/bin/env python3
"""
Test Enhanced Relationships

This script tests the enhanced relationship detection and visualization.
It parses a Java project, extracts relationships, and visualizes them.

Usage:
    python test_enhanced_relationships.py --repo-path <path_to_repo> --output-file <path_to_output.png>
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Test Enhanced Relationships")
    parser.add_argument("--repo-path", required=True, help="Path to the Java repository")
    parser.add_argument("--output-file", default="samples/enhanced_graph.png", help="Path to save the visualization")
    parser.add_argument("--graph-file", default="samples/dependency_graph.json", help="Path to save the dependency graph JSON")
    parser.add_argument("--project-id", default=None, help="Project ID (defaults to folder name)")
    parser.add_argument("--show", action="store_true", help="Show the visualization")
    
    args = parser.parse_args()
    
    # Validate repo path
    repo_path = Path(args.repo_path)
    if not repo_path.exists() or not repo_path.is_dir():
        logger.error(f"Repository path does not exist or is not a directory: {repo_path}")
        sys.exit(1)
    
    # Set project ID if not provided
    project_id = args.project_id or repo_path.name
    
    # Import the necessary modules
    try:
        from codebase_analyser import CodebaseAnalyser
        from codebase_analyser.parsing.enhanced_dependency_analyzer import EnhancedDependencyAnalyzer
    except ImportError as e:
        logger.error(f"Failed to import required modules: {e}")
        sys.exit(1)
    
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
    
    # Analyze dependencies with the enhanced analyzer
    logger.info("Analyzing dependencies with enhanced analyzer")
    dependency_analyzer = EnhancedDependencyAnalyzer()
    dependency_graph = dependency_analyzer.analyze_dependencies(chunks)
    
    # Convert to dictionary
    graph_dict = dependency_graph.to_dict()
    
    # Save the dependency graph
    logger.info(f"Saving dependency graph to {args.graph_file}")
    with open(args.graph_file, 'w') as f:
        json.dump(graph_dict, f, indent=2)
    
    # Visualize the graph
    logger.info(f"Visualizing dependency graph to {args.output_file}")
    
    # Use the enhanced visualization script
    try:
        from scripts.enhance_graph_visualization import create_networkx_graph, visualize_enhanced_graph
        
        # Create a NetworkX graph
        G = create_networkx_graph(graph_dict)
        
        # Visualize the graph
        visualize_enhanced_graph(
            G,
            args.output_file,
            title=f"Enhanced Code Relationships - {project_id}",
            show=args.show
        )
    except ImportError as e:
        logger.error(f"Failed to import visualization modules: {e}")
        
        # Fall back to basic visualization
        try:
            import networkx as nx
            import matplotlib.pyplot as plt
            
            # Create a NetworkX graph
            G = nx.DiGraph()
            
            # Add nodes
            for node in graph_dict['nodes']:
                G.add_node(node['id'], **node)
            
            # Add edges
            for edge in graph_dict['edges']:
                G.add_edge(edge['source_id'], edge['target_id'], **edge)
            
            # Create the figure
            plt.figure(figsize=(12, 8))
            plt.title(f"Code Relationships - {project_id}")
            
            # Draw the graph
            pos = nx.spring_layout(G, seed=42)
            nx.draw(G, pos, with_labels=True, node_size=500, node_color='lightblue', 
                    font_size=8, arrows=True)
            
            # Save the figure
            plt.savefig(args.output_file, dpi=300, bbox_inches='tight')
            
            if args.show:
                plt.show()
            else:
                plt.close()
        except Exception as e:
            logger.error(f"Failed to visualize graph: {e}")
    
    logger.info("Enhanced relationship testing completed successfully")

if __name__ == "__main__":
    main()
