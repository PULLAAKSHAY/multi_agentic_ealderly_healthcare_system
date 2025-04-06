import datetime
from crewai.tools import tool # Import the decorator
import config # Import your config file
import smtplib
import ssl
import os # Need os import here too


@tool("Simulated Notification Tool")
def notification_tool(recipient_and_message: str) -> str:
    """
    Simulates sending a notification message (e.g., reminder, alert) to a recipient (e.g., 'User', 'Caregiver', 'SystemLog').
    The message will be printed to the console and appended to a log file.
    For 'Caregiver' recipients, it will also attempt to send an email notification.
    Input should be a string containing the recipient and the message, separated by a pipe '|'. Example: 'Caregiver|Alert for User D1001: Fall detected in Living Room.'
    """
    try:
        # Handle potential extra whitespace and ensure splitting works
        parts = recipient_and_message.split('|', 1)
        if len(parts) != 2:
             raise ValueError("Input must contain exactly one pipe '|' separator.")
        recipient = parts[0].strip()
        message = parts[1].strip()
        if not recipient or not message:
            raise ValueError("Recipient and message cannot be empty.")

    except ValueError as e:
        return f"Error: Input format incorrect. Expected 'Recipient|Message'. Received: '{recipient_and_message}'. Details: {e}"
    except Exception as e:
         return f"Error processing input '{recipient_and_message}': {e}"


    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] TO: {recipient} | MSG: {message}"

    print(f"--- NOTIFICATION START ---")
    print(log_message)
    print(f"--- NOTIFICATION END ---")

    try:
        # Ensure directory exists (though setup.py should handle this)
        log_dir = os.path.dirname(config.NOTIFICATION_LOG_FILE)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        with open(config.NOTIFICATION_LOG_FILE, 'a') as f:
            f.write(log_message + '\n')
        # return f"Notification successfully simulated for {recipient} and logged." # Original return

    except Exception as e:
        print(f"Error writing to notification log file '{config.NOTIFICATION_LOG_FILE}': {e}")
        return f"Notification simulated for {recipient}, but failed to write to log file."

    # --- Email Sending (for Caregiver Notifications) ---
    if recipient == "Caregiver":
        email_subject = f"Elderly Care Alert: {message[:50]}..." # Short subject line
        email_body = f"Dear Caregiver,\n\nThis is an automated alert from the Elderly Care System:\n\n{message}\n\nTimestamp: {timestamp}\n\nPlease take appropriate action.\n\nSincerely,\nElderly Care AI System"

        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(config.SMTP_SERVER, config.SMTP_PORT, context=context) as server:
                server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
                server.sendmail(config.NOTIFICATION_EMAIL_FROM, config.NOTIFICATION_EMAIL_TO_CAREGIVER, f"Subject: {email_subject}\n\n{email_body}")
            print(f"--- EMAIL NOTIFICATION SENT TO CAREGIVER ---")
        except Exception as e:
            print(f"--- EMAIL NOTIFICATION FAILED TO SEND TO CAREGIVER ---")
            print(f"Error sending email: {e}")
            return f"Notification simulated and logged, but email to caregiver failed. Check logs for email sending errors."

    return f"Notification successfully simulated and logged. Email sent to caregiver (if applicable)."


# --- Helper Function (Not a CrewAI tool) ---


def create_alert_payload(user_id, alert_type, severity, details):
    """Helper to create a structured alert dictionary."""
    return {
        "user_id": user_id,
        "alert_type": alert_type,
        "severity": severity,
        "details": details,
        "timestamp": datetime.datetime.now().isoformat()
    }