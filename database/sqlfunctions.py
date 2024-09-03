### START OF FILE database/sqlfunctions.py ###

import sqlite3
import os
import shutil
import datetime
from error_handler import handle_error  # Import the error handler

DATABASE_NAME = "database/db_files/app_data.db"

def create_database():
    """Creates the SQLite database and tables."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[LOG] - {timestamp} - Creating database: {DATABASE_NAME}")

    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS article_elements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT UNIQUE,
                title_rule TEXT,
                body_start_rule TEXT,
                body_end_rule TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prompt_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_name TEXT UNIQUE,
                template_content TEXT,
                version INTEGER
            )
        """)

        # Create the agent_memory table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT,
                key TEXT,
                value TEXT,
                timestamp DATETIME
            )
        """)

            # Create the agent_memory table (add this if you missed it)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT,
            key TEXT,
            value TEXT,
            timestamp DATETIME
        )
    """)

        conn.commit()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[LOG] - {timestamp} - Database and tables created.")

    except Exception as e:
        handle_error(e, "create_database()")

    finally:
        conn.close()

def restore_database(backup_filename):
    """Restores the database from a specified backup file."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[LOG] - {timestamp} - Restoring database from: {backup_filename}")
    backup_filepath = os.path.join("database/db_backup", backup_filename)

    try:
        if not os.path.exists(backup_filepath):
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[ERROR] - {timestamp} - Backup file not found: {backup_filepath}")
            return

        shutil.copy2(backup_filepath, DATABASE_NAME)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[LOG] - {timestamp} - Database restored successfully.")
    except Exception as e:
        handle_error(e, "restore_database()", {"backup_filename": backup_filename})

def setup_memory_database():
    """Sets up the database for the memory functions in memory.py."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[LOG] - {timestamp} - setup_memory_database: Setting up database for memory functions...")

    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        # Create the agent_memory table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT,
                key TEXT,
                value TEXT,
                timestamp DATETIME
            )
        """)

        conn.commit()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[LOG] - {timestamp} - setup_memory_database: Database setup complete.")

    except Exception as e:
        handle_error(e, "setup_memory_database()")

    finally:
        conn.close()

### END OF FILE database/sqlfunctions.py ###