import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Plan your pets' care tasks for the day.")

# Streamlit reruns this script on every click, so keep the Owner in session_state
# and only create it the first time.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan", available_minutes=120)

owner: Owner = st.session_state.owner

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

st.divider()

st.subheader("Today's Schedule")
scheduler = Scheduler(owner)
schedule = scheduler.todays_schedule()

if not schedule:
    st.info("No pending tasks. Add some tasks above.")
else:
    st.table(
        [
            {
                "time": t.time,
                "pet": t.pet_name,
                "task": t.description,
                "minutes": t.duration_minutes,
                "priority": t.priority,
                "frequency": t.frequency,
            }
            for t in schedule
        ]
    )
    total = sum(t.duration_minutes for t in schedule)
    if total > owner.available_minutes:
        st.warning(f"Total: {total} min, which is more than the {owner.available_minutes} min you have.")
    else:
        st.success(f"Total: {total} min of {owner.available_minutes} min available.")

    st.markdown("**Mark a task done**")
    labels = [f"{t.time} · {t.pet_name} · {t.description}" for t in schedule]
    choice = st.selectbox("Task", labels, label_visibility="collapsed")
    if st.button("Mark complete"):
        schedule[labels.index(choice)].mark_complete()
        st.rerun()
