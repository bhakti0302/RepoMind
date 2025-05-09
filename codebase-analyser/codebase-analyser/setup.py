from setuptools import setup, find_packages

setup(
    name="codebase_analyser",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "tree-sitter>=0.20.1",
        "tree-sitter-languages>=1.5.0",
        "lancedb>=0.3.3",
        "numpy>=1.24.3",
        "pydantic>=2.4.2",
        "transformers>=4.34.0",
        "torch>=2.0.1",
        "tqdm>=4.66.1",
    ],
    python_requires=">=3.8",
    author="RepoMind Team",
    author_email="team@repomind.example.com",
    description="Codebase analysis service for RepoMind",
    keywords="code-analysis, tree-sitter, embeddings",
    url="https://github.com/yourusername/repomind",
)