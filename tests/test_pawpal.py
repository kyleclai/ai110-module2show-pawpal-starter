"""
Tests for PawPal+ core logic.

Run with: python -m pytest
"""

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
# Scheduler tests
# ---------------------------------------------------------------------------

def test_scheduler_respects_time_budget():
    """Scheduler should not schedule more minutes than the owner's budget."""
    owner = Owner("Jordan", available_minutes_per_day=30)
    pet = Pet("Mochi", "dog", 3)
    pet.add_task(Task("Long walk", 25, "high"))
    pet.add_task(Task("Meds", 10, "high"))   # 25 + 10 = 35 > 30, so Meds should be dropped
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    schedule = scheduler.build_schedule(pet)
    total = sum(t.duration_minutes for t in schedule)
    assert total <= owner.available_minutes_per_day


def test_full_schedule_shares_budget_across_pets():
    """build_full_schedule() should share the time budget across all pets."""
    owner = Owner("Jordan", available_minutes_per_day=40)
    dog = Pet("Mochi", "dog", 3)
    cat = Pet("Luna", "cat", 5)
    dog.add_task(Task("Walk", 30, "high"))
    cat.add_task(Task("Feed", 15, "high"))   # 30 + 15 = 45 > 40, so Feed should be dropped
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
    pet.add_task(Task("Meds", 10, "high"))   # only one fits; Meds should win
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    schedule = scheduler.build_schedule(pet)
    assert len(schedule) == 1
    assert schedule[0].title == "Meds"
