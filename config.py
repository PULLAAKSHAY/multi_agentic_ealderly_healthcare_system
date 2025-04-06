import os
from dotenv import load_dotenv

load_dotenv()

# --- Basic Configuration ---
DATABASE_PATH = os.path.join("database", "elderly_care.db")
CSV_HEALTH = os.path.join("data", "health_monitoring.csv")
CSV_SAFETY = os.path.join("data", "safety_monitoring.csv")
CSV_REMINDER = os.path.join("data", "daily_reminder.csv")

# --- Ollama Configuration ---
# Specify the Ollama model you want to use (make sure it's pulled)
# Examples: "llama3:8b-instruct", "mistral:7b-instruct", "phi3:mini"
OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "ollama/phi3:mini")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "https://apparent-anteater-epic.ngrok-free.app") # Default Ollama server root URL

# --- Agent Configuration ---
# Define default thresholds (These could eventually be user-specific and stored in DB)
DEFAULT_THRESHOLDS = {
    "HEART_RATE_LOW": 50,
    "HEART_RATE_HIGH": 110,
    "BP_SYS_HIGH": 140,
    "BP_DIA_HIGH": 90,
    "GLUCOSE_LOW": 70,
    "GLUCOSE_HIGH": 140,
    "SPO2_LOW": 92,
    "INACTIVITY_THRESHOLD_SECONDS": 7200 # 2 hours
}

# --- Notification Simulation ---
NOTIFICATION_LOG_FILE = "notifications.log"

# --- Email Configuration ---
# Email server settings (for caregiver alerts)
SMTP_SERVER = os.getenv("SMTP_SERVER", "your_smtp_server.com") # e.g., smtp.gmail.com
SMTP_PORT = int(os.getenv("SMTP_PORT", 465)) # Common ports: 465 (SSL), 587 (TLS)
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "your_email@example.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your_email_password")
NOTIFICATION_EMAIL_FROM = os.getenv("NOTIFICATION_EMAIL_FROM", "your_email@example.com")
NOTIFICATION_EMAIL_TO_CAREGIVER = os.getenv("NOTIFICATION_EMAIL_TO_CAREGIVER", "caregiver_email@example.com")
NOTIFICATION_EMAIL_TO_USER = os.getenv("NOTIFICATION_EMAIL_TO_USER", "user_email@example.com") # If needed for user reminders