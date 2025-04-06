import sqlite3
import pandas as pd
import os
import config # Import your config file

# Function to create tables based on ARCHITECTURE.md schema
def create_tables(conn):
    cursor = conn.cursor()
    # Simplified users table for hackathon - assumes thresholds are general for now
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        name TEXT,
        emergency_contact TEXT
    )""")

    # Load column names directly from CSVs to ensure alignment
    try:
        health_cols = pd.read_csv(config.CSV_HEALTH, nrows=0).columns.tolist()
        health_cols_sql = ", ".join([f'"{col.replace("/", "_").replace("(Yes/No)","").replace("(","").replace(")","").replace("%","").replace("₂","2").strip()}" TEXT' for col in health_cols]) # Basic cleaning
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS health_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            {health_cols_sql}
        )""")

        safety_cols = pd.read_csv(config.CSV_SAFETY, nrows=0).columns.tolist()
        # Handle potential missing columns gracefully if needed
        safety_cols_sql = ", ".join([f'"{col.replace("/", "_").replace("(Yes/No)","").replace("(","").replace(")","").replace(" ", "_").strip()}" TEXT' for col in safety_cols]) # Basic cleaning
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS safety_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            {safety_cols_sql}
        )""")

        reminder_cols = pd.read_csv(config.CSV_REMINDER, nrows=0).columns.tolist()
        reminder_cols_sql = ", ".join([f'"{col.replace("/", "_").replace("(Yes/No)","").replace("(","").replace(")","").replace(" ", "_").strip()}" TEXT' for col in reminder_cols]) # Basic cleaning
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS reminders (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            {reminder_cols_sql}
        )""")

        # Alert and Agent Log tables
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            alert_type TEXT,
            severity TEXT,
            details TEXT,
            notification_sent_status BOOLEAN DEFAULT FALSE
        )""")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            agent_name TEXT,
            action_description TEXT,
            status TEXT,
            details TEXT
        )""")

        print("Tables checked/created successfully.")
        conn.commit()

    except FileNotFoundError as e:
        print(f"Error finding CSV file for schema generation: {e}")
    except Exception as e:
        print(f"Error creating tables: {e}")


def clean_column_names(df):
    """Basic cleaning for DataFrame columns to match SQL conventions."""
    df.columns = [col.replace("/", "_").replace("(Yes/No)","").replace("(","").replace(")","").replace("%","").replace("₂","2").replace(" ", "_").strip() for col in df.columns]
    return df

def load_data(conn):
    print("Loading data from CSVs...")
    try:
        # Health Data
        df_health = pd.read_csv(config.CSV_HEALTH)
        df_health = clean_column_names(df_health)
        df_health.to_sql('health_logs', conn, if_exists='replace', index=False)
        print(f"Loaded {len(df_health)} records into health_logs.")

        # Safety Data
        df_safety = pd.read_csv(config.CSV_SAFETY)
        df_safety = clean_column_names(df_safety)
        df_safety.to_sql('safety_logs', conn, if_exists='replace', index=False)
        print(f"Loaded {len(df_safety)} records into safety_logs.")

        # Reminder Data
        df_reminder = pd.read_csv(config.CSV_REMINDER)
        df_reminder = clean_column_names(df_reminder)
        df_reminder.to_sql('reminders', conn, if_exists='replace', index=False)
        print(f"Loaded {len(df_reminder)} records into reminders.")

        # Add dummy user data based on Device IDs found
        all_device_ids = set(df_health['Device-ID_User-ID']) | set(df_safety['Device-ID_User-ID']) | set(df_reminder['Device-ID_User-ID'])
        cursor = conn.cursor()
        for user_id in all_device_ids:
            cursor.execute("INSERT OR IGNORE INTO users (user_id, name, emergency_contact) VALUES (?, ?, ?)",
                           (user_id, f"User {user_id}", f"Contact_{user_id}@example.com"))
        conn.commit()
        print(f"Ensured {len(all_device_ids)} users exist in users table.")


    except FileNotFoundError as e:
        print(f"Error: CSV file not found. Make sure these files are in the 'data' directory: {e}")
    except Exception as e:
        print(f"Error loading data into database: {e}")


def setup_database():
    # Ensure database directory exists
    os.makedirs(os.path.dirname(config.DATABASE_PATH), exist_ok=True)

    conn = None
    try:
        conn = sqlite3.connect(config.DATABASE_PATH)
        print(f"Database connected at {config.DATABASE_PATH}")
        create_tables(conn)
        load_data(conn) # Load fresh data each time setup is run
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    print("Setting up database and loading initial data...")
    setup_database()
    print("Setup complete.")