from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_status():
    task = Task("Feeding", "08:00")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog")
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task("Morning walk", "07:30"))
    assert len(pet.get_tasks()) == 1


def make_scheduler():
    owner = Owner("Jordan")
    mochi, luna = Pet("Mochi", "dog"), Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)
    mochi.add_task(Task("Evening walk", "18:00"))
    mochi.add_task(Task("Morning walk", "7:30"))
    luna.add_task(Task("Feeding", "08:00"))
    return Scheduler(owner), mochi, luna


def test_sort_by_time_orders_tasks_chronologically():
    scheduler, _, _ = make_scheduler()
    assert [t.description for t in scheduler.sort_by_time()] == ["Morning walk", "Feeding", "Evening walk"]


def test_filter_by_pet_and_status():
    scheduler, mochi, _ = make_scheduler()
    mochi.tasks[0].mark_complete()
    assert {t.pet_name for t in scheduler.filter_tasks(pet_name="Luna")} == {"Luna"}
    assert [t.description for t in scheduler.filter_tasks(completed=True)] == ["Evening walk"]
    assert [t.description for t in scheduler.filter_tasks(pet_name="Mochi", completed=False)] == ["Morning walk"]


def test_completing_daily_task_creates_next_day_copy():
    scheduler, mochi, _ = make_scheduler()
    walk = mochi.tasks[1]
    new_task = scheduler.mark_task_complete(walk)
    assert walk.completed is True
    assert new_task in mochi.tasks
    assert new_task.completed is False
    assert new_task.due_date == walk.due_date + timedelta(days=1)


def test_completing_weekly_task_moves_one_week():
    task = Task("Brushing", "12:00", frequency="weekly", due_date=date(2026, 10, 19))
    assert task.next_occurrence().due_date == date(2026, 10, 26)


def test_one_time_task_does_not_repeat():
    scheduler, mochi, _ = make_scheduler()
    pill = Task("Heartworm pill", "09:00", frequency="once")
    mochi.add_task(pill)
    count = len(mochi.tasks)
    assert scheduler.mark_task_complete(pill) is None
    assert len(mochi.tasks) == count


def test_detect_conflicts_warns_on_same_time():
    scheduler, mochi, _ = make_scheduler()
    assert scheduler.detect_conflicts() == []
    mochi.add_task(Task("Heartworm pill", "08:00"))
    warnings = scheduler.detect_conflicts()
    assert len(warnings) == 1
    assert "Feeding" in warnings[0] and "Heartworm pill" in warnings[0]


# --- Edge cases ---


def test_pet_with_no_tasks_and_owner_with_no_pets():
    owner = Owner("Jordan")
    scheduler = Scheduler(owner)
    assert scheduler.get_tasks() == []
    assert scheduler.todays_schedule() == []
    assert scheduler.detect_conflicts() == []
    owner.add_pet(Pet("Mochi", "dog"))
    assert scheduler.filter_tasks(pet_name="Mochi") == []
    assert "No tasks scheduled." in scheduler.format_schedule()


def test_same_time_tasks_are_ordered_by_priority():
    scheduler, mochi, _ = make_scheduler()
    mochi.add_task(Task("Low thing", "12:00", priority="low"))
    mochi.add_task(Task("High thing", "12:00", priority="high"))
    noon = [t.description for t in scheduler.sort_by_time() if t.time == "12:00"]
    assert noon == ["High thing", "Low thing"]


def test_sort_handles_unpadded_hours():
    # "9:00" would sort after "10:00" as plain text; it should come first.
    tasks = [Task("Late", "10:00"), Task("Early", "9:00")]
    scheduler = Scheduler(Owner("Jordan"))
    assert [t.description for t in scheduler.sort_by_time(tasks)] == ["Early", "Late"]


def test_recurring_copy_keeps_details_and_is_hidden_until_its_day():
    scheduler, mochi, _ = make_scheduler()
    walk = mochi.tasks[1]
    new_task = scheduler.mark_task_complete(walk)
    assert (new_task.description, new_task.time, new_task.pet_name) == (walk.description, walk.time, "Mochi")
    assert new_task is not walk
    assert new_task not in scheduler.todays_schedule()
    assert new_task in scheduler.todays_schedule(today=walk.due_date + timedelta(days=1))


def test_completed_tasks_do_not_cause_conflicts():
    scheduler, mochi, luna = make_scheduler()
    mochi.add_task(Task("Heartworm pill", "08:00"))
    luna.tasks[0].mark_complete()  # Feeding at 08:00
    assert scheduler.detect_conflicts() == []


def test_same_time_on_different_days_is_not_a_conflict():
    scheduler, mochi, _ = make_scheduler()
    tomorrow = date.today() + timedelta(days=1)
    mochi.add_task(Task("Vet visit", "08:00", due_date=tomorrow))
    assert scheduler.detect_conflicts() == []


def test_three_way_conflict_gives_one_warning():
    scheduler, mochi, luna = make_scheduler()
    mochi.add_task(Task("Pill", "08:00"))
    luna.add_task(Task("Litter box", "8:00"))
    warnings = scheduler.detect_conflicts()
    assert len(warnings) == 1
    assert all(name in warnings[0] for name in ["Feeding", "Pill", "Litter box"])
