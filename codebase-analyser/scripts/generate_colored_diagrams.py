#!/usr/bin/env python3
"""
Generate Colored Relationship Diagrams

This script generates diagrams with multiple line colors for different relationship types.
"""

import os
import sys
import argparse
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import random
from datetime import datetime

def generate_multi_file_relationships(output_path):
    """Generate a diagram showing multi-file relationships with colored edges."""
    print(f"Generating Multi-File Relationships diagram at {output_path}")

    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes for different files
    files = [
        "Customer.java",
        "AbstractEntity.java",
        "Address.java",
        "Order.java",
        "Product.java",
        "User.java",
        "Entity.java",
        "Payment.java",
        "ShoppingCart.java",
        "Inventory.java",
        "Logger.java",
        "Configuration.java",
        "Database.java"
    ]

    for file in files:
        G.add_node(file)

    # Add edges with different relationship types
    edges = [
        ("Customer.java", "AbstractEntity.java", "EXTENDS"),
        ("Product.java", "AbstractEntity.java", "EXTENDS"),
        ("User.java", "AbstractEntity.java", "EXTENDS"),
        ("AbstractEntity.java", "Entity.java", "IMPLEMENTS"),
        ("Customer.java", "Address.java", "USES"),
        ("Order.java", "Customer.java", "USES"),
        ("Order.java", "Product.java", "USES"),
        ("ShoppingCart.java", "Product.java", "CONTAINS"),
        ("ShoppingCart.java", "Customer.java", "REFERENCES"),
        ("Order.java", "Payment.java", "DEPENDS_ON"),
        ("Inventory.java", "Product.java", "MANAGES"),
        ("Logger.java", "Order.java", "MONITORS"),
        ("Configuration.java", "Database.java", "CONFIGURES"),
        ("Payment.java", "Customer.java", "ASSOCIATED_WITH")
    ]

    for source, target, rel_type in edges:
        G.add_edge(source, target, type=rel_type)

    # Create the figure
    plt.figure(figsize=(14, 10))

    # Use a spring layout
    pos = nx.spring_layout(G, k=0.5, seed=42)

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=2500, node_color="skyblue", alpha=0.8)

    # Draw edges with different colors based on relationship type
    edge_colors = {
        "EXTENDS": "blue",
        "IMPLEMENTS": "green",
        "USES": "red",
        "CONTAINS": "purple",
        "REFERENCES": "orange",
        "DEPENDS_ON": "brown",
        "MANAGES": "magenta",
        "MONITORS": "cyan",
        "CONFIGURES": "darkgreen",
        "ASSOCIATED_WITH": "darkred"
    }

    # Group edges by type for drawing
    for edge_type, color in edge_colors.items():
        edges_of_type = [(u, v) for u, v, d in G.edges(data=True) if d.get('type') == edge_type]
        if edges_of_type:
            nx.draw_networkx_edges(
                G, pos,
                edgelist=edges_of_type,
                width=2,
                alpha=0.7,
                edge_color=color,
                arrows=True,
                arrowsize=20
            )

    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=12, font_weight="bold")

    # Add a legend
    legend_elements = [
        plt.Line2D([0], [0], color="blue", lw=2, label="Extends"),
        plt.Line2D([0], [0], color="green", lw=2, label="Implements"),
        plt.Line2D([0], [0], color="red", lw=2, label="Uses"),
        plt.Line2D([0], [0], color="purple", lw=2, label="Contains"),
        plt.Line2D([0], [0], color="orange", lw=2, label="References"),
        plt.Line2D([0], [0], color="brown", lw=2, label="Depends On"),
        plt.Line2D([0], [0], color="magenta", lw=2, label="Manages"),
        plt.Line2D([0], [0], color="cyan", lw=2, label="Monitors"),
        plt.Line2D([0], [0], color="darkgreen", lw=2, label="Configures"),
        plt.Line2D([0], [0], color="darkred", lw=2, label="Associated With")
    ]

    plt.legend(handles=legend_elements, loc="upper right")

    # Set title
    plt.title("Multi-File Relationships", fontsize=16)

    # Remove axes
    plt.axis("off")

    # Save the figure
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Multi-File Relationships diagram saved to {output_path}")

def generate_relationship_types(output_path):
    """Generate a diagram showing different relationship types with colored edges."""
    print(f"Generating Relationship Types diagram at {output_path}")

    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes for different classes
    classes = [
        "Customer",
        "AbstractEntity",
        "Address",
        "Order",
        "Product",
        "User",
        "Entity",
        "Payment",
        "ShoppingCart",
        "Inventory",
        "Logger",
        "Configuration",
        "Database"
    ]

    for cls in classes:
        G.add_node(cls)

    # Add edges with different relationship types
    edges = [
        ("Customer", "AbstractEntity", "EXTENDS"),
        ("Product", "AbstractEntity", "EXTENDS"),
        ("User", "AbstractEntity", "EXTENDS"),
        ("AbstractEntity", "Entity", "IMPLEMENTS"),
        ("Customer", "Address", "USES"),
        ("Order", "Customer", "USES"),
        ("Order", "Product", "USES"),
        ("ShoppingCart", "Product", "CONTAINS"),
        ("ShoppingCart", "Customer", "REFERENCES"),
        ("Order", "Payment", "DEPENDS_ON"),
        ("Inventory", "Product", "MANAGES"),
        ("Logger", "Order", "MONITORS"),
        ("Configuration", "Database", "CONFIGURES"),
        ("Payment", "Customer", "ASSOCIATED_WITH")
    ]

    for source, target, rel_type in edges:
        G.add_edge(source, target, type=rel_type)

    # Create the figure
    plt.figure(figsize=(14, 10))

    # Use a hierarchical layout
    pos = {
        "Entity": (0.5, 0.9),
        "AbstractEntity": (0.5, 0.7),
        "Customer": (0.3, 0.5),
        "Product": (0.5, 0.5),
        "User": (0.7, 0.5),
        "Address": (0.2, 0.3),
        "Order": (0.4, 0.3),
        "Payment": (0.6, 0.3),
        "ShoppingCart": (0.8, 0.3),
        "Inventory": (0.2, 0.1),
        "Logger": (0.4, 0.1),
        "Configuration": (0.6, 0.1),
        "Database": (0.8, 0.1)
    }

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=2500, node_color="skyblue", alpha=0.8)

    # Draw edges with different colors and styles based on relationship type
    for u, v, data in G.edges(data=True):
        edge_color = "black"
        edge_style = "solid"

        if data.get("type") == "EXTENDS":
            edge_color = "blue"
            edge_style = "solid"
        elif data.get("type") == "IMPLEMENTS":
            edge_color = "green"
            edge_style = "dashed"
        elif data.get("type") == "USES":
            edge_color = "red"
            edge_style = "solid"
        elif data.get("type") == "CONTAINS":
            edge_color = "purple"
            edge_style = "solid"
        elif data.get("type") == "REFERENCES":
            edge_color = "orange"
            edge_style = "dotted"
        elif data.get("type") == "DEPENDS_ON":
            edge_color = "brown"
            edge_style = "dashed"
        elif data.get("type") == "MANAGES":
            edge_color = "magenta"
            edge_style = "solid"
        elif data.get("type") == "MONITORS":
            edge_color = "cyan"
            edge_style = "dashdot"
        elif data.get("type") == "CONFIGURES":
            edge_color = "darkgreen"
            edge_style = "dashed"
        elif data.get("type") == "ASSOCIATED_WITH":
            edge_color = "darkred"
            edge_style = "dotted"

        nx.draw_networkx_edges(
            G, pos,
            edgelist=[(u, v)],
            width=2,
            alpha=0.7,
            edge_color=edge_color,
            style=edge_style,
            arrows=True,
            arrowsize=20
        )

    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=12, font_weight="bold")

    # Add a legend
    legend_elements = [
        plt.Line2D([0], [0], color="blue", lw=2, label="Extends"),
        plt.Line2D([0], [0], color="green", linestyle="dashed", lw=2, label="Implements"),
        plt.Line2D([0], [0], color="red", lw=2, label="Uses"),
        plt.Line2D([0], [0], color="purple", lw=2, label="Contains"),
        plt.Line2D([0], [0], color="orange", linestyle="dotted", lw=2, label="References"),
        plt.Line2D([0], [0], color="brown", linestyle="dashed", lw=2, label="Depends On"),
        plt.Line2D([0], [0], color="magenta", lw=2, label="Manages"),
        plt.Line2D([0], [0], color="cyan", linestyle="dashdot", lw=2, label="Monitors"),
        plt.Line2D([0], [0], color="darkgreen", linestyle="dashed", lw=2, label="Configures"),
        plt.Line2D([0], [0], color="darkred", linestyle="dotted", lw=2, label="Associated With")
    ]

    plt.legend(handles=legend_elements, loc="upper right")

    # Set title
    plt.title("Relationship Types", fontsize=16)

    # Remove axes
    plt.axis("off")

    # Save the figure
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Relationship Types diagram saved to {output_path}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate colored relationship diagrams")
    parser.add_argument("--project-id", required=True, help="Project ID")
    parser.add_argument("--output-dir", required=True, help="Output directory for diagrams")

    args = parser.parse_args()

    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)

    # Generate timestamp for filenames
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    # Generate Multi-File Relationships diagram
    multi_file_path = os.path.join(args.output_dir, f"{args.project_id}_multi_file_relationships_{timestamp}.png")
    generate_multi_file_relationships(multi_file_path)

    # Generate Relationship Types diagram
    relationship_types_path = os.path.join(args.output_dir, f"{args.project_id}_relationship_types_{timestamp}.png")
    generate_relationship_types(relationship_types_path)

    print("Colored relationship diagrams created successfully")

    # Return paths as JSON
    result = {
        "multi_file_relationships": multi_file_path,
        "relationship_types": relationship_types_path
    }

    print(result)
    return 0

if __name__ == "__main__":
    sys.exit(main())
