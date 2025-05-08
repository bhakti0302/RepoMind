#!/usr/bin/env python3
"""
Test script for the embedding generator.
"""

import os
import sys
import argparse
import numpy as np
import json
from pathlib import Path
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

from codebase_analyser.embeddings import EmbeddingGenerator


def test_embedding_generator(
    model_name=None,
    cache_dir=None,
    visualize=False,
    save_dir=None
):
    """Test the embedding generator.
    
    Args:
        model_name: Name of the pre-trained model to use
        cache_dir: Directory to cache the model and tokenizer
        visualize: Whether to visualize the embeddings
        save_dir: Directory to save the visualization
    """
    print(f"Testing embedding generator with model {model_name or 'default'}...")
    
    # Create an embedding generator
    generator = EmbeddingGenerator(
        model_name=model_name,
        cache_dir=cache_dir,
        batch_size=4
    )
    
    # Sample code snippets in different languages
    code_samples = [
        {
            "language": "java",
            "content": """
            public class HelloWorld {
                public static void main(String[] args) {
                    System.out.println("Hello, World!");
                }
            }
            """
        },
        {
            "language": "python",
            "content": """
            def hello_world():
                print("Hello, World!")
                
            if __name__ == "__main__":
                hello_world()
            """
        },
        {
            "language": "javascript",
            "content": """
            function helloWorld() {
                console.log("Hello, World!");
            }
            
            helloWorld();
            """
        },
        {
            "language": "java",
            "content": """
            public class Calculator {
                public int add(int a, int b) {
                    return a + b;
                }
                
                public int subtract(int a, int b) {
                    return a - b;
                }
            }
            """
        },
        {
            "language": "python",
            "content": """
            class Calculator:
                def add(self, a, b):
                    return a + b
                    
                def subtract(self, a, b):
                    return a - b
            """
        },
        {
            "language": "javascript",
            "content": """
            class Calculator {
                add(a, b) {
                    return a + b;
                }
                
                subtract(a, b) {
                    return a - b;
                }
            }
            """
        }
    ]
    
    # Generate embeddings for the code samples
    print("Generating embeddings for code samples...")
    chunks_with_embeddings = generator.generate_embeddings_for_chunks(code_samples)
    
    # Print embedding dimensions
    for i, chunk in enumerate(chunks_with_embeddings):
        embedding = chunk["embedding"]
        print(f"Sample {i+1} ({chunk['language']}): Embedding shape {len(embedding)}")
    
    # Test similarity between embeddings
    print("\nTesting similarity between embeddings...")
    for i in range(len(chunks_with_embeddings)):
        for j in range(i+1, len(chunks_with_embeddings)):
            embedding1 = np.array(chunks_with_embeddings[i]["embedding"])
            embedding2 = np.array(chunks_with_embeddings[j]["embedding"])
            
            # Compute cosine similarity
            similarity = np.dot(embedding1, embedding2)
            
            print(f"Similarity between sample {i+1} ({chunks_with_embeddings[i]['language']}) "
                  f"and sample {j+1} ({chunks_with_embeddings[j]['language']}): {similarity:.4f}")
    
    # Visualize embeddings if requested
    if visualize:
        visualize_embeddings(chunks_with_embeddings, save_dir)
    
    # Close the generator
    generator.close()
    
    print("\nEmbedding generator test completed successfully!")


def visualize_embeddings(chunks_with_embeddings, save_dir=None):
    """Visualize the embeddings using PCA and t-SNE.
    
    Args:
        chunks_with_embeddings: List of code chunks with embeddings
        save_dir: Directory to save the visualization
    """
    print("\nVisualizing embeddings...")
    
    # Extract embeddings and languages
    embeddings = np.array([chunk["embedding"] for chunk in chunks_with_embeddings])
    languages = [chunk["language"] for chunk in chunks_with_embeddings]
    
    # Create a color map for languages
    unique_languages = list(set(languages))
    color_map = {lang: i for i, lang in enumerate(unique_languages)}
    colors = [color_map[lang] for lang in languages]
    
    # Create a figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # PCA visualization
    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(embeddings)
    
    ax1.scatter(pca_result[:, 0], pca_result[:, 1], c=colors, cmap='viridis')
    ax1.set_title('PCA Visualization')
    ax1.set_xlabel('Principal Component 1')
    ax1.set_ylabel('Principal Component 2')
    
    # Add legend
    for lang, color_idx in color_map.items():
        ax1.scatter([], [], c=[color_idx], cmap='viridis', label=lang)
    ax1.legend()
    
    # t-SNE visualization
    tsne = TSNE(n_components=2, random_state=42)
    tsne_result = tsne.fit_transform(embeddings)
    
    ax2.scatter(tsne_result[:, 0], tsne_result[:, 1], c=colors, cmap='viridis')
    ax2.set_title('t-SNE Visualization')
    ax2.set_xlabel('t-SNE Component 1')
    ax2.set_ylabel('t-SNE Component 2')
    
    # Add legend
    for lang, color_idx in color_map.items():
        ax2.scatter([], [], c=[color_idx], cmap='viridis', label=lang)
    ax2.legend()
    
    plt.tight_layout()
    
    # Save the visualization if requested
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
        plt.savefig(os.path.join(save_dir, 'embedding_visualization.png'))
        print(f"Visualization saved to {os.path.join(save_dir, 'embedding_visualization.png')}")
    
    plt.show()


def main():
    parser = argparse.ArgumentParser(description="Test the embedding generator")
    parser.add_argument("--model", help="Name of the pre-trained model to use")
    parser.add_argument("--cache-dir", help="Directory to cache the model and tokenizer")
    parser.add_argument("--visualize", action="store_true", help="Visualize the embeddings")
    parser.add_argument("--save-dir", help="Directory to save the visualization")
    
    args = parser.parse_args()
    
    test_embedding_generator(
        model_name=args.model,
        cache_dir=args.cache_dir,
        visualize=args.visualize,
        save_dir=args.save_dir
    )


if __name__ == "__main__":
    main()
