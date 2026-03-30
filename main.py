from pawpal_system import Task, Pet, Plan, Owner, TIME_UNIT

PRIORITY_LABELS = {1: "Low", 2: "Medium", 3: "High"}

def print_task_row(task):
    status = "Done" if task.completed else "Pending"
    print(
        f"    - {task.name:<20} {task.time} min"
        f"  |  Priority: {PRIORITY_LABELS[task.priority_level]:<6}"
        f"  |  Pref: {PRIORITY_LABELS[task.preference_level]:<6}"
        f"  |  {task.frequency.capitalize():<7}"
        f"  |  {task.time_of_day.capitalize():<9}"
        f"  |  [{status}]"
    )

# --- Create Owner ---
owner = Owner()
owner.name = "Alex"
owner.add_availability(200)

# --- Create Tasks for Bella (added out of order: low priority first) ---
groom_dog = Task()
groom_dog.set_name("Brush Coat")
groom_dog.set_time(20)
groom_dog.set_frequency("weekly")
groom_dog.set_priority_level(1)
groom_dog.set_preference_level(2)
groom_dog.set_time_of_day("morning")

feed_dog = Task()
feed_dog.set_name("Feed")
feed_dog.set_time(10)
feed_dog.set_frequency("daily")
feed_dog.set_priority_level(3)
feed_dog.set_preference_level(2)
feed_dog.set_time_of_day("morning")

walk = Task()
walk.set_name("Walk")
walk.set_time(30)
walk.set_frequency("daily")
walk.set_priority_level(3)
walk.set_preference_level(3)
walk.set_time_of_day("morning")

evening_meds_dog = Task()
evening_meds_dog.set_name("Evening Meds")
evening_meds_dog.set_time(5)
evening_meds_dog.set_frequency("daily")
evening_meds_dog.set_priority_level(3)
evening_meds_dog.set_preference_level(1)
evening_meds_dog.set_time_of_day("evening")

# --- Create Pet 1: Bella the Dog (tasks added low → high priority) ---
bella = Pet()
bella.set_name("Bella")
bella.set_species("Dog")
bella.set_age(4)
bella.add_task(groom_dog)        # priority 1 — added first (out of order)
bella.add_task(feed_dog)         # priority 3
bella.add_task(walk)             # priority 3
bella.add_task(evening_meds_dog) # priority 3, evening — conflicts with Mochi's evening task

# --- Create Tasks for Mochi (added out of order: longest first) ---
playtime = Task()
playtime.set_name("Playtime")
playtime.set_time(25)
playtime.set_frequency("daily")
playtime.set_priority_level(2)
playtime.set_preference_level(3)
playtime.set_time_of_day("afternoon")

clean_litter = Task()
clean_litter.set_name("Clean Litter Box")
clean_litter.set_time(15)
clean_litter.set_frequency("daily")
clean_litter.set_priority_level(2)
clean_litter.set_preference_level(1)
clean_litter.set_time_of_day("morning")

feed_cat = Task()
feed_cat.set_name("Feed")
feed_cat.set_time(10)
feed_cat.set_frequency("daily")
feed_cat.set_priority_level(3)
feed_cat.set_preference_level(2)
feed_cat.set_time_of_day("morning")

evening_feeding_cat = Task()
evening_feeding_cat.set_name("Evening Feeding")
evening_feeding_cat.set_time(10)
evening_feeding_cat.set_frequency("daily")
evening_feeding_cat.set_priority_level(3)
evening_feeding_cat.set_preference_level(2)
evening_feeding_cat.set_time_of_day("evening")

# --- Create Pet 2: Mochi the Cat (tasks added longest → shortest) ---
mochi = Pet()
mochi.set_name("Mochi")
mochi.set_species("Cat")
mochi.set_age(2)
mochi.add_task(playtime)           # 25 min — added first (out of order)
mochi.add_task(clean_litter)       # 15 min
mochi.add_task(feed_cat)           # 10 min
mochi.add_task(evening_feeding_cat) # 10 min, evening — conflicts with Bella's evening task

# --- Register Pets and Build Monday Plans ---
owner.add_pet(bella)
owner.add_pet(mochi)

bella_plan = Plan()
bella_plan.set_pet(bella)
bella_plan.set_day("monday")

mochi_plan = Plan()
mochi_plan.set_pet(mochi)
mochi_plan.set_day("monday")

owner.add_plan(bella_plan)
owner.add_plan(mochi_plan)
conflicts = owner.get_time_slot_conflicts(mochi_plan)

# --- Mark one task done to demonstrate status filtering ---
bella_plan.tasks[0].complete_task()

# ============================================================
print(f"=== {owner.name}'s Monday Schedule ===")
print(f"Time remaining after scheduling: {owner.time_available} {TIME_UNIT}\n")

for plan in owner.get_plans_by_day("monday"):
    pet = plan.pet
    print(f"[ {pet.name} | {pet.species} | Age {pet.age} ]")
    print(f"  Total time: {plan.get_total_time()} min\n")

    print("  Sorted by priority (high → low), preference, then frequency:")
    for task in plan.get_tasks_by_priority():
        print_task_row(task)

    print("\n  Sorted by duration (shortest first):")
    for task in plan.get_tasks_by_duration(shortest_first=True):
        print_task_row(task)

    print("\n  Sorted by duration (longest first):")
    for task in plan.get_tasks_by_duration(shortest_first=False):
        print_task_row(task)

    pending = plan.get_tasks_by_status(completed=False)
    done    = plan.get_tasks_by_status(completed=True)
    print(f"\n  Pending tasks ({len(pending)}):")
    for task in pending:
        print_task_row(task)
    print(f"\n  Completed tasks ({len(done)}):")
    for task in done:
        print_task_row(task)
    print()

# --- Filter tasks by pet name ---
print("=== Tasks by pet name ===")
for pet_name in ["Bella", "Mochi"]:
    tasks = owner.get_tasks_by_pet_name(pet_name)
    print(f"\n  {pet_name}'s tasks ({len(tasks)}):")
    for task in tasks:
        print_task_row(task)

# --- Time slot conflicts ---
print("\n=== Time Slot Conflicts ===")
if conflicts:
    for c in conflicts:
        print(f"  ! {c}")
else:
    print("  No conflicts detected.")
