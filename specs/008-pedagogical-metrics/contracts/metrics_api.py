"""API Contracts for Pedagogical Metrics Module.

This module defines the Python interfaces (protocols/ABCs) for the metrics system.
These are contracts that implementations must fulfill.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple


# =============================================================================
# Data Transfer Objects
# =============================================================================


@dataclass
class BKTResult:
    """Result of a BKT mastery calculation."""

    mastery_probability: float  # P(L) after update, 0-1
    confidence_lower: float  # 95% CI lower bound
    confidence_upper: float  # 95% CI upper bound
    is_mastered: bool  # True if P(L) >= threshold
    observations: int  # Total observations used


@dataclass
class IRTResult:
    """Result of an IRT probability calculation."""

    probability: float  # P(correct | theta, a, b, c)
    information: float  # Fisher information at this theta
    standard_error: float  # SE of ability estimate


@dataclass
class AbilityEstimate:
    """Learner ability estimate."""

    theta: float  # Ability estimate (-4 to +4)
    standard_error: float  # SE of estimate
    responses_used: int  # Number of responses in estimate


class ZPDZone(Enum):
    """Zone of Proximal Development status."""

    FRUSTRATION_RISK = "frustration_risk"  # < 50% for 2+ consecutive
    BELOW_ZPD = "below_zpd"  # < 60% success rate
    OPTIMAL = "optimal"  # 60-85% success rate
    ABOVE_ZPD = "above_zpd"  # > 85% success rate
    BOREDOM_RISK = "boredom_risk"  # > 90% for 3+ consecutive


@dataclass
class ZPDResult:
    """Zone of Proximal Development assessment result."""

    zone: ZPDZone
    success_rate: float  # Recent EMA success rate
    recommended_difficulty: int  # 1-6 scale
    consecutive_correct: int
    consecutive_incorrect: int


class BehavioralIndicator(Enum):
    """Behavioral indicator types."""

    NORMAL = "normal"
    FRUSTRATION = "frustration"
    BOREDOM = "boredom"
    RAPID_ATTEMPT = "rapid_attempt"
    EXCESSIVE_HINTS = "excessive_hints"


@dataclass
class BehavioralResult:
    """Behavioral analysis result."""

    indicator: BehavioralIndicator
    confidence: float  # 0-1 confidence in assessment
    response_time_ratio: float  # actual / expected
    hints_used: int
    details: str


# =============================================================================
# Service Contracts
# =============================================================================


class BKTService(ABC):
    """Contract for Bayesian Knowledge Tracing service."""

    @abstractmethod
    def update(
        self,
        user_id: str,
        concept_name: str,
        correct: bool,
        p_l0: float = 0.1,
        p_t: float = 0.3,
        p_g: float = 0.2,
        p_s: float = 0.1,
    ) -> BKTResult:
        """Update mastery probability after an observation.

        Args:
            user_id: User identifier
            concept_name: Concept identifier
            correct: Whether the response was correct
            p_l0: Initial knowledge probability (used if first observation)
            p_t: Learning rate
            p_g: Guess probability
            p_s: Slip probability

        Returns:
            BKTResult with updated mastery probability
        """
        pass

    @abstractmethod
    def get_mastery(
        self, user_id: str, concept_name: str, threshold: float = 0.95
    ) -> Optional[BKTResult]:
        """Get current mastery probability for a concept.

        Args:
            user_id: User identifier
            concept_name: Concept identifier
            threshold: Mastery threshold (default 0.95)

        Returns:
            BKTResult or None if no data
        """
        pass

    @abstractmethod
    def get_unmastered_concepts(
        self, user_id: str, threshold: float = 0.95
    ) -> List[Tuple[str, float]]:
        """Get concepts below mastery threshold.

        Args:
            user_id: User identifier
            threshold: Mastery threshold

        Returns:
            List of (concept_name, mastery_probability) tuples
        """
        pass


class IRTService(ABC):
    """Contract for Item Response Theory service."""

    @abstractmethod
    def calculate_probability(
        self,
        theta: float,
        discrimination: float = 1.0,
        difficulty: float = 0.0,
        guessing: float = 0.25,
    ) -> IRTResult:
        """Calculate probability of correct response.

        Args:
            theta: Learner ability (-4 to +4)
            discrimination: Question discrimination (0.5-2.5)
            difficulty: Question difficulty (-3 to +3)
            guessing: Guessing probability (0-0.35)

        Returns:
            IRTResult with probability and information
        """
        pass

    @abstractmethod
    def estimate_ability(
        self,
        responses: List[bool],
        difficulties: List[float],
        discriminations: Optional[List[float]] = None,
        guessings: Optional[List[float]] = None,
        theta_init: float = 0.0,
    ) -> AbilityEstimate:
        """Estimate learner ability from response pattern.

        Args:
            responses: List of correct (True) / incorrect (False)
            difficulties: Difficulty parameter for each question
            discriminations: Discrimination parameters (default all 1.0)
            guessings: Guessing parameters (default all 0.25)
            theta_init: Initial ability estimate

        Returns:
            AbilityEstimate with theta and standard error
        """
        pass

    @abstractmethod
    def select_optimal_question(
        self,
        theta: float,
        question_pool: List[dict],
    ) -> dict:
        """Select question with maximum information at current ability.

        Args:
            theta: Current ability estimate
            question_pool: List of question dicts with 'id', 'a', 'b', 'c' keys

        Returns:
            Selected question dict
        """
        pass


class ZPDService(ABC):
    """Contract for Zone of Proximal Development service."""

    @abstractmethod
    def evaluate(
        self,
        user_id: str,
        concept_name: str,
        recent_results: List[bool],
    ) -> ZPDResult:
        """Evaluate learner's current ZPD status.

        Args:
            user_id: User identifier
            concept_name: Concept identifier
            recent_results: Recent correct/incorrect results (newest last)

        Returns:
            ZPDResult with zone status and recommendations
        """
        pass

    @abstractmethod
    def get_optimal_difficulty(
        self,
        current_success_rate: float,
        current_difficulty: int,
    ) -> int:
        """Get recommended difficulty level.

        Args:
            current_success_rate: Recent success rate (0-1)
            current_difficulty: Current difficulty level (1-6)

        Returns:
            Recommended difficulty level (1-6)
        """
        pass


class BehavioralService(ABC):
    """Contract for behavioral indicator detection."""

    @abstractmethod
    def analyze(
        self,
        response_time_ms: int,
        expected_time_ms: int,
        hints_used: int,
        consecutive_incorrect: int,
        consecutive_correct: int,
    ) -> BehavioralResult:
        """Analyze behavioral indicators.

        Args:
            response_time_ms: Actual response time
            expected_time_ms: Expected response time
            hints_used: Number of hints used on this question
            consecutive_incorrect: Consecutive incorrect streak
            consecutive_correct: Consecutive correct streak

        Returns:
            BehavioralResult with indicator assessment
        """
        pass

    @abstractmethod
    def detect_frustration(
        self,
        recent_times: List[int],
        recent_hints: List[int],
        recent_correct: List[bool],
    ) -> Tuple[bool, float]:
        """Detect frustration indicators.

        Args:
            recent_times: Recent response times (ms)
            recent_hints: Recent hint counts
            recent_correct: Recent correctness

        Returns:
            Tuple of (is_frustrated, confidence)
        """
        pass

    @abstractmethod
    def detect_boredom(
        self,
        recent_times: List[int],
        expected_times: List[int],
        recent_correct: List[bool],
    ) -> Tuple[bool, float]:
        """Detect boredom indicators.

        Args:
            recent_times: Recent response times (ms)
            expected_times: Expected response times (ms)
            recent_correct: Recent correctness

        Returns:
            Tuple of (is_bored, confidence)
        """
        pass


# =============================================================================
# Tool Context Integration Contract
# =============================================================================


class MetricsToolContext(ABC):
    """Contract for metrics integration with ADK ToolContext."""

    @abstractmethod
    def update_mastery_bkt(
        self,
        concept_name: str,
        correct: bool,
        response_time_ms: Optional[int] = None,
        hints_used: int = 0,
    ) -> BKTResult:
        """Update mastery using BKT and behavioral tracking.

        Args:
            concept_name: Concept identifier
            correct: Whether response was correct
            response_time_ms: Response time if available
            hints_used: Hints used for this question

        Returns:
            BKTResult with updated mastery
        """
        pass

    @abstractmethod
    def get_zpd_recommendation(self) -> ZPDResult:
        """Get ZPD status and difficulty recommendation.

        Returns:
            ZPDResult with current status and recommendations
        """
        pass

    @abstractmethod
    def get_learner_profile(self) -> dict:
        """Get comprehensive learner profile.

        Returns:
            Dict with ability, mastery, ZPD status, behavioral indicators
        """
        pass
