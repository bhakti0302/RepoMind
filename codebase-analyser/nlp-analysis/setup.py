# codebase-analyser/nlp-analysis/setup.py
from setuptools import setup, find_packages

setup(
    name="nlp-analysis",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "spacy>=3.5.0",
        "lancedb>=0.3.0",
        "networkx>=3.0",
        "matplotlib>=3.7.0",
        "python-dotenv>=1.0.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "scikit-learn>=1.2.0",
        "transformers>=4.30.0",
        "torch>=2.0.0",
        "openai>=1.0.0",
        "tiktoken>=0.5.0",
        "requests>=2.28.0",
        "tqdm>=4.65.0",
        "pyyaml>=6.0",
        "jsonschema>=4.17.0"
    ],
)