# # Create a fixed version of the component analyzer

# """
# Component Analyzer module.

# This module provides functionality for analyzing components in requirements text.
# """

# import os
# import sys
# import logging
# import re
# from typing import Dict, List, Any, Optional

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
# )
# logger = logging.getLogger(__name__)

# class ComponentAnalyzer:
#     """Component analyzer for requirements text."""
    
#     def __init__(self, nlp=None):
#         """Initialize the component analyzer.
        
#         Args:
#             nlp: spaCy NLP model (optional)
#         """
#         self.nlp = nlp
    
#     def analyze_components(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
#         """Analyze components in text.
        
#         Args:
#             text: Text to analyze
            
#         Returns:
#             Dictionary of component types and lists of components
#         """
#         try:
#             # Initialize components
#             components = {
#                 "functional_requirements": [],
#                 "non_functional_requirements": [],
#                 "constraints": [],
#                 "actions": []
#             }
            
#             # Extract sections
#             sections = self._extract_sections(text)
            
#             # Process functional requirements
#             if "functional_requirements" in sections:
#                 functional_text = sections["functional_requirements"]
#                 requirements = self._extract_requirements(functional_text)
#                 for req in requirements:
#                     components["functional_requirements"].append({
#                         "text": req,
#                         "start": text.find(req),
#                         "end": text.find(req) + len(req)
#                     })
            
#             # Process non-functional requirements
#             if "non_functional_requirements" in sections:
#                 non_functional_text = sections["non_functional_requirements"]
#                 requirements = self._extract_requirements(non_functional_text)
#                 for req in requirements:
#                     components["non_functional_requirements"].append({
#                         "text": req,
#                         "start": text.find(req),
#                         "end": text.find(req) + len(req)
#                     })
            
#             # Extract constraints from requirements
#             constraints = []
            
#             # Add functional requirements that contain constraints
#             for req in components["functional_requirements"]:
#                 if any(modal in req["text"].lower() for modal in ["must", "should", "shall", "will"]):
#                     constraints.append({
#                         "type": "requirement",
#                         "text": req["text"],
#                         "start": req["start"],
#                         "end": req["end"]
#                     })
            
#             # Add non-functional requirements that contain constraints
#             for req in components["non_functional_requirements"]:
#                 if any(modal in req["text"].lower() for modal in ["must", "should", "shall", "will"]):
#                     constraints.append({
#                         "type": "requirement",
#                         "text": req["text"],
#                         "start": req["start"],
#                         "end": req["end"]
#                     })
            
#             components["constraints"] = constraints
            
#             # Extract actions (verbs with subjects and objects)
#             actions = self._extract_actions(text)
#             components["actions"] = actions
            
#             return components
        
#         except Exception as e:
#             logger.error(f"Error analyzing components: {e}")
#             return {
#                 "functional_requirements": [],
#                 "non_functional_requirements": [],
#                 "constraints": [],
#                 "actions": []
#             }
    
#     def _extract_sections(self, text: str) -> Dict[str, str]:
#         """Extract sections from text.
        
#         Args:
#             text: Text to extract sections from
            
#         Returns:
#             Dictionary of section types and section text
#         """
#         sections = {}
        
#         # Define section patterns
#         section_patterns = {
#             "functional_requirements": r"#+\s*Functional\s+Requirements\s*\n(.*?)(?=#+\s*|\Z)",
#             "non_functional_requirements": r"#+\s*Non-?Functional\s+Requirements\s*\n(.*?)(?=#+\s*|\Z)"
#         }
        
#         # Extract sections
#         for section_type, pattern in section_patterns.items():
#             matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
#             if matches:
#                 sections[section_type] = matches[0]
        
#         return sections
    
#     def _extract_requirements(self, text: str) -> List[str]:
#         """Extract requirements from text.
        
#         Args:
#             text: Text to extract requirements from
            
#         Returns:
#             List of requirements
#         """
#         # Clean up the text
#         text = text.strip()
        
#         # Extract numbered requirements
#         requirements = []
        
#         # Pattern for numbered requirements (e.g., "1. Requirement text")
#         numbered_pattern = r"(\d+\.)\s*(.*?)(?=\d+\.|$)"
#         matches = re.findall(numbered_pattern, text, re.DOTALL)
        
#         if matches:
#             for _, req_text in matches:
#                 # Clean up the requirement text
#                 req_text = req_text.strip()
#                 if req_text:
#                     requirements.append(req_text)
#         else:
#             # If no numbered requirements, try bullet points
#             bullet_pattern = r"[-*]\s*(.*?)(?=[-*]|$)"
#             matches = re.findall(bullet_pattern, text, re.DOTALL)
            
#             if matches:
#                 for req_text in matches:
#                     # Clean up the requirement text
#                     req_text = req_text.strip()
#                     if req_text:
#                         requirements.append(req_text)
#             else:
#                 # If no bullet points, split by lines
#                 lines = [line.strip() for line in text.split("\n") if line.strip()]
#                 for line in lines:
#                     # Skip lines that look like headers
#                     if not line.startswith("#"):
#                         requirements.append(line)
        
#         return requirements
    
#     def _extract_actions(self, text: str) -> List[Dict[str, Any]]:
#         """Extract actions from text.
        
#         Args:
#             text: Text to extract actions from
            
#         Returns:
#             List of actions
#         """
#         actions = []
        
#         # Define common action verbs
#         action_verbs = ["search", "display", "respond", "handle"]
        
#         # Find sentences containing action verbs
#         sentences = re.split(r'(?<=[.!?])\s+', text)
        
#         for sentence in sentences:
#             for verb in action_verbs:
#                 match = re.search(r'\b' + verb + r'\b', sentence, re.IGNORECASE)
#                 if match:
#                     # Extract subject (simplified)
#                     subject_match = re.search(r'\b(system|user|application|service|component)\b', 
#                                              sentence, re.IGNORECASE)
#                     subject = subject_match.group(0) if subject_match else ""
                    
#                     # Extract object (simplified)
#                     words_after_verb = sentence[match.end():].strip()
#                     object_match = re.search(r'\b\w+\b', words_after_verb)
#                     obj = object_match.group(0) if object_match else ""
                    
#                     # Add the action
#                     actions.append({
#                         "verb": verb,
#                         "text": verb,
#                         "subjects": [subject] if subject else [],
#                         "objects": [obj] if obj else [],
#                         "start": text.find(sentence) + match.start(),
#                         "end": text.find(sentence) + match.end()
#                     })
#                     break  # Only add the verb once per sentence
        
#         return actions



# Create a backup of the original file

# Edit the component analyzer
"""
Component Analyzer module.

This module provides functionality for analyzing components in requirements text.
"""

import os
import sys
import logging
import re
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class ComponentAnalyzer:
    """Component analyzer for requirements text."""
    
    def __init__(self, nlp=None):
        """Initialize the component analyzer.
        
        Args:
            nlp: spaCy NLP model (optional)
        """
        self.nlp = nlp
    
    def analyze_components(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze components in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary of component types and lists of components
        """
        try:
            # Initialize components
            components = {
                "functional_requirements": [],
                "non_functional_requirements": [],
                "constraints": [],
                "actions": []
            }
            
            # Extract sections
            sections = self._extract_sections(text)
            
            # If no sections were found using headers, try to extract requirements directly
            if not sections:
                # Look for requirements-like statements in the text
                requirements = self._extract_requirements_from_text(text)
                
                # Categorize requirements
                for req in requirements:
                    # Simple heuristic: if it contains words like "performance", "security", "usability",
                    # it's likely a non-functional requirement
                    non_functional_keywords = ["performance", "security", "usability", "reliability", 
                                              "availability", "maintainability", "scalability", "response time",
                                              "throughput", "capacity", "compliance", "compatibility"]
                    
                    is_non_functional = any(keyword in req.lower() for keyword in non_functional_keywords)
                    
                    if is_non_functional:
                        components["non_functional_requirements"].append({
                            "text": req,
                            "start": text.find(req),
                            "end": text.find(req) + len(req)
                        })
                    else:
                        components["functional_requirements"].append({
                            "text": req,
                            "start": text.find(req),
                            "end": text.find(req) + len(req)
                        })
            else:
                # Process functional requirements
                if "functional_requirements" in sections:
                    functional_text = sections["functional_requirements"]
                    requirements = self._extract_requirements(functional_text)
                    for req in requirements:
                        components["functional_requirements"].append({
                            "text": req,
                            "start": text.find(req),
                            "end": text.find(req) + len(req)
                        })
                
                # Process non-functional requirements
                if "non_functional_requirements" in sections:
                    non_functional_text = sections["non_functional_requirements"]
                    requirements = self._extract_requirements(non_functional_text)
                    for req in requirements:
                        components["non_functional_requirements"].append({
                            "text": req,
                            "start": text.find(req),
                            "end": text.find(req) + len(req)
                        })
            
            # Extract constraints (modal verbs with context)
            constraints = self._extract_constraints(text)
            components["constraints"] = constraints
            
            # Extract actions (verbs with subjects and objects)
            actions = self._extract_actions(text)
            components["actions"] = actions
            
            return components
        
        except Exception as e:
            logger.error(f"Error analyzing components: {e}")
            return {
                "functional_requirements": [],
                "non_functional_requirements": [],
                "constraints": [],
                "actions": []
            }
    
    def _extract_sections(self, text: str) -> Dict[str, str]:
        """Extract sections from text.
        
        Args:
            text: Text to extract sections from
            
        Returns:
            Dictionary of section types and section text
        """
        sections = {}
        
        # Define section patterns (more flexible)
        section_patterns = {
            "functional_requirements": [
                r"#+\s*Functional\s+Requirements\s*\n(.*?)(?=#+\s*|\Z)",
                r"Functional\s+Requirements:?\s*\n(.*?)(?=\w+:|\Z)",
                r"User\s+Requirements:?\s*\n(.*?)(?=\w+:|\Z)",
                r"Features:?\s*\n(.*?)(?=\w+:|\Z)",
                r"Requirements:?\s*\n(.*?)(?=\w+:|\Z)"
            ],
            "non_functional_requirements": [
                r"#+\s*Non-?Functional\s+Requirements\s*\n(.*?)(?=#+\s*|\Z)",
                r"Non-?Functional\s+Requirements:?\s*\n(.*?)(?=\w+:|\Z)",
                r"System\s+Requirements:?\s*\n(.*?)(?=\w+:|\Z)",
                r"Quality\s+Attributes:?\s*\n(.*?)(?=\w+:|\Z)",
                r"Constraints:?\s*\n(.*?)(?=\w+:|\Z)"
            ]
        }
        
        # Extract sections
        for section_type, patterns in section_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
                if matches:
                    sections[section_type] = matches[0]
                    break
        
        return sections
    
    def _extract_requirements(self, text: str) -> List[str]:
        """Extract requirements from text.
        
        Args:
            text: Text to extract requirements from
            
        Returns:
            List of requirements
        """
        # Clean up the text
        text = text.strip()
        
        # Extract numbered requirements
        requirements = []
        
        # Pattern for numbered requirements (e.g., "1. Requirement text")
        numbered_pattern = r"(\d+\.)\s*(.*?)(?=\d+\.|$)"
        matches = re.findall(numbered_pattern, text, re.DOTALL)
        
        if matches:
            for _, req_text in matches:
                # Clean up the requirement text
                req_text = req_text.strip()
                if req_text:
                    requirements.append(req_text)
        else:
            # If no numbered requirements, try bullet points
            bullet_pattern = r"[-*]\s*(.*?)(?=[-*]|$)"
            matches = re.findall(bullet_pattern, text, re.DOTALL)
            
            if matches:
                for req_text in matches:
                    # Clean up the requirement text
                    req_text = req_text.strip()
                    if req_text:
                        requirements.append(req_text)
            else:
                # If no bullet points, split by lines
                lines = [line.strip() for line in text.split("\n") if line.strip()]
                for line in lines:
                    # Skip lines that look like headers
                    if not line.startswith("#"):
                        requirements.append(line)
        
        return requirements
    
    def _extract_requirements_from_text(self, text: str) -> List[str]:
        """Extract requirements directly from text without relying on sections.
        
        Args:
            text: Text to extract requirements from
            
        Returns:
            List of requirements
        """
        requirements = []
        
        # Look for sentences that might be requirements
        # Requirements often contain modal verbs like "shall", "should", "must", "will"
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Skip short sentences
            if len(sentence.split()) < 3:
                continue
                
            # Check if it looks like a requirement
            if (re.search(r'\b(shall|should|must|will|need|require|support|provide|allow|enable)\b', 
                         sentence, re.IGNORECASE) or
                re.search(r'\bsystem\b.*\b(display|show|list|present|generate|create|store|retrieve|process)\b', 
                         sentence, re.IGNORECASE)):
                requirements.append(sentence)
        
        # Also look for numbered or bulleted items
        numbered_pattern = r"(\d+\.)\s*(.*?)(?=\d+\.|$)"
        matches = re.findall(numbered_pattern, text, re.DOTALL)
        
        if matches:
            for _, req_text in matches:
                req_text = req_text.strip()
                if req_text and len(req_text.split()) >= 3:
                    requirements.append(req_text)
        
        bullet_pattern = r"[-*]\s*(.*?)(?=[-*]|$)"
        matches = re.findall(bullet_pattern, text, re.DOTALL)
        
        if matches:
            for req_text in matches:
                req_text = req_text.strip()
                if req_text and len(req_text.split()) >= 3:
                    requirements.append(req_text)
        
        return requirements
    
    def _extract_constraints(self, text: str) -> List[Dict[str, Any]]:
        """Extract constraints from text.
        
        Args:
            text: Text to extract constraints from
            
        Returns:
            List of constraints
        """
        constraints = []
        
        # Define modal verbs
        modal_verbs = ["must", "should", "shall", "will", "may", "can", "could", "would"]
        
        # Find sentences containing modal verbs
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        for sentence in sentences:
            for modal in modal_verbs:
                if re.search(r'\b' + modal + r'\b', sentence, re.IGNORECASE):
                    # Found a constraint
                    constraints.append({
                        "type": "modal",
                        "text": sentence.strip(),
                        "start": text.find(sentence),
                        "end": text.find(sentence) + len(sentence)
                    })
                    break  # Only add the sentence once
        
        return constraints
    
    def _extract_actions(self, text: str) -> List[Dict[str, Any]]:
        """Extract actions from text.
        
        Args:
            text: Text to extract actions from
            
        Returns:
            List of actions
        """
        actions = []
        
        # Define common action verbs
        action_verbs = ["implement", "create", "develop", "build", "design", "provide", 
                        "allow", "enable", "support", "manage", "handle", "process", 
                        "display", "show", "view", "search", "find", "retrieve", 
                        "store", "save", "update", "delete", "remove", "add", 
                        "insert", "modify", "change", "track", "monitor", "analyze", 
                        "generate", "calculate", "compute", "validate", "verify", 
                        "check", "test", "debug", "deploy", "install", "configure", 
                        "customize", "integrate", "export", "import", "upload", 
                        "download", "send", "receive", "notify", "alert", "warn", 
                        "log", "record", "report", "print", "scan", "filter", 
                        "sort", "group", "categorize", "classify", "organize", 
                        "schedule", "plan", "execute", "run", "start", "stop", 
                        "pause", "resume", "cancel", "abort", "retry", "repeat", 
                        "refresh", "reload", "reset", "respond", "handle"]
        
        # Find sentences containing action verbs
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        for sentence in sentences:
            for verb in action_verbs:
                match = re.search(r'\b' + verb + r'\b', sentence, re.IGNORECASE)
                if match:
                    # Extract subject (simplified)
                    subject_match = re.search(r'\b(system|user|application|service|component|employee|department)\b', 
                                             sentence, re.IGNORECASE)
                    subject = subject_match.group(0) if subject_match else ""
                    
                    # Extract object (simplified)
                    words_after_verb = sentence[match.end():].strip()
                    object_match = re.search(r'\b\w+\b', words_after_verb)
                    obj = object_match.group(0) if object_match else ""
                    
                    # Add the action
                    actions.append({
                        "verb": verb,
                        "text": verb,
                        "subjects": [subject] if subject else [],
                        "objects": [obj] if obj else [],
                        "start": text.find(sentence) + match.start(),
                        "end": text.find(sentence) + match.end()
                    })
                    break  # Only add the verb once per sentence
        
        return actions
