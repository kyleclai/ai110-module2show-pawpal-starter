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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

The conflict detector only flags tasks whose time windows literally overlap — it doesn't try to reschedule them or pick one over the other. So if two tasks conflict, the scheduler will still include both in the schedule and just show a warning instead of crashing or dropping the lower-priority one.

I think that's the right call for this app. The owner knows their day better than the algorithm does — maybe they planned for someone else to handle one of those tasks, or maybe one of the times is approximate. Surfacing the conflict and letting the owner decide is more useful than silently dropping a task they might actually need. The tradeoff is that the "schedule" could technically be unexecutable if conflicts are ignored, but a warning is a much safer failure mode than silent data loss.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
