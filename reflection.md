# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

My first UML had four classes connected in a simple chain: an Owner has many Pets, each Pet has many Tasks, and a Scheduler plans for one Owner.

- **Task** held one care activity: what it is, when, how long, how important, and whether it's done.
- **Pet** held the pet's info and its own list of tasks.
- **Owner** held the pets and my available time, and had one method to collect every pet's tasks.
- **Scheduler** was the "brain": it read tasks from the Owner, sorted them, and built the day's plan.

I kept the Scheduler separate from the data classes on purpose, so all the scheduling rules live in one place.

**b. Design changes**

Yes, a few times. The biggest change was adding a `due_date` to Task. My first design only had a time of day, but once I added recurring tasks I needed a way to say "this walk is for tomorrow." Without a date, tomorrow's copy would show up in today's schedule right next to the one I just finished. I also renamed Task's `title` to `description` and added `frequency` to match the assignment. On top of that, I added `mark_task_complete()` to the Scheduler instead of just using `Task.mark_complete()`, because creating the next task means adding it to the right pet, and a Task doesn't know about its Pet. I also added a small `time_to_minutes()` helper after realizing "9:00" sorts after "10:00" as plain text. The final diagram is in `diagrams/uml_final.mmd`.

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

I used Claude Code inside VS Code for the whole project, mostly in agent mode. First it turned my four classes (Owner, Pet, Task, Scheduler) into a Mermaid UML diagram. Then I gave it the class descriptions from the assignment, and it wrote the code in `pawpal_system.py`, the `main.py` demo, and the two starter tests. The most helpful prompts were specific about the rules. For example, I told it the Scheduler has to get tasks through the Owner's `get_all_tasks()` method instead of from a single pet, and that made it build the multi-pet design correctly.

The features that helped most were:

- **Agent mode editing several files at once.** Adding recurring tasks touched `pawpal_system.py`, `main.py`, `app.py`, the tests, and the README together. Doing that by hand, I would have missed something.
- **Running the code itself.** The assistant ran `python main.py` and `python -m pytest` after each change, so I could see real output instead of trusting that it worked. It even caught its own mistake once: the conflict warning didn't show in the demo because it marked the task complete before printing the check, so it moved the check earlier.
- **Asking "why" questions.** Asking how to sort "HH:MM" strings with a lambda key, and how `timedelta` works for daily vs. weekly, taught me the idea instead of just handing me code.

**b. Judgment and verification**

The AI's first UML draft gave Task a `title` and a `preferred_time` and didn't include a frequency. The assignment says a Task should have a description, time, frequency, and completion status, so I didn't keep that version. I had the code follow the assignment's fields and then updated the UML to match. I also checked that the Scheduler only gets its tasks through `owner.get_all_tasks()`. It never reads a pet's list directly, which is what the multi-pet requirement asks for. To check the results, I ran `python main.py` and saw that tasks from both pets printed in time order. I also ran `python -m pytest`, and both tests passed.

One suggestion I changed to keep the design clean: for recurring tasks, the easy option was to put all the logic in `Task.mark_complete()`. But a Task only knows about itself, not which Pet it belongs to, so it would have needed a reference back to its Pet, which would make the classes tangled. Instead I split it: `Task.next_occurrence()` only *creates* the next copy, and `Scheduler.mark_task_complete()` decides where it goes. That kept Task simple and kept the "managing tasks across pets" job in the Scheduler, where it belongs. I also turned down the one-line list comprehension for `filter_tasks()` (see 2b) because readability mattered more to me.

**c. Organizing by phase**

I worked through the project one phase at a time (design, core classes, UI, smarter scheduling, testing, polish), and gave the assistant one phase's instructions at a time. Keeping each phase separate helped me stay organized: each step had a clear goal and a clear "done" point (the demo runs, the tests pass, the commit is pushed), and I committed after each one. When something needed checking later, I knew which commit and which phase it came from. Honestly, I kept most of it in one long chat instead of opening a fresh session each time. That kept the earlier context handy, but a fresh session per phase would have kept each conversation more focused, especially for testing, where I wanted the AI to question my code instead of assuming it was right.

**d. Being the lead architect**

The AI can write a lot of code quickly, but it doesn't know what I actually need unless I tell it. My job was to decide the structure (which class owns what), set the rules (the Scheduler only talks to the Owner), and check every result against the requirements. When I was specific, the code came out right. When I wasn't, it filled the gaps with reasonable guesses that didn't always match the assignment. I learned to treat the AI like a fast teammate whose work I review, not like an answer key: run it, test it, read it, and push back when the design gets messy.

---

## 4. Testing and Verification

**a. What you tested**

I tested the main things my scheduler promises to do: tasks come out in time order, filters return the right pet's tasks or only done/not-done ones, completing a daily or weekly task creates the next one on the right date, and two tasks at the same time get a warning. I also tested edge cases, like an owner with no pets, a pet with no tasks, two tasks at the same time with different priorities, and a time typed as "9:00" instead of "09:00". These tests matter because the schedule is the whole point of the app. If sorting or repeating tasks broke, an owner could miss a feeding or a pill without noticing. The tests also let me change the code later and know right away if I broke something.

**b. Confidence**

I'd give it 4 out of 5. All 15 tests pass, and the demo in `main.py` and the Streamlit app behave the way I expect. I'm not at 5 because conflict detection only catches tasks that start at the exact same time, so a 30-minute walk at 7:30 and a feeding at 7:45 wouldn't be flagged. If I had more time, I'd test overlapping durations, tasks that run past midnight, invalid times like "25:00" or "abc", two pets with the same name, and what happens when the total minutes go over the owner's available time.

---

## 5. Reflection

**a. What went well**

I'm most happy with how the recurring tasks and the `due_date` fit together. Marking a daily walk complete creates tomorrow's walk, and it stays hidden until tomorrow, without me doing anything. I'm also happy that the Scheduler is the only class with scheduling rules, so the Streamlit app and `main.py` both just call the same methods. And having 15 passing tests makes me trust the code.

**b. What you would improve**

I'd make conflict detection check overlapping durations, not just matching start times, and suggest a free time slot instead of only warning. I'd also use the owner's available minutes to actually build a plan (for example, drop low-priority tasks when the day is too full) instead of only warning. Finally, I'd save pets and tasks to a file so they're still there after the app closes, and validate input, like rejecting "25:00".

**c. Key takeaway**

Design first, then let the AI build. Because I had a clear UML and clear responsibilities for each class, I could judge every AI suggestion with one question: "Does this belong in this class?" That made it easy to spot when a suggestion would tangle the design, and it made the final code much easier to test and explain.
