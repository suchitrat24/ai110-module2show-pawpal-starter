# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🧩 Implementation Summary

The core logic lives in `pawpal_system.py` and is built from four classes:

- **Task**: one care activity, with a description, time (`HH:MM`), duration, priority, frequency (once/daily/weekly), and completion status. `mark_complete()` marks it done.
- **Pet**: a pet's details plus its list of tasks. `add_task()` attaches a task and tags it with the pet's name.
- **Owner**: holds multiple pets. `get_all_tasks()` returns every pet's tasks in one list.
- **Scheduler**: the "brain." It pulls tasks through `Owner.get_all_tasks()`, so it sees every pet. It then filters out completed tasks, sorts by time (with priority as the tie-breaker), and formats today's schedule.

How they connect: Owner → many Pets → many Tasks, and the Scheduler talks only to the Owner.

## 🖥️ Sample Output

Output of `python main.py`:

```
Tasks as added (unsorted):
  2026-10-19 18:00  Mochi  Evening walk    (daily, todo)
  2026-10-19 07:30  Mochi  Morning walk    (daily, todo)
  2026-10-19 08:00  Mochi  Heartworm pill  (once, todo)
  2026-10-19 12:00  Luna   Brushing        (weekly, todo)
  2026-10-19 08:00  Luna   Feeding         (daily, todo)

Sorted by time:
  2026-10-19 07:30  Mochi  Morning walk    (daily, todo)
  2026-10-19 08:00  Luna   Feeding         (daily, todo)
  2026-10-19 08:00  Mochi  Heartworm pill  (once, todo)
  2026-10-19 12:00  Luna   Brushing        (weekly, todo)
  2026-10-19 18:00  Mochi  Evening walk    (daily, todo)

Only Mochi's tasks:
  2026-10-19 07:30  Mochi  Morning walk    (daily, todo)
  2026-10-19 08:00  Mochi  Heartworm pill  (once, todo)
  2026-10-19 18:00  Mochi  Evening walk    (daily, todo)

Conflict check:
  WARNING: Conflict at 08:00 on 2026-10-19: Mochi: Heartworm pill, Luna: Feeding

Completed tasks:
  2026-10-19 07:30  Mochi  Morning walk    (daily, done)
  2026-10-19 08:00  Mochi  Heartworm pill  (once, done)

Pending tasks (note tomorrow's Morning walk):
  2026-10-19 08:00  Luna   Feeding         (daily, todo)
  2026-10-19 12:00  Luna   Brushing        (weekly, todo)
  2026-10-19 18:00  Mochi  Evening walk    (daily, todo)
  2026-10-20 07:30  Mochi  Morning walk    (daily, todo)

Today's Schedule for Jordan
========================================
08:00  Luna     Feeding             10 min  [high, daily]
12:00  Luna     Brushing            15 min  [low, weekly]
18:00  Mochi    Evening walk        30 min  [high, daily]
----------------------------------------
Total: 55 min of 120 min available
```

## 🧪 Testing PawPal+

Run the test suite from the project folder:

```bash
python -m pytest
```

The 15 tests in `tests/test_pawpal.py` cover:

- **Basics:** `mark_complete()` changes a task's status, and `add_task()` increases a pet's task count.
- **Sorting:** tasks come back in chronological order. Tasks at the same time are ordered by priority (high first). Unpadded times like `"9:00"` sort before `"10:00"`.
- **Filtering:** by pet, by completion status, and by both together.
- **Recurring tasks:** completing a daily task creates a copy for the next day, and a weekly task moves 7 days. A `once` task doesn't repeat. The new copy keeps the same details and stays out of today's schedule until its day.
- **Conflict detection:** two tasks at the same time get flagged. Three tasks at the same time give one warning. Completed tasks and tasks on different days are *not* flagged.
- **Edge cases:** an owner with no pets, and a pet with no tasks, return empty lists and an empty schedule instead of crashing.

Successful test run:

```
============================= test session starts =============================
platform win32 -- Python 3.13.15, pytest-9.1.1, pluggy-1.7.0
rootdir: D:\CodePath AI 110\ai110-module2show-pawpal-starter
plugins: anyio-4.15.1
collected 15 items

tests\test_pawpal.py ...............                                     [100%]

============================= 15 passed in 0.07s ==============================
```

**Confidence level: ⭐⭐⭐⭐ (4/5).** Every core behavior and the edge cases I could think of pass. I'm not giving it 5 because conflict detection only checks exact start times (not overlapping durations), and the Streamlit UI is only tested by hand.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Sorts with `sorted()` and a lambda key of `(due_date, minutes after midnight, priority)`. Times are converted with `time_to_minutes()`, so `"7:30"` and `"07:30"` sort the same. Priority breaks ties at the same time. |
| Filtering | `Scheduler.filter_tasks(pet_name=..., completed=...)` | Filters by pet, by completion status, or both. Leaving a filter as `None` skips it. `filter_by_pet()` and `get_pending_tasks()` are shortcuts built on it. |
| Conflict handling | `Scheduler.detect_conflicts()` | Groups pending tasks by exact date + start time and returns a warning string for each slot with 2+ tasks (same pet or different pets). It never raises an error. The warnings show in `format_schedule()` and in the Streamlit app. |
| Recurring tasks | `Task.next_occurrence()`, `Scheduler.mark_task_complete()` | Completing a `daily` or `weekly` task adds a fresh copy to the same pet, due `today + timedelta(days=1)` or `+ timedelta(weeks=1)`. `once` tasks don't repeat. |
| Today's plan | `Scheduler.todays_schedule()` | Shows only pending tasks due today, in time order, so tomorrow's copies stay hidden until their day. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
