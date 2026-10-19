"""PawPal+ core logic: Task, Pet, Owner, and Scheduler."""

import json
from dataclasses import asdict, dataclass, field, replace
from datetime import date, timedelta
from pathlib import Path

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}
RECURRENCE_STEP = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}


def time_to_minutes(time_str: str) -> int:
    """Convert an "HH:MM" string to minutes after midnight (so "7:30" and "07:30" sort the same)."""
    hours, minutes = time_str.split(":")
    return int(hours) * 60 + int(minutes)


def minutes_to_time(minutes: int) -> str:
    """Convert minutes after midnight back to a zero-padded "HH:MM" string."""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


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
    due_date: date = field(default_factory=date.today)

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Reset this task to not done."""
        self.completed = False

    def priority_value(self) -> int:
        """Return a sortable number for priority (lower means more urgent)."""
        return PRIORITY_RANK.get(self.priority, len(PRIORITY_RANK))

    def next_occurrence(self) -> "Task | None":
        """Return a fresh copy due on the next date for daily/weekly tasks, or None for one-time tasks."""
        step = RECURRENCE_STEP.get(self.frequency)
        if step is None:
            return None
        return replace(self, completed=False, due_date=self.due_date + step)

    def to_dict(self) -> dict:
        """Return a JSON-safe dict of this task (the date becomes an ISO string)."""
        data = asdict(self)
        data["due_date"] = self.due_date.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Rebuild a Task from a dict made by to_dict()."""
        data = dict(data)
        if "due_date" in data:
            data["due_date"] = date.fromisoformat(data["due_date"])
        return cls(**data)


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

    def to_dict(self) -> dict:
        """Return a JSON-safe dict of this pet and its tasks."""
        return {
            "name": self.name,
            "species": self.species,
            "age": self.age,
            "tasks": [task.to_dict() for task in self.tasks],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Pet":
        """Rebuild a Pet (and its tasks) from a dict made by to_dict()."""
        pet = cls(data["name"], data["species"], age=data.get("age", 0))
        for task_data in data.get("tasks", []):
            pet.add_task(Task.from_dict(task_data))
        return pet


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

    def to_dict(self) -> dict:
        """Return a JSON-safe dict of this owner, their pets, and all tasks."""
        return {
            "name": self.name,
            "available_minutes": self.available_minutes,
            "pets": [pet.to_dict() for pet in self.pets],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Owner":
        """Rebuild an Owner (with pets and tasks) from a dict made by to_dict()."""
        owner = cls(data["name"], available_minutes=data.get("available_minutes", 120))
        for pet_data in data.get("pets", []):
            owner.add_pet(Pet.from_dict(pet_data))
        return owner

    def save_to_json(self, path: str | Path = "data.json") -> None:
        """Save this owner, their pets, and all tasks to a JSON file."""
        path = Path(path)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
        tmp.replace(path)  # write then swap, so a crash never leaves a half-written file

    @classmethod
    def load_from_json(cls, path: str | Path = "data.json") -> "Owner | None":
        """Load an owner from a JSON file, or return None if the file doesn't exist yet."""
        path = Path(path)
        if not path.exists():
            return None
        return cls.from_dict(json.loads(path.read_text(encoding="utf-8")))


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
        return self.filter_tasks(completed=False)

    def sort_by_time(self, tasks: list[Task] | None = None) -> list[Task]:
        """Return tasks ordered by date and time of day, with priority breaking ties."""
        tasks = self.get_tasks() if tasks is None else tasks
        return sorted(tasks, key=lambda t: (t.due_date, time_to_minutes(t.time), t.priority_value()))

    def filter_tasks(
        self,
        pet_name: str | None = None,
        completed: bool | None = None,
        tasks: list[Task] | None = None,
    ) -> list[Task]:
        """Return tasks matching a pet name and/or completion status; a None filter is skipped."""
        tasks = self.get_tasks() if tasks is None else tasks
        result = []
        for task in tasks:
            if pet_name is not None and task.pet_name != pet_name:
                continue
            if completed is not None and task.completed != completed:
                continue
            result.append(task)
        return result

    def filter_by_pet(self, pet_name: str) -> list[Task]:
        """Return only the tasks for one pet."""
        return self.filter_tasks(pet_name=pet_name)

    def mark_task_complete(self, task: Task) -> Task | None:
        """Complete a task and, if it repeats, add its next occurrence to the same pet; return the new task."""
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task is not None:
            pet = self.owner.get_pet(task.pet_name)
            if pet is not None:
                pet.add_task(next_task)
        return next_task

    def detect_conflicts(self, tasks: list[Task] | None = None) -> list[str]:
        """Return a warning for each group of pending tasks booked at the same date and time."""
        tasks = self.get_pending_tasks() if tasks is None else tasks
        slots: dict[tuple[date, int], list[Task]] = {}
        for task in tasks:
            slots.setdefault((task.due_date, time_to_minutes(task.time)), []).append(task)

        warnings = []
        for clashing in slots.values():
            if len(clashing) > 1:
                names = ", ".join(f"{t.pet_name}: {t.description}" for t in clashing)
                warnings.append(f"Conflict at {clashing[0].time} on {clashing[0].due_date}: {names}")
        return warnings

    def find_next_available_slot(
        self,
        duration_minutes: int,
        on: date | None = None,
        earliest: str = "07:00",
        latest: str = "21:00",
    ) -> str | None:
        """Return the earliest "HH:MM" start with room for a task of this length, or None if the day is full.

        Pending tasks on that date are treated as busy blocks from their start time to start + duration.
        The method walks those blocks in time order and returns the first gap that is long enough.
        """
        on = date.today() if on is None else on
        busy = sorted(
            (time_to_minutes(t.time), time_to_minutes(t.time) + t.duration_minutes)
            for t in self.get_pending_tasks()
            if t.due_date == on
        )
        candidate = time_to_minutes(earliest)
        for start, end in busy:
            if start - candidate >= duration_minutes:
                break
            candidate = max(candidate, end)
        if candidate + duration_minutes > time_to_minutes(latest):
            return None
        return minutes_to_time(candidate)

    def todays_schedule(self, today: date | None = None) -> list[Task]:
        """Return pending tasks due today, in time order."""
        today = date.today() if today is None else today
        due_today = [t for t in self.get_pending_tasks() if t.due_date == today]
        return self.sort_by_time(due_today)

    def format_schedule(self) -> str:
        """Return today's schedule, plus any conflict warnings, as readable text for the terminal."""
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
        for warning in self.detect_conflicts(tasks):
            lines.append(f"WARNING: {warning}")
        return "\n".join(lines)
