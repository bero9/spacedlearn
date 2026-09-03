from dataclasses import dataclass
from typing import Tuple
import math

@dataclass(frozen=True)
class FSRSParameters:
    """
    Configuration parameters for FSRS-6.
    """

    desired_retention: float = 0.90

    maximum_interval: int = 36500

    weights: tuple[float, ...] = (
        0.212,
        1.2931,
        2.3065,
        8.2956,
        6.4133,
        0.8334,
        3.0194,
        0.001,
        1.8722,
        0.1666,
        0.796,
        1.4835,
        0.0614,
        0.2629,
        1.6483,
        0.6014,
        1.8729,
        0.5425,
        0.0912,
        0.0658,
        0.1542,
    )

    def __post_init__(self):
        if not 0.0 < self.desired_retention < 1.0:
            raise ValueError(
                "desired_retention must be between 0 and 1."
            )

        if self.maximum_interval <= 0:
            raise ValueError(
                "maximum_interval must be greater than 0."
            )

        if len(self.weights) != 21:
            raise ValueError(
                "FSRS-6 requires exactly 21 weights."
            )
@dataclass(frozen=True)
class FSRSState:
    """
    Pure Python representation of the FSRS memory state.

    This object is intentionally independent of Django models.
    """

    stability: float = 0.0
    difficulty: float = 0.0
    elapsed_days: float = 0.0
    scheduled_days: float = 0.0
    repetitions: int = 0
    lapses: int = 0

class FSRSCore:

    SUPPORTED_RATINGS: Tuple[str, ...] = (
        "again",
        "hard",
        "good",
        "easy",
    )

    def __init__(
        self,
        parameters: FSRSParameters | None = None,
    ):
        self.parameters = (
            parameters
            if parameters is not None
            else FSRSParameters()
        )

    def initial_state(self) -> FSRSState:
        return  FSRSState()

    def review(
        self,
        *,
        state: FSRSState,
        rating: str,
    ) -> FSRSState:
        if rating not in self.SUPPORTED_RATINGS:
            raise ValueError(
                f"Unsupported rating: {rating}"
            )

        if state.stability == 0.0:
            return FSRSState(
                stability=self.initial_stability(rating),
                difficulty=self.initial_difficulty(rating),
                elapsed_days=state.elapsed_days,
                scheduled_days=state.scheduled_days,
                repetitions=state.repetitions + 1,
                lapses=state.lapses,
            )
        retrievability = self.retrievability(
            elapsed_days=state.elapsed_days,
            stability=state.stability,
        )

        new_difficulty = self.next_difficulty(
            difficulty=state.difficulty,
            rating=rating,
        )
        new_lapses = state.lapses

        if rating == "again":
            new_lapses += 1
            new_stability = self.next_lapse_stability(
                stability=state.stability,
                difficulty=state.difficulty,
                retrievability=retrievability,
            )
        else:
            new_stability = self.next_stability(
                stability=state.stability,
                difficulty=state.difficulty,
                retrievability=retrievability,
                rating=rating,
            )

        return FSRSState(
            stability=new_stability,
            difficulty=new_difficulty,
            elapsed_days=state.elapsed_days,
            scheduled_days=state.scheduled_days,
            repetitions=state.repetitions + 1,
            lapses=new_lapses,
        )
    def retrievability(
    self,
    *,
    elapsed_days: float,
    stability: float,
    ) -> float:
        if elapsed_days < 0:
            raise ValueError(
                "elapsed_days cannot be negative."
        )

        if stability <= 0:
            raise ValueError(
                "stability must be greater than zero."
        )

        w20 = self.parameters.weights[19]

        factor = (
            math.pow(0.9, -1.0 / w20) - 1.0
    )

        return math.pow(
            1.0 + factor * elapsed_days / stability,
            -w20,
    )   
    def initial_stability(self, rating: str) -> float:
        if rating not in self.SUPPORTED_RATINGS:
            raise ValueError(
                f"Unsupported rating: {rating}"
        )

        rating_index = {
            "again": 0,
            "hard": 1,
            "good": 2,
            "easy": 3,
        }[rating]

        return self.parameters.weights[rating_index]
    def initial_difficulty(self, rating: str) -> float:
        if rating not in self.SUPPORTED_RATINGS:
            raise ValueError(
                f"Unsupported rating: {rating}"
            )

        rating_index = {
            "again": 1,
            "hard": 2,
            "good": 3,
            "easy": 4,
        }[rating]

        w4 = self.parameters.weights[4]
        w5 = self.parameters.weights[5]

        difficulty = (
            w4
            - math.exp(
                w5 * (rating_index - 1)
            )
            + 1.0
        )

        return max(
            1.0,
            min(10.0, difficulty),
        )
    def next_difficulty(self, *, difficulty: float, rating: str) -> float:
        if rating not in self.SUPPORTED_RATINGS:
            raise ValueError(f"Unsupported rating: {rating}")

        rating_index = {
            "again": 1,
            "hard": 2,
            "good": 3,
            "easy": 4,
        }[rating]

        weights = self.parameters.weights

        w6 = weights[6]
        w7 = weights[7]

        adjusted_difficulty = (
            difficulty - w6 * (rating_index - 3)
        )

        initial_difficulty = weights[4]

        new_difficulty = (
            w7 * initial_difficulty
            + (1.0 - w7) * adjusted_difficulty
        )

        return max(
            1.0,
            min(10.0, new_difficulty),
        )
    def next_stability(
        self,
        *,
        stability: float,
        difficulty: float,
        retrievability: float,
        rating: str,
    ) -> float:
        if rating not in self.SUPPORTED_RATINGS:
            raise ValueError(f"Unsupported rating: {rating}")

        if rating == "again":
            raise ValueError(
                "Rating 'again' must use next_lapse_stability()."
            )

        weights = self.parameters.weights

        w8 = weights[8]
        w9 = weights[9]
        w10 = weights[10]
        w15 = weights[15]
        w16 = weights[16]

        hard_penalty = (
            w15 if rating == "hard" else 1.0
        )

        easy_bonus = (
            w16 if rating == "easy" else 1.0
        )

        stability_increase = (
            math.exp(w8)
            * (11.0 - difficulty)
            * math.pow(stability, -w9)
            * (
                math.exp(
                    w10 * (1.0 - retrievability)
                )
                - 1.0
            )
            * hard_penalty
            * easy_bonus
        )

        new_stability = stability * (
            1.0 + stability_increase
        )

        return max(
            new_stability,
            stability,
        )
    def next_lapse_stability(
        self,
        *,
        stability: float,
        difficulty: float,
        retrievability: float,
    ) -> float:
        weights = self.parameters.weights

        long_term = (
            weights[11]
            * math.pow(
                difficulty,
                -weights[12],
            )
            * (
                math.pow(
                    stability + 1.0,
                    weights[13],
                )
                - 1.0
            )
            * math.exp(
                weights[14]
                * (1.0 - retrievability)
            )
        )

        short_term = (
            stability
            / math.exp(
                weights[17] * weights[18]
            )
        )

        return min(
            long_term,
            short_term,
        )