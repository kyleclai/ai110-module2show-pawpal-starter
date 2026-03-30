"""
Tests for PawPal+ core logic.

Covers: task completion, task management, scheduling correctness,
time-based sorting, filtering, recurring task recurrence, and
conflict detection.

Run with: python -m pytest
"""

from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler


# ---------------------------------------------------------------------------
# Task tests
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    """mark_complete() should flip is_completed from False to True."""
    task = Task("Morning walk", duration_minutes=30, priority="high")
    assert task.is_completed is False
    task.mark_complete()
    assert task.is_completed is True


def test_completed_task_does_not_affect_uncompleted():
    """Completing one task should not affect another task's status."""
    task_a = Task("Walk", 20, "high")
    task_b = Task("Feed", 10, "high")
    task_a.mark_complete()
    assert task_b.is_completed is False


# ---------------------------------------------------------------------------
# Pet tests
# ---------------------------------------------------------------------------

def test_add_task_increases_count():
    """Adding a task to a Pet should increase its task count by one."""
    pet = Pet("Mochi", "dog", 3)
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task("Morning walk", 30, "high"))
    assert len(pet.get_tasks()) == 1


def test_get_pending_tasks_excludes_completed():
    """get_pending_tasks() should exclude tasks that are already completed."""
    pet = Pet("Luna", "cat", 5)
    done = Task("Grooming", 15, "low")
    pending = Task("Feeding", 10, "high")
    done.mark_complete()
    pet.add_task(done)
    pet.add_task(pending)
    assert len(pet.get_pending_tasks()) == 1
    assert pet.get_pending_tasks()[0].title == "Feeding"


def test_remove_task_by_title():
    """remove_task() should remove the matching task and return True."""
    pet = Pet("Mochi", "dog", 3)
    pet.add_task(Task("Walk", 20, "high"))
    pet.add_task(Task("Meds", 5, "high"))
    removed = pet.remove_task("Walk")
    assert removed is True
    assert len(pet.get_tasks()) == 1
    assert pet.get_tasks()[0].title == "Meds"


# ---------------------------------------------------------------------------
# Scheduling tests
# ---------------------------------------------------------------------------

def test_scheduler_respects_time_budget():
    """Scheduler should not schedule more minutes than the owner's budget."""
    owner = Owner("Jordan", available_minutes_per_day=30)
    pet = Pet("Mochi", "dog", 3)
    pet.add_task(Task("Long walk", 25, "high"))
    pet.add_task(Task("Meds", 10, "high"))  # 25 + 10 > 30 — Meds should be dropped
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    total = sum(t.duration_minutes for t in scheduler.build_schedule(pet))
    assert total <= owner.available_minutes_per_day


def test_full_schedule_shares_budget_across_pets():
    """build_full_schedule() should share the time budget across all pets."""
    owner = Owner("Jordan", available_minutes_per_day=40)
    dog = Pet("Mochi", "dog", 3)
    cat = Pet("Luna", "cat", 5)
    dog.add_task(Task("Walk", 30, "high"))
    cat.add_task(Task("Feed", 15, "high"))  # 30 + 15 > 40 — Feed should be dropped
    owner.add_pet(dog)
    owner.add_pet(cat)
    scheduler = Scheduler(owner)
    full_schedule = scheduler.build_full_schedule()
    total = sum(t.duration_minutes for tasks in full_schedule.values() for t in tasks)
    assert total <= owner.available_minutes_per_day


def test_scheduler_prioritizes_high_before_low():
    """High-priority tasks should be scheduled before low-priority ones."""
    owner = Owner("Jordan", available_minutes_per_day=25)
    pet = Pet("Mochi", "dog", 3)
    pet.add_task(Task("Enrichment", 20, "low"))
    pet.add_task(Task("Meds", 10, "high"))  # only one fits; Meds should win
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    schedule = scheduler.build_schedule(pet)
    assert len(schedule) == 1
    assert schedule[0].title == "Meds"


# ---------------------------------------------------------------------------
# Sorting tests
# ---------------------------------------------------------------------------

def test_sort_by_time_returns_chronological_order():
    """sort_by_time() should order tasks earliest start_time first."""
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog", 3)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    tasks = [
        Task("Evening walk", 25, "medium", start_time="18:00"),
        Task("Morning walk", 30, "high",   start_time="07:00"),
        Task("Noon meds",    5,  "high",   start_time="12:00"),
    ]
    sorted_tasks = scheduler.sort_by_time(tasks)
    times = [t.start_time for t in sorted_tasks]
    assert times == ["07:00", "12:00", "18:00"]


def test_sort_by_time_places_untimed_tasks_last():
    """Tasks without a start_time should appear after all timed tasks."""
    owner = Owner("Jordan")
    owner.add_pet(Pet("Mochi", "dog", 3))
    scheduler = Scheduler(owner)

    tasks = [
        Task("Untimed task", 10, "high"),
        Task("Morning walk", 30, "high", start_time="07:00"),
    ]
    sorted_tasks = scheduler.sort_by_time(tasks)
    assert sorted_tasks[0].start_time == "07:00"
    assert sorted_tasks[1].start_time is None


# ---------------------------------------------------------------------------
# Filtering tests
# ---------------------------------------------------------------------------

def test_filter_by_pet_name():
    """filter_tasks(pet_name=...) should return only tasks belonging to that pet."""
    owner = Owner("Jordan")
    dog = Pet("Mochi", "dog", 3)
    cat = Pet("Luna", "cat", 5)
    dog.add_task(Task("Walk", 20, "high"))
    cat.add_task(Task("Feed", 10, "high"))
    owner.add_pet(dog)
    owner.add_pet(cat)
    scheduler = Scheduler(owner)

    mochi_tasks = scheduler.filter_tasks(pet_name="Mochi")
    assert len(mochi_tasks) == 1
    assert mochi_tasks[0].title == "Walk"


def test_filter_by_completion_status():
    """filter_tasks(completed=False) should return only pending tasks."""
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog", 3)
    done = Task("Old task", 10, "low")
    done.mark_complete()
    pet.add_task(done)
    pet.add_task(Task("New task", 20, "high"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    pending = scheduler.filter_tasks(completed=False)
    assert len(pending) == 1
    assert pending[0].title == "New task"


# ---------------------------------------------------------------------------
# Recurrence tests
# ---------------------------------------------------------------------------

def test_daily_task_recurrence_creates_next_day_task():
    """Completing a daily task should add a new task due tomorrow."""
    today = date.today()
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog", 3)
    pet.add_task(Task("Morning walk", 30, "high", frequency="daily", due_date=today))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    next_task = scheduler.mark_task_complete(pet, "Morning walk")

    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.is_completed is False
    assert len(pet.get_tasks()) == 2  # original + new occurrence


def test_weekly_task_recurrence_creates_next_week_task():
    """Completing a weekly task should add a new task due seven days later."""
    today = date.today()
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog", 3)
    pet.add_task(Task("Flea meds", 5, "high", frequency="weekly", due_date=today))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    next_task = scheduler.mark_task_complete(pet, "Flea meds")

    assert next_task is not None
    assert next_task.due_date == today + timedelta(weeks=1)


def test_as_needed_task_no_recurrence():
    """Completing an 'as-needed' task should NOT add a new occurrence."""
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog", 3)
    pet.add_task(Task("Vet visit", 60, "high", frequency="as-needed"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    next_task = scheduler.mark_task_complete(pet, "Vet visit")

    assert next_task is None
    assert len(pet.get_tasks()) == 1  # no new task added


# ---------------------------------------------------------------------------
# Conflict detection tests
# ---------------------------------------------------------------------------

def test_detect_conflicts_flags_overlapping_tasks():
    """Scheduler should return a warning when two tasks' time windows overlap."""
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog", 3)
    # 09:00–10:00 overlaps with 09:30–10:00
    pet.add_task(Task("Vet appointment", 60, "high", frequency="as-needed", start_time="09:00"))
    pet.add_task(Task("Meds",            30, "high", frequency="daily",     start_time="09:30"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    warnings = scheduler.detect_conflicts(pet)
    assert len(warnings) == 1
    assert "Vet appointment" in warnings[0]
    assert "Meds" in warnings[0]


def test_no_conflict_for_sequential_tasks():
    """Tasks that end before the next one starts should produce no warnings."""
    owner = Owner("Jordan")
    pet = Pet("Luna", "cat", 5)
    # 08:00–08:10, then 08:10–08:30 — exactly sequential, no overlap
    pet.add_task(Task("Feeding",  10, "high",   frequency="daily", start_time="08:00"))
    pet.add_task(Task("Playtime", 20, "medium", frequency="daily", start_time="08:10"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    warnings = scheduler.detect_conflicts(pet)
    assert len(warnings) == 0


def test_no_conflict_for_untimed_tasks():
    """Tasks without start_time should never trigger a conflict warning."""
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog", 3)
    pet.add_task(Task("Walk", 30, "high"))  # no start_time
    pet.add_task(Task("Meds", 5,  "high"))  # no start_time
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    warnings = scheduler.detect_conflicts(pet)
    assert len(warnings) == 0
