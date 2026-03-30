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

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
