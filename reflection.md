# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

My scheduler looks at a task's time of day, its due date, its priority, whether it's already done, and how many minutes I have available. Time matters most, because pet care really happens on a clock: a dog needs to go out in the morning no matter what. So I sort by date and time first, and I only use priority to break ties when two tasks are at the same time. Completed tasks and tasks due on a later day are left out of today's plan. The available minutes are only used to warn me if the day is overbooked. They don't drop any tasks automatically, because I'd rather decide myself what to skip.

**b. Tradeoffs**

My conflict detection only checks for tasks that start at the exact same date and time. It doesn't check whether durations overlap. For example, a 30-minute walk at 07:30 and a feeding at 07:45 really do overlap, but my scheduler won't flag them. I think that's reasonable for now. Most pet care tasks are short and booked at round times, and the exact-match check is simple and easy to read. It also just returns a warning message instead of crashing, so the owner can decide what to do. Checking real overlaps would mean comparing each task's start + duration against the others, which I'd add next if I had more time.

I made a similar call on readability. When I asked the AI how `filter_tasks()` could be simplified, it suggested a single list comprehension with both conditions packed into one line. That's more "Pythonic," but I found it harder to read with two optional filters. I kept my version with a plain `for` loop and two `continue` checks, because each filter is easy to see. Both run in the same O(n) time, so I didn't lose any performance.

---

## 3. AI Collaboration

**a. How you used AI**

I used Claude Code in agent mode for most of the build. First it turned my four classes (Owner, Pet, Task, Scheduler) into a Mermaid UML diagram. Then I gave it the class descriptions from the assignment, and it wrote the code in `pawpal_system.py`, the `main.py` demo, and the two starter tests. The most helpful prompts were specific about the rules. For example, I told it the Scheduler has to get tasks through the Owner's `get_all_tasks()` method instead of from a single pet, and that made it build the multi-pet design correctly.

**b. Judgment and verification**

The AI's first UML draft gave Task a `title` and a `preferred_time` and didn't include a frequency. The assignment says a Task should have a description, time, frequency, and completion status, so I didn't keep that version. I had the code follow the assignment's fields and then updated the UML to match. I also checked that the Scheduler only gets its tasks through `owner.get_all_tasks()`. It never reads a pet's list directly, which is what the multi-pet requirement asks for. To check the results, I ran `python main.py` and saw that tasks from both pets printed in time order. I also ran `python -m pytest`, and both tests passed.

---

## 4. Testing and Verification

**a. What you tested**

I tested the main things my scheduler promises to do: tasks come out in time order, filters return the right pet's tasks or only done/not-done ones, completing a daily or weekly task creates the next one on the right date, and two tasks at the same time get a warning. I also tested edge cases, like an owner with no pets, a pet with no tasks, two tasks at the same time with different priorities, and a time typed as "9:00" instead of "09:00". These tests matter because the schedule is the whole point of the app. If sorting or repeating tasks broke, an owner could miss a feeding or a pill without noticing. The tests also let me change the code later and know right away if I broke something.

**b. Confidence**

I'd give it 4 out of 5. All 15 tests pass, and the demo in `main.py` and the Streamlit app behave the way I expect. I'm not at 5 because conflict detection only catches tasks that start at the exact same time, so a 30-minute walk at 7:30 and a feeding at 7:45 wouldn't be flagged. If I had more time, I'd test overlapping durations, tasks that run past midnight, invalid times like "25:00" or "abc", two pets with the same name, and what happens when the total minutes go over the owner's available time.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
