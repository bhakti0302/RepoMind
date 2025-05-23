"""
Relevance Scorer module.

This module provides functionality for scoring and ranking search results.
"""

import os
import sys
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class RelevanceScorer:
    """Scorer for ranking search results by relevance."""

    def __init__(
        self,
        semantic_weight: float = 0.5,
        type_weight: float = 0.2,
        graph_weight: float = 0.2,
        recency_weight: float = 0.1,
        weights_config: Dict[str, float] = None
    ):
        """Initialize the relevance scorer.

        Args:
            semantic_weight: Weight for semantic similarity score
            type_weight: Weight for chunk type relevance
            graph_weight: Weight for graph proximity
            recency_weight: Weight for recency (if available)
            weights_config: Custom weights configuration
        """
        # Set default weights
        self.semantic_weight = semantic_weight
        self.type_weight = type_weight
        self.graph_weight = graph_weight
        self.recency_weight = recency_weight

        # Override with custom weights if provided
        if weights_config:
            self.semantic_weight = weights_config.get("semantic", semantic_weight)
            self.type_weight = weights_config.get("type", type_weight)
            self.graph_weight = weights_config.get("graph", graph_weight)
            self.recency_weight = weights_config.get("recency", recency_weight)

        # Normalize weights to sum to 1.0
        total_weight = self.semantic_weight + self.type_weight + self.graph_weight + self.recency_weight
        if total_weight > 0:
            self.semantic_weight /= total_weight
            self.type_weight /= total_weight
            self.graph_weight /= total_weight
            self.recency_weight /= total_weight

        # Define relevance scores for different chunk types
        self.type_relevance = {
            "class": 1.0,
            "interface": 0.9,
            "method": 0.8,
            "field": 0.7,
            "file": 0.6,
            "package": 0.5,
            "import": 0.4,
            "comment": 0.3
        }

        # Define relevance scores for different relationship types
        self.relationship_relevance = {
            "CONTAINS": 1.0,
            "IMPLEMENTS": 0.9,
            "EXTENDS": 0.9,
            "CALLS": 0.8,
            "USES": 0.7,
            "IMPORTS": 0.6,
            "REFERENCES": 0.5
        }

    def score_result(self, result: Dict[str, Any], query: str = None) -> float:
        """Score a single search result.

        Args:
            result: Search result
            query: Original query (for additional scoring)

        Returns:
            Relevance score between 0 and 1
        """
        try:
            # Get the semantic similarity score (already between 0 and 1)
            semantic_score = result.get("score", 0.0)

            # Get the chunk type score
            chunk_type = result.get("chunk_type", "").lower()
            type_score = self.type_relevance.get(chunk_type, 0.5)

            # Get the graph proximity score
            graph_score = 0.0

            # Check for relationship information
            relationship_type = result.get("relationship_to_result")
            if relationship_type:
                # Get the relationship score
                graph_score = self.relationship_relevance.get(relationship_type, 0.5)

            # Check for hop distance (multi-hop traversal)
            hop_distance = result.get("hop_distance")
            if hop_distance is not None:
                # Decrease score with increasing hop distance
                hop_factor = max(0.0, 1.0 - (hop_distance * 0.2))
                graph_score = graph_score * hop_factor

            # Get the recency score (if available)
            recency_score = 0.0
            if "timestamp" in result:
                # Normalize timestamp to a score between 0 and 1
                # This is a placeholder - actual implementation would depend on how timestamps are stored
                recency_score = 0.5

            # Calculate the weighted score
            weighted_score = (
                self.semantic_weight * semantic_score +
                self.type_weight * type_score +
                self.graph_weight * graph_score +
                self.recency_weight * recency_score
            )

            # Add explanation if requested
            if "explain_score" in result and result["explain_score"]:
                result["score_explanation"] = {
                    "semantic_score": semantic_score,
                    "semantic_weight": self.semantic_weight,
                    "type_score": type_score,
                    "type_weight": self.type_weight,
                    "graph_score": graph_score,
                    "graph_weight": self.graph_weight,
                    "recency_score": recency_score,
                    "recency_weight": self.recency_weight,
                    "weighted_score": weighted_score
                }

            return min(1.0, max(0.0, weighted_score))

        except Exception as e:
            logger.error(f"Error scoring result: {e}")
            return 0.0

    def rank_results(
        self,
        results: List[Dict[str, Any]],
        query: str = None,
        min_score: float = 0.0
    ) -> List[Dict[str, Any]]:
        """Rank search results by relevance.

        Args:
            results: List of search results
            query: Original query (for additional scoring)
            min_score: Minimum score threshold

        Returns:
            Ranked list of search results
        """
        try:
            # Score each result
            scored_results = []
            for result in results:
                # Calculate the relevance score
                relevance_score = self.score_result(result, query)

                # Skip results below the minimum score
                if relevance_score < min_score:
                    continue

                # Add the relevance score to the result
                result_copy = result.copy()
                result_copy["relevance_score"] = relevance_score

                scored_results.append(result_copy)

            # Sort by relevance score (descending)
            ranked_results = sorted(
                scored_results,
                key=lambda x: x.get("relevance_score", 0.0),
                reverse=True
            )

            return ranked_results

        except Exception as e:
            logger.error(f"Error ranking results: {e}")
            return results

    def filter_results(
        self,
        results: List[Dict[str, Any]],
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Filter search results based on criteria.

        Args:
            results: List of search results
            filters: Dictionary of filter criteria

        Returns:
            Filtered list of search results
        """
        try:
            if not filters:
                return results

            filtered_results = []

            for result in results:
                # Check if the result matches all filters
                match = True

                for key, value in filters.items():
                    if key not in result or result[key] != value:
                        match = False
                        break

                if match:
                    filtered_results.append(result)

            return filtered_results

        except Exception as e:
            logger.error(f"Error filtering results: {e}")
            return results

    def diversify_results(
        self,
        results: List[Dict[str, Any]],
        max_per_type: int = 3
    ) -> List[Dict[str, Any]]:
        """Diversify search results to include different types.

        Args:
            results: List of search results
            max_per_type: Maximum number of results per chunk type

        Returns:
            Diversified list of search results
        """
        try:
            # Group results by chunk type
            results_by_type = {}

            for result in results:
                chunk_type = result.get("chunk_type", "unknown")

                if chunk_type not in results_by_type:
                    results_by_type[chunk_type] = []

                results_by_type[chunk_type].append(result)

            # Take the top N results from each type
            diversified_results = []

            for chunk_type, type_results in results_by_type.items():
                # Sort by relevance score (descending)
                type_results.sort(
                    key=lambda x: x.get("relevance_score", 0.0),
                    reverse=True
                )

                # Take the top N results
                diversified_results.extend(type_results[:max_per_type])

            # Sort the diversified results by relevance score
            diversified_results.sort(
                key=lambda x: x.get("relevance_score", 0.0),
                reverse=True
            )

            return diversified_results

        except Exception as e:
            logger.error(f"Error diversifying results: {e}")
            return results


    def configure_weights(self, weights_config: Dict[str, float]) -> None:
        """Configure the weights for scoring.

        Args:
            weights_config: Dictionary mapping weight names to values
        """
        try:
            # Update weights
            if "semantic" in weights_config:
                self.semantic_weight = weights_config["semantic"]
            if "type" in weights_config:
                self.type_weight = weights_config["type"]
            if "graph" in weights_config:
                self.graph_weight = weights_config["graph"]
            if "recency" in weights_config:
                self.recency_weight = weights_config["recency"]

            # Normalize weights to sum to 1.0
            total_weight = self.semantic_weight + self.type_weight + self.graph_weight + self.recency_weight
            if total_weight > 0:
                self.semantic_weight /= total_weight
                self.type_weight /= total_weight
                self.graph_weight /= total_weight
                self.recency_weight /= total_weight

            logger.info(f"Configured weights: semantic={self.semantic_weight:.2f}, type={self.type_weight:.2f}, graph={self.graph_weight:.2f}, recency={self.recency_weight:.2f}")

        except Exception as e:
            logger.error(f"Error configuring weights: {e}")

    def configure_type_relevance(self, type_relevance: Dict[str, float]) -> None:
        """Configure the relevance scores for different chunk types.

        Args:
            type_relevance: Dictionary mapping chunk types to relevance scores
        """
        try:
            # Update type relevance scores
            for chunk_type, relevance in type_relevance.items():
                self.type_relevance[chunk_type.lower()] = relevance

            logger.info(f"Configured type relevance: {self.type_relevance}")

        except Exception as e:
            logger.error(f"Error configuring type relevance: {e}")

    def configure_relationship_relevance(self, relationship_relevance: Dict[str, float]) -> None:
        """Configure the relevance scores for different relationship types.

        Args:
            relationship_relevance: Dictionary mapping relationship types to relevance scores
        """
        try:
            # Update relationship relevance scores
            for relationship_type, relevance in relationship_relevance.items():
                self.relationship_relevance[relationship_type] = relevance

            logger.info(f"Configured relationship relevance: {self.relationship_relevance}")

        except Exception as e:
            logger.error(f"Error configuring relationship relevance: {e}")


# Example usage
if __name__ == "__main__":
    # Create a scorer with default weights
    scorer = RelevanceScorer()

    # Example search results
    results = [
        {"node_id": "1", "chunk_type": "class", "name": "UserService", "score": 0.85},
        {"node_id": "2", "chunk_type": "method", "name": "authenticate", "score": 0.92, "relationship_to_result": "CONTAINS", "related_to": "1"},
        {"node_id": "3", "chunk_type": "field", "name": "username", "score": 0.78},
        {"node_id": "4", "chunk_type": "class", "name": "AuthManager", "score": 0.81},
        {"node_id": "5", "chunk_type": "interface", "name": "UserRepository", "score": 0.75, "hop_distance": 1}
    ]

    # Rank the results
    ranked_results = scorer.rank_results(results)

    # Print the ranked results
    print("Ranked Results (Default Weights):")
    for i, result in enumerate(ranked_results, 1):
        print(f"{i}. {result['name']} ({result['chunk_type']})")
        print(f"   Semantic Score: {result['score']:.2f}")
        print(f"   Relevance Score: {result['relevance_score']:.2f}")

    # Configure weights to prioritize graph relationships
    scorer.configure_weights({
        "semantic": 0.3,
        "type": 0.2,
        "graph": 0.5,
        "recency": 0.0
    })

    # Rank the results with new weights
    ranked_results_graph = scorer.rank_results(results)

    # Print the ranked results
    print("\nRanked Results (Graph-Prioritized Weights):")
    for i, result in enumerate(ranked_results_graph, 1):
        print(f"{i}. {result['name']} ({result['chunk_type']})")
        print(f"   Semantic Score: {result['score']:.2f}")
        print(f"   Relevance Score: {result['relevance_score']:.2f}")

    # Diversify the results
    diversified_results = scorer.diversify_results(ranked_results, max_per_type=2)

    # Print the diversified results
    print("\nDiversified Results:")
    for i, result in enumerate(diversified_results, 1):
        print(f"{i}. {result['name']} ({result['chunk_type']})")
        print(f"   Relevance Score: {result['relevance_score']:.2f}")
