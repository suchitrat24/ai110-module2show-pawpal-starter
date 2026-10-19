from pawpal_system import Owner, Pet, Scheduler, Task

owner = Owner("Jordan", available_minutes=120)

mochi = Pet("Mochi", "dog", age=3)
luna = Pet("Luna", "cat", age=5)
owner.add_pet(mochi)
owner.add_pet(luna)

mochi.add_task(Task("Evening walk", "18:00", duration_minutes=30, priority="high"))
mochi.add_task(Task("Morning walk", "07:30", duration_minutes=30, priority="high"))
luna.add_task(Task("Feeding", "08:00", duration_minutes=10, priority="high"))
luna.add_task(Task("Brushing", "12:00", duration_minutes=15, priority="low", frequency="weekly"))
mochi.add_task(Task("Heartworm pill", "08:00", duration_minutes=5, priority="medium", frequency="once"))

scheduler = Scheduler(owner)
print(scheduler.format_schedule())
