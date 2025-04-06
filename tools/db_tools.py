import sqlite3
from crewai.tools import tool
from pydantic import BaseModel, Field # Import BaseModel
import config

# --- Input Schemas ---
class DbQueryInput(BaseModel):
    """Input schema for the Database Query Tool."""
    query: str = Field(..., description="The SQLite SELECT query to execute.")

class DbUpdateInput(BaseModel):
    """Input schema for the Database Update Tool."""
    statement: str = Field(..., description="The SQLite INSERT, UPDATE, or DELETE statement to execute.")

# --- Tools ---
@tool("Database Query Tool")
def db_query_tool(query: str) -> str:
    """
    Executes a SQLite SELECT query and returns the results.
    Use this to fetch information like user details, health logs, safety events, or reminders.
    Input MUST be a JSON object with a 'query' key containing the SQL SELECT statement.
    Example Input: {"query": "SELECT * FROM health_logs WHERE `Device-ID_User-ID` = 'D1000' ORDER BY Timestamp DESC LIMIT 5;"}
    """
    # (Keep the existing function body the same)
    conn = None
    try:
        conn = sqlite3.connect(config.DATABASE_PATH)
        cursor = conn.cursor()
        if not query.strip().upper().startswith("SELECT"):
            return "Error: Only SELECT queries are allowed."
        cursor.execute(query)
        results = cursor.fetchall()
        if results:
            col_names = [description[0] for description in cursor.description]
            max_results = 10
            limited_results = results[:max_results]
            result_str = f"Query successful. Columns: {col_names}. Results: {limited_results}"
            if len(results) > max_results:
                 result_str += f" (Returning first {max_results} of {len(results)} results)."
            return result_str
        else:
            return "Query executed successfully, but returned no results."
    except sqlite3.Error as e:
        return f"Database query error: {e}. Query: {query}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"
    finally:
        if conn:
            conn.close()


@tool("Database Update Tool")
def db_update_tool(statement: str) -> str:
    """
    Executes a SQLite INSERT, UPDATE, or DELETE statement.
    Use this ONLY for logging agent actions, alerts, or updating statuses.
    Input MUST be a JSON object with a 'statement' key containing the SQL statement.
    BE VERY CAREFUL with UPDATE and DELETE. Prefer INSERT for logging.
    Example Input: {"statement": "INSERT INTO agent_logs (agent_name, action_description, status) VALUES ('Coordinator', 'Generated High HR alert for D1000', 'Success');"}
    """
    # (Keep the existing function body the same)
    conn = None
    allowed_starts = ("INSERT", "UPDATE", "DELETE")
    normalized_statement = statement.strip().upper()
    is_allowed = False
    for prefix in allowed_starts:
        if normalized_statement.startswith(prefix):
            is_allowed = True
            break
    if not is_allowed:
        return f"Error: Only {', '.join(allowed_starts)} statements are allowed. Statement received: '{statement[:50]}...'"
    try:
        conn = sqlite3.connect(config.DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(statement)
        conn.commit()
        rows_affected = cursor.rowcount
        return f"Database update successful. Statement executed. Rows affected: {rows_affected if rows_affected != -1 else 'N/A for INSERT'}"
    except sqlite3.Error as e:
        return f"Database update error: {e}. Statement: {statement}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"
    finally:
        if conn:
            conn.close()