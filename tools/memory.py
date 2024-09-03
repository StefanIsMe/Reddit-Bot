import sqlite3  # Import sqlite3 for database interaction
import datetime # Import for datetime operations

from database.sqlfunctions import DATABASE_NAME
from error_handler import handle_error

def create_user_memory_table():
    """Creates the user memory table in the database if it doesn't exist."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[LOG] - {timestamp} - create_user_memory_table: Creating user memory table...")

    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        # Check if the table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_memory'")
        if cursor.fetchone():
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[LOG] - {timestamp} - create_user_memory_table: User memory table already exists.")
            return

        # Create the table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE,
                value TEXT,
                timestamp DATETIME
            )
        """)

        conn.commit()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[LOG] - {timestamp} - create_user_memory_table: User memory table created.")

    except Exception as e:
        handle_error(e, "create_user_memory_table()")

    finally:
        conn.close()

def add_memory_item(key, value):
    """Adds a new memory item to the user memory table."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[LOG] - {timestamp} - add_memory_item: Adding memory item '{key}': '{value}'...")

    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        # Check if the memory item already exists
        cursor.execute("SELECT 1 FROM user_memory WHERE key = ?", (key,))
        if cursor.fetchone():
            # Update the existing memory item
            cursor.execute("UPDATE user_memory SET value = ?, timestamp = ? WHERE key = ?", (value, datetime.datetime.now(), key))
        else:
            # Insert a new memory item
            cursor.execute("INSERT INTO user_memory (key, value, timestamp) VALUES (?, ?, ?)", (key, value, datetime.datetime.now()))

        conn.commit()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[LOG] - {timestamp} - add_memory_item: Memory item added/updated.")

    except Exception as e:
        handle_error(e, "add_memory_item()", {"key": key, "value": value})

    finally:
        conn.close()

def get_memory_item(key):
    """Retrieves a memory item from the user memory table."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[LOG] - {timestamp} - get_memory_item: Retrieving memory item '{key}'...")

    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        cursor.execute("SELECT value FROM user_memory WHERE key = ?", (key,))
        result = cursor.fetchone()
        if result:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[LOG] - {timestamp} - get_memory_item: Retrieved value: '{result[0]}'")
            return result[0]
        else:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[LOG] - {timestamp} - get_memory_item: Memory item not found.")
            return None

    except Exception as e:
        handle_error(e, "get_memory_item()", {"key": key})
        return None

    finally:
        conn.close()

def delete_memory_item(key):
    """Deletes a memory item from the user memory table."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[LOG] - {timestamp} - delete_memory_item: Deleting memory item '{key}'...")

    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM user_memory WHERE key = ?", (key,))
        conn.commit()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[LOG] - {timestamp} - delete_memory_item: Memory item deleted.")

    except Exception as e:
        handle_error(e, "delete_memory_item()", {"key": key})

    finally:
        conn.close()

def delete_all_memory_items():
    """Deletes all memory items from the user memory table."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[LOG] - {timestamp} - delete_all_memory_items: Deleting all memory items...")

    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM user_memory")
        conn.commit()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[LOG] - {timestamp} - delete_all_memory_items: All memory items deleted.")

    except Exception as e:
        handle_error(e, "delete_all_memory_items()")

    finally:
        conn.close()