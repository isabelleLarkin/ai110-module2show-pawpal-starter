import copy
import streamlit as st
from pawpal_system import Task, Pet, Plan, Owner, VALID_DAYS, VALID_TIME_SLOTS

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

Use this app to build and view a daily care schedule for your pets.
"""
)

st.divider()

# --- Session State Initialization ---
if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "schedule" not in st.session_state:
    st.session_state.schedule = None

if "feedback" not in st.session_state:
    st.session_state.feedback = None

PRIORITY_MAP = {"low": 1, "medium": 2, "high": 3}
PRIORITY_LABELS = {1: "Low", 2: "Medium", 3: "High"}
PRIORITY_ICONS = {1: "🟢 Low", 2: "🟡 Medium", 3: "🔴 High"}
FREQUENCY_ICONS = {"daily": "📅 Daily", "weekly": "🗓️ Weekly", "monthly": "📆 Monthly"}
SLOT_ICONS = {"morning": "🌅 Morning", "afternoon": "☀️ Afternoon", "evening": "🌙 Evening", "anytime": "🕐 Anytime"}

# --- Owner & Pet Setup ---
st.subheader("Owner & Pet")

owner_name = st.text_input("Owner name", value="Jordan")

col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col3:
    age = st.number_input("Pet age", min_value=0, max_value=30, value=2)

availability = st.number_input("Your availability today (minutes)", min_value=0, max_value=480, value=120)

# --- Tasks ---
st.divider()
st.subheader("Tasks")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

col4, col5, col6 = st.columns(3)
with col4:
    frequency = st.selectbox("Frequency", ["daily", "weekly", "monthly"])
with col5:
    preference = st.selectbox("Preference", ["low", "medium", "high"], index=1)
with col6:
    time_of_day = st.selectbox("Time of day", VALID_TIME_SLOTS, index=3)

col_add, col_clear = st.columns([1, 1])

with col_add:
    if st.button("Add task"):
        existing_names = [t.name for t in st.session_state.tasks]
        if task_title in existing_names:
            st.session_state.feedback = ("warning", f"'{task_title}' is already in the task list.")
        else:
            task = Task()
            task.set_name(task_title)
            task.set_time(int(duration))
            task.set_priority_level(PRIORITY_MAP[priority])
            task.set_frequency(frequency)
            task.set_preference_level(PRIORITY_MAP[preference])
            task.set_time_of_day(time_of_day)
            st.session_state.tasks.append(task)
            st.session_state.schedule = None
            st.session_state.feedback = ("success", f"'{task_title}' added.")

with col_clear:
    if st.button("Clear all tasks"):
        st.session_state.tasks = []
        st.session_state.schedule = None
        st.session_state.feedback = ("info", "All tasks cleared.")

# --- Persistent feedback message ---
if st.session_state.feedback:
    level, msg = st.session_state.feedback
    if level == "success":
        st.success(msg)
    elif level == "warning":
        st.warning(msg)
    elif level == "info":
        st.info(msg)
    elif level == "error":
        st.error(msg)

if st.session_state.tasks:
    st.caption(f"{len(st.session_state.tasks)} task(s) queued — {sum(t.time for t in st.session_state.tasks)} min total")
    st.table([
        {
            "Task": t.name,
            "Duration (min)": t.time,
            "Priority": PRIORITY_ICONS[t.priority_level],
            "Preference": PRIORITY_ICONS[t.preference_level],
            "Frequency": FREQUENCY_ICONS[t.frequency],
            "Time of Day": SLOT_ICONS[t.time_of_day],
        }
        for t in st.session_state.tasks
    ])
else:
    st.info("No tasks yet. Add one above.")

# --- Generate Schedule ---
st.divider()
st.subheader("Build Schedule")

day = st.selectbox("Schedule day", VALID_DAYS, index=0)

if st.button("Generate schedule"):
    if not st.session_state.tasks:
        st.session_state.feedback = ("warning", "Add at least one task before generating a schedule.")
        st.session_state.schedule = None
    else:
        total_task_time = sum(t.time for t in st.session_state.tasks)
        if total_task_time > availability:
            st.session_state.feedback = (
                "error",
                f"Not enough time. Tasks require {total_task_time} min "
                f"but you only have {int(availability)} min available."
            )
            st.session_state.schedule = None
        else:
            # Build pet with copies of tasks to avoid shared mutation
            pet = Pet()
            pet.set_name(pet_name)
            pet.set_species(species)
            pet.set_age(int(age))
            for t in st.session_state.tasks:
                pet.add_task(copy.copy(t))

            # Build owner and plan
            owner = Owner()
            owner.name = owner_name
            owner.add_availability(int(availability))
            owner.add_pet(pet)

            plan = Plan()
            plan.set_pet(pet)
            plan.set_day(day)
            conflicts = owner.get_time_slot_conflicts(plan)
            owner.add_plan(plan)

            # Store schedule output in session state
            st.session_state.schedule = {
                "owner": owner.name,
                "pet": pet.name,
                "day": day.capitalize(),
                "total_time": plan.get_total_time(),
                "time_remaining": owner.time_available,
                "conflicts": conflicts,
                "plan": plan,
            }
            st.session_state.feedback = None

# --- Persistent Schedule Display ---
if st.session_state.schedule:
    s = st.session_state.schedule
    plan = s["plan"]

    st.divider()
    st.subheader(f"📋 {s['day']} Schedule — {s['pet']}")
    st.success(f"Schedule generated for **{s['owner']}**. All tasks fit within your availability.")

    conflicts = s.get("conflicts", [])
    if conflicts:
        for conflict in conflicts:
            st.warning(f"⚠️ Time slot conflict: {conflict}")
    else:
        st.success("✅ No time slot conflicts.")

    pending = len(plan.get_tasks_by_status(completed=False))
    done = len(plan.get_tasks_by_status(completed=True))

    m1, m2, m3 = st.columns(3)
    m1.metric("Total time", f"{s['total_time']} min")
    m2.metric("Time remaining", f"{s['time_remaining']} min")
    m3.metric("Tasks", f"{pending} pending · {done} done")

    st.divider()

    sort_mode = st.radio(
        "Sort tasks by",
        ["Priority", "Duration (shortest first)", "Duration (longest first)"],
        horizontal=True,
    )

    if sort_mode == "Priority":
        sorted_tasks = plan.get_tasks_by_priority()
    elif sort_mode == "Duration (shortest first)":
        sorted_tasks = plan.get_tasks_by_duration(shortest_first=True)
    else:
        sorted_tasks = plan.get_tasks_by_duration(shortest_first=False)

    st.table([
        {
            "Task": t.name,
            "Duration (min)": t.time,
            "Priority": PRIORITY_ICONS[t.priority_level],
            "Preference": PRIORITY_ICONS[t.preference_level],
            "Frequency": FREQUENCY_ICONS[t.frequency],
            "Time of Day": SLOT_ICONS[t.time_of_day],
            "Status": "✅ Done" if t.completed else "⏳ Pending",
        }
        for t in sorted_tasks
    ])
