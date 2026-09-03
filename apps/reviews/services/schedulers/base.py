from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class SchedulingResult:
    state: str
    due_at: datetime
    stability: float
    difficulty: float
    repetitions: int
    lapses: int


class BaseScheduler:

    def schedule(self, *, state, rating, now):
        raise NotImplementedError