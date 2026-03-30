"""
PawPal+ — backend logic layer.

Classes:
    Task      — a single pet care task (dataclass)
    Pet       — a pet with a list of tasks (dataclass)
    Owner     — the pet owner with preferences and a list of pets
    Scheduler — builds and explains a daily care schedule across all pets
"""

from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """A single pet care item with a title, duration, priority, and frequency."""

    title: str
    duration_minutes: int
    priority: str        # "low" | "medium" | "high"
    frequency: str = "daily"   # "daily" | "weekly" | "as-needed"
    is_completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.is_completed = True


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    """A pet owned by an Owner, holding a list of care tasks."""

    name: str
    species: str
    age: int  # years
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append a new care task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, title: str) -> bool:
        """Remove the first task whose title matches; return True if removed."""
        for i, task in enumerate(self.tasks):
            if task.title == title:
                self.tasks.pop(i)
                return True
        return False

    def get_tasks(self) -> list[Task]:
        """Return a copy of all tasks (completed and pending)."""
        return list(self.tasks)

    def get_pending_tasks(self) -> list[Task]:
        """Return only tasks that have not been completed."""
        return [t for t in self.tasks if not t.is_completed]


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

class Owner:
    """A pet owner with a daily time budget, preferences, and a list of pets."""

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
        """Register a new pet with this owner."""
        self.pets.append(pet)

    def get_pets(self) -> list[Pet]:
        """Return a copy of the owner's pet list."""
        return list(self.pets)

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every (pet, task) pair across all registered pets."""
        return [(pet, task) for pet in self.pets for task in pet.get_tasks()]


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    """Builds and explains a daily care schedule across all of the owner's pets."""

    _PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}

    def __init__(self, owner: Owner) -> None:
        self.owner = owner
        # available_minutes is a live property — stays in sync if owner's budget changes.

    @property
    def available_minutes(self) -> int:
        """Return the owner's current daily time budget."""
        return self.owner.available_minutes_per_day

    def build_schedule(self, pet: Pet) -> list[Task]:
        """
        Return an ordered list of pending tasks for a single pet that fit within
        the owner's full time budget (priority-first, then shortest-first tiebreaker).
        """
        return self._fit_tasks(pet.get_pending_tasks(), self.available_minutes)

    def build_full_schedule(self) -> dict[str, list[Task]]:
        """
        Build a schedule across all owner's pets, sharing a single time budget.

        All pending tasks from every pet are collected, sorted globally by
        priority then duration, and assigned greedily until time runs out.
        Returns a dict mapping pet name → list of scheduled tasks.
        """
        # Collect all pending tasks tagged with their pet
        candidates: list[tuple[Pet, Task]] = [
            (pet, task)
            for pet in self.owner.get_pets()
            for task in pet.get_pending_tasks()
        ]

        # Sort globally: high priority first, shorter tasks as tiebreaker
        candidates.sort(
            key=lambda pt: (self._PRIORITY_RANK.get(pt[1].priority, 99), pt[1].duration_minutes)
        )

        # Greedy fill against a single shared budget
        result: dict[str, list[Task]] = {pet.name: [] for pet in self.owner.get_pets()}
        time_remaining = self.available_minutes

        for pet, task in candidates:
            if task.duration_minutes <= time_remaining:
                result[pet.name].append(task)
                time_remaining -= task.duration_minutes

        return result

    def explain_plan(self, schedule: list[Task]) -> str:
        """Return a readable summary of a single-pet schedule."""
        if not schedule:
            return "No tasks could be scheduled — no pending tasks or no time available."

        total = sum(t.duration_minutes for t in schedule)
        lines = [f"Schedule for {self.owner.name} ({self.available_minutes} min available):", ""]
        for i, task in enumerate(schedule, start=1):
            lines.append(f"  {i}. {task.title} — {task.duration_minutes} min [{task.priority}, {task.frequency}]")
        lines += ["", f"Total: {total} min  |  Remaining: {self.available_minutes - total} min"]
        return "\n".join(lines)

    def explain_full_plan(self, full_schedule: dict[str, list[Task]]) -> str:
        """Return a readable summary of a full multi-pet schedule."""
        total_scheduled = sum(t.duration_minutes for tasks in full_schedule.values() for t in tasks)
        lines = [
            f"Today's PawPal+ Schedule for {self.owner.name}",
            f"Time budget: {self.available_minutes} min",
            "=" * 45,
        ]

        has_tasks = False
        for pet_name, tasks in full_schedule.items():
            if tasks:
                has_tasks = True
                lines.append(f"\n  {pet_name}:")
                for i, task in enumerate(tasks, start=1):
                    lines.append(
                        f"    {i}. {task.title} — {task.duration_minutes} min "
                        f"[{task.priority} priority, {task.frequency}]"
                    )

        if not has_tasks:
            return "No tasks to schedule today."

        lines += [
            "",
            "=" * 45,
            f"Total scheduled: {total_scheduled} min  |  "
            f"Remaining: {self.available_minutes - total_scheduled} min",
        ]
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fit_tasks(self, tasks: list[Task], budget: int) -> list[Task]:
        """Greedily select tasks that fit within budget, priority-first."""
        sorted_tasks = sorted(
            tasks,
            key=lambda t: (self._PRIORITY_RANK.get(t.priority, 99), t.duration_minutes),
        )
        schedule: list[Task] = []
        time_remaining = budget
        for task in sorted_tasks:
            if task.duration_minutes <= time_remaining:
                schedule.append(task)
                time_remaining -= task.duration_minutes
        return schedule
