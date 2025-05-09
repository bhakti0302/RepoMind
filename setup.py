#!/usr/bin/env python3
"""
Setup script for the codebase analyser package.
"""

from setuptools import setup, find_packages

setup(
    name="codebase_analyser",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "tree-sitter",
        "numpy",
        "pandas",
        "transformers",
        "torch",
        "lancedb",
        "pyarrow",
        "matplotlib",
        "networkx",
        "pydot"
    ],
    python_requires=">=3.8",
    author="RepoMind Team",
    author_email="example@example.com",
    description="A tool for analyzing codebases and generating embeddings",
    keywords="code, analysis, embeddings, ast, parsing",
    url="https://github.com/yourusername/repomind",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
