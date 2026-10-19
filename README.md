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

## ✨ Features

- **Multi-pet support:** one owner can manage several pets. The scheduler gets every pet's tasks through `Owner.get_all_tasks()`.
- **Sorting by time:** `Scheduler.sort_by_time()` orders tasks by date, then time of day. Tasks at the same time are ordered by priority (high → medium → low). Times like `"9:00"` and `"09:00"` are treated the same.
- **Filtering:** `Scheduler.filter_tasks()` shows tasks for one pet, only pending or only completed tasks, or both filters together.
- **Daily and weekly recurrence:** marking a `daily` or `weekly` task complete with `Scheduler.mark_task_complete()` automatically adds the next one (+1 day or +7 days, using `timedelta`). `once` tasks don't repeat.
- **Today's plan:** `Scheduler.todays_schedule()` shows only pending tasks due today, so finished tasks and future repeats stay out of the way.
- **Conflict warnings:** `Scheduler.detect_conflicts()` flags tasks booked at the same date and time, for the same pet or different pets. It returns readable warning messages instead of crashing.
- **Next available slot:** `Scheduler.find_next_available_slot()` finds the earliest free time today that fits a task of a given length. It uses each task's *duration*, not just its start time, so it works around a 30-minute walk instead of booking into the middle of it. The app uses it to suggest a time whenever there's a conflict.
- **Saves between runs:** pets and tasks are saved to `data.json` with `Owner.save_to_json()` and loaded back with `Owner.load_from_json()`, so nothing is lost when you close the app.
- **Time budget check:** the app compares the total task minutes with the owner's available minutes and warns when the day is overbooked.
- **Tested:** 21 pytest tests cover the features above plus edge cases (see [Testing PawPal+](#-testing-pawpal)).

## 🧩 Implementation Summary

The core logic lives in `pawpal_system.py` and is built from four classes:

- **Task**: one care activity, with a description, time (`HH:MM`), duration, priority, frequency (once/daily/weekly), and completion status. `mark_complete()` marks it done.
- **Pet**: a pet's details plus its list of tasks. `add_task()` attaches a task and tags it with the pet's name.
- **Owner**: holds multiple pets. `get_all_tasks()` returns every pet's tasks in one list.
- **Scheduler**: the "brain." It pulls tasks through `Owner.get_all_tasks()`, so it sees every pet. It then filters out completed tasks, sorts by time (with priority as the tie-breaker), and formats today's schedule.

How they connect: Owner → many Pets → many Tasks, and the Scheduler talks only to the Owner. The full class diagram is in [`diagrams/uml_final.mmd`](diagrams/uml_final.mmd).

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

Next available slot (searching from 08:00):
  15-min task: 08:10
  240-min task: 12:15

Saved and reloaded demo_data.json: 2 pets, 6 tasks, match = True
```

## 🧪 Testing PawPal+

Run the test suite from the project folder:

```bash
python -m pytest
```

The 21 tests in `tests/test_pawpal.py` cover:

- **Basics:** `mark_complete()` changes a task's status, and `add_task()` increases a pet's task count.
- **Sorting:** tasks come back in chronological order. Tasks at the same time are ordered by priority (high first). Unpadded times like `"9:00"` sort before `"10:00"`.
- **Filtering:** by pet, by completion status, and by both together.
- **Recurring tasks:** completing a daily task creates a copy for the next day, and a weekly task moves 7 days. A `once` task doesn't repeat. The new copy keeps the same details and stays out of today's schedule until its day.
- **Conflict detection:** two tasks at the same time get flagged. Three tasks at the same time give one warning. Completed tasks and tasks on different days are *not* flagged.
- **Next available slot:** an empty day starts at 07:00. Short tasks fit into small gaps, and longer ones skip ahead past busy blocks. Completed tasks and other days are ignored, and it returns `None` when the day is full.
- **Persistence:** saving and loading gives back the same owner, pets, and tasks (including completion status and `due_date`). Loading a missing file returns `None`.
- **Edge cases:** an owner with no pets, and a pet with no tasks, return empty lists and an empty schedule instead of crashing.

Successful test run:

```
============================= test session starts =============================
platform win32 -- Python 3.13.15, pytest-9.1.1, pluggy-1.7.0
rootdir: D:\CodePath AI 110\ai110-module2show-pawpal-starter
plugins: anyio-4.15.1
collected 21 items

tests\test_pawpal.py .....................                               [100%]

============================= 21 passed in 0.05s ==============================
```

**Confidence level: ⭐⭐⭐⭐ (4/5).** Every core behavior and the edge cases I could think of pass. I'm not giving it 5 because conflict detection only checks exact start times (the slot finder does use durations, but conflict warnings don't yet), and the Streamlit UI is only tested by simulated clicks, not real browser use.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Sorts with `sorted()` and a lambda key of `(due_date, minutes after midnight, priority)`. Times are converted with `time_to_minutes()`, so `"7:30"` and `"07:30"` sort the same. Priority breaks ties at the same time. |
| Filtering | `Scheduler.filter_tasks(pet_name=..., completed=...)` | Filters by pet, by completion status, or both. Leaving a filter as `None` skips it. `filter_by_pet()` and `get_pending_tasks()` are shortcuts built on it. |
| Conflict handling | `Scheduler.detect_conflicts()` | Groups pending tasks by exact date + start time and returns a warning string for each slot with 2+ tasks (same pet or different pets). It never raises an error. The warnings show in `format_schedule()` and in the Streamlit app. |
| Recurring tasks | `Task.next_occurrence()`, `Scheduler.mark_task_complete()` | Completing a `daily` or `weekly` task adds a fresh copy to the same pet, due `today + timedelta(days=1)` or `+ timedelta(weeks=1)`. `once` tasks don't repeat. |
| Next available slot | `Scheduler.find_next_available_slot(duration, on, earliest, latest)` | Treats each pending task that day as a busy block from start to start + duration, walks the blocks in time order, and returns the first gap long enough (default 07:00–21:00), or `None`. O(n log n) for the sort. |
| Today's plan | `Scheduler.todays_schedule()` | Shows only pending tasks due today, in time order, so tomorrow's copies stay hidden until their day. |

## 💾 Data Persistence

PawPal+ remembers your pets and tasks between runs by saving them to `data.json` in the project folder.

**How it works**

1. **Converting objects to plain data:** JSON only understands dicts, lists, strings, numbers, and booleans, so each class has a `to_dict()` and a `from_dict()` method. `Task` stores its `due_date` as an ISO string (`"2026-10-19"`) and turns it back into a `date` when loading. `Pet` and `Owner` call their children's methods, so the whole tree (Owner → Pets → Tasks) is converted in one call. I used custom dict conversion instead of a library like marshmallow, because the data is small and this needs no extra dependency.
2. **Saving:** `Owner.save_to_json(path="data.json")` writes the JSON to a temporary file and then swaps it into place, so a crash in the middle of saving never leaves a half-written `data.json`.
3. **Loading:** `Owner.load_from_json(path="data.json")` returns the rebuilt `Owner`, or `None` if the file doesn't exist yet (first run).
4. **In the Streamlit app:** on startup, `app.py` loads `data.json` if it exists, or starts fresh if not. If the file is damaged, it shows a warning instead of crashing. At the end of every run, it saves only if something changed. The sidebar has a **Clear saved data** button to start over.

`data.json` is listed in `.gitignore` because it's personal, local data that changes every time you use the app.

**Files modified for persistence**

| File | Change |
|------|--------|
| `pawpal_system.py` | Added `to_dict()`/`from_dict()` to `Task`, `Pet`, and `Owner`, plus `Owner.save_to_json()` and `Owner.load_from_json()` |
| `app.py` | Loads from `data.json` on startup, auto-saves after changes, adds a **Clear saved data** button |
| `main.py` | Saves to `demo_data.json`, reloads it, and checks the data matches |
| `tests/test_pawpal.py` | Round-trip save/load test and missing-file test |
| `.gitignore` | Ignores `data.json`, `demo_data.json`, and temporary save files |

## 📸 Demo Walkthrough

Start the app with `streamlit run app.py`.

**Main UI features**

| Section | What you can do |
|---------|-----------------|
| **Owner** | Set your name and how many minutes you have for pet care today. |
| **Add a Pet** | Add a pet with a name, species, and age. Blank names and duplicate names are rejected. |
| **Add a Task** | Pick a pet and enter the task, time, duration, priority, and how often it repeats (once, daily, weekly). Open **🔍 Find a free time today** to get the next open slot for a task of any length. |
| **Today's Schedule** | See today's pending tasks sorted by time, with a summary (tasks today, minutes needed, conflicts), conflict and overbooked warnings, a 💡 suggested free time for conflicts, and ⚠️ next to clashing rows. Mark a task complete here. |
| **Browse Tasks** | Filter every task by pet and by status (all, pending, completed), including future repeats. |
| **Sidebar** | Shows that data saves to `data.json` automatically, with a **Clear saved data** button. |

**Example workflow**

1. Set the owner to **Jordan** with **120** minutes available.
2. Add two pets: **Mochi** (dog) and **Luna** (cat).
3. Add tasks out of order: Mochi's *Evening walk* at 18:00, Mochi's *Morning walk* at 07:30, and Luna's *Feeding* at 08:00.
4. Open **Today's Schedule**. The tasks show in time order: 07:30 → 08:00 → 18:00.
5. Add Mochi's *Heartworm pill* at 08:00. A **Time conflict** warning appears above the table, suggesting you move one task, and both 08:00 rows get a ⚠️. A 💡 tip below it suggests the next free time that fits.
6. Mark *Morning walk* complete. A pop-up says the next one is scheduled for tomorrow, and the walk leaves today's list.
7. In **Browse Tasks**, choose **Mochi** + **Pending** to see tomorrow's *Morning walk*, or **Completed** to see what's done.
8. Close the app and run `streamlit run app.py` again. Your pets and tasks are still there, loaded from `data.json`.

**Key Scheduler behaviors shown**

- Sorting by time, with priority breaking ties (`sort_by_time`)
- Conflict warnings for tasks at the same time (`detect_conflicts`)
- Daily/weekly recurrence when a task is completed (`mark_task_complete` → `next_occurrence`)
- Filtering by pet and status (`filter_tasks`)
- Today-only, pending-only plan (`todays_schedule`)
- Next free time that fits a task's length (`find_next_available_slot`)
- Saving and loading between runs (`save_to_json` / `load_from_json`)

**Sample CLI output (`python main.py`)**

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

Next available slot (searching from 08:00):
  15-min task: 08:10
  240-min task: 12:15

Saved and reloaded demo_data.json: 2 pets, 6 tasks, match = True
```

