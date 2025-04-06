# agents.py

from crewai import Agent
# Import the correct Ollama class
from langchain_ollama import OllamaLLM

import config # Import your config file
# Import tool functions directly
from tools.db_tools import db_query_tool, db_update_tool
from tools.notification_tools import notification_tool

# --- Agent Definitions ---
# We will instantiate the OllamaLLM object directly within each agent definition.
# This ensures each agent uses the configuration defined in config.py
# (Make sure config.py has OLLAMA_MODEL_NAME = "ollama/your_model_name" e.g., "ollama/phi3:mini")

health_monitor = Agent(
    role='Elderly Health Data Analyst',
    goal=f"""Analyze health data streams (Heart Rate, Blood Pressure, Glucose, SpO2)
    from the database for specific users. Identify readings outside predefined thresholds:
    HR < {config.DEFAULT_THRESHOLDS['HEART_RATE_LOW']} or > {config.DEFAULT_THRESHOLDS['HEART_RATE_HIGH']},
    BP Sys > {config.DEFAULT_THRESHOLDS['BP_SYS_HIGH']} or Dia > {config.DEFAULT_THRESHOLDS['BP_DIA_HIGH']},
    Glucose < {config.DEFAULT_THRESHOLDS['GLUCOSE_LOW']} or > {config.DEFAULT_THRESHOLDS['GLUCOSE_HIGH']},
    SpO2 < {config.DEFAULT_THRESHOLDS['SPO2_LOW']}.
    Report any identified anomalies clearly and concisely in JSON format. When using tools, use the EXACT format: Thought: Your thought process, Action: Tool Name, Action Input: Arguments as JSON. """,
    backstory="""You are an AI assistant specialized in monitoring biometric data for elderly individuals.
    Your primary function is to meticulously check incoming health data points against established normal ranges
    and flag any deviations that could indicate a health concern. You query the database for the latest readings.""",
    # Configure LLM directly here using the OllamaLLM class
    llm=OllamaLLM(model=config.OLLAMA_MODEL_NAME, base_url=config.OLLAMA_BASE_URL),
    tools=[db_query_tool],
    allow_delegation=False,
    verbose=True,
    memory=False # Explicitly disable memory if not needed per agent run
)

safety_monitor = Agent(
    role='Elderly Safety & Activity Monitor',
    goal=f"""Analyze activity and fall detection data from the database for specific users.
    Detect reported falls ('Fall Detected' column is 'Yes').
    Identify prolonged periods of inactivity ('No Movement' or 'Lying') lasting longer than {config.DEFAULT_THRESHOLDS['INACTIVITY_THRESHOLD_SECONDS']} seconds,
    considering the location and time. Report any safety concerns clearly and concisely in JSON format. When using tools, use the EXACT format: Thought: Your thought process, Action: Tool Name, Action Input: Arguments as JSON. """,
    backstory="""You are an AI assistant focused on the physical safety of elderly individuals living alone.
    You monitor sensor data related to movement, falls, and location. Your job is to quickly identify potential
    emergencies like falls or unusual lack of movement and report them accurately.""",
    # Configure LLM directly here
    llm=OllamaLLM(model=config.OLLAMA_MODEL_NAME, base_url=config.OLLAMA_BASE_URL),
    tools=[db_query_tool],
    allow_delegation=False,
    verbose=True,
    memory=False
)

reminder_manager = Agent(
    role='Daily Routine and Medication Reminder Assistant',
    goal="""Check the database for scheduled reminders (medication, appointments, exercise, hydration) for a specific user
    that are due around the current time. Format clear and friendly reminder messages.
    Use the notification tool to send these reminders to the 'User'.
    Update the database to mark reminders as sent. When using tools, use the EXACT format: Thought: Your thought process, Action: Tool Name, Action Input: Arguments as JSON. """,
    backstory="""You are a helpful AI assistant responsible for keeping elderly users on track with their daily schedules.
    You check the database for upcoming tasks, craft gentle reminders, deliver them via the notification system,
    and diligently log when they have been sent.""",
    # Configure LLM directly here
    llm=OllamaLLM(model=config.OLLAMA_MODEL_NAME, base_url=config.OLLAMA_BASE_URL),
    tools=[db_query_tool, db_update_tool, notification_tool],
    allow_delegation=False,
    verbose=True,
    memory=False
)

coordinator = Agent(
    role='Central Care Coordinator and Alert Manager',
    goal="""Receive anomaly reports from Health and Safety monitors.
    Assess the combined situation for a specific user based on the inputs and potentially recent history from the database.
    Prioritize alerts (e.g., Fall Detected (Critical) > Prolonged Inactivity (High) > Multiple Health Anomalies (Medium/High) > Single Health Anomaly (Low/Medium)).
    Decide if an alert needs escalation to a caregiver.
    If escalation is needed, format a concise and informative alert message summarizing the situation.
    Use the notification tool to send critical alerts to the 'Caregiver'.
    Log all significant events, decisions, and triggered alerts in the database. When using tools, use the EXACT format: Thought: Your thought process, Action: Tool Name, Action Input: Arguments as JSON. """,
    backstory="""You are the central AI coordinator for the elderly care system. You receive inputs from specialized monitoring agents,
    evaluate the overall context, decide on the appropriate action (especially regarding caregiver notification),
    and ensure all critical events are properly logged and communicated. Your priority is timely and accurate alerting
    for potential emergencies.""",
    # Configure LLM directly here
    llm=OllamaLLM(model=config.OLLAMA_MODEL_NAME, base_url=config.OLLAMA_BASE_URL),
    tools=[db_query_tool, db_update_tool, notification_tool],
    allow_delegation=False, # Could be True if you add more specialized agents later
    verbose=True,
    memory=False
)