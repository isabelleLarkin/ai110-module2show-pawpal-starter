import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pawpal_system import Task, Pet


def test_complete_task_marks_task_as_done():
    task = Task()
    task.set_name("Walk")
    task.set_time(30)
    task.set_frequency("daily")
    task.set_priority_level(3)

    task.complete_task()

    assert task.completed == True


def test_add_task_increases_pet_task_count():
    pet = Pet()
    pet.set_name("Bella")
    pet.set_species("Dog")
    pet.set_age(4)

    task = Task()
    task.set_name("Feed")
    task.set_time(10)
    task.set_frequency("daily")
    task.set_priority_level(3)

    pet.add_task(task)

    assert len(pet.required_tasks) == 1
