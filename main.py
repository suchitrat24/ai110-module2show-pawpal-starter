from pawpal_system import Owner, Pet, Scheduler, Task

owner = Owner("Jordan", available_minutes=120)

mochi = Pet("Mochi", "dog", age=3)
luna = Pet("Luna", "cat", age=5)
owner.add_pet(mochi)
owner.add_pet(luna)

# Tasks are added out of order on purpose so sorting has something to fix.
mochi.add_task(Task("Evening walk", "18:00", duration_minutes=30, priority="high"))
luna.add_task(Task("Brushing", "12:00", duration_minutes=15, priority="low", frequency="weekly"))
mochi.add_task(Task("Morning walk", "07:30", duration_minutes=30, priority="high"))
luna.add_task(Task("Feeding", "08:00", duration_minutes=10, priority="high"))
# Same time as Luna's feeding, to trigger a conflict warning.
mochi.add_task(Task("Heartworm pill", "08:00", duration_minutes=5, priority="medium", frequency="once"))

scheduler = Scheduler(owner)


def show(title, tasks):
    """Print a titled list of tasks, one per line."""
    print(f"\n{title}")
    for t in tasks:
        status = "done" if t.completed else "todo"
        print(f"  {t.due_date} {t.time}  {t.pet_name:<6} {t.description:<15} ({t.frequency}, {status})")


show("Tasks as added (unsorted):", scheduler.get_tasks())
show("Sorted by time:", scheduler.sort_by_time())
show("Only Mochi's tasks:", scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Mochi")))

print("\nConflict check:")
conflicts = scheduler.detect_conflicts()
for warning in conflicts:
    print(f"  WARNING: {warning}")
if not conflicts:
    print("  No conflicts found.")

# Completing a daily task should create tomorrow's copy; a one-time task should not repeat.
morning_walk = mochi.tasks[1]
scheduler.mark_task_complete(morning_walk)
scheduler.mark_task_complete(mochi.tasks[2])  # Heartworm pill (once)

show("Completed tasks:", scheduler.filter_tasks(completed=True))
show("Pending tasks (note tomorrow's Morning walk):", scheduler.sort_by_time(scheduler.filter_tasks(completed=False)))

print()
print(scheduler.format_schedule())
