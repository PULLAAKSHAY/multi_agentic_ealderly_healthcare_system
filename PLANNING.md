# Planning Document: Multi-Agent Elderly Care System

## 1. Introduction

This document outlines the plan for developing a multi-agent AI system for elderly care, leveraging local Ollama models. The system aims to provide real-time monitoring, reminders, safety alerts, and facilitate communication between the elderly individual, caregivers, family, and healthcare providers.

## 2. Phases of Development

### Phase 1: Foundation & Setup (Sprint 1)

- **Objective:** Set up the development environment and basic agent framework.
- **Tasks:**
  - Install Python and necessary base libraries (Pandas, NumPy).
  - Set up Ollama and download initial LLM models (e.g., Llama 3 Instruct 8B, Phi-3 Mini). Test basic interaction via `ollama-python`.
  - Choose and install a multi-agent framework (e.g., CrewAI).
  - Set up basic project structure (directories for agents, tools, data, logs).
  - Initialize Git repository and consider adding `.gitignore`.
  - Set up database using `data_setup.py`.
  - Define basic agent skeletons (`HealthMonitorAgent`, `SafetyMonitorAgent`, `ReminderAgent`, `CoordinatorAgent`, `NotificationAgent`).

### Phase 2: Core Agent Logic & Simulation (Sprints 2-3)

- **Objective:** Implement core functionality for individual agents using rule-based logic and simulated data.
- **Tasks:**
  - **Data Loading & Validation:** Create functions to load and parse the provided CSV datasets (`health_monitoring.csv`, `safety_monitoring.csv`, `daily_reminder.csv`). Implement data validation checks when loading CSV datasets to ensure data integrity.
  - **HealthMonitorAgent:** Implement logic to process simulated health data rows, check against predefined (or dataset-derived) thresholds, and identify anomalies. Output potential alert status.
  - **SafetyMonitorAgent:** Implement logic to process simulated safety data rows, detect falls (based on 'Fall Detected' column for now), identify prolonged inactivity, and output potential alert status.
  - **ReminderAgent:** Implement logic to manage a schedule (derived from `daily_reminder.csv`), determine when reminders are due, and track acknowledgments (simulated). Output reminder requests.
  - **Simulation Harness:** Develop a simple runner script to feed data row-by-row (or in time-based batches) from the CSVs to the respective agents to simulate real-time events.

### Phase 3: Agent Integration & Coordination (Sprint 4)

- **Objective:** Enable communication between agents via the Coordinator.
- **Tasks:**
  - Define communication protocols/message formats between agents and the Coordinator within the chosen framework (CrewAI).
  - Implement `CoordinatorAgent` logic:
    - Receive status/alerts from `HealthMonitorAgent` and `SafetyMonitorAgent`.
    - Receive reminder requests from `ReminderAgent`.
    - Implement basic decision-making rules (e.g., if high-severity health alert OR fall detected -> trigger immediate notification; if reminder due -> trigger reminder notification).
    - Pass notification requests to `NotificationAgent`.
  - Implement basic `NotificationAgent`: Log notification requests (type, recipient, message content) to the console/file initially.

### Phase 4: Data Persistence & Tools (Sprint 5)

- **Objective:** Implement long-term storage and core tools.
- **Tasks:**
  - Set up a local database (SQLite for simplicity, PostgreSQL for robustness). SQLite database is used for simplicity.
  - Define database schemas (User Profiles, Alert History, Reminder Logs, Health Data Log, Safety Data Log).
  - Integrate database tools (e.g., SQLAlchemy) into agents where necessary (e.g., Coordinator logs alerts, ReminderAgent logs reminder status).
  - Consider implementing a scheduling mechanism for reminder tasks (e.g., using `APScheduler` or simple time-based triggers in a loop in `main.py`).
  - Implement basic notification tool integration (e.g., `smtplib` for email - requires configuration).

### Phase 5: LLM Integration & Advanced Features (Sprints 6-7)

- **Objective:** Enhance agent capabilities using local Ollama LLMs.
- **Tasks:** Specify the LLM model in `config.py` (e.g., Phi-3 Mini).
  - **HealthMonitorAgent:** Use LLM to summarize health status over a period or interpret combined abnormal readings for nuanced alerts.
  - **SafetyMonitorAgent:** Use LLM to describe the safety event in natural language for alerts.
  - **ReminderAgent:** Use LLM to generate more natural-sounding reminder messages (potentially personalized). Consider TTS integration (`pyttsx3`) for voice notes.
  - **CoordinatorAgent:** Use LLM to assess the overall situation based on inputs from multiple agents, potentially prioritize alerts, or draft more detailed notifications.
  - **RAG (Optional):** If needed, set up a Vector DB (ChromaDB) with relevant context (e.g., user-specific care notes, general medical info) and implement RAG patterns for agents to query.
  - Develop a simple interface (e.g., basic web UI using Flask/Streamlit or CLI) for caregivers to view status or receive alerts.

### Phase 6: Testing, Evaluation & Refinement (Sprint 8+)

- **Objective:** Thoroughly test the system, evaluate its performance, and refine logic.
- **Tasks:**
  - Expand the simulation harness to cover edge cases and complex scenarios derived from the datasets.
  - Evaluate the system's accuracy (correct alerts/reminders triggered) and timeliness.
  - Test LLM performance (quality of summaries, interpretations, latency) with local Ollama models. Optimize model choice/quantization if needed.
  - Refine agent prompts, coordination logic, and decision rules based on testing.
  - Conduct user acceptance testing (UAT) with simulated user/caregiver interactions.
  - Consider fine-tuning specific LLMs if performance on particular tasks is insufficient and appropriate training data can be curated/generated (future work).

## 3. Technology Stack

- **Programming Language:** Python 3.x
- **Multi-Agent Framework:** CrewAI
- **LLMs:** Ollama running locally (e.g., Phi-3 Mini)
- **LLM Interaction:** `ollama-python`
- **Databases:** SQLite
  - Relational: SQLite (initial) / PostgreSQL (production)
  - Vector (Optional for RAG): ChromaDB / FAISS
- **Data Handling:** Pandas, NumPy
- **Scheduling:** APScheduler
- **Notifications:** `smtplib` (Email), Twilio SDK (SMS - requires external account), App Push Notifications (requires platform-specific setup - future)
- **Text-to-Speech (TTS):** `pyttsx3` (local)
- **Web Framework (Optional UI):** Flask / Streamlit
- **Version Control:** Git

## 4. Dataset Usage

The provided CSV datasets (`daily_reminder.csv`, `health_monitoring.csv`, `safety_monitoring.csv`) will be primarily used for:

- **Simulation:** Driving the system with realistic event sequences.
- **Evaluation:** Assessing the accuracy and timeliness of agent responses against known outcomes in the data.
- **Rule Derivation:** Informing the thresholds and logic for rule-based components (e.g., vital sign thresholds, inactivity duration).
- **Synthetic Data Generation (Potential):** As a basis for creating more varied or conversational training/testing data for LLMs if needed.
- **Not for Direct LLM Fine-tuning (Initially):** The structured log format is not ideal for fine-tuning general LLMs directly without significant transformation.

## 5. Potential Challenges & Mitigation

- **LLM Performance (Local):** Local models can be resource-intensive and potentially slower or less capable than cloud APIs.
  - **Mitigation:** Use quantized models, select appropriate models for tasks (smaller models for simpler tasks), optimize prompts, potentially offload heavy tasks to non-LLM components.
- **Real-time Processing:** Ensuring timely detection and alerting.
  - **Mitigation:** Optimize code, use efficient data structures, potentially use asynchronous processing (`asyncio`), carefully manage LLM call latency.
- **Reliability & Accuracy:** Ensuring agents make correct decisions, especially in critical safety/health scenarios.
  - **Mitigation:** Rigorous testing, use rule-based checks alongside LLMs, implement robust error handling, clear escalation paths in the Coordinator.
- **Data Privacy & Security:** Handling sensitive health data.
  - **Mitigation:** Store data securely, implement access controls (especially if adding UI), anonymize data where possible during development/testing. Ensure compliance if deployed.
- **Integration Complexity:** Coordinating multiple agents, tools, and data sources.
  - **Mitigation:** Use a well-defined architecture, clear communication protocols (framework features), modular design.
