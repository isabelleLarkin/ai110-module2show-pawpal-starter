import copy
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List

TIME_UNIT = "minutes"


VALID_FREQUENCIES = ["daily", "weekly", "monthly"]
FREQUENCY_PRIORITY = {"daily": 3, "weekly": 2, "monthly": 1}
FREQUENCY_DAYS = {"daily": 1, "weekly": 7, "monthly": 30}

VALID_TIME_SLOTS = ["morning", "afternoon", "evening", "anytime"]

@dataclass
class Task:
    name: str = ""
    time: int = 0           # duration in TIME_UNIT (minutes)
    priority_level: int = 0 # 1 = low, 2 = medium, 3 = high
    frequency: str = ""     # "daily", "weekly", or "monthly"
    completed: bool = False
    preference_level: int = 0  # 1 = low, 2 = medium, 3 = high
    time_of_day: str = "anytime"  # "morning", "afternoon", "evening", or "anytime"
    scheduled_date: date = field(default_factory=date.today)

    def set_name(self, name: str):
        """Set the task name, rejecting empty strings."""
        if not name:
            raise ValueError("Task name cannot be empty.")
        self.name = name

    def set_time(self, time: int):
        """Set the task duration in minutes; must be greater than zero."""
        if time <= 0:
            raise ValueError(f"Time must be a positive number of {TIME_UNIT}.")
        self.time = time

    def set_priority_level(self, level: int):
        """Set the priority level to 1 (low), 2 (medium), or 3 (high)."""
        if level not in (1, 2, 3):
            raise ValueError("Priority level must be 1 (low), 2 (medium), or 3 (high).")
        self.priority_level = level

    def set_frequency(self, frequency: str):
        """Set how often the task recurs: daily, weekly, or monthly."""
        if frequency not in VALID_FREQUENCIES:
            raise ValueError(f"Frequency must be one of: {VALID_FREQUENCIES}.")
        self.frequency = frequency

    def complete_task(self):
        """Mark the task as completed."""
        self.completed = True

    def reset_task(self):
        """Reset the task completion status to pending."""
        self.completed = False

    def set_preference_level(self, level: int):
        """Set the owner's preference level for this task: 1 (low), 2 (medium), or 3 (high)."""
        if level not in (1, 2, 3):
            raise ValueError("Preference level must be 1 (low), 2 (medium), or 3 (high).")
        self.preference_level = level

    def set_time_of_day(self, slot: str):
        """Set the preferred time of day: morning, afternoon, evening, or anytime."""
        if slot not in VALID_TIME_SLOTS:
            raise ValueError(f"Time of day must be one of: {VALID_TIME_SLOTS}.")
        self.time_of_day = slot

    def set_scheduled_date(self, d: date):
        """Set the date this task occurrence is scheduled for."""
        self.scheduled_date = d

    def get_next_occurrence(self) -> "Task":
        """Return a new pending Task scheduled for the next occurrence based on frequency."""
        if self.frequency not in FREQUENCY_DAYS:
            raise ValueError(f"Cannot compute next occurrence: frequency '{self.frequency}' is not set.")
        next_task = copy.copy(self)
        next_task.completed = False
        next_task.scheduled_date = self.scheduled_date + timedelta(days=FREQUENCY_DAYS[self.frequency])
        return next_task


@dataclass
class Pet:
    name: str = ""
    species: str = ""
    age: int = 0
    required_tasks: List[Task] = field(default_factory=list)

    def set_name(self, name: str):
        """Set the pet's name, rejecting empty strings."""
        if not name:
            raise ValueError("Pet name cannot be empty.")
        self.name = name

    def set_species(self, species: str):
        """Set the pet's species, rejecting empty strings."""
        if not species:
            raise ValueError("Species cannot be empty.")
        self.species = species

    def set_age(self, age: int):
        """Set the pet's age, rejecting negative values."""
        if age < 0:
            raise ValueError("Age cannot be negative.")
        self.age = age

    def add_task(self, task: Task):
        """Add a task to the pet's required tasks, blocking duplicate names."""
        if any(t.name == task.name for t in self.required_tasks):
            raise ValueError(f"Task '{task.name}' is already in {self.name}'s required tasks.")
        self.required_tasks.append(task)

    def remove_task(self, task: Task):
        """Remove a task from the pet's required tasks."""
        if task not in self.required_tasks:
            raise ValueError(f"Task '{task.name}' not found in {self.name}'s required tasks.")
        self.required_tasks.remove(task)


VALID_DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

@dataclass
class Plan:
    pet: Pet = None
    day: str = ""
    tasks: List[Task] = field(default_factory=list)

    def set_day(self, day: str):
        """Set the day of the plan to a valid weekday name."""
        if day.lower() not in VALID_DAYS:
            raise ValueError(f"Day must be one of: {VALID_DAYS}.")
        self.day = day.lower()

    def set_pet(self, pet: Pet):
        """Assign a pet to the plan and seed tasks from the pet's required tasks."""
        if pet is None:
            raise ValueError("Pet cannot be None.")
        if self.pet is not None:
            raise ValueError(f"Pet is already set to '{self.pet.name}'. Create a new Plan to assign a different pet.")
        self.pet = pet
        self.tasks = [copy.copy(task) for task in pet.required_tasks]

    def add_task(self, task: Task):
        """Add an extra task to the plan beyond the pet's defaults, blocking duplicate names."""
        if self.pet is None:
            raise ValueError("A pet must be set before adding tasks to the plan.")
        if any(t.name == task.name for t in self.tasks):
            raise ValueError(f"Task '{task.name}' is already in the plan.")
        self.tasks.append(task)

    def remove_task(self, task: Task):
        """Remove a task from the plan."""
        if task not in self.tasks:
            raise ValueError(f"Task '{task.name}' not found in the plan.")
        self.tasks.remove(task)

    def get_total_time(self) -> int:
        """Return the total time in minutes required to complete all tasks in the plan."""
        return sum(task.time for task in self.tasks)

    def get_pending_tasks(self) -> List[Task]:
        """Return all tasks in the plan that have not yet been completed."""
        return self.get_tasks_by_status(completed=False)

    def get_tasks_by_status(self, completed: bool) -> List[Task]:
        """Return tasks matching the given completion status."""
        return [task for task in self.tasks if task.completed == completed]

    def get_tasks_by_priority(self) -> List[Task]:
        """Return tasks sorted by priority, then preference, then frequency urgency — all highest first."""
        return sorted(
            self.tasks,
            key=lambda task: (
                task.priority_level,
                task.preference_level,
                FREQUENCY_PRIORITY.get(task.frequency, 0),
            ),
            reverse=True,
        )

    def get_tasks_by_duration(self, shortest_first: bool = True) -> List[Task]:
        """Return all tasks sorted by duration. Shortest first by default."""
        return sorted(self.tasks, key=lambda task: task.time, reverse=not shortest_first)

    def get_tasks_by_frequency(self, frequency: str) -> List[Task]:
        """Return all tasks in the plan matching the given frequency."""
        if frequency not in VALID_FREQUENCIES:
            raise ValueError(f"Frequency must be one of: {VALID_FREQUENCIES}.")
        return [task for task in self.tasks if task.frequency == frequency]

    def complete_task(self, task: "Task"):
        """Mark a task complete and append its next occurrence to the plan."""
        if task not in self.tasks:
            raise ValueError(f"Task '{task.name}' not found in the plan.")
        task.complete_task()
        self.tasks.append(task.get_next_occurrence())

    def reset_all_tasks(self):
        """Reset the completion status of all tasks in the plan to pending."""
        for task in self.tasks:
            task.reset_task()


@dataclass
class Owner:
    name: str = ""
    pets: List[Pet] = field(default_factory=list)
    plans: List[Plan] = field(default_factory=list)
    time_available: int = 0

    def add_pet(self, pet: Pet):
        """Add a pet to the owner's pet list, blocking duplicates."""
        if pet in self.pets:
            raise ValueError(f"'{pet.name}' is already added to {self.name}'s pets.")
        self.pets.append(pet)

    def remove_pet(self, pet: Pet):
        """Remove a pet and all associated plans, restoring their time to availability."""
        if pet not in self.pets:
            raise ValueError(f"'{pet.name}' not found in {self.name}'s pets.")
        pet_plans = [plan for plan in self.plans if plan.pet == pet]
        for plan in pet_plans:
            self.remove_plan(plan)
        self.pets.remove(pet)

    def add_availability(self, time: int):
        """Increase the owner's available time by the given number of minutes."""
        if time < 0:
            raise ValueError(f"Time must be a positive number of {TIME_UNIT}.")
        self.time_available += time

    def subtract_availability(self, time: int):
        """Decrease the owner's available time, blocking if insufficient time remains."""
        if time < 0:
            raise ValueError(f"Time must be a positive number of {TIME_UNIT}.")
        if time > self.time_available:
            raise ValueError(f"Cannot subtract {time} {TIME_UNIT}: only {self.time_available} available.")
        self.time_available -= time

    def add_plan(self, plan: Plan):
        """Add a plan to the schedule, deducting its time and blocking duplicates or overflows."""
        if plan in self.plans:
            raise ValueError(f"This plan is already in {self.name}'s schedule.")
        if any(p.pet == plan.pet and p.day == plan.day for p in self.plans):
            raise ValueError(f"A plan for '{plan.pet.name}' on {plan.day} already exists.")
        if not self.can_fit_plan(plan):
            raise ValueError(f"Not enough time available. Plan requires {plan.get_total_time()} {TIME_UNIT}, but only {self.time_available} remaining.")
        self.plans.append(plan)
        self.subtract_availability(plan.get_total_time())

    def remove_plan(self, plan: Plan):
        """Remove a plan from the schedule and restore its time to availability."""
        if plan not in self.plans:
            raise ValueError(f"Plan not found in {self.name}'s schedule.")
        self.plans.remove(plan)
        self.add_availability(plan.get_total_time())

    def get_plans(self) -> List[Plan]:
        """Return all plans in the owner's schedule."""
        return self.plans

    def get_plans_by_day(self, day: str) -> List[Plan]:
        """Return all plans scheduled for the given day."""
        if day.lower() not in VALID_DAYS:
            raise ValueError(f"Day must be one of: {VALID_DAYS}.")
        return [plan for plan in self.plans if plan.day == day.lower()]

    def get_plans_by_pet(self, pet: Pet) -> List[Plan]:
        """Return all plans associated with the given pet."""
        if pet not in self.pets:
            raise ValueError(f"'{pet.name}' is not one of {self.name}'s pets.")
        return [plan for plan in self.plans if plan.pet == pet]

    def can_fit_plan(self, plan: Plan) -> bool:
        """Return True if the plan's total time fits within the owner's available time."""
        return plan.get_total_time() <= self.time_available

    def get_all_tasks(self) -> List[Task]:
        """Return a flat list of all required tasks across every pet the owner has."""
        return [task for pet in self.pets for task in pet.required_tasks]

    def get_tasks_by_pet_name(self, pet_name: str) -> List[Task]:
        """Return all required tasks for the pet with the given name."""
        pet = next((p for p in self.pets if p.name == pet_name), None)
        if pet is None:
            raise ValueError(f"No pet named '{pet_name}' found.")
        return list(pet.required_tasks)

    def get_time_slot_conflicts(self, plan: Plan) -> List[str]:
        """Return conflict descriptions where this plan's tasks share a time slot with existing plans."""
        conflicts = []
        for existing_plan in self.plans:
            if existing_plan.pet == plan.pet:
                continue
            for new_task in plan.tasks:
                if new_task.time_of_day == "anytime":
                    continue
                for existing_task in existing_plan.tasks:
                    if existing_task.time_of_day == "anytime":
                        continue
                    if new_task.time_of_day == existing_task.time_of_day:
                        conflicts.append(
                            f"'{new_task.name}' ({plan.pet.name}) and "
                            f"'{existing_task.name}' ({existing_plan.pet.name}) "
                            f"are both scheduled in the {new_task.time_of_day}."
                        )
        return conflicts
