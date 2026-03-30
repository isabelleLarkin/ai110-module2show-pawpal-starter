import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import date
from pawpal_system import Task, Pet, Plan, Owner


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_task(name, time=10, priority=2, preference=2, frequency="daily", slot="anytime", scheduled=None):
    t = Task()
    t.set_name(name)
    t.set_time(time)
    t.set_priority_level(priority)
    t.set_preference_level(preference)
    t.set_frequency(frequency)
    t.set_time_of_day(slot)
    if scheduled:
        t.set_scheduled_date(scheduled)
    return t

def make_pet(name, tasks=None):
    p = Pet()
    p.set_name(name)
    p.set_species("Dog")
    p.set_age(3)
    for t in (tasks or []):
        p.add_task(t)
    return p

def make_plan(pet, day="monday"):
    plan = Plan()
    plan.set_day(day)
    plan.set_pet(pet)
    return plan

def make_owner(time=300):
    o = Owner()
    o.name = "Alex"
    o.add_availability(time)
    return o


# ---------------------------------------------------------------------------
# Existing tests (kept intact)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Sorting: get_tasks_by_priority
# ---------------------------------------------------------------------------

def test_priority_sort_orders_highest_first():
    low  = make_task("Brush", priority=1)
    med  = make_task("Feed",  priority=2)
    high = make_task("Walk",  priority=3)
    pet  = make_pet("Bella", [low, med, high])
    plan = make_plan(pet)

    result = plan.get_tasks_by_priority()

    assert [t.name for t in result] == ["Walk", "Feed", "Brush"]


def test_priority_sort_breaks_ties_by_preference():
    # Both priority=2; differ only on preference
    low_pref  = make_task("Bath",  priority=2, preference=1)
    high_pref = make_task("Train", priority=2, preference=3)
    pet  = make_pet("Mochi", [low_pref, high_pref])
    plan = make_plan(pet)

    result = plan.get_tasks_by_priority()

    assert result[0].name == "Train"
    assert result[1].name == "Bath"


def test_priority_sort_breaks_ties_by_frequency_urgency():
    # Both priority=2, preference=2; differ only on frequency
    monthly = make_task("Grooming",   priority=2, preference=2, frequency="monthly")
    daily   = make_task("Walk",       priority=2, preference=2, frequency="daily")
    weekly  = make_task("Playtime",   priority=2, preference=2, frequency="weekly")
    pet  = make_pet("Bella", [monthly, weekly, daily])
    plan = make_plan(pet)

    result = plan.get_tasks_by_priority()

    assert [t.name for t in result] == ["Walk", "Playtime", "Grooming"]


def test_priority_sort_empty_plan_returns_empty():
    pet  = make_pet("Bella")
    plan = make_plan(pet)

    assert plan.get_tasks_by_priority() == []


# ---------------------------------------------------------------------------
# Sorting: get_tasks_by_duration
# ---------------------------------------------------------------------------

def test_duration_sort_shortest_first_by_default():
    pet  = make_pet("Bella", [make_task("A", time=30), make_task("B", time=10), make_task("C", time=20)])
    plan = make_plan(pet)

    result = plan.get_tasks_by_duration()

    assert [t.time for t in result] == [10, 20, 30]


def test_duration_sort_longest_first():
    pet  = make_pet("Bella", [make_task("A", time=30), make_task("B", time=10), make_task("C", time=20)])
    plan = make_plan(pet)

    result = plan.get_tasks_by_duration(shortest_first=False)

    assert [t.time for t in result] == [30, 20, 10]


def test_duration_sort_does_not_mutate_plan_tasks():
    pet  = make_pet("Bella", [make_task("A", time=30), make_task("B", time=10)])
    plan = make_plan(pet)
    original_order = [t.name for t in plan.tasks]

    plan.get_tasks_by_duration()

    assert [t.name for t in plan.tasks] == original_order


# ---------------------------------------------------------------------------
# Filtering: get_tasks_by_frequency
# ---------------------------------------------------------------------------

def test_frequency_filter_returns_only_matching_tasks():
    daily  = make_task("Feed",     frequency="daily")
    weekly = make_task("Grooming", frequency="weekly")
    pet    = make_pet("Bella", [daily, weekly])
    plan   = make_plan(pet)

    result = plan.get_tasks_by_frequency("daily")

    assert len(result) == 1
    assert result[0].name == "Feed"


def test_frequency_filter_returns_empty_when_no_match():
    pet  = make_pet("Bella", [make_task("Feed", frequency="daily")])
    plan = make_plan(pet)

    assert plan.get_tasks_by_frequency("monthly") == []


def test_frequency_filter_raises_on_invalid_frequency():
    pet  = make_pet("Bella", [make_task("Feed")])
    plan = make_plan(pet)

    with pytest.raises(ValueError):
        plan.get_tasks_by_frequency("hourly")


# ---------------------------------------------------------------------------
# Recurrence logic
# ---------------------------------------------------------------------------

def test_next_occurrence_is_pending():
    task = make_task("Walk", frequency="daily")
    task.complete_task()

    next_task = task.get_next_occurrence()

    assert next_task.completed == False


def test_next_occurrence_daily_advances_one_day():
    today = date(2025, 6, 10)
    task  = make_task("Walk", frequency="daily", scheduled=today)

    next_task = task.get_next_occurrence()

    assert next_task.scheduled_date == date(2025, 6, 11)


def test_next_occurrence_weekly_advances_seven_days():
    today = date(2025, 6, 10)
    task  = make_task("Bath", frequency="weekly", scheduled=today)

    next_task = task.get_next_occurrence()

    assert next_task.scheduled_date == date(2025, 6, 17)


def test_next_occurrence_monthly_advances_thirty_days():
    today = date(2025, 6, 10)
    task  = make_task("Vet checkup", frequency="monthly", scheduled=today)

    next_task = task.get_next_occurrence()

    assert next_task.scheduled_date == date(2025, 7, 10)


def test_next_occurrence_preserves_task_name_and_time():
    task = make_task("Walk", time=45, frequency="daily")

    next_task = task.get_next_occurrence()

    assert next_task.name == "Walk"
    assert next_task.time == 45


def test_plan_complete_task_appends_next_occurrence():
    task = make_task("Walk", frequency="daily")
    pet  = make_pet("Bella", [task])
    plan = make_plan(pet)
    initial_count = len(plan.tasks)

    plan.complete_task(plan.tasks[0])

    assert len(plan.tasks) == initial_count + 1


def test_plan_complete_task_marks_original_done():
    task = make_task("Walk", frequency="daily")
    pet  = make_pet("Bella", [task])
    plan = make_plan(pet)
    target = plan.tasks[0]

    plan.complete_task(target)

    assert target.completed == True


def test_plan_complete_task_next_occurrence_is_pending():
    task = make_task("Walk", frequency="daily")
    pet  = make_pet("Bella", [task])
    plan = make_plan(pet)

    plan.complete_task(plan.tasks[0])
    next_occurrence = plan.tasks[-1]

    assert next_occurrence.completed == False


def test_plan_complete_task_raises_if_task_not_in_plan():
    pet  = make_pet("Bella", [make_task("Walk")])
    plan = make_plan(pet)
    stranger = make_task("Swim")

    with pytest.raises(ValueError):
        plan.complete_task(stranger)


def test_completing_task_twice_adds_two_occurrences():
    task = make_task("Walk", frequency="daily")
    pet  = make_pet("Bella", [task])
    plan = make_plan(pet)

    first_target = plan.tasks[0]
    plan.complete_task(first_target)
    second_target = plan.tasks[-1]   # the appended next occurrence
    plan.complete_task(second_target)

    # original + 2 next occurrences
    assert len(plan.tasks) == 3
    assert plan.tasks[1].completed == True
    assert plan.tasks[2].completed == False


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def test_no_conflict_when_different_slots():
    walk  = make_task("Walk",  slot="morning")
    groom = make_task("Groom", slot="evening")
    pet1  = make_pet("Bella",  [walk])
    pet2  = make_pet("Mochi",  [groom])
    owner = make_owner()
    owner.add_pet(pet1)
    owner.add_pet(pet2)

    plan1 = make_plan(pet1)
    owner.add_plan(plan1)
    plan2 = make_plan(pet2)

    conflicts = owner.get_time_slot_conflicts(plan2)

    assert conflicts == []


def test_conflict_detected_when_same_slot_different_pets():
    walk1 = make_task("Walk",  slot="morning")
    walk2 = make_task("Run",   slot="morning")
    pet1  = make_pet("Bella",  [walk1])
    pet2  = make_pet("Mochi",  [walk2])
    owner = make_owner()
    owner.add_pet(pet1)
    owner.add_pet(pet2)

    plan1 = make_plan(pet1)
    owner.add_plan(plan1)
    plan2 = make_plan(pet2)

    conflicts = owner.get_time_slot_conflicts(plan2)

    assert len(conflicts) == 1
    assert "morning" in conflicts[0]


def test_no_conflict_for_same_pet_same_slot():
    walk  = make_task("Walk",  slot="morning")
    train = make_task("Train", slot="morning")
    pet   = make_pet("Bella",  [walk, train])
    owner = make_owner()
    owner.add_pet(pet)

    plan1 = make_plan(pet)
    owner.add_plan(plan1)
    plan2 = make_plan(pet, day="tuesday")

    conflicts = owner.get_time_slot_conflicts(plan2)

    assert conflicts == []


def test_anytime_tasks_never_conflict():
    task1 = make_task("Feed",  slot="anytime")
    task2 = make_task("Brush", slot="anytime")
    pet1  = make_pet("Bella",  [task1])
    pet2  = make_pet("Mochi",  [task2])
    owner = make_owner()
    owner.add_pet(pet1)
    owner.add_pet(pet2)

    plan1 = make_plan(pet1)
    owner.add_plan(plan1)
    plan2 = make_plan(pet2)

    conflicts = owner.get_time_slot_conflicts(plan2)

    assert conflicts == []


def test_conflict_message_names_both_tasks_and_pets():
    walk = make_task("Walk", slot="afternoon")
    run  = make_task("Run",  slot="afternoon")
    pet1 = make_pet("Bella", [walk])
    pet2 = make_pet("Mochi", [run])
    owner = make_owner()
    owner.add_pet(pet1)
    owner.add_pet(pet2)

    plan1 = make_plan(pet1)
    owner.add_plan(plan1)
    plan2 = make_plan(pet2)

    conflicts = owner.get_time_slot_conflicts(plan2)

    assert any("Bella" in c and "Mochi" in c for c in conflicts)


# ---------------------------------------------------------------------------
# Availability and plan management
# ---------------------------------------------------------------------------

def test_add_plan_deducts_time():
    task  = make_task("Walk", time=30)
    pet   = make_pet("Bella", [task])
    owner = make_owner(time=100)
    owner.add_pet(pet)

    owner.add_plan(make_plan(pet))

    assert owner.time_available == 70


def test_remove_plan_restores_time():
    task  = make_task("Walk", time=30)
    pet   = make_pet("Bella", [task])
    owner = make_owner(time=100)
    owner.add_pet(pet)
    plan  = make_plan(pet)
    owner.add_plan(plan)

    owner.remove_plan(plan)

    assert owner.time_available == 100


def test_add_plan_blocked_when_insufficient_time():
    task  = make_task("Walk", time=200)
    pet   = make_pet("Bella", [task])
    owner = make_owner(time=50)
    owner.add_pet(pet)

    with pytest.raises(ValueError):
        owner.add_plan(make_plan(pet))


def test_add_plan_blocked_on_exact_duplicate_pet_day():
    task  = make_task("Walk", time=10)
    pet   = make_pet("Bella", [task])
    owner = make_owner(time=300)
    owner.add_pet(pet)
    owner.add_plan(make_plan(pet, "monday"))

    with pytest.raises(ValueError):
        owner.add_plan(make_plan(pet, "monday"))


def test_add_plan_succeeds_when_time_exactly_fits():
    task  = make_task("Walk", time=100)
    pet   = make_pet("Bella", [task])
    owner = make_owner(time=100)
    owner.add_pet(pet)

    owner.add_plan(make_plan(pet))  # should not raise

    assert owner.time_available == 0


def test_remove_pet_cascades_to_plans_and_restores_time():
    task  = make_task("Walk", time=30)
    pet   = make_pet("Bella", [task])
    owner = make_owner(time=100)
    owner.add_pet(pet)
    owner.add_plan(make_plan(pet))

    owner.remove_pet(pet)

    assert len(owner.plans) == 0
    assert owner.time_available == 100
