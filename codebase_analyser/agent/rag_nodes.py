"""
RAG (Retrieval-Augmented Generation) nodes for the agent.
"""
import os
import logging
import json
from typing import Dict, List, Any
import numpy as np

from ..database import open_unified_storage, close_unified_storage
from ..embeddings import EmbeddingGenerator
from ..state import AgentState
from ...database.lancedb_manager import LanceDBManager
from ...retrieval.multi_hop import retrieve_architectural_patterns, retrieve_implementation_details
from ...retrieval.relevance import score_relevance

logger = logging.getLogger(__name__)

async def retrieve_architectural_context(state: AgentState) -> AgentState:
    """Retrieve architectural context from the codebase."""
    try:
        # Get the requirements
        requirements = state.requirements
        
        # Extract key information for retrieval
        query = requirements.get("description", "")
        language = requirements.get("language", "")
        
        # Retrieve architectural patterns
        patterns = await retrieve_architectural_patterns(query, language)
        
        # Update the state
        return AgentState(
            **state.dict(),
            architectural_context=patterns
        )
    except Exception as e:
        # Log the error and return the original state
        print(f"Error retrieving architectural context: {str(e)}")
        return state

async def retrieve_implementation_context(state: AgentState) -> AgentState:
    """Retrieve implementation context from the codebase."""
    try:
        # Get the requirements and architectural context
        requirements = state.requirements
        architectural_context = state.architectural_context
        
        # Extract key information for retrieval
        query = requirements.get("description", "")
        language = requirements.get("language", "")
        
        # Use architectural context to guide implementation details retrieval
        details = await retrieve_implementation_details(
            query, 
            language, 
            architectural_context
        )
        
        # Update the state
        return AgentState(
            **state.dict(),
            implementation_context=details
        )
    except Exception as e:
        # Log the error and return the original state
        print(f"Error retrieving implementation context: {str(e)}")
        return state

async def combine_context(state: AgentState) -> AgentState:
    """Combine architectural and implementation context."""
    try:
        # Get the contexts
        architectural_context = state.architectural_context
        implementation_context = state.implementation_context
        
        # Score relevance of each context item
        scored_arch = score_relevance(architectural_context, state.requirements)
        scored_impl = score_relevance(implementation_context, state.requirements)
        
        # Sort by relevance score
        sorted_arch = sorted(scored_arch, key=lambda x: x["score"], reverse=True)
        sorted_impl = sorted(scored_impl, key=lambda x: x["score"], reverse=True)
        
        # Take top N most relevant items
        top_arch = sorted_arch[:3]  # Adjust number as needed
        top_impl = sorted_impl[:5]  # Adjust number as needed
        
        # Format the combined context
        combined = "ARCHITECTURAL PATTERNS:\n"
        for item in top_arch:
            combined += f"- {item['name']} (Score: {item['score']:.2f})\n"
            combined += f"  {item['description']}\n"
            combined += f"  Example: {item['example']}\n\n"
        
        combined += "\nIMPLEMENTATION DETAILS:\n"
        for item in top_impl:
            combined += f"- {item['name']} (Score: {item['score']:.2f})\n"
            combined += f"  {item['code']}\n\n"
        
        # Update the state
        return AgentState(
            **state.dict(),
            combined_context=combined
        )
    except Exception as e:
        # Log the error and return the original state
        print(f"Error combining context: {str(e)}")
        return state
