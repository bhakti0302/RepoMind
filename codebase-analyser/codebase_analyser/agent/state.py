"""
State definition for the LangGraph agent.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

@dataclass
class AgentState:
    """State for the agent graph."""
    
    # Input requirements
    requirements: Dict[str, Any] = field(default_factory=dict)
    
    # Optional prompt template
    prompt_template: Optional[str] = None
    
    # Processed requirements
    processed_requirements: Dict[str, Any] = field(default_factory=dict)
    
    # Context information
    architectural_context: List[Dict[str, Any]] = field(default_factory=list)
    implementation_context: List[Dict[str, Any]] = field(default_factory=list)
    combined_context: str = ""
    
    # Generated code
    generated_code: str = ""
    
    # Validation results
    validation_result: Dict[str, Any] = field(default_factory=dict)
    
    # Human feedback
    human_feedback: Optional[str] = None
    
    # Errors encountered during execution
    errors: List[Dict[str, Any]] = field(default_factory=list)
    
    # Output for downstream agents
    downstream_data: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamp for tracking execution time
    timestamp: Optional[datetime] = None
    
    # File path where the code was saved
    file_path: Optional[str] = None
    
    def __repr__(self) -> str:
        """String representation of the state."""
        return (
            f"AgentState(requirements={self.requirements}, "
            f"processed_requirements={self.processed_requirements}, "
            f"generated_code_length={len(self.generated_code) if self.generated_code else 0}, "
            f"validation_result={self.validation_result}, "
            f"errors={self.errors}, "
            f"timestamp={self.timestamp})"
        )
