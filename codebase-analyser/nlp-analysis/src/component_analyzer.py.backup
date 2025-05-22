"""
Component Analyzer module.

This module provides functionality for analyzing components in business requirements.
"""

import logging
import spacy
from spacy.tokens import Doc
from typing import Dict, List, Optional, Any, Union, Set

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class ComponentAnalyzer:
    """Analyzer for components in business requirements."""
    
    def __init__(self, nlp=None):
        """Initialize the component analyzer.
        
        Args:
            nlp: spaCy NLP model (if None, will load en_core_web_md)
        """
        self.nlp = nlp
        if self.nlp is None:
            try:
                self.nlp = spacy.load("en_core_web_md")
                logger.info("Loaded spaCy model: en_core_web_md")
            except OSError:
                logger.error("Failed to load spaCy model")
                raise
    
    def extract_actions(self, doc: Doc) -> List[Dict[str, Any]]:
        """Extract actions from a spaCy Doc.
        
        Args:
            doc: spaCy Doc object
            
        Returns:
            List of actions with their objects
        """
        actions = []
        
        for token in doc:
            # Look for verbs
            if token.pos_ == "VERB":
                # Find the subject of the verb
                subjects = [child for child in token.children if child.dep_ in ("nsubj", "nsubjpass")]
                
                # Find the objects of the verb
                objects = [child for child in token.children if child.dep_ in ("dobj", "pobj", "attr")]
                
                # Expand objects to include their children
                expanded_objects = []
                for obj in objects:
                    # Get the full noun phrase
                    if obj.dep_ == "pobj" and obj.head.pos_ == "ADP":
                        # For prepositional objects, include the preposition
                        prep = obj.head.text
                        obj_text = f"{prep} {obj.text}"
                    else:
                        obj_text = obj.text
                    
                    # Include any adjectives or compound nouns
                    for child in obj.children:
                        if child.dep_ in ("amod", "compound"):
                            obj_text = f"{child.text} {obj_text}"
                    
                    expanded_objects.append(obj_text)
                
                # Create action entry
                action = {
                    "verb": token.lemma_,
                    "text": token.text,
                    "subjects": [subj.text for subj in subjects],
                    "objects": expanded_objects,
                    "start": token.idx,
                    "end": token.idx + len(token.text)
                }
                
                actions.append(action)
        
        return actions
    
    def extract_constraints(self, doc: Doc) -> List[Dict[str, Any]]:
        """Extract constraints from a spaCy Doc.
        
        Args:
            doc: spaCy Doc object
            
        Returns:
            List of constraints
        """
        constraints = []
        
        # Look for modal verbs and negations
        for token in doc:
            if token.pos_ == "AUX" and token.tag_ == "MD":
                # Modal verb (should, must, can, etc.)
                constraint = {
                    "type": "modal",
                    "text": token.text,
                    "start": token.idx,
                    "end": token.idx + len(token.text)
                }
                constraints.append(constraint)
            
            elif token.dep_ == "neg":
                # Negation
                constraint = {
                    "type": "negation",
                    "text": token.text,
                    "start": token.idx,
                    "end": token.idx + len(token.text)
                }
                constraints.append(constraint)
        
        # Look for conditional clauses
        for token in doc:
            if token.text.lower() in ("if", "when", "unless", "until", "while"):
                # Find the scope of the condition
                condition_text = self._get_subtree_text(token)
                
                constraint = {
                    "type": "condition",
                    "text": condition_text,
                    "start": token.idx,
                    "end": token.idx + len(condition_text)
                }
                constraints.append(constraint)
        
        return constraints
    
    def _get_subtree_text(self, token) -> str:
        """Get the text of a token's subtree.
        
        Args:
            token: spaCy Token object
            
        Returns:
            Text of the token's subtree
        """
        # Sort the subtree by position in the document
        subtree = sorted([t for t in token.subtree], key=lambda t: t.i)
        
        # Join the text of the subtree
        return " ".join([t.text for t in subtree])
    
    def analyze_components(self, text: str) -> Dict[str, Any]:
        """Analyze components in business requirements text.
        
        Args:
            text: Business requirements text
            
        Returns:
            Dictionary containing analyzed components
        """
        try:
            # Process the text with spaCy
            doc = self.nlp(text)
            
            # Extract actions
            actions = self.extract_actions(doc)
            
            # Extract constraints
            constraints = self.extract_constraints(doc)
            
            # Extract functional requirements (sentences with actions)
            functional_reqs = []
            for sent in doc.sents:
                # Check if the sentence contains a verb
                if any(token.pos_ == "VERB" for token in sent):
                    functional_reqs.append({
                        "text": sent.text,
                        "start": sent.start_char,
                        "end": sent.end_char
                    })
            
            # Extract non-functional requirements (sentences with quality attributes)
            nfr_keywords = {
                "performance", "security", "reliability", "usability", "maintainability",
                "scalability", "availability", "efficiency", "portability", "testability",
                "fast", "secure", "reliable", "user-friendly", "maintainable", "scalable",
                "available", "efficient", "portable", "testable"
            }
            
            non_functional_reqs = []
            for sent in doc.sents:
                # Check if the sentence contains NFR keywords
                sent_text_lower = sent.text.lower()
                if any(keyword in sent_text_lower for keyword in nfr_keywords):
                    non_functional_reqs.append({
                        "text": sent.text,
                        "start": sent.start_char,
                        "end": sent.end_char
                    })
            
            return {
                "actions": actions,
                "constraints": constraints,
                "functional_requirements": functional_reqs,
                "non_functional_requirements": non_functional_reqs
            }
        
        except Exception as e:
            logger.error(f"Error analyzing components: {e}")
            return {"error": str(e)}
    
    def analyze_components_from_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze components in a business requirements file.
        
        Args:
            file_path: Path to the requirements file
            
        Returns:
            Dictionary containing analyzed components
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            logger.info(f"Analyzing components from file: {file_path}")
            return self.analyze_components(text)
        
        except Exception as e:
            logger.error(f"Error reading or analyzing file {file_path}: {e}")
            return {"error": str(e)}


# Example usage
if __name__ == "__main__":
    analyzer = ComponentAnalyzer()
    
    # Example text
    example_text = """
    The system must authenticate users before allowing access to protected resources.
    Users should be able to reset their passwords via email.
    The application should respond to user requests within 500ms.
    If a user enters incorrect credentials, the system should display an error message.
    """
    
    result = analyzer.analyze_components(example_text)
    print("Analyzed Components:")
    
    print("\nActions:")
    for action in result["actions"]:
        print(f"  - {action['verb']} (Subjects: {action['subjects']}, Objects: {action['objects']})")
    
    print("\nConstraints:")
    for constraint in result["constraints"]:
        print(f"  - {constraint['type']}: {constraint['text']}")
    
    print("\nFunctional Requirements:")
    for req in result["functional_requirements"]:
        print(f"  - {req['text']}")
    
    print("\nNon-Functional Requirements:")
    for req in result["non_functional_requirements"]:
        print(f"  - {req['text']}")
