#!/usr/bin/env python3
"""
Enhanced Codebase Analysis Script

This script runs the complete codebase analysis pipeline and generates
comprehensive visualizations using all available visualization tools.
"""

import os
import sys
import argparse
import logging
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import networkx as nx

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path to import codebase_analyser
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from codebase_analyser import CodebaseAnalyser
from codebase_analyser.database import open_unified_storage, close_unified_storage
from codebase_analyser.embeddings import EmbeddingGenerator
from codebase_analyser.graph.visualizer import visualize_dependency_graph
from codebase_analyser.parsing.dependency_analyzer import DependencyAnalyzer
from codebase_analyser.chunking.code_chunk import CodeChunk


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run complete codebase analysis with enhanced visualizations")
    
    # Basic options
    parser.add_argument("repo_path", help="Path to the repository to analyze")
    parser.add_argument("--db-path", help="Path to the database file (default: .lancedb)")
    parser.add_argument("--visualize", action="store_true", help="Generate dependency graph visualization")
    parser.add_argument("--output-dir", default="samples", help="Directory to save visualization outputs")
    parser.add_argument("--graph-format", default="png", choices=["png", "dot"], help="Format for graph visualization")
    
    # Project options
    parser.add_argument("--project-id", help="Project ID for multi-project support")
    
    # Performance options
    parser.add_argument("--max-files", type=int, help="Maximum number of files to process (for testing)")
    parser.add_argument("--skip-large-files", action="store_true", help="Skip files larger than 1MB")
    
    # Enhanced visualization options
    parser.add_argument("--all-visualizations", action="store_true", 
                        help="Generate all available visualizations")
    parser.add_argument("--code-relationships", action="store_true", 
                        help="Generate code relationship visualizations")
    parser.add_argument("--complex-relationships", action="store_true", 
                        help="Generate complex relationship visualizations")
    parser.add_argument("--testshreya", action="store_true", 
                        help="Generate testshreya-specific visualizations")
    
    return parser.parse_args()


def analyze_codebase(args):
    """Run the complete codebase analysis pipeline with enhanced visualizations."""
    start_time = time.time()
    repo_path = args.repo_path

    # Validate repository path
    if not os.path.isdir(repo_path):
        logger.error(f"Repository path does not exist: {repo_path}")
        return False

    logger.info(f"Starting analysis of repository: {repo_path}")

    # Step 1: Parse codebase and generate chunks
    logger.info("Step 1: Parsing codebase and generating chunks")
    analyzer = CodebaseAnalyser(repo_path)

    # Process files
    file_count = 0
    skipped_count = 0
    max_files = args.max_files if args.max_files else float('inf')

    # Set up database path
    db_path = args.db_path
    if not db_path:
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".lancedb")
    
    # Set up project ID
    project_id = args.project_id
    if not project_id:
        project_id = os.path.basename(os.path.abspath(repo_path))

    # Open storage connection
    storage_manager = open_unified_storage(db_path, project_id)

    try:
        # Step 2: Process files and store chunks
        logger.info("Step 2: Processing files and storing chunks")
        
        # Your existing code for processing files...
        
        # Step 3: Generate embeddings
        logger.info("Step 3: Generating embeddings")
        
        # Your existing code for generating embeddings...
        
        # Step 4: Generate visualizations
        logger.info("Step 4: Generating visualizations")
        
        # Create visualizations directory
        visualizations_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                         'data', 'visualizations', project_id)
        os.makedirs(visualizations_dir, exist_ok=True)
        
        # Generate timestamp for filenames
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Generate UML diagrams
        try:
            from scripts.generate_uml_diagrams import generate_uml_diagrams
            generate_uml_diagrams(project_id, visualizations_dir, db_path)
            logger.info("UML-style diagrams generated successfully")
        except Exception as e:
            logger.error(f"Error generating UML-style diagrams: {e}")
        
        # Generate colored relationship diagrams
        try:
            from scripts.generate_colored_diagrams import generate_multi_file_relationships, generate_relationship_types
            
            multi_file_path = os.path.join(visualizations_dir, f"{project_id}_multi_file_relationships_{timestamp}.png")
            relationship_types_path = os.path.join(visualizations_dir, f"{project_id}_relationship_types_{timestamp}.png")
            
            generate_multi_file_relationships(multi_file_path)
            generate_relationship_types(relationship_types_path)
            
            logger.info("Colored relationship diagrams generated successfully")
        except Exception as e:
            logger.error(f"Error generating colored relationship diagrams: {e}")
        
        # Generate additional visualizations if requested
        if args.all_visualizations or args.code_relationships:
            try:
                from scripts.visualize_code_relationships import visualize_code_relationships
                
                code_rel_path = os.path.join(visualizations_dir, f"{project_id}_code_relationships_{timestamp}.png")
                visualize_code_relationships(db_path, project_id, code_rel_path)
                
                logger.info("Code relationship visualization generated successfully")
            except Exception as e:
                logger.error(f"Error generating code relationship visualization: {e}")
        
        if args.all_visualizations or args.complex_relationships:
            try:
                from scripts.visualize_complex_relationships import visualize_complex_relationships
                
                complex_rel_path = os.path.join(visualizations_dir, f"{project_id}_complex_relationships_{timestamp}.png")
                visualize_complex_relationships(db_path, project_id, complex_rel_path)
                
                logger.info("Complex relationship visualization generated successfully")
            except Exception as e:
                logger.error(f"Error generating complex relationship visualization: {e}")
        
        if args.all_visualizations or args.testshreya:
            try:
                from scripts.visualize_testshreya import visualize_testshreya_project
                
                testshreya_path = os.path.join(visualizations_dir, f"{project_id}_testshreya_{timestamp}.png")
                visualize_testshreya_project(db_path, testshreya_path)
                
                logger.info("TestShreya visualization generated successfully")
            except Exception as e:
                logger.error(f"Error generating TestShreya visualization: {e}")
        
        # Step 5: Generate basic dependency graph visualization if requested
        if args.visualize:
            logger.info("Step 5: Generating dependency graph visualization")
            
            # Build the graph
            nx_graph = storage_manager._build_graph_from_dependencies()
            
            # Convert NetworkX graph to the expected format
            dependency_graph = {
                'nodes': [],
                'edges': []
            }
            
            # Add nodes
            for node_id, node_attrs in nx_graph.nodes(data=True):
                node = {
                    'id': node_id,
                    'type': node_attrs.get('type', 'unknown'),
                    'name': node_attrs.get('name', node_id),
                    'qualified_name': node_attrs.get('qualified_name', node_id)
                }
                dependency_graph['nodes'].append(node)
            
            # Add edges
            for source, target, edge_attrs in nx_graph.edges(data=True):
                edge = {
                    'source_id': source,
                    'target_id': target,
                    'type': edge_attrs.get('type', 'UNKNOWN'),
                    'strength': edge_attrs.get('strength', 1.0),
                    'is_direct': edge_attrs.get('is_direct', True),
                    'is_required': edge_attrs.get('is_required', False),
                    'description': edge_attrs.get('description', '')
                }
                dependency_graph['edges'].append(edge)
            
            # Generate visualization
            output_file = os.path.join(args.output_dir, f"dependency_graph.{args.graph_format}")
            visualize_dependency_graph(
                dependency_graph=dependency_graph,
                output_file=output_file,
                title="Dependency Graph",
                layout="spring"
            )
            logger.info(f"Saved visualization to {output_file}")
    finally:
        # Close storage connection
        close_unified_storage(storage_manager)
    
    elapsed_time = time.time() - start_time
    logger.info(f"Analysis completed in {elapsed_time:.2f} seconds")
    return True


def main():
    """Main entry point."""
    args = parse_args()
    success = analyze_codebase(args)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
