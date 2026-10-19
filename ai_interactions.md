# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I used Claude Code (agent mode in VS Code) for the two stretch challenges:

1. **Advanced algorithm:** add a third scheduling capability beyond sorting, filtering, recurrence, and conflict detection. We chose **"next available slot"**: find the earliest free time today that fits a task of a given length.
2. **Data persistence:** make pets and tasks survive between runs by saving them to `data.json`, with `save_to_json` and `load_from_json` methods in `pawpal_system.py`. I asked how to serialize nested objects to JSON. It compared a library like marshmallow with custom dictionary conversion, and I chose custom `to_dict()`/`from_dict()` methods because the data is small and it avoids a new dependency.

**What did the agent do?**

| File | What changed |
|------|--------------|
| `pawpal_system.py` | Added `Scheduler.find_next_available_slot()` and a `minutes_to_time()` helper. Added `to_dict()`/`from_dict()` to `Task`, `Pet`, and `Owner`, plus `Owner.save_to_json()` and `Owner.load_from_json()` (safe write through a temp file; returns `None` if the file doesn't exist). |
| `app.py` | Loads `data.json` on startup (with a warning instead of a crash if the file is damaged), auto-saves only when something changed, adds a sidebar **Clear saved data** button, a **🔍 Find a free time today** helper, and a 💡 suggested free time under conflict warnings. |
| `main.py` | Demos the slot finder (searching from 08:00) and a save → load round trip that checks the data matches. |
| `tests/test_pawpal.py` | 6 new tests: 4 for the slot finder (empty day, gaps between tasks, ignoring completed and other-day tasks, a full day) and 2 for persistence (round trip, missing file). 21 tests total, all passing. |
| `README.md` | Added both features to the Features list and the Smarter Scheduling table, a new 💾 Data Persistence section, and refreshed the sample output and test output. |
| `diagrams/uml_final.mmd`, `diagrams/uml.mmd` | Added the new methods and the `data.json` dependency. |
| `.gitignore` | Ignores `data.json`, `demo_data.json`, and temp save files. |

It ran `python -m pytest` and `python main.py` after each step. It also ran a simulated Streamlit session that adds a pet and two clashing tasks, checks the suggested slot, closes and reopens the app to confirm the data reloaded, then clears the saved data.

**What did you have to verify or fix manually?**

These problems were caught during review and fixed before I accepted the changes:

- **Suggesting a time that had already passed.** The first version of the app always searched from 07:00, so at 4 PM it suggested "07:00". The app now starts searching from the current time. The method itself still takes an `earliest` argument, so tests and `main.py` can use fixed times.
- **A hard-to-read line in `app.py`.** The first try at "longest conflicting task" was a long, tangled expression. It was rewritten to reuse the conflict time slots the page already computes.
- **A weak demo.** The first `main.py` demo returned 07:00 for every length because the morning walk was already completed, which didn't show anything. It now searches from 08:00, so it visibly skips past Feeding (08:00–08:10) and Brushing (12:00–12:15).
- **Keeping personal data out of git.** I decided `data.json` shouldn't be committed and added it to `.gitignore`.

I also checked that conflict detection still only checks exact start times. The slot finder uses durations, but I left `detect_conflicts()` alone to keep the change small. Changing it is listed as a future improvement.

---


