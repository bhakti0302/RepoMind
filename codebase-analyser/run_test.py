#!/usr/bin/env python3
"""
Script to run the test_agent.py with the OpenRouter API key.
"""
import os
import subprocess
import sys

def main():
    # Set the OpenRouter API key
    os.environ["OPENROUTER_API_KEY"] = "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"
    
    # Run the test_agent.py script
    subprocess.run([sys.executable, "test_agent.py"])

if __name__ == "__main__":
    main()