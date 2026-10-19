from collections import Counter
from datetime import datetime
from pathlib import Path

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task, time_to_minutes

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Plan your pets' care tasks for the day.")

DATA_FILE = Path(__file__).parent / "data.json"

# Streamlit reruns this script on every click, so keep the Owner in session_state
# and only create it the first time: from data.json if it exists, otherwise fresh.
if "owner" not in st.session_state:
    try:
        st.session_state.owner = Owner.load_from_json(DATA_FILE)
    except (ValueError, KeyError, TypeError) as err:
        st.session_state.owner = None
        st.warning(f"Couldn't read {DATA_FILE.name} ({err}). Starting with a fresh owner.")
    if st.session_state.owner is None:
        st.session_state.owner = Owner("Jordan", available_minutes=120)
    st.session_state.saved = st.session_state.owner.to_dict()

owner: Owner = st.session_state.owner

# Free-slot searches start from now (or 07:00 if it's earlier), so we never suggest a time that's passed.
search_from = max("07:00", datetime.now().strftime("%H:%M"))

with st.sidebar:
    st.markdown("**💾 Saved data**")
    st.caption(f"Pets and tasks save automatically to `{DATA_FILE.name}` and reload next time.")
    if st.button("Clear saved data"):
        DATA_FILE.unlink(missing_ok=True)
        del st.session_state["owner"]
        st.rerun()

st.subheader("Owner")
col1, col2 = st.columns(2)
with col1:
    owner.name = st.text_input("Owner name", value=owner.name)
with col2:
    owner.available_minutes = int(
        st.number_input(
            "Minutes available today", min_value=0, max_value=1440, value=owner.available_minutes
        )
    )

st.divider()

st.subheader("Add a Pet")
with st.form("add_pet", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        pet_name = st.text_input("Pet name")
    with col2:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with col3:
        age = st.number_input("Age", min_value=0, max_value=40, value=1)
    if st.form_submit_button("Add pet"):
        if not pet_name.strip():
            st.error("Please enter a pet name.")
        elif owner.get_pet(pet_name.strip()):
            st.error(f"{pet_name.strip()} is already added.")
        else:
            owner.add_pet(Pet(pet_name.strip(), species, age=int(age)))
            st.success(f"Added {pet_name.strip()}!")

if owner.pets:
    st.write("Your pets:")
    st.table(
        [{"name": p.name, "species": p.species, "age": p.age, "tasks": len(p.tasks)} for p in owner.pets]
    )
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.subheader("Add a Task")
if not owner.pets:
    st.caption("Add a pet first, then you can give it tasks.")
else:
    with st.form("add_task", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            task_pet = st.selectbox("Pet", [p.name for p in owner.pets])
            description = st.text_input("Task", value="Morning walk")
            task_time = st.time_input("Time")
        with col2:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
            frequency = st.selectbox("Frequency", ["once", "daily", "weekly"], index=1)
        if st.form_submit_button("Add task"):
            if not description.strip():
                st.error("Please enter a task description.")
            else:
                owner.get_pet(task_pet).add_task(
                    Task(
                        description.strip(),
                        task_time.strftime("%H:%M"),
                        duration_minutes=int(duration),
                        priority=priority,
                        frequency=frequency,
                    )
                )
                st.success(f"Added '{description.strip()}' for {task_pet}.")

    with st.expander("🔍 Find a free time today"):
        need = st.number_input("How many minutes do you need?", min_value=1, max_value=240, value=20)
        slot = Scheduler(owner).find_next_available_slot(int(need), earliest=search_from)
        if slot:
            st.success(f"Next free {int(need)}-min slot today: **{slot}** (searching {search_from}–21:00).")
        else:
            st.warning(f"No free {int(need)}-min slot left today ({search_from}–21:00).")

st.divider()

st.subheader("Today's Schedule")
scheduler = Scheduler(owner)
schedule = scheduler.todays_schedule()

PRIORITY_ICON = {"high": "🔴 high", "medium": "🟡 medium", "low": "🟢 low"}

if not schedule:
    st.info("No pending tasks for today. Add some tasks above.")
else:
    conflicts = scheduler.detect_conflicts(schedule)
    total = sum(t.duration_minutes for t in schedule)

    col1, col2, col3 = st.columns(3)
    col1.metric("Tasks today", len(schedule))
    col2.metric("Minutes needed", f"{total} / {owner.available_minutes}")
    col3.metric("Conflicts", len(conflicts))

    # Warnings go above the table so the owner sees them before reading the plan.
    for warning in conflicts:
        st.warning(
            f"⚠️ **Time conflict:** {warning}.  \n"
            "You can't do these at the same time. Move one to a different time, "
            "or handle the higher-priority one first."
        )
    slot_counts = Counter(time_to_minutes(t.time) for t in schedule)
    conflict_slots = {slot for slot, count in slot_counts.items() if count > 1}
    if conflicts:
        longest = max(t.duration_minutes for t in schedule if time_to_minutes(t.time) in conflict_slots)
        slot = scheduler.find_next_available_slot(longest, earliest=search_from)
        if slot:
            st.info(f"💡 Next free {longest}-min slot today is **{slot}**. Try moving one of the clashing tasks there.")
    if total > owner.available_minutes:
        st.warning(
            f"⏰ **Overbooked:** these tasks need {total} min but you have {owner.available_minutes} min. "
            "Consider skipping or shortening a 🟢 low-priority task."
        )
    elif not conflicts:
        st.success(f"✅ No conflicts. {total} of {owner.available_minutes} min used.")

    st.caption("Sorted by time; tasks at the same time are ordered by priority.")
    st.table(
        [
            {
                "time": t.time,
                "pet": t.pet_name,
                "task": t.description,
                "minutes": t.duration_minutes,
                "priority": PRIORITY_ICON.get(t.priority, t.priority),
                "repeats": t.frequency,
                "": "⚠️" if time_to_minutes(t.time) in conflict_slots else "",
            }
            for t in schedule
        ]
    )

    st.markdown("**Mark a task done**")
    labels = [f"{t.time} · {t.pet_name} · {t.description}" for t in schedule]
    choice = st.selectbox("Task", labels, label_visibility="collapsed")
    if st.button("Mark complete"):
        next_task = scheduler.mark_task_complete(schedule[labels.index(choice)])
        if next_task:
            st.toast(f"Next '{next_task.description}' scheduled for {next_task.due_date}.")
        st.rerun()

st.divider()

st.subheader("Browse Tasks")
col1, col2 = st.columns(2)
with col1:
    pet_filter = st.selectbox("Pet", ["All"] + [p.name for p in owner.pets])
with col2:
    status_filter = st.selectbox("Status", ["All", "Pending", "Completed"])
filtered = scheduler.filter_tasks(
    pet_name=None if pet_filter == "All" else pet_filter,
    completed={"All": None, "Pending": False, "Completed": True}[status_filter],
)
if filtered:
    st.table(
        [
            {
                "date": str(t.due_date),
                "time": t.time,
                "pet": t.pet_name,
                "task": t.description,
                "frequency": t.frequency,
                "done": "✅" if t.completed else "",
            }
            for t in scheduler.sort_by_time(filtered)
        ]
    )
else:
    st.caption("No tasks match these filters.")

# Save after every run where something changed, so data.json always matches the app.
current = owner.to_dict()
if current != st.session_state.get("saved"):
    owner.save_to_json(DATA_FILE)
    st.session_state.saved = current
