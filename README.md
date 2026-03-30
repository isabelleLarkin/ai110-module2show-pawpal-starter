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
