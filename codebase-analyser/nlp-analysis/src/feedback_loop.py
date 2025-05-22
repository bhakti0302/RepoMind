"""
Feedback Loop module.

This module provides functionality for iterative improvement through feedback.
"""

import os
import sys
import logging
import json
import time
from typing import Dict, List, Any, Optional, Union, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import local modules
from src.code_validator import CodeValidator
from src.prompt_builder import PromptBuilder
from src.output_formatter import OutputFormatter
from src.utils import save_json, load_json, ensure_dir

class FeedbackLoop:
    """Loop for iterative improvement through feedback."""
    
    def __init__(
        self,
        output_dir: str = None,
        max_iterations: int = 3,
        improvement_threshold: float = 0.1
    ):
        """Initialize the feedback loop.
        
        Args:
            output_dir: Path to the output directory
            max_iterations: Maximum number of iterations
            improvement_threshold: Threshold for improvement
        """
        self.output_dir = output_dir
        self.max_iterations = max_iterations
        self.improvement_threshold = improvement_threshold
        
        # Initialize components
        self.code_validator = CodeValidator()
        self.prompt_builder = PromptBuilder()
        self.output_formatter = OutputFormatter(output_dir=output_dir)
        
        # Create output directory if specified
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def _evaluate_code(
        self,
        code: str,
        language: str = None
    ) -> Dict[str, Any]:
        """Evaluate code quality.
        
        Args:
            code: Generated code
            language: Programming language
            
        Returns:
            Dictionary containing evaluation results
        """
        try:
            # Validate syntax
            validation_result = self.code_validator.validate_syntax(code, language)
            
            # Check style
            style_result = self.code_validator.check_style(code, language)
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(validation_result, style_result)
            
            return {
                "validation_result": validation_result,
                "style_result": style_result,
                "quality_score": quality_score
            }
        
        except Exception as e:
            logger.error(f"Error evaluating code: {e}")
            return {
                "validation_result": {"valid": False, "errors": [str(e)]},
                "style_result": {"valid": False, "errors": [str(e)]},
                "quality_score": 0.0
            }
    
    def _calculate_quality_score(
        self,
        validation_result: Dict[str, Any],
        style_result: Dict[str, Any]
    ) -> float:
        """Calculate code quality score.
        
        Args:
            validation_result: Validation results
            style_result: Style check results
            
        Returns:
            Quality score between 0 and 1
        """
        try:
            # Initialize score
            score = 1.0
            
            # Deduct points for syntax errors
            if not validation_result["valid"]:
                error_count = len(validation_result["errors"])
                syntax_penalty = min(0.5, error_count * 0.1)
                score -= syntax_penalty
            
            # Deduct points for style issues
            if not style_result["valid"]:
                warning_count = len(style_result["warnings"])
                style_penalty = min(0.3, warning_count * 0.05)
                score -= style_penalty
            
            # Ensure score is between 0 and 1
            return max(0.0, min(1.0, score))
        
        except Exception as e:
            logger.error(f"Error calculating quality score: {e}")
            return 0.0
    
    def _generate_feedback(
        self,
        evaluation_result: Dict[str, Any],
        iteration: int
    ) -> str:
        """Generate feedback based on evaluation results.
        
        Args:
            evaluation_result: Evaluation results
            iteration: Current iteration
            
        Returns:
            Generated feedback
        """
        try:
            # Get validation and style results
            validation_result = evaluation_result["validation_result"]
            style_result = evaluation_result["style_result"]
            quality_score = evaluation_result["quality_score"]
            
            # Generate feedback
            feedback = self.code_validator.generate_feedback(validation_result, style_result)
            
            # Add quality score
            feedback += f"\n\n## Quality Score\n\nYour code has a quality score of {quality_score:.2f} out of 1.0."
            
            # Add iteration-specific feedback
            if iteration < self.max_iterations:
                feedback += f"\n\n## Next Steps\n\nThis is iteration {iteration} of {self.max_iterations}. "
                feedback += "Please address the issues mentioned above and improve your implementation."
            else:
                feedback += "\n\n## Final Feedback\n\nThis is the final iteration. "
                
                if quality_score >= 0.8:
                    feedback += "Your implementation is of high quality. Great job!"
                elif quality_score >= 0.6:
                    feedback += "Your implementation is acceptable but could be improved further."
                else:
                    feedback += "Your implementation needs significant improvement."
            
            return feedback
        
        except Exception as e:
            logger.error(f"Error generating feedback: {e}")
            return f"Error generating feedback: {e}"
    
    def run_feedback_loop(
        self,
        requirements: str,
        context: str,
        initial_code: str,
        language: str = None,
        llm_client = None
    ) -> Dict[str, Any]:
        """Run the feedback loop for iterative improvement.
        
        Args:
            requirements: Business requirements
            context: Retrieved context
            initial_code: Initial code implementation
            language: Programming language
            llm_client: Client for LLM API
            
        Returns:
            Dictionary containing feedback loop results
        """
        try:
            logger.info("Starting feedback loop")
            
            # Initialize results
            results = {
                "iterations": [],
                "final_code": initial_code,
                "final_quality_score": 0.0,
                "improvement": 0.0
            }
            
            # Initialize current code
            current_code = initial_code
            
            # Evaluate initial code
            initial_evaluation = self._evaluate_code(current_code, language)
            initial_quality_score = initial_evaluation["quality_score"]
            
            # Add initial iteration
            results["iterations"].append({
                "iteration": 0,
                "code": current_code,
                "evaluation": initial_evaluation,
                "feedback": self._generate_feedback(initial_evaluation, 0)
            })
            
            # Run iterations
            for i in range(1, self.max_iterations + 1):
                logger.info(f"Running iteration {i}")
                
                # Get previous iteration
                prev_iteration = results["iterations"][-1]
                prev_code = prev_iteration["code"]
                prev_evaluation = prev_iteration["evaluation"]
                prev_quality_score = prev_evaluation["quality_score"]
                
                # Generate feedback
                feedback = self._generate_feedback(prev_evaluation, i)
                
                # Check if code is already perfect
                if prev_quality_score >= 0.95:
                    logger.info("Code is already of high quality. Stopping iterations.")
                    break
                
                # Build refinement prompt
                refinement_prompt = self.prompt_builder.build_code_refinement_prompt(
                    requirements=requirements,
                    context=context,
                    initial_code=prev_code,
                    feedback=feedback
                )
                
                # Get refined code from LLM
                if llm_client:
                    # Use LLM client to get refined code
                    llm_response = llm_client.generate(refinement_prompt)
                    refined_code = llm_response
                else:
                    # Simulate LLM response for testing
                    logger.warning("No LLM client provided. Using initial code as refined code.")
                    refined_code = prev_code
                
                # Evaluate refined code
                evaluation = self._evaluate_code(refined_code, language)
                quality_score = evaluation["quality_score"]
                
                # Add iteration
                results["iterations"].append({
                    "iteration": i,
                    "code": refined_code,
                    "evaluation": evaluation,
                    "feedback": self._generate_feedback(evaluation, i),
                    "improvement": quality_score - prev_quality_score
                })
                
                # Update current code
                current_code = refined_code
                
                # Check if improvement is below threshold
                if quality_score - prev_quality_score < self.improvement_threshold:
                    logger.info(f"Improvement below threshold ({quality_score - prev_quality_score:.2f} < {self.improvement_threshold}). Stopping iterations.")
                    break
                
                # Add delay to avoid rate limiting
                time.sleep(1)
            
            # Set final results
            final_iteration = results["iterations"][-1]
            results["final_code"] = final_iteration["code"]
            results["final_quality_score"] = final_iteration["evaluation"]["quality_score"]
            results["improvement"] = results["final_quality_score"] - initial_quality_score
            
            # Save results if output directory is specified
            if self.output_dir:
                # Save final code
                code_blocks = self.output_formatter.extract_code_from_llm_response(results["final_code"])
                saved_files = self.output_formatter.save_extracted_code(code_blocks, self.output_dir)
                
                # Save feedback loop results
                results_file = os.path.join(self.output_dir, "feedback_loop_results.json")
                save_json(results, results_file)
                
                logger.info(f"Saved feedback loop results to {results_file}")
                logger.info(f"Saved final code to {', '.join(saved_files)}")
            
            return results
        
        except Exception as e:
            logger.error(f"Error running feedback loop: {e}")
            return {"error": str(e)}
    
    def collect_user_feedback(
        self,
        code: str,
        user_feedback: str
    ) -> Dict[str, Any]:
        """Collect user feedback for learning.
        
        Args:
            code: Generated code
            user_feedback: User feedback
            
        Returns:
            Dictionary containing feedback collection results
        """
        try:
            logger.info("Collecting user feedback")
            
            # Create feedback entry
            feedback_entry = {
                "timestamp": time.time(),
                "code": code,
                "user_feedback": user_feedback
            }
            
            # Save feedback if output directory is specified
            if self.output_dir:
                # Create feedback directory
                feedback_dir = os.path.join(self.output_dir, "user_feedback")
                ensure_dir(feedback_dir)
                
                # Save feedback entry
                feedback_file = os.path.join(feedback_dir, f"feedback_{int(time.time())}.json")
                save_json(feedback_entry, feedback_file)
                
                logger.info(f"Saved user feedback to {feedback_file}")
            
            return feedback_entry
        
        except Exception as e:
            logger.error(f"Error collecting user feedback: {e}")
            return {"error": str(e)}


# Example usage
if __name__ == "__main__":
    # Create a feedback loop
    feedback_loop = FeedbackLoop(output_dir="output")
    
    # Example requirements
    requirements = """
    The system should implement a UserService class that handles authentication.
    The login method should verify user credentials against the database.
    The system should return JWT tokens for authenticated users.
    """
    
    # Example context
    context = """
    public class UserService {
        private final UserRepository userRepository;
        
        public UserService(UserRepository userRepository) {
            this.userRepository = userRepository;
        }
        
        // Other methods...
    }
    """
    
    # Example initial code
    initial_code = """
    ## File: UserService.java
    ```java
    public class UserService {
        private final UserRepository userRepository;
        
        public UserService(UserRepository userRepository) {
            this.userRepository = userRepository;
        }
        
        public User authenticate(String username, String password) {
            User user = userRepository.findByUsername(username);
            if (user != null && passwordEncoder.matches(password, user.getPassword())) {
                return user;
            }
            return null;
        }
    }
    ```
    """
    
    # Run feedback loop
    results = feedback_loop.run_feedback_loop(
        requirements=requirements,
        context=context,
        initial_code=initial_code,
        language="java"
    )
    
    # Print results
    print(f"Final quality score: {results['final_quality_score']:.2f}")
    print(f"Improvement: {results['improvement']:.2f}")
    
    # Collect user feedback
    user_feedback = "The implementation is good, but it should also handle account locking after failed attempts."
    feedback_entry = feedback_loop.collect_user_feedback(results["final_code"], user_feedback)
    
    print(f"User feedback collected: {feedback_entry['user_feedback']}")
