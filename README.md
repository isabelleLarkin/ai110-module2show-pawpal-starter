# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

# Smarter Scheduling

## New Features

### Multi-criteria Task Sorting
Tasks are now sorted by three tiebreakers in order: priority level (high to low), owner preference (high to low), then frequency urgency (daily before weekly before monthly). This means the most important, most preferred, and most time-sensitive tasks always surface first.

### Time-of-Day Scheduling
Each task has a `time_of_day` field (morning, afternoon, evening, anytime). Tasks tagged with a specific slot can be grouped and reviewed by time of day, giving the owner a clearer picture of when their day fills up.

### Multi-Pet Conflict Detection
When adding a plan for a new pet, `Owner.get_time_slot_conflicts()` checks whether any of its tasks share a time slot with tasks already scheduled for other pets. Conflicts are returned as descriptive messages so the owner can decide how to resolve them.

### Automatic Task Rescheduling
Calling `Plan.complete_task()` marks a task done and immediately appends a new pending instance scheduled for the next occurrence — 1 day later for daily tasks, 7 days for weekly, 30 days for monthly. The completed and upcoming instances coexist in the plan so history is preserved.

### Filtering by Completion Status
`Plan.get_tasks_by_status(completed=True/False)` returns tasks filtered by whether they are done or still pending. `get_pending_tasks()` is a convenience wrapper around this. Both work correctly after tasks are rescheduled.

### Filtering by Pet Name
`Owner.get_tasks_by_pet_name(name)` looks up a pet by name and returns its required tasks, making it easy to review one pet's workload without iterating all pets manually.

### Duration Sorting
`Plan.get_tasks_by_duration(shortest_first=True/False)` sorts tasks by how long they take. Useful for batching quick tasks early in the day or identifying which tasks are eating up the most time.

### Task Isolation Between Pet and Plan
When a plan is created, tasks are deep-copied from the pet's template. Completing or modifying a task in the plan no longer affects the pet's original task definitions.

# Testing PawPal+
Command: python3 -m pytest

The test suite covers 33 cases across five areas. Sorting tests verify that get_tasks_by_priority correctly orders tasks by priority, then preference, then frequency urgency as a tiebreaker, that get_tasks_by_duration respects the shortest_first flag, and that neither sort mutates the original task list. Filtering tests confirm that get_tasks_by_frequency returns only matching tasks, returns an empty list when nothing matches, and raises on an invalid frequency string. Recurrence tests check that get_next_occurrence advances the scheduled date by the right number of days for daily, weekly, and monthly frequencies, that the returned task is always pending, and that name and duration are preserved; they also verify that plan.complete_task marks the original done, appends a pending next occurrence, and chains correctly when called twice in a row. Conflict detection tests confirm that tasks from different pets sharing a time slot are flagged, that same-pet overlaps and "anytime" tasks are never flagged, and that conflict messages identify both pets and tasks by name. Finally, availability and plan management tests cover time deduction on add, time restoration on remove, blocking when a plan exceeds available time or duplicates a pet-day pair, the exact-fit boundary case, and cascading plan removal when a pet is deleted.

I would give my system 4 stars, because all of the tests passed, however the logic is complex so there is the possibility of an unforeseen error.

# Features

## Task Management
- **Task creation with validation** — enforces non-empty name, positive duration, valid priority (1–3), valid frequency, and valid time-of-day slot before setting any attribute
- **Completion tracking** — `completeTask()` and `resetTask()` toggle a boolean flag, enabling status filtering across a plan
- **Recurrence scheduling** — `getNextOccurrence()` computes the next task date by advancing `scheduledDate` by a frequency-mapped day offset (`daily=1`, `weekly=7`, `monthly=30`) and returns a fresh pending copy

---

## Pet Management
- **Duplicate task prevention** — `addTask()` checks by name before appending, blocking the same task from appearing twice in `requiredTasks`
- **Task removal with existence check** — `removeTask()` validates presence before removing, raising a descriptive error if not found

---

## Plan Scheduling
- **Pet-seeded task list** — `setPet()` deep-copies the pet's `requiredTasks` into the plan at assignment time, isolating plan tasks from future pet mutations
- **Multi-key priority sort** — `getTasksByPriority()` sorts by `priorityLevel` → `preferenceLevel` → frequency urgency (`daily > weekly > monthly`), all descending
- **Duration sort** — `getTasksByDuration()` sorts by `time` ascending or descending via a `shortestFirst` flag, without mutating the original task list
- **Status filtering** — `getTasksByStatus(completed)` filters tasks by boolean completion state; `getPendingTasks()` wraps this for the common case
- **Frequency filtering** — `getTasksByFrequency()` returns only tasks matching a given recurrence string, validated against `VALID_FREQUENCIES`
- **Total time aggregation** — `getTotalTime()` sums `time` across all plan tasks in a single pass
- **Completion with auto-recurrence** — `completeTask(task)` marks a task done and immediately appends its next occurrence to the plan via `getNextOccurrence()`
- **Bulk reset** — `resetAllTasks()` iterates all plan tasks and calls `resetTask()` on each

---

## Owner & Schedule Management
- **Availability budgeting** — `addAvailability()` and `subtractAvailability()` maintain a running `timeAvailable` balance; subtraction blocks if the deduction would go below zero
- **Feasibility check** — `canFitPlan()` compares `plan.getTotalTime()` against `timeAvailable` before committing
- **Atomic plan commitment** — `addPlan()` enforces three guards in sequence: duplicate plan, duplicate pet+day combination, and time budget overflow — then deducts time automatically on success
- **Cascading pet removal** — `removePet()` first finds and removes all plans associated with that pet (restoring their time), then removes the pet
- **Plan removal with time restoration** — `removePlan()` adds the plan's total time back to `timeAvailable` on removal
- **Schedule lookup** — `getPlansByDay()` and `getPlansByPet()` filter the plans list by day string or pet object reference
- **Cross-pet task aggregation** — `getAllTasks()` flattens `requiredTasks` across all owned pets into a single list
- **Pet name lookup** — `getTasksByPetName()` resolves a pet by name string and returns its task list, raising an error if not found
- **Time slot conflict detection** — `getTimeSlotConflicts()` compares `timeOfDay` values across all existing plans against a candidate plan, skipping `"anytime"` tasks and same-pet plans, and returns a list of human-readable conflict descriptions
