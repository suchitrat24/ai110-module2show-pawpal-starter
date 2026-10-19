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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

I used Claude Code in agent mode for most of the build. First it turned my four classes (Owner, Pet, Task, Scheduler) into a Mermaid UML diagram. Then I gave it the class descriptions from the assignment, and it wrote the code in `pawpal_system.py`, the `main.py` demo, and the two starter tests. The most helpful prompts were specific about the rules. For example, I told it the Scheduler has to get tasks through the Owner's `get_all_tasks()` method instead of from a single pet, and that made it build the multi-pet design correctly.

**b. Judgment and verification**

The AI's first UML draft gave Task a `title` and a `preferred_time` and didn't include a frequency. The assignment says a Task should have a description, time, frequency, and completion status, so I didn't keep that version. I had the code follow the assignment's fields and then updated the UML to match. I also checked that the Scheduler only gets its tasks through `owner.get_all_tasks()`. It never reads a pet's list directly, which is what the multi-pet requirement asks for. To check the results, I ran `python main.py` and saw that tasks from both pets printed in time order. I also ran `python -m pytest`, and both tests passed.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
