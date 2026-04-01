# PawPal+ Module 2 — Implementation Plan

## Status Legend
- [ ] Not started
- [x] Complete

---

## Step 1: Understand the Problem
- [x] Repo cloned and open in VS Code
- [x] Read README.md scenario
- [ ] Identify three core user actions
- [ ] Document them in reflection.md under "System Design"

**Three core actions:**
1. **Add a pet** — owner registers a pet with basic info (name, species, age)
2. **Add/manage care tasks** — owner creates tasks with title, duration, and priority
3. **Generate a daily schedule** — system produces an ordered plan of tasks based on available time and priority

---

## Step 2: List the Building Blocks

**Four main classes:**

| Class | Attributes | Methods |
|---|---|---|
| `Owner` | name, available_minutes_per_day, preferences | `add_pet()`, `get_pets()` |
| `Pet` | name, species, age, owner | `add_task()`, `get_tasks()` |
| `Task` | title, duration_minutes, priority, is_completed | `mark_complete()` |
| `Scheduler` | pet, available_minutes | `build_schedule()`, `explain_plan()` |

---

## Step 3: Draft UML with Mermaid.js

Generate a Mermaid class diagram reflecting the four classes and their relationships:
- `Owner` has one or more `Pet`s (1 to many)
- `Pet` has one or more `Task`s (1 to many)
- `Scheduler` takes an `Owner` (and their `Pet`s) as input and produces a schedule

Mermaid diagram will be embedded in plan.md and reflection.md.

---

## Step 4: Translate UML into Python Skeleton

- [ ] Create `pawpal_system.py`
- [ ] Implement `Task` as a Python dataclass
- [ ] Implement `Pet` as a Python dataclass
- [ ] Implement `Owner` as a regular class
- [ ] Implement `Scheduler` as a regular class with stub methods
- [ ] Commit: `chore: add class skeletons from UML`

---

## Step 5: Reflect and Refine

- [ ] Fill in reflection.md section "1a. Initial design"
- [ ] Review skeleton for missing relationships or logic gaps
- [ ] Document any changes in reflection.md section "1b. Design changes"

---

---

## Phase 4: Polish & Package

- [x] **Step 1** — Enhance UI to surface smart logic visually
  - [x] Conflict warnings promoted to `st.error` banner with per-warning `st.warning` rows
  - [x] Scheduled tasks displayed as `st.table` with Start, Duration, Priority, Frequency columns
  - [x] Time-remaining metric shown after schedule generation
  - [x] Conflict resolution tip caption added under warnings
- [x] **Step 2** — Finalize UML to match final implementation
  - [x] Added `Task` fields: `frequency`, `start_time`, `due_date`; method: `next_occurrence()`
  - [x] Added `Pet` method: `remove_task()`
  - [x] Added `Owner` method: `get_all_tasks()`
  - [x] Added `Scheduler` methods: `sort_by_time()`, `filter_tasks()`, `mark_task_complete()`, `detect_conflicts()`, `detect_all_conflicts()`, `build_full_schedule()`, `explain_full_plan()`
- [x] **Step 3** — Polish README.md with Features list and Demo section
- [x] **Step 4** — Complete reflection.md with AI strategy section

---

## Final UML Diagram (updated to match implementation)

```mermaid
classDiagram
    class Owner {
        +str name
        +int available_minutes_per_day
        +list~str~ preferences
        +list~Pet~ pets
        +add_pet(pet: Pet) None
        +get_pets() list~Pet~
        +get_all_tasks() list~tuple~
    }

    class Pet {
        +str name
        +str species
        +int age
        +list~Task~ tasks
        +add_task(task: Task) None
        +remove_task(title: str) bool
        +get_tasks() list~Task~
        +get_pending_tasks() list~Task~
    }

    class Task {
        +str title
        +int duration_minutes
        +str priority
        +str frequency
        +Optional~str~ start_time
        +Optional~date~ due_date
        +bool is_completed
        +mark_complete() None
        +next_occurrence() Optional~Task~
    }

    class Scheduler {
        +Owner owner
        +int available_minutes
        +build_schedule(pet: Pet) list~Task~
        +build_full_schedule() dict
        +sort_by_time(tasks: list~Task~) list~Task~
        +filter_tasks(pet_name, completed) list~Task~
        +mark_task_complete(pet, title) Optional~Task~
        +detect_conflicts(pet: Pet) list~str~
        +detect_all_conflicts() list~str~
        +explain_plan(schedule: list~Task~) str
        +explain_full_plan(full_schedule: dict) str
    }

    Owner "1" --> "1..*" Pet : owns
    Pet "1" --> "0..*" Task : has
    Scheduler "1" --> "1" Owner : references
    Scheduler "1" --> "0..*" Pet : schedules for
```

---

## Original UML Diagram (Phase 1 draft)

```mermaid
classDiagram
    class Owner {
        +str name
        +int available_minutes_per_day
        +list~str~ preferences
        +list~Pet~ pets
        +add_pet(pet: Pet) None
        +get_pets() list~Pet~
    }

    class Pet {
        +str name
        +str species
        +int age
        +list~Task~ tasks
        +add_task(task: Task) None
        +get_tasks() list~Task~
        +get_pending_tasks() list~Task~
    }

    class Task {
        +str title
        +int duration_minutes
        +str priority
        +bool is_completed
        +mark_complete() None
    }

    class Scheduler {
        +Owner owner
        +int available_minutes
        +build_schedule(pet: Pet) list~Task~
        +explain_plan(schedule: list~Task~) str
    }

    Owner "1" --> "1..*" Pet : owns
    Pet "1" --> "0..*" Task : has
    Scheduler "1" --> "1" Owner : references
    Scheduler "1" --> "*" Pet : schedules for
```
