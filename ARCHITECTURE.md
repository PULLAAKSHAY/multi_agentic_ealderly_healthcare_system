# Architecture Document: Multi-Agent Elderly Care System

# version 0.0.1

## 1. Introduction

This document describes the architecture of the multi-agent AI system for elderly care. The system employs a modular design based on distinct agents collaborating through a central coordinator, leveraging local Ollama LLMs for intelligent processing and decision support.

## 2. System Overview

The system operates by ingesting data from various sources (simulated initially, potentially real sensors/wearables later), processing this data through specialized agents, coordinating responses, and triggering appropriate actions like reminders or alerts to relevant parties (elderly individual, caregivers, family).

```mermaid
graph TD
    subgraph ExternalSources
        direction LR
        WearablesSensors[Wearable/Environment Sensors] --> HealthDataInput{Health Data Stream};
        WearablesSensors --> SafetyDataInput{Safety Data Stream};
        ManualInput[Manual Input/Schedules] --> ReminderDataInput{Reminder Schedule};
    end

    subgraph MultiAgentSystem
        direction LR
        HealthDataInput --> HMA[HealthMonitorAgent];
        SafetyDataInput --> SMA[SafetyMonitorAgent];
        ReminderDataInput --> RA[ReminderAgent];

        HMA -->|Health Status/Alerts| CA(CoordinatorAgent);
        SMA -->|Safety Status/Alerts| CA;
        RA -->|Reminder Requests/Status| CA;

        CA -->|Commands/Queries| HMA;
        CA -->|Commands/Queries| SMA;
        CA -->|Commands/Queries| RA;
        CA -->|Notification Tasks| NA[NotificationAgent];
        CA -->|Interaction Tasks| UIA[UserInteractionAgent];

        subgraph LLM_Support
            direction TB
            Ollama[Ollama (Local LLMs)]
            HMA -->|Analysis Req| Ollama;
            SMA -->|Interpretation Req| Ollama;
            RA -->|Generation Req| Ollama;
            CA -->|Decision Support Req| Ollama;
            Ollama -->|Responses| HMA;
            Ollama -->|Responses| SMA;
            Ollama -->|Responses| RA;
            Ollama -->|Responses| CA;
        end

        subgraph ToolsAndMemory
            direction TB
            DB[(Database: SQL/Vector)];
            Scheduler[Scheduling Tool];
            TTS[TTS Tool];
            CommTools[Communication APIs];

            HMA <--> DB;
            SMA <--> DB;
            RA <--> DB;
            RA <--> Scheduler;
            CA <--> DB;
            NA <--> CommTools;
            UIA <--> TTS;
            UIA <--> DB;
        end

        UIA -->|Voice Reminders/Queries| ElderlyUser(Elderly User);
        ElderlyUser -->|Voice Ack/Input| UIA;

        NA -->|Alerts/Notifications| Caregivers[Caregivers/Family];
        NA -->|Alerts/Notifications| HealthcareProviders[Healthcare Providers];

        Caregivers -->|Status Queries?| UIA;
    end

    style ExternalSources fill:#f9f,stroke:#333,stroke-width:2px
    style MultiAgentSystem fill:#ccf,stroke:#333,stroke-width:2px
```

## 3. Agent Descriptions

- **HealthMonitorAgent**: Analyzes health data from the `health_logs` table using `health_analysis_task` to detect anomalies based on predefined thresholds.
- **SafetyMonitorAgent**: Analyzes safety data from the `safety_logs` table using `safety_analysis_task` to detect falls and prolonged inactivity.
- **ReminderAgent**: Manages and sends reminders from the `reminders` table using `reminder_check_and_send_task` for scheduled events like medication and appointments.
- **CoordinatorAgent**: Central agent that uses `coordination_task` to receive reports from health and safety monitors, assess the situation, prioritize alerts, and trigger caregiver notifications if necessary.
- **NotificationAgent**: (Currently basic) Sends notifications using the `notification_tool`.
- **UserInteractionAgent**: (Placeholder) Intended for future user interaction features.

## 4. Data Flow

1. **Data Ingestion**: The system starts with CSV datasets (`health_monitoring.csv`, `safety_monitoring.csv`, `daily_reminder.csv`) located in the `data/` directory.
2. **Database Setup**: The `data_setup.py` script initializes an SQLite database (`elderly_care.db` in the `database/` directory) and loads data from the CSV files into database tables (`health_logs`, `safety_logs`, `reminders`).
3. **Agent Data Access**: Agents (`HealthMonitorAgent`, `SafetyMonitorAgent`, `ReminderAgent`, `CoordinatorAgent`) use the `db_query_tool` to query the SQLite database for relevant data to perform their tasks.
4. **Alerting and Reminders**:
   - `HealthMonitorAgent` and `SafetyMonitorAgent` analyze health and safety data and report anomalies/concerns to the `CoordinatorAgent`.
   - `ReminderAgent` checks for due reminders and uses the `notification_tool` to send reminders.
   - `CoordinatorAgent` assesses alerts and uses the `notification_tool` to send caregiver alerts when necessary.
5. **Data Persistence**: The system uses the SQLite database to persist health and safety logs, reminders, alerts, and agent logs.
