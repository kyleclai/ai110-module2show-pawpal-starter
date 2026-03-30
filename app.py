import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session state — Owner persists across reruns
# ---------------------------------------------------------------------------

if "owner" not in st.session_state:
    st.session_state.owner = None

# ---------------------------------------------------------------------------
# Section 1: Owner setup
# ---------------------------------------------------------------------------

st.subheader("Owner Setup")

with st.form("owner_form"):
    col1, col2 = st.columns(2)
    with col1:
        owner_name = st.text_input("Your name", value="Jordan")
    with col2:
        available_minutes = st.number_input(
            "Minutes available today", min_value=15, max_value=480, value=120, step=15
        )
    save_owner = st.form_submit_button("Save Owner")

if save_owner:
    if st.session_state.owner is None:
        st.session_state.owner = Owner(
            name=owner_name, available_minutes_per_day=int(available_minutes)
        )
    else:
        # Update existing owner without wiping pets
        st.session_state.owner.name = owner_name
        st.session_state.owner.available_minutes_per_day = int(available_minutes)
    st.success(f"Saved: {owner_name}, {available_minutes} min/day")

if st.session_state.owner is None:
    st.info("Fill in your name and daily time above to get started.")
    st.stop()

owner: Owner = st.session_state.owner

# ---------------------------------------------------------------------------
# Section 2: Add a pet
# ---------------------------------------------------------------------------

st.divider()
st.subheader("Your Pets")

with st.form("add_pet_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        pet_name = st.text_input("Pet name")
    with col2:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with col3:
        age = st.number_input("Age (years)", min_value=0, max_value=30, value=2)
    add_pet = st.form_submit_button("Add Pet")

if add_pet:
    if not pet_name.strip():
        st.warning("Please enter a pet name.")
    elif any(p.name == pet_name.strip() for p in owner.get_pets()):
        st.warning(f"A pet named '{pet_name}' already exists.")
    else:
        owner.add_pet(Pet(name=pet_name.strip(), species=species, age=int(age)))
        st.success(f"Added {pet_name}!")

pets = owner.get_pets()
if pets:
    for pet in pets:
        pending = len(pet.get_pending_tasks())
        total = len(pet.get_tasks())
        st.write(f"- **{pet.name}** ({pet.species}, {pet.age} yr) — {pending} pending / {total} total task(s)")
else:
    st.info("No pets yet. Add one above.")

# ---------------------------------------------------------------------------
# Section 3: Add a task
# ---------------------------------------------------------------------------

if pets:
    st.divider()
    st.subheader("Add a Task")

    with st.form("add_task_form"):
        pet_names = [p.name for p in pets]
        selected_pet_name = st.selectbox("Assign to pet", pet_names)
        col1, col2 = st.columns(2)
        with col1:
            task_title = st.text_input("Task title", value="Morning walk")
            priority = st.selectbox("Priority", ["high", "medium", "low"])
        with col2:
            duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
            frequency = st.selectbox("Frequency", ["daily", "weekly", "as-needed"])
        add_task = st.form_submit_button("Add Task")

    if add_task:
        if not task_title.strip():
            st.warning("Please enter a task title.")
        else:
            target_pet = next(p for p in owner.get_pets() if p.name == selected_pet_name)
            target_pet.add_task(
                Task(
                    title=task_title.strip(),
                    duration_minutes=int(duration),
                    priority=priority,
                    frequency=frequency,
                )
            )
            st.success(f"Added '{task_title}' to {selected_pet_name}!")

    # Show current tasks per pet
    for pet in pets:
        if pet.get_tasks():
            st.markdown(f"**{pet.name}'s tasks**")
            for task in pet.get_tasks():
                status = "✅" if task.is_completed else "⬜"
                st.write(
                    f"  {status} {task.title} — {task.duration_minutes} min "
                    f"[{task.priority}, {task.frequency}]"
                )

# ---------------------------------------------------------------------------
# Section 4: Generate schedule
# ---------------------------------------------------------------------------

st.divider()
st.subheader("Generate Today's Schedule")

if not pets:
    st.info("Add at least one pet and some tasks first.")
elif not any(pet.get_pending_tasks() for pet in pets):
    st.info("No pending tasks to schedule.")
else:
    if st.button("Generate Schedule", type="primary"):
        scheduler = Scheduler(owner)
        full_schedule = scheduler.build_full_schedule()
        total_scheduled = sum(
            t.duration_minutes for tasks in full_schedule.values() for t in tasks
        )

        st.success("Here's your plan for today!")

        for pet in pets:
            scheduled = full_schedule.get(pet.name, [])
            if scheduled:
                st.markdown(f"**{pet.name}**")
                for i, task in enumerate(scheduled, start=1):
                    st.write(
                        f"  {i}. {task.title} — {task.duration_minutes} min "
                        f"[{task.priority} priority, {task.frequency}]"
                    )

        st.divider()
        remaining = owner.available_minutes_per_day - total_scheduled
        st.metric("Total scheduled", f"{total_scheduled} min")
        st.metric("Time remaining", f"{remaining} min")

        # Warn about anything that didn't fit
        skipped = [
            (pet.name, task.title)
            for pet in pets
            for task in pet.get_pending_tasks()
            if task not in full_schedule.get(pet.name, [])
        ]
        if skipped:
            st.warning(
                "These tasks didn't fit in today's budget: "
                + ", ".join(f"{name}: {title}" for name, title in skipped)
            )
