"""
main.py — CLI demo script for PawPal+.

Run with: python main.py
"""

from pawpal_system import Owner, Pet, Task, Scheduler


def main() -> None:
    # --- Set up owner ---
    owner = Owner("Jordan", available_minutes_per_day=90)

    # --- Create pets ---
    mochi = Pet("Mochi", "dog", 3)
    luna = Pet("Luna", "cat", 5)

    # --- Add tasks to Mochi ---
    mochi.add_task(Task("Morning walk",    duration_minutes=30, priority="high",   frequency="daily"))
    mochi.add_task(Task("Evening walk",    duration_minutes=25, priority="medium", frequency="daily"))
    mochi.add_task(Task("Flea medication", duration_minutes=5,  priority="high",   frequency="weekly"))

    # --- Add tasks to Luna ---
    luna.add_task(Task("Feeding",   duration_minutes=10, priority="high",   frequency="daily"))
    luna.add_task(Task("Playtime",  duration_minutes=20, priority="medium", frequency="daily"))
    luna.add_task(Task("Grooming",  duration_minutes=15, priority="low",    frequency="weekly"))

    # --- Register pets with the owner ---
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # --- Build and print the full daily schedule ---
    scheduler = Scheduler(owner)
    full_schedule = scheduler.build_full_schedule()
    print(scheduler.explain_full_plan(full_schedule))


if __name__ == "__main__":
    main()
