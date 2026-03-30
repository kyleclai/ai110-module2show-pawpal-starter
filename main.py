"""
main.py — CLI demo script for PawPal+.

Demonstrates: full schedule, time-based sorting, filtering,
recurring task completion, and conflict detection.

Run with: python main.py
"""

from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler


def section(title: str) -> None:
    print(f"\n{'=' * 50}")
    print(f"  {title}")
    print(f"{'=' * 50}")


def main() -> None:
    # -----------------------------------------------------------------------
    # Setup
    # -----------------------------------------------------------------------
    owner = Owner("Jordan", available_minutes_per_day=90)

    mochi = Pet("Mochi", "dog", 3)
    luna = Pet("Luna", "cat", 5)

    # Tasks added out of order on purpose to show sort_by_time
    mochi.add_task(Task("Evening walk",    duration_minutes=25, priority="medium", frequency="daily",   start_time="18:00", due_date=date.today()))
    mochi.add_task(Task("Flea medication", duration_minutes=5,  priority="high",   frequency="weekly",  start_time="09:30", due_date=date.today()))
    mochi.add_task(Task("Morning walk",    duration_minutes=30, priority="high",   frequency="daily",   start_time="07:00", due_date=date.today()))

    luna.add_task(Task("Feeding",          duration_minutes=10, priority="high",   frequency="daily",   start_time="08:00", due_date=date.today()))
    luna.add_task(Task("Playtime",         duration_minutes=20, priority="medium", frequency="daily",   start_time="17:00", due_date=date.today()))
    luna.add_task(Task("Grooming",         duration_minutes=15, priority="low",    frequency="weekly",  due_date=date.today()))

    owner.add_pet(mochi)
    owner.add_pet(luna)

    scheduler = Scheduler(owner)

    # -----------------------------------------------------------------------
    # 1. Full schedule (priority-based, shared budget)
    # -----------------------------------------------------------------------
    section("1. Full Daily Schedule (priority-based)")
    full_schedule = scheduler.build_full_schedule()
    print(scheduler.explain_full_plan(full_schedule))

    # -----------------------------------------------------------------------
    # 2. Sort by time
    # -----------------------------------------------------------------------
    section("2. Mochi's Tasks Sorted by Start Time")
    sorted_tasks = scheduler.sort_by_time(mochi.get_tasks())
    for task in sorted_tasks:
        time_str = task.start_time or "(no time set)"
        print(f"  {time_str}  {task.title} — {task.duration_minutes} min [{task.priority}]")

    # -----------------------------------------------------------------------
    # 3. Filter tasks
    # -----------------------------------------------------------------------
    section("3. Filter: All Pending Tasks for Luna")
    luna_pending = scheduler.filter_tasks(pet_name="Luna", completed=False)
    for task in luna_pending:
        print(f"  - {task.title} [{task.priority}, {task.frequency}]")

    section("3b. Filter: All Completed Tasks (across all pets)")
    completed = scheduler.filter_tasks(completed=True)
    print(f"  {len(completed)} completed task(s) found")

    # -----------------------------------------------------------------------
    # 4. Recurring task completion
    # -----------------------------------------------------------------------
    section("4. Recurring Task Completion")
    print(f"  Marking Mochi's 'Morning walk' as complete...")
    next_task = scheduler.mark_task_complete(mochi, "Morning walk")
    if next_task:
        print(f"  Next occurrence added: '{next_task.title}' due {next_task.due_date}")
    print(f"  Mochi now has {len(mochi.get_tasks())} total tasks "
          f"({len(mochi.get_pending_tasks())} pending)")

    # -----------------------------------------------------------------------
    # 5. Conflict detection
    # -----------------------------------------------------------------------
    section("5. Conflict Detection")

    # Add two tasks that overlap: 09:00 for 60 min vs 09:30 for 30 min
    mochi.add_task(Task("Vet appointment", duration_minutes=60, priority="high",
                        frequency="as-needed", start_time="09:00"))
    # Flea medication is already at 09:30 for 5 min — overlaps with vet (09:00–10:00)

    conflicts = scheduler.detect_conflicts(mochi)
    if conflicts:
        for warning in conflicts:
            print(f"  ⚠  {warning}")
    else:
        print("  No conflicts detected.")

    # -----------------------------------------------------------------------
    # 6. All-clear example
    # -----------------------------------------------------------------------
    section("6. No-Conflict Example (sequential tasks)")
    luna_conflicts = scheduler.detect_conflicts(luna)
    if luna_conflicts:
        for w in luna_conflicts:
            print(f"  ⚠  {w}")
    else:
        print("  Luna's tasks have no time conflicts.")


if __name__ == "__main__":
    main()
