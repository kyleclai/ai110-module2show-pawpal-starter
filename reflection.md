# PawPal+ Project Reflection

## 1. System Design

**Three core user actions:**
1. **Add a pet** — the owner registers a pet (name, species, age) so the app knows who needs care.
2. **Add/manage care tasks** — the owner creates tasks with a title, duration, and priority level (e.g., "Morning walk — 30 min — high").
3. **Generate a daily schedule** — the system produces an ordered list of tasks that fits within the owner's available time, prioritizing high-importance tasks first.

**a. Initial design**

The system is modeled with four classes:

- **`Owner`** — holds the pet owner's name, how many minutes per day they have available, and any preferences. Responsible for managing the list of pets.
- **`Pet`** — holds basic pet info (name, species, age) and owns the list of care tasks. Responsible for adding tasks and filtering pending ones.
- **`Task`** (dataclass) — a single care item with a title, duration in minutes, priority (`"low"`, `"medium"`, `"high"`), and a completion flag.
- **`Scheduler`** — receives an `Owner` and builds a daily schedule for a given `Pet`. It sorts tasks by priority, fits as many as possible within the available time window, and generates a human-readable explanation.

Relationships: an `Owner` has one or more `Pet`s; each `Pet` has zero or more `Task`s; the `Scheduler` references both `Owner` and `Pet` to produce the plan.

**b. Design changes**

Yes, my design changed after I reviewed the skeleton more carefully with AI assistance. A few things stood out.

First, I had a `_PRIORITY_ORDER` dict sitting on the `Owner` class that was never actually used — the same thing already existed on `Scheduler` as `_PRIORITY_RANK`. I removed it from `Owner` because priority ordering is really a scheduling concern, not something the owner should know about. Keeping both would've been confusing.

Second, I noticed that `Scheduler` was storing `available_minutes` as a snapshot copied from the owner at construction time. That means if someone updated the owner's time budget later, the scheduler would silently keep using the old number. I changed it to a `@property` that reads from the owner directly so it always stays in sync.

Third, I updated my UML diagram. The label "uses" on the Scheduler→Owner relationship felt too vague — I changed it to "references" since the Scheduler holds onto the Owner and reads its data. I also added cardinality to those relationships, since I had it on Owner→Pet and Pet→Task but not on the Scheduler relationships, which was inconsistent.

One thing I haven't fixed yet: if you call `build_schedule()` for multiple pets, each call gets the owner's full time budget independently. So an owner with two pets could end up with more tasks scheduled than they actually have time for. That's a real limitation I'd want to address in the next iteration.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers two hard constraints: the owner's daily time budget (anything that doesn't fit is skipped) and task completion status (completed tasks are never rescheduled). Within those constraints it uses two soft rankings: priority level (`high` → `medium` → `low`) and duration (shorter tasks win tiebreakers so we fit more into a limited window). Start time is treated as a preference, not a constraint — a timed task that conflicts with another isn't dropped, it's just flagged.

I prioritized time budget first because it's the most concrete constraint the owner controls. Priority ranking came second because an overrun day is better than a day where the dog didn't get its medication. Duration tiebreaking came last as an optimization to maximize the number of tasks completed.

**b. Tradeoffs**

The conflict detector only flags tasks whose time windows literally overlap — it doesn't try to reschedule them or pick one over the other. So if two tasks conflict, the scheduler will still include both in the schedule and just show a warning instead of crashing or dropping the lower-priority one.

I think that's the right call for this app. The owner knows their day better than the algorithm does — maybe they planned for someone else to handle one of those tasks, or maybe one of the times is approximate. Surfacing the conflict and letting the owner decide is more useful than silently dropping a task they might actually need. The tradeoff is that the "schedule" could technically be unexecutable if conflicts are ignored, but a warning is a much safer failure mode than silent data loss.

---

## 3. AI Collaboration

**a. How you used AI**

I used VS Code Copilot across every phase of the project, but for different purposes in each one. In Phase 1 I used Copilot Chat with `#codebase` to pressure-test my UML — I'd describe a relationship ("the Scheduler references the Owner to read the time budget") and ask whether the diagram reflected it accurately. That back-and-forth caught the missing cardinality annotations before I wrote a single line of code. In Phase 2 I used inline completions heavily for the dataclass fields and the `_PRIORITY_RANK` dict, where the pattern was obvious and Copilot got it right on first completion. In Phase 3 I switched to targeted chat prompts for the algorithmic parts: I asked "given this greedy approach, what edge case would break it?" for `build_full_schedule`, which is how I noticed the shared-budget problem with independent `build_schedule` calls. The most useful prompts were always specific and included the actual code: vague questions got generic answers, but "here's my `detect_conflicts` method — does the interval check handle tasks that share an exact start time?" got a precise answer immediately.

**b. Judgment and verification**

The clearest moment was when Copilot suggested making `Scheduler` a subclass of `Owner` to avoid passing the owner in as a constructor argument. The suggestion was syntactically reasonable and would have removed a line from every call site. I rejected it because it broke the domain model: a Scheduler is not a type of Owner, it uses an Owner. Inheriting would have made `Scheduler` responsible for managing pets and tracking time budgets, which are Owner concerns. I verified by sketching what the class interface would look like — `self.add_pet()` and `self.pets` showing up on a Scheduler felt obviously wrong. The fix (keep composition, keep the constructor argument) also made the tests cleaner because I could pass in different Owner objects without subclassing.

**c. AI strategy — VS Code Copilot experience**

The most effective Copilot feature was inline completion for boilerplate patterns I knew well — things like `@staticmethod _to_minutes` or the `__init__` parameter lists. These are low-judgment tasks where Copilot's speed is a genuine win and verification is instant (the code is short and obvious). Copilot Chat with `#file:pawpal_system.py` was most useful for checking consistency: "does my UML match this file?" or "do any methods here have the wrong return type?" are queries where the AI is reading the whole file so I don't have to.

I rejected one AI-generated test that asserted `scheduler.available_minutes == 120` immediately after construction. That assertion is fine at the moment it was written, but the test didn't change the owner's budget between assertions, so it wasn't actually testing the `@property` behavior I added — it was just testing construction. I rewrote it to mutate `owner.available_minutes_per_day` and confirm the scheduler reflected the new value, which is the behavior that matters.

Using separate chat sessions per phase was the right call. By the time I was working on conflict detection, the Phase 1 chat had context about UML decisions that weren't relevant anymore, and mixing them would have produced confused suggestions. A fresh session meant Copilot's context window held only the current file and the current question, which kept the answers tight.

The main thing I learned about being the lead architect: the AI is very good at generating locally correct code (code that compiles, follows the pattern in front of it, passes obvious tests), but it has no model of what the system should *be*. Every meaningful design decision — what the classes own, what they delegate, where the boundary between "user concern" and "algorithm concern" sits — required my judgment. The AI made me faster at executing those decisions; it didn't make the decisions for me.

---

## 4. Testing and Verification

**a. What you tested**

I wrote 18 tests across six areas: `Task.mark_complete()` and isolation between tasks; `Pet` task CRUD (add, remove, pending filter); scheduler time-budget enforcement and shared-budget across pets; priority ordering; chronological sorting and untimed-task placement; filter_tasks by pet name and status; recurring task date arithmetic (daily +1, weekly +7, as-needed no-op); and conflict detection (overlap, sequential, untimed). These were the important tests because they cover every decision point the scheduler makes — if any of these fail, the schedule the user sees is wrong in a way they can't easily spot.

**b. Confidence**

Confidence: ★★★★☆. The core paths are well-covered. Known gaps: tasks spanning midnight (start_time "23:45", duration 30 would overflow to the next day but the interval math ignores date), owners with zero available minutes (no crash test, just returns an empty dict), and tasks added to the same pet with duplicate titles (mark_task_complete marks the first match, which could silently skip the intended one). I'd add those three test cases next.

---

## 5. Reflection

**a. What went well**

The part I'm most satisfied with is the conflict detection logic and how it surfaces in the UI. The interval-overlap check (`a_start < b_end and b_start < a_end`) is one of those small algorithms that feels elegant when it works — two lines that correctly handle all four overlap cases. And the decision to warn rather than auto-resolve the conflict felt like the right product call for the audience. Pet owners have context the algorithm doesn't have; showing them the conflict and trusting them to fix it respects that.

**b. What you would improve**

The biggest redesign would be fixing the shared-budget problem I noted in Phase 1. Right now `build_full_schedule` correctly shares the budget across pets in a single call, but if you call `build_schedule` per pet independently, each call gets the full budget. I'd want to either remove `build_schedule` entirely (force everyone to use `build_full_schedule`) or add a `budget_override` parameter so callers can pass in remaining time explicitly. I'd also add a way to re-order tasks manually in the UI — right now the schedule is entirely algorithm-driven and the owner can't drag a lower-priority task to the top if they just feel like doing it first.

**c. Key takeaway**

The AI is a fast executor, not a designer. It can fill in a method body faster than I can type, and it can read a file and spot inconsistencies I might miss after staring at it for an hour. But it has no stake in the architecture. It doesn't care whether `available_minutes` is a snapshot or a live property, whether `Scheduler` inherits from `Owner` or composes it, or whether the conflict detector drops tasks or warns about them. Those decisions shape the whole system and every one of them required a human to make a judgment call about what the software should be. The clearest lesson: use AI to go faster inside the design you've chosen, not to choose the design for you.
