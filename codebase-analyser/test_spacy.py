"""
Simple test script to verify spaCy installation.
"""
import sys
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")

try:
    import spacy
    print(f"spaCy version: {spacy.__version__}")
    
    # Try loading the model
    try:
        nlp = spacy.load("en_core_web_md")
        print("Successfully loaded en_core_web_md model")
        
        # Test the model
        doc = nlp("This is a test sentence to verify spaCy is working correctly.")
        print("Tokens:", [token.text for token in doc])
        print("Entities:", [(ent.text, ent.label_) for ent in doc.ents])
        
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Try running: python -m spacy download en_core_web_md")
        
except ImportError:
    print("spaCy is not installed. Install it with: pip install spacy")