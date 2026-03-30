# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

---

## Smarter Scheduling

Beyond basic priority-based scheduling, PawPal+ includes four algorithmic improvements:

**Time-based sorting** — Tasks that have a `start_time` (HH:MM) set are sorted chronologically within the schedule. Tasks without a start time appear at the end.

**Filtering** — `Scheduler.filter_tasks()` lets you query tasks across all pets by pet name, completion status, or both.

**Recurring tasks** — When a `daily` or `weekly` task is marked complete via `Scheduler.mark_task_complete()`, a new copy is automatically created with a due date shifted by 1 day or 7 days respectively. `as-needed` tasks do not recur.

**Conflict detection** — `Scheduler.detect_conflicts()` checks all timed tasks for a pet and returns a warning string for any pair whose time windows overlap (using interval overlap: `a_start < b_end and b_start < a_end`). `detect_all_conflicts()` runs this check across every pet at once.

---

## Testing PawPal+

Run the automated test suite with:

```bash
python -m pytest
```

The suite covers 18 tests across five areas:

| Area | What's tested |
|---|---|
| Task | `mark_complete()` flips status; completing one task doesn't affect others |
| Pet | `add_task()` increases count; `get_pending_tasks()` excludes completed; `remove_task()` works |
| Scheduling | Time budget is respected; budget is shared across pets; high priority beats low |
| Sorting & filtering | Chronological ordering; untimed tasks placed last; filter by pet name and status |
| Recurrence | Daily → +1 day; weekly → +7 days; as-needed → no new task |
| Conflict detection | Overlapping windows flagged; sequential tasks clear; untimed tasks never conflict |

**Confidence level: ★★★★☆**
Core logic is well-covered. Edge cases not yet tested include tasks that span midnight, owners with zero available minutes, and duplicate pet names.
