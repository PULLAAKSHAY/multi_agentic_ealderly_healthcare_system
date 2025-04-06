# Multi-Agent Elderly Healthcare System

## 1. Description

This project implements a multi-agent AI system designed for elderly care simulation. It leverages the CrewAI framework and local Ollama LLMs to provide monitoring, reminders, and safety alerts based on simulated data. The system aims to facilitate communication and timely intervention for elderly individuals.

The system uses several specialized agents:

- **HealthMonitorAgent**: Analyzes simulated health data (heart rate, blood pressure, etc.) for anomalies.
- **SafetyMonitorAgent**: Monitors simulated safety data for falls or prolonged inactivity.
- **ReminderAgent**: Manages and sends scheduled reminders (medication, appointments).
- **CoordinatorAgent**: Receives reports from monitors, assesses the situation, prioritizes alerts, and notifies caregivers if necessary.

Data is ingested from CSV files, stored and managed in an SQLite database, and processed sequentially by the agents within defined workflows (alerting and reminders).

## 2. Features

- **Health Monitoring**: Detects health readings outside predefined thresholds.
- **Safety Monitoring**: Identifies falls and potential prolonged inactivity based on simulated sensor data.
- **Reminders**: Sends scheduled reminders for medication, appointments, etc.
- **Alert Coordination**: Assesses combined health and safety status, prioritizes issues, and escalates critical alerts to caregivers.
- **Local LLM Integration**: Uses Ollama (e.g., Phi-3 Mini) for analysis, interpretation, and decision support within agents.
- **Database Persistence**: Uses SQLite to store simulated logs, reminders, and alerts.

## 3. Architecture

The system follows a multi-agent architecture orchestrated by the CrewAI framework. Specialized agents collaborate by performing specific tasks and passing information sequentially. Ollama provides local LLM capabilities to enhance agent intelligence. An SQLite database handles data persistence.

For a detailed visualization and description, please refer to `ARCHITECTURE.md`. _(Note: The Mermaid diagram in `ARCHITECTURE.md` may need updating to reflect the `data_setup.py` script and specific database type (SQLite).)_

## 4. Technology Stack

- **Programming Language**: Python 3.10+
- **Multi-Agent Framework**: CrewAI
- **LLMs**: Ollama (tested with Phi-3 Mini)
- **LLM Interaction**: `langchain_ollama`
- **Database**: SQLite
- **Data Handling**: Pandas
- **Core Libraries**: `crewai`, `langchain-community`, `langchain-ollama`, `pandas`, `sqlalchemy` (See `requirements.txt` for full list)

## 5. Setup Instructions

1.  **Prerequisites**:

    - Python 3.10 or higher installed.
    - Ollama installed and running. ([Ollama Installation Guide](https://ollama.com/))

2.  **Clone Repository**:

    ```bash
    git clone <your-repository-url>
    cd multi_agentic_ealderly_healthcare_system
    ```

    _(Replace `<your-repository-url>` with the actual URL after creating the repository)_

3.  **Create Virtual Environment**:

    ```bash
    python -m venv myenv
    source myenv/bin/activate  # On Windows use `myenv\Scripts\activate`
    ```

4.  **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

5.  **Download LLM Model**:
    Pull the required model using Ollama (the default in `config.py` is `phi3:mini`).

    ```bash
    ollama pull phi3:mini
    ```

    _If you use a different model or Ollama URL, update `OLLAMA_MODEL_NAME` and `OLLAMA_BASE_URL` in `config.py`._

6.  **Initialize Database**:
    Run the setup script to create the SQLite database (`database/elderly_care.db`) and load data from the CSV files located in the `data/` directory.
    ```bash
    python data_setup.py
    ```

## 6. Usage

Run the main simulation script:

```bash
python main.py
```

The script will:

1.  Initialize the database (if not already done by `data_setup.py`).
2.  Define the alerting and reminder crews.
3.  Execute the workflows sequentially for a predefined `target_user_id` (currently set in `main.py`).
4.  Print the detailed execution steps (verbose mode is enabled) and the final results from both the alerting and reminder workflows to the console.

## 7. Project Structure

```
.
├── .env                  # Environment variables (if needed)
├── agents.py             # Defines the CrewAI agents
├── ARCHITECTURE.md       # System architecture details
├── config.py             # Configuration (LLM model, thresholds)
├── data/                 # Contains input CSV data files
│   ├── daily_reminder.csv
│   ├── health_monitoring.csv
│   └── safety_monitoring.csv
├── database/             # Contains the SQLite database
│   └── elderly_care.db
├── data_setup.py         # Script to initialize the database
├── main.py               # Main script to run the CrewAI workflows
├── myenv/                # Python virtual environment (if created)
├── PLANNING.md           # Project planning document
├── README.md             # This file
├── requirements.txt      # Python dependencies
├── tasks.py              # Defines the CrewAI tasks
├── tools/                # Custom tools for agents
│   ├── __init__.py
│   ├── db_tools.py
│   └── notification_tools.py
└── verify_llm.py         # Utility to test LLM connection
```

## 8. Future Enhancements (Ideas from PLANNING.md)

- Integrate real-time data streams from sensors/wearables.
- Implement more sophisticated scheduling for reminders.
- Enhance notification system (Email, SMS).
- Develop a simple UI (Flask/Streamlit) for caregivers.
- Implement RAG for context-aware agent responses.
- Add more robust error handling and logging.
- Explore fine-tuning local LLMs for specific tasks.
