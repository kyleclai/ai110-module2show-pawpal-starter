"""
PawPal+ — backend logic layer.

Classes:
    Task      — a single pet care task (dataclass)
    Pet       — a pet with a list of tasks (dataclass)
    Owner     — the pet owner with preferences and a list of pets
    Scheduler — builds and explains a daily care schedule
"""

from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """A single pet care item."""

    title: str
    duration_minutes: int
    priority: str  # "low" | "medium" | "high"
    is_completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.is_completed = True


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    """A pet owned by an Owner."""

    name: str
    species: str
    age: int  # years
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet."""
        self.tasks.append(task)

    def get_tasks(self) -> list[Task]:
        """Return all tasks."""
        return list(self.tasks)

    def get_pending_tasks(self) -> list[Task]:
        """Return only tasks that have not been completed."""
        return [t for t in self.tasks if not t.is_completed]


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

class Owner:
    """A pet owner with a daily time budget and care preferences."""

    _PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}

    def __init__(
        self,
        name: str,
        available_minutes_per_day: int = 120,
        preferences: Optional[list[str]] = None,
    ) -> None:
        self.name = name
        self.available_minutes_per_day = available_minutes_per_day
        self.preferences: list[str] = preferences or []
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner."""
        self.pets.append(pet)

    def get_pets(self) -> list[Pet]:
        """Return all registered pets."""
        return list(self.pets)


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    """Builds a daily care schedule for a pet, given the owner's time budget."""

    _PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}

    def __init__(self, owner: Owner) -> None:
        self.owner = owner
        self.available_minutes: int = owner.available_minutes_per_day

    def build_schedule(self, pet: Pet) -> list[Task]:
        """
        Return an ordered list of tasks that fit within the available time.

        Strategy:
        - Consider only pending (incomplete) tasks.
        - Sort by priority (high → medium → low), then by duration (shorter first
          as a tiebreaker so we can fit more tasks).
        - Greedily add tasks until we run out of time.
        """
        pending = pet.get_pending_tasks()
        sorted_tasks = sorted(
            pending,
            key=lambda t: (self._PRIORITY_RANK.get(t.priority, 99), t.duration_minutes),
        )

        schedule: list[Task] = []
        time_remaining = self.available_minutes

        for task in sorted_tasks:
            if task.duration_minutes <= time_remaining:
                schedule.append(task)
                time_remaining -= task.duration_minutes

        return schedule

    def explain_plan(self, schedule: list[Task]) -> str:
        """
        Return a human-readable explanation of a schedule produced by build_schedule().
        """
        if not schedule:
            return "No tasks could be scheduled — either there are no pending tasks or no time is available."

        total = sum(t.duration_minutes for t in schedule)
        lines = [
            f"Schedule for {self.owner.name} ({self.available_minutes} min available):",
            "",
        ]
        for i, task in enumerate(schedule, start=1):
            lines.append(
                f"  {i}. {task.title} — {task.duration_minutes} min [{task.priority} priority]"
            )
        lines += [
            "",
            f"Total scheduled time: {total} min",
            f"Time remaining: {self.available_minutes - total} min",
        ]
        return "\n".join(lines)
