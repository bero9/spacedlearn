from datetime import timedelta

from apps.reviews.services.schedulers.base import (
    BaseScheduler,
    SchedulingResult,
)
from apps.reviews.services.schedulers.core.fsrs_core import (
    FSRSCore,
    FSRSState,
)


class FSRSScheduler(BaseScheduler):

    def __init__(self, core=None):
        self.core = core or FSRSCore()

    def schedule(self, *, state, rating, now):
        fsrs_state = FSRSState(
            stability=state["stability"],
            difficulty=state["difficulty"],
            elapsed_days=state.get("elapsed_days", 0.0),
            scheduled_days=state.get("scheduled_days", 0.0),
            repetitions=state["repetitions"],
            lapses=state["lapses"],
        )

        new_state = self.core.review(
            state=fsrs_state,
            rating=rating,
        )
        interval_days = self.core.next_interval(
            stability=new_state.stability,
            retention=self.core.parameters.desired_retention,
        )

        due_at = now + timedelta(
            days=interval_days,
        )

        return SchedulingResult(
            state=state["state"],
            due_at=due_at,
            stability=new_state.stability,
            difficulty=new_state.difficulty,
            repetitions=new_state.repetitions,
            lapses=new_state.lapses,
        )