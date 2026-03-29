from dataclasses import dataclass, field
from typing import List


@dataclass
class Task:
    name: str = ""
    time: int = 0
    priority_level: str = ""
    frequency: str = ""
    completed: bool = False
    preference_level: str = ""

    def set_name(self, name: str):
        pass

    def set_time(self, time: int):
        pass

    def set_priority_level(self, level: str):
        pass

    def set_frequency(self, frequency: str):
        pass

    def complete_task(self):
        pass

    def set_preference_level(self, level: str):
        pass


@dataclass
class Pet:
    name: str = ""
    species: str = ""
    age: int = 0
    required_tasks: List[Task] = field(default_factory=list)

    def set_name(self, name: str):
        pass

    def set_species(self, species: str):
        pass

    def set_age(self, age: int):
        pass

    def add_task(self, task: Task):
        pass


@dataclass
class Plan:
    day: str = ""
    pet: Pet = None
    tasks: List[Task] = field(default_factory=list)

    def set_day(self, day: str):
        pass

    def set_pet(self, pet: Pet):
        pass

    def add_task(self, task: Task):
        pass


@dataclass
class Owner:
    name: str = ""
    pets: List[Pet] = field(default_factory=list)
    time_available: int = 0

    def add_pet(self, pet: Pet):
        pass

    def add_schedule(self, time: int):
        pass
