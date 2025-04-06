from crewai import Task
from agents import health_monitor, safety_monitor, reminder_manager, coordinator
import datetime
import config # Import config for thresholds if needed in descriptions
import json # Import json module for parsing JSON outputs

# Note: We will pass dynamic data like user_id and timestamp via inputs in main.py
# The f-strings here are illustrative placeholders.

# --- Task Definitions ---

# Task for Health Monitoring Agent
health_analysis_task = Task(
    description=(
        "1. Identify the target user ID: '{user_id}'.\n"
        "2. Query the 'health_logs' table for the most recent entry for this user.\n"
        "   Example Query: SELECT Timestamp, Heart_Rate, Blood_Pressure, Glucose_Levels, Oxygen_Saturation_SpO2 FROM health_logs WHERE `Device-ID_User-ID` = '{user_id}' ORDER BY Timestamp DESC LIMIT 1;\n"
        "3. Analyze the fetched data point (Heart_Rate, Blood_Pressure, Glucose_Levels, Oxygen_Saturation_SpO2). Note: Blood_Pressure is a text field like '140/90', you MUST parse it to get Systolic and Diastolic values.\n"
        "4. Compare each value against these thresholds:\n"
        f"   - Heart_Rate: < {config.DEFAULT_THRESHOLDS['HEART_RATE_LOW']} or > {config.DEFAULT_THRESHOLDS['HEART_RATE_HIGH']}\n"
        f"   - Blood_Pressure (Parsed): Systolic > {config.DEFAULT_THRESHOLDS['BP_SYS_HIGH']} or Diastolic > {config.DEFAULT_THRESHOLDS['BP_DIA_HIGH']}\n"
        f"   - Glucose_Levels: < {config.DEFAULT_THRESHOLDS['GLUCOSE_LOW']} or > {config.DEFAULT_THRESHOLDS['GLUCOSE_HIGH']}\n"
        f"   - Oxygen_Saturation_SpO2: < {config.DEFAULT_THRESHOLDS['SPO2_LOW']}\n"
        "5. If any value is outside its threshold, create a health anomaly report in JSON format.\n" # Output in JSON
        "   The report should clearly state the user ID, status ('anomalies_detected' or 'no_anomalies'), a list of anomalies (if any), and a report summary.\n" # JSON structure description
        "6. If multiple anomalies are found in the single data point, list them all in the 'anomalies' array.\n"
        "7. If no anomalies are found, set status to 'no_anomalies' and anomalies to an empty array."
    ),
    expected_output=(
        "A JSON object summarizing the health analysis. "
        "It should include user_id, status ('anomalies_detected' or 'no_anomalies'), "
        "anomalies (list of detected anomalies or empty list), and report_summary (text summary)."
        "Example (Anomaly): JSON object with status 'anomalies_detected' and a list of anomalies. "
        "Example (No Anomaly): JSON object with status 'no_anomalies' and an empty list of anomalies."
    ),
    agent=health_monitor,
    # context=[] # This task usually runs first or in parallel, doesn't need context from others initially
)

# Task for Safety Monitoring Agent
safety_analysis_task = Task(
    description=(
        "1. Identify the target user ID: '{user_id}'.\n"
        "2. Query the 'safety_logs' table for the most recent entry for this user.\n"
        "   Example Query: SELECT * FROM safety_logs WHERE `Device-ID_User-ID` = '{user_id}' ORDER BY Timestamp DESC LIMIT 1;\n"
        "3. Analyze the fetched data point, specifically checking the 'Fall_Detected' column.\n"
        "4. If 'Fall_Detected' is 'Yes', immediately create a 'Fall Detected' safety alert report in JSON format including user ID, status 'safety_concern_detected', concern_type 'fall_detected', and details like location and timestamp in 'details'.\n" # JSON output for fall
        "5. If no fall is detected, check the 'Movement_Activity' in the fetched data point.\n"
        "6. If 'Movement_Activity' is 'No Movement' or 'Lying' in this latest log entry, this indicates potential inactivity.\n"
        "   Create a 'Potential Inactivity' report in JSON format including user ID, status 'safety_concern_detected', concern_type 'potential_inactivity'.\n"
        "   Include details like location and timestamp from the log. Set duration to null, as actual duration requires comparing multiple logs (which is outside this task's scope).\n" # JSON output for potential inactivity
        "7. If neither a fall nor potential inactivity ('No Movement' or 'Lying') is detected in the latest log, report in JSON format with status 'no_safety_concern', concern_type and details as null." # JSON output for no concern
    ),
    expected_output=(
        "A JSON object summarizing the safety analysis. "
        "It should include user_id, status ('safety_concern_detected' or 'no_safety_concern'), "
        "concern_type (e.g., 'fall_detected', 'prolonged_inactivity' or null), "
        "details (relevant details like location, duration or null), and report_summary (text summary)."
        "Example (Concern): JSON object with status 'safety_concern_detected' and details about the concern. "
        "Example (No Concern): JSON object with status 'no_safety_concern' and null for concern_type and details."
    ),
    agent=safety_monitor,
    # context=[] # This task usually runs first or in parallel
)

# Task for Reminder Agent
# This task would ideally be triggered based on time, not just user ID.
# For the hackathon, we can simplify and check for *any* unsent reminder for the user.
reminder_check_and_send_task = Task(
    description=(
        "1. Identify the target user ID: '{user_id}'.\n"
        "2. Query the 'reminders' table for any reminders for this user where 'Reminder_Sent_YesNo' is 'No'.\n"
        "   Example Query: SELECT * FROM reminders WHERE `Device-ID_User-ID` = '{user_id}' AND Reminder_Sent_YesNo = 'No' LIMIT 5;\n" # Limit to avoid overload
        "3. For each unsent reminder found:\n"
        "   a. Format a friendly reminder message including the 'Reminder_Type' and 'Scheduled_Time'.\n"
        "   b. Use the 'Simulated Notification Tool' to send the message to the 'User'. Input format: 'User|Your reminder message'.\n"
        "   c. Use the 'Database Update Tool' to update the reminder's status in the database, setting 'Reminder_Sent_YesNo' to 'Yes'. "
        "      Example Update: UPDATE reminders SET Reminder_Sent_YesNo = 'Yes' WHERE log_id = [the reminder's log_id];\n"
        "4. Report on the actions taken, e.g., 'Sent 2 reminders for user {user_id} and updated status.' or 'No pending reminders found for user {user_id}'."
    ),
     expected_output=(
         "A summary report stating how many reminders were sent for user {user_id}, confirmation that their status was updated in the database, "
         "or a message indicating no pending reminders were found."
         "Example Output: 'Sent 1 reminder (Medication at 11:30) for user D1004 and updated status in DB.'\n"
         "Example Output: 'No pending reminders found for user D1001.'"
     ),
    agent=reminder_manager
)


# Task for Coordinator Agent - This task DEPENDS on the outputs of the monitoring tasks
coordination_task = Task(
    description=(
        "1. Review the Health Anomaly Report provided in the context (output of health_analysis_task).\n"
        "2. Review the Safety Alert Report provided in the context (output of safety_analysis_task).\n"
        "3. Identify the user ID: '{user_id}' from the context or inputs.\n"
        "4. **[Validation Step]**: Parse and validate the JSON format of both Health and Safety reports. Ensure they contain expected fields (user_id, status, report_summary, etc.).\n" # Validation step
        "   If validation fails for either report, log an error and proceed with available information.\n" # Robustness: Handle potential parsing errors
        "5. Assess the severity based on the validated reports. Priority: Fall Detected (Critical) > Prolonged Inactivity (High) > Multiple Health Anomalies (Medium/High) > Single Health Anomaly (Low/Medium).\n"
        "6. Decide if a notification to the 'Caregiver' is necessary based on severity (e.g., required for Critical/High, optional for Medium, not needed for Low or No issues).\n"
        "7. If notification is needed:\n"
        "   a. Format a single, concise alert message summarizing all critical findings from both health and safety reports.\n"
        "   b. Use the 'Simulated Notification Tool' to send this consolidated message to the 'Caregiver'. Input format: 'Caregiver|Your alert message'.\n"
        "   c. Use the 'Database Update Tool' to log the generated alert in the 'alerts' table. Include user_id, alert_type (e.g., 'Fall', 'High HR', 'Combined'), severity, details, and set notification_sent_status to TRUE.\n"
        "      Example INSERT: INSERT INTO alerts (user_id, alert_type, severity, details, notification_sent_status) VALUES ('{user_id}', 'Fall', 'Critical', 'Fall detected in Living Room.', 1);\n"
        "8. If no notification is needed, simply state 'No caregiver notification required based on current reports for user {user_id}'.\n"
        "9. Use the 'Database Update Tool' to log your decision process (e.g., alert generated, or no action needed) in the 'agent_logs' table for the 'Coordinator' agent.\n" # More informative logging
        "   Example Log: INSERT INTO agent_logs (agent_name, action_description, status, details) VALUES ('Coordinator', 'Decision process completed', 'Success', 'Caregiver alert decision made based on health and safety reports.');\n" # More informative log example
    ),
    expected_output=(
        "A final report stating whether a caregiver alert was generated and sent for user {user_id}. "
        "If an alert was sent, include the message content. If not, state why. "
        "Also confirm that the decision and any alerts were logged in the database."
        "Example Output (Alert Sent): 'Caregiver alert generated and sent for D1001 due to Fall Detected. Alert logged in DB. Coordinator action logged.'\n"
        "Example Output (No Alert): 'No caregiver notification required based on current reports for user D1004 (No anomalies/concerns). Coordinator action logged.'"

    ),
    agent=coordinator,
    context=[health_analysis_task, safety_analysis_task] # CRITICAL: This task uses outputs from previous tasks
)