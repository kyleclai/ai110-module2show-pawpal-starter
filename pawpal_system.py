"""
PawPal+ — backend logic layer.

Classes:
    Task      — a single pet care task (dataclass)
    Pet       — a pet with a list of tasks (dataclass)
    Owner     — the pet owner with preferences and a list of pets
    Scheduler — builds, sorts, filters, and validates a daily care schedule
"""

import copy
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """A single pet care item with title, duration, priority, frequency, and optional start time."""

    title: str
    duration_minutes: int
    priority: str           # "low" | "medium" | "high"
    frequency: str = "daily"        # "daily" | "weekly" | "as-needed"
    start_time: Optional[str] = None  # "HH:MM" 24-hour format; None = unscheduled
    due_date: Optional[date] = None
    is_completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.is_completed = True

    def next_occurrence(self) -> Optional["Task"]:
        """
        Return a fresh copy of this task due on its next occurrence date,
        or None if the task is not recurring (frequency == 'as-needed').
        """
        if self.frequency == "as-needed":
            return None
        base = self.due_date or date.today()
        delta = timedelta(days=1) if self.frequency == "daily" else timedelta(weeks=1)
        new_task = copy.copy(self)
        new_task.is_completed = False
        new_task.due_date = base + delta
        return new_task


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
    """
    Builds and explains a daily care schedule.

    Capabilities:
    - Priority-based greedy scheduling across all pets (shared time budget)
    - Time-based sorting of tasks with a start_time
    - Filtering by pet name or completion status
    - Recurring task completion (auto-creates next occurrence)
    - Conflict detection for overlapping timed tasks
    """

    _PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    @property
    def available_minutes(self) -> int:
        """Return the owner's current daily time budget (live, not a snapshot)."""
        return self.owner.available_minutes_per_day

    # ------------------------------------------------------------------
    # Scheduling
    # ------------------------------------------------------------------

    def build_schedule(self, pet: Pet) -> list[Task]:
        """
        Return pending tasks for a single pet that fit within the owner's
        full time budget. Sorted by priority, then shortest-first tiebreaker.
        """
        return self._fit_tasks(pet.get_pending_tasks(), self.available_minutes)

    def build_full_schedule(self) -> dict[str, list[Task]]:
        """
        Build a schedule across all owner's pets, sharing a single time budget.

        All pending tasks are collected, sorted globally by priority then
        duration, and assigned greedily until time runs out.
        Returns {pet_name: [scheduled_tasks]}.
        """
        candidates: list[tuple[Pet, Task]] = [
            (pet, task)
            for pet in self.owner.get_pets()
            for task in pet.get_pending_tasks()
        ]
        candidates.sort(
            key=lambda pt: (self._PRIORITY_RANK.get(pt[1].priority, 99), pt[1].duration_minutes)
        )
        result: dict[str, list[Task]] = {pet.name: [] for pet in self.owner.get_pets()}
        time_remaining = self.available_minutes
        for pet, task in candidates:
            if task.duration_minutes <= time_remaining:
                result[pet.name].append(task)
                time_remaining -= task.duration_minutes
        return result

    # ------------------------------------------------------------------
    # Sorting and filtering
    # ------------------------------------------------------------------

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """
        Sort tasks chronologically by start_time ('HH:MM').
        Tasks with no start_time are placed at the end in their original order.
        """
        timed = [t for t in tasks if t.start_time is not None]
        untimed = [t for t in tasks if t.start_time is None]
        timed.sort(key=lambda t: self._to_minutes(t.start_time))  # type: ignore[arg-type]
        return timed + untimed

    def filter_tasks(
        self,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> list[Task]:
        """
        Return tasks across all owner's pets, optionally filtered by pet name
        and/or completion status. Pass None to skip that filter.
        """
        results: list[Task] = []
        for pet in self.owner.get_pets():
            if pet_name is not None and pet.name != pet_name:
                continue
            for task in pet.get_tasks():
                if completed is not None and task.is_completed != completed:
                    continue
                results.append(task)
        return results

    # ------------------------------------------------------------------
    # Recurring tasks
    # ------------------------------------------------------------------

    def mark_task_complete(self, pet: Pet, title: str) -> Optional[Task]:
        """
        Mark the first matching pending task complete. If it recurs, add the
        next occurrence to the pet and return it; otherwise return None.
        """
        for task in pet.tasks:
            if task.title == title and not task.is_completed:
                task.mark_complete()
                next_task = task.next_occurrence()
                if next_task is not None:
                    pet.add_task(next_task)
                return next_task
        return None

    # ------------------------------------------------------------------
    # Conflict detection
    # ------------------------------------------------------------------

    def detect_conflicts(self, pet: Pet) -> list[str]:
        """
        Return warning strings for any pending tasks whose time windows overlap.
        Only tasks with a start_time are checked; tasks without one are ignored.
        """
        timed = [t for t in pet.get_pending_tasks() if t.start_time is not None]
        warnings: list[str] = []
        for i in range(len(timed)):
            for j in range(i + 1, len(timed)):
                a, b = timed[i], timed[j]
                a_start = self._to_minutes(a.start_time)   # type: ignore[arg-type]
                a_end = a_start + a.duration_minutes
                b_start = self._to_minutes(b.start_time)   # type: ignore[arg-type]
                b_end = b_start + b.duration_minutes
                if a_start < b_end and b_start < a_end:
                    warnings.append(
                        f"Conflict for {pet.name}: '{a.title}' ({a.start_time}, "
                        f"{a.duration_minutes} min) overlaps '{b.title}' "
                        f"({b.start_time}, {b.duration_minutes} min)"
                    )
        return warnings

    def detect_all_conflicts(self) -> list[str]:
        """Run detect_conflicts() across every pet and return all warnings."""
        all_warnings: list[str] = []
        for pet in self.owner.get_pets():
            all_warnings.extend(self.detect_conflicts(pet))
        return all_warnings

    # ------------------------------------------------------------------
    # Plan explanation
    # ------------------------------------------------------------------

    def explain_plan(self, schedule: list[Task]) -> str:
        """Return a readable summary of a single-pet schedule."""
        if not schedule:
            return "No tasks could be scheduled — no pending tasks or no time available."
        total = sum(t.duration_minutes for t in schedule)
        lines = [f"Schedule for {self.owner.name} ({self.available_minutes} min available):", ""]
        for i, task in enumerate(schedule, start=1):
            time_str = f" @ {task.start_time}" if task.start_time else ""
            lines.append(
                f"  {i}. {task.title}{time_str} — {task.duration_minutes} min "
                f"[{task.priority}, {task.frequency}]"
            )
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
                sorted_tasks = self.sort_by_time(tasks)
                lines.append(f"\n  {pet_name}:")
                for i, task in enumerate(sorted_tasks, start=1):
                    time_str = f" @ {task.start_time}" if task.start_time else ""
                    lines.append(
                        f"    {i}. {task.title}{time_str} — {task.duration_minutes} min "
                        f"[{task.priority}, {task.frequency}]"
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

    @staticmethod
    def _to_minutes(time_str: str) -> int:
        """Convert 'HH:MM' to minutes since midnight."""
        h, m = map(int, time_str.split(":"))
        return h * 60 + m
