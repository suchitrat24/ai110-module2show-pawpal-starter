"""PawPal+ core logic: Task, Pet, Owner, and Scheduler."""

from dataclasses import dataclass, field

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    """A single pet care activity."""

    description: str
    time: str  # "HH:MM", 24-hour clock
    duration_minutes: int = 15
    priority: str = "medium"
    frequency: str = "daily"  # "once", "daily", or "weekly"
    completed: bool = False
    pet_name: str = ""

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Reset this task to not done."""
        self.completed = False

    def priority_value(self) -> int:
        """Return a sortable number for priority (lower means more urgent)."""
        return PRIORITY_RANK.get(self.priority, len(PRIORITY_RANK))


@dataclass
class Pet:
    """A pet and the care tasks it needs."""

    name: str
    species: str
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, description: str) -> bool:
        """Remove the first task with this description; return True if one was removed."""
        for task in self.tasks:
            if task.description == description:
                self.tasks.remove(task)
                return True
        return False

    def get_tasks(self) -> list[Task]:
        """Return this pet's tasks."""
        return list(self.tasks)


@dataclass
class Owner:
    """A pet owner who manages one or more pets."""

    name: str
    available_minutes: int = 120
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_pet(self, name: str) -> Pet | None:
        """Return the pet with this name, or None."""
        for pet in self.pets:
            if pet.name == name:
                return pet
        return None

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    """Retrieves, organizes, and manages tasks across all of an owner's pets."""

    def __init__(self, owner: Owner):
        """Create a scheduler for the given owner."""
        self.owner = owner

    def get_tasks(self) -> list[Task]:
        """Fetch all tasks from the owner's pets."""
        return self.owner.get_all_tasks()

    def get_pending_tasks(self) -> list[Task]:
        """Return tasks that are not completed yet."""
        return [t for t in self.get_tasks() if not t.completed]

    def sort_by_time(self, tasks: list[Task] | None = None) -> list[Task]:
        """Return tasks ordered by time of day, then by priority."""
        tasks = self.get_tasks() if tasks is None else tasks
        return sorted(tasks, key=lambda t: (t.time, t.priority_value()))

    def filter_by_pet(self, pet_name: str) -> list[Task]:
        """Return only the tasks for one pet."""
        return [t for t in self.get_tasks() if t.pet_name == pet_name]

    def todays_schedule(self) -> list[Task]:
        """Return today's pending tasks in time order."""
        return self.sort_by_time(self.get_pending_tasks())

    def format_schedule(self) -> str:
        """Return today's schedule as readable text for the terminal."""
        tasks = self.todays_schedule()
        lines = [f"Today's Schedule for {self.owner.name}", "=" * 40]
        if not tasks:
            lines.append("No tasks scheduled.")
        for t in tasks:
            lines.append(
                f"{t.time}  {t.pet_name:<8} {t.description:<18} "
                f"{t.duration_minutes:>3} min  [{t.priority}, {t.frequency}]"
            )
        total = sum(t.duration_minutes for t in tasks)
        lines.append("-" * 40)
        lines.append(f"Total: {total} min of {self.owner.available_minutes} min available")
        return "\n".join(lines)
