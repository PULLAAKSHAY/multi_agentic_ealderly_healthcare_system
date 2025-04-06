from crewai import Crew, Process
from agents import health_monitor, safety_monitor, reminder_manager, coordinator
from tasks import health_analysis_task, safety_analysis_task, reminder_check_and_send_task, coordination_task
import data_setup # To ensure DB is ready

# --- Run Setup ---
# Consider running this only once, or add checks in data_setup to avoid reloading constantly
# For hackathon, running it each time ensures a clean slate with loaded data.
print("Running initial data setup...")
data_setup.setup_database()
print("-" * 50)


# --- Define the Crew ---

# Define the agents involved in this crew run
# Note: Reminder agent runs a separate process for now for simplicity
alerting_agents = [health_monitor, safety_monitor, coordinator]
reminder_agents = [reminder_manager]

# Define the tasks for the alerting workflow
alerting_tasks = [
    health_analysis_task,
    safety_analysis_task,
    coordination_task # This task depends on the previous two
]

# Define the tasks for the reminder workflow
reminder_tasks = [
    reminder_check_and_send_task
]

# --- Instantiate and Kick off the Crew ---

# Create the Crew for the Alerting Workflow
# Process.sequential ensures tasks run in the order defined
alerting_crew = Crew(
    agents=alerting_agents,
    tasks=alerting_tasks,
    process=Process.sequential,
    verbose=True  # <--- CHANGE HERE
    # memory=True # Optional: Enable memory for context across runs (more advanced)
)

# Create the Crew for the Reminder Workflow
reminder_crew = Crew(
    agents=reminder_agents,
    tasks=reminder_tasks,
    process=Process.sequential,
    verbose=True # <--- CHANGE HERE
)

# --- Simulate Running for a Specific User ---
# In a real system, this would be triggered by new data events.
# Here, we manually kick off the process for one user.
target_user_id = 'D1000' # Example User ID from your CSV data
# target_user_id = 'D1001' # Another example
# target_user_id = 'D1002' # Yet another

print(f"\n--- Starting Alerting Workflow for User: {target_user_id} ---")
# Provide the user ID as input to the tasks that need it
alerting_result = alerting_crew.kickoff(inputs={'user_id': target_user_id})

print(f"\n--- Alerting Workflow for User {target_user_id} Completed ---")
print("Final Alerting Result:")
print(alerting_result)
print("-" * 50)


print(f"\n--- Starting Reminder Workflow for User: {target_user_id} ---")
# Provide the user ID as input
reminder_result = reminder_crew.kickoff(inputs={'user_id': target_user_id})

print(f"\n--- Reminder Workflow for User {target_user_id} Completed ---")
print("Final Reminder Result:")
print(reminder_result)
print("-" * 50)

# You could loop through multiple users or simulate time passing for a more complex demo