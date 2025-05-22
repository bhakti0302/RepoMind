#!/usr/bin/env python3

"""
Install Microsoft's GraphRAG library and its dependencies.

This script installs Microsoft's GraphRAG library and its dependencies,
and verifies the installation by running a simple test.
"""

import os
import sys
import logging
import subprocess
import importlib.util
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def check_python_version():
    """Check if the Python version is compatible with GraphRAG."""
    logger.info(f"Checking Python version...")
    
    major, minor, micro = sys.version_info[:3]
    logger.info(f"Python version: {major}.{minor}.{micro}")
    
    if major < 3 or (major == 3 and minor < 8):
        logger.error(f"Python version 3.8 or higher is required. Current version: {major}.{minor}.{micro}")
        return False
    
    logger.info(f"Python version is compatible with GraphRAG.")
    return True

def check_package_installed(package_name):
    """Check if a package is installed."""
    logger.info(f"Checking if {package_name} is installed...")
    
    spec = importlib.util.find_spec(package_name)
    if spec is None:
        logger.info(f"{package_name} is not installed.")
        return False
    
    logger.info(f"{package_name} is installed.")
    return True

def install_package(package_name, version=None):
    """Install a package using pip."""
    package_spec = f"{package_name}=={version}" if version else package_name
    logger.info(f"Installing {package_spec}...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_spec])
        logger.info(f"Successfully installed {package_spec}.")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error installing {package_spec}: {e}")
        return False

def install_graphrag():
    """Install Microsoft's GraphRAG library and its dependencies."""
    logger.info("Installing Microsoft's GraphRAG library and its dependencies...")
    
    # Check if GraphRAG is already installed
    if check_package_installed("graphrag"):
        logger.info("GraphRAG is already installed.")
        return True
    
    # Install GraphRAG from GitHub
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "git+https://github.com/microsoft/graphrag.git"
        ])
        logger.info("Successfully installed GraphRAG from GitHub.")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error installing GraphRAG from GitHub: {e}")
        
        # Try installing dependencies first
        logger.info("Installing dependencies first...")
        dependencies = [
            "networkx",
            "numpy",
            "pandas",
            "scikit-learn",
            "torch",
            "transformers",
            "sentence-transformers",
            "langchain",
            "langchain-community",
            "langchain-core",
            "langchain-openai",
            "pydantic",
            "tqdm"
        ]
        
        for dependency in dependencies:
            if not check_package_installed(dependency):
                if not install_package(dependency):
                    logger.error(f"Failed to install {dependency}.")
                    return False
        
        # Try installing GraphRAG again
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "git+https://github.com/microsoft/graphrag.git"
            ])
            logger.info("Successfully installed GraphRAG from GitHub after installing dependencies.")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error installing GraphRAG from GitHub after installing dependencies: {e}")
            return False

def test_graphrag():
    """Test if GraphRAG is working correctly."""
    logger.info("Testing GraphRAG installation...")
    
    try:
        # Try importing GraphRAG
        import graphrag
        logger.info(f"Successfully imported GraphRAG version {graphrag.__version__}")
        
        # Try importing key components
        from graphrag.knowledge_graph import KnowledgeGraph
        from graphrag.retrieval import GraphRetriever
        from graphrag.reasoning import ReasoningEngine
        
        logger.info("Successfully imported key GraphRAG components.")
        
        # Create a simple test
        logger.info("Creating a simple test...")
        
        # Create a simple knowledge graph
        kg = KnowledgeGraph()
        
        # Add some nodes
        kg.add_node("node1", {"name": "Node 1", "type": "class"})
        kg.add_node("node2", {"name": "Node 2", "type": "method"})
        
        # Add an edge
        kg.add_edge("node1", "node2", "CONTAINS")
        
        logger.info("Successfully created a simple knowledge graph.")
        logger.info(f"Knowledge graph has {len(kg.nodes)} nodes and {len(kg.edges)} edges.")
        
        logger.info("GraphRAG is working correctly.")
        return True
    
    except ImportError as e:
        logger.error(f"Error importing GraphRAG: {e}")
        return False
    except Exception as e:
        logger.error(f"Error testing GraphRAG: {e}")
        return False

def main():
    """Main function."""
    logger.info("Starting GraphRAG installation...")
    
    # Check Python version
    if not check_python_version():
        logger.error("Python version check failed. Exiting.")
        return False
    
    # Install GraphRAG
    if not install_graphrag():
        logger.error("GraphRAG installation failed. Exiting.")
        return False
    
    # Test GraphRAG
    if not test_graphrag():
        logger.error("GraphRAG test failed. Exiting.")
        return False
    
    logger.info("GraphRAG installation and test completed successfully.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
