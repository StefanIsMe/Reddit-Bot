### START OF FILE database/reddit_account_management.py ###

import sqlite3
from database.sqlfunctions import DATABASE_NAME
from error_handler import handle_error
import datetime, time


def delete_reddit_account(email):
    """Deletes a Reddit account from the database, including its profile table."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(
        f"[LOG] - {timestamp} - delete_reddit_account: Deleting account with email '{email}'..."
    )

    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        # Delete the account from the main accounts table
        cursor.execute("DELETE FROM reddit_accounts WHERE email = ?", (email,))

        # Delete the profile table (if it exists)
        simple_username = email.split("@")[0].replace(".", "_")  # Simplified username
        table_name = f"profile_{simple_username}"
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

        conn.commit()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[LOG] - {timestamp} - delete_reddit_account: Account and profile table deleted."
        )
        return f"Successfully deleted Reddit account: {email}"

    except sqlite3.Error as e:
        handle_error(
            e, "delete_reddit_account() - SQLite Error", {"email": email}
        )
        return (
            f"Error: Could not delete Reddit account due to a database error."
        )

    finally:
        conn.close()


def enforce_action_cooldown(username, action_type, cooldown_minutes=10):
    """
    Enforces a cooldown period for a specific action type, displaying a live countdown
    if the cooldown is active. If no cooldown is required, displays the time since
    the last action.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(
        f"[DEBUG] - {timestamp} - [FUNCTION START] - enforce_action_cooldown()"
    )
    print(
        f"[LOG] - {timestamp} - enforce_action_cooldown: Enforcing cooldown for '{action_type}' action by user '{username}'..."
    )

    # --- Print the input arguments ---
    print(
        f"[DEBUG] - {timestamp} - enforce_action_cooldown: username: {username}"
    )
    print(
        f"[DEBUG] - {timestamp} - enforce_action_cooldown: action_type: {action_type}"
    )
    print(
        f"[DEBUG] - {timestamp} - enforce_action_cooldown: cooldown_minutes: {cooldown_minutes}"
    )

    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        table_name = (
            f"profile_{username.split('@')[0].replace('.', '_')}"
        )

        cursor.execute(
            f"""
            SELECT timestamp 
            FROM {table_name}
            WHERE action_type = ? 
            ORDER BY timestamp DESC
            LIMIT 1
        """,
            (action_type,),
        )
        last_action_timestamp = cursor.fetchone()

        if last_action_timestamp:
            last_action_time = datetime.datetime.strptime(
                last_action_timestamp[0], "%Y-%m-%d %H:%M:%S.%f"
            )
            cooldown_seconds = cooldown_minutes * 60
            time_since_last_action = (
                datetime.datetime.now() - last_action_time
            ).total_seconds()
            minutes, seconds = divmod(time_since_last_action, 60)

            if time_since_last_action < cooldown_seconds:
                remaining_seconds = cooldown_seconds - time_since_last_action
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(
                    f"[LOG] - {timestamp} - enforce_action_cooldown: Cooldown for '{action_type}' is still active. Waiting..."
                )

                # --- Live Countdown ---
                while remaining_seconds > 0:
                    minutes, seconds = divmod(remaining_seconds, 60)
                    print(
                        f"Cooldown remaining: {int(minutes):02d}:{int(seconds):02d}",
                        end="\r",
                    )
                    time.sleep(1)
                    remaining_seconds -= 1

                print(
                    "Cooldown expired!                                          "
                )  # Clear the countdown line

            else:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(
                    f"[LOG] - {timestamp} - enforce_action_cooldown: No cooldown needed. Last '{action_type}' action was {int(minutes)} minutes and {int(seconds)} seconds ago."
                )

        else:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(
                f"[LOG] - {timestamp} - enforce_action_cooldown: No previous '{action_type}' action found. No cooldown needed."
            )

    except Exception as e:
        handle_error(
            e,
            "enforce_action_cooldown()",
            {
                "username": username,
                "action_type": action_type,
                "cooldown_minutes": cooldown_minutes,
            },
        )

    finally:
        conn.close()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[DEBUG] - {timestamp} - [FUNCTION END] - enforce_action_cooldown()"
        )


def has_performed_action_on_post(username, action_type, target_url):
    """
    Checks if the specified user has already performed the given action type on the target URL.

    This function prevents redundant actions by querying the user's profile table in the database.

    Args:
        username (str): The username (email) of the Reddit user.
        action_type (str): The type of action (e.g., "comment", "upvote").
        target_url (str): The URL of the target post or comment.

    Returns:
        bool: True if the user has performed the action on the target, False otherwise.
             Returns a string describing the error if an exception occurs.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(
        f"[LOG] - {timestamp} - [FUNCTION START] - has_performed_action_on_post()"
    )
    print(
        f"[LOG] - {timestamp} - has_performed_action_on_post: Checking if user '{username}' has performed action '{action_type}' on post '{target_url}'..."
    )

    try:
        # --- Step 1: Connect to the database ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP START] - Connecting to the database.")
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP END] - Connected to the database.")

        # --- Step 2: Extract simplified username and construct table name ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[DEBUG] - {timestamp} - [STEP START] - Extracting simplified username and constructing table name."
        )
        simple_username = username.split("@")[0].replace(".", "_")  # Simplified username
        table_name = f"profile_{simple_username}"
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[DEBUG] - {timestamp} - [STEP END] - Extracted simplified username and constructed table name."
        )

        # --- Step 3: Execute the SQL query to check for existing action ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[DEBUG] - {timestamp} - [STEP START] - Executing SQL query to check for existing action."
        )
        cursor.execute(
            f"""
            SELECT 1
            FROM {table_name}   
            WHERE action_type = ? AND target_id = ?
        """,
            (action_type, target_url),
        )
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[DEBUG] - {timestamp} - [STEP END] - Executed SQL query to check for existing action."
        )

        # --- Step 4: Fetch the result ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP START] - Fetching the result.")
        result = cursor.fetchone()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP END] - Fetched the result.")

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[LOG] - {timestamp} - has_performed_action_on_post: Result: {bool(result)}"
        )
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[LOG] - {timestamp} - [FUNCTION END] - has_performed_action_on_post()"
        )
        return bool(result)

    except sqlite3.Error as e:
        handle_error(
            e,
            "has_performed_action_on_post() - SQLite Error",
            {
                "username": username,
                "action_type": action_type,
                "target_url": target_url,
            },
        )
        return (
            f"Error: Could not check for previous actions due to a database error: {e}"
        )

    except Exception as e:
        handle_error(
            e,
            "has_performed_action_on_post()",
            {
                "username": username,
                "action_type": action_type,
                "target_url": target_url,
            },
        )
        return (
            f"Error: An unexpected error occurred while checking for previous actions: {e}"
        )

    finally:
        conn.close()


def save_reddit_account(email, password):
    """
    Saves a new Reddit account's email, password, and status to the database.
    Creates the corresponding profile table.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[LOG] - {timestamp} - save_reddit_account: Saving Reddit account: {email}")
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        # --- Create the table if it doesn't exist ---
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS reddit_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE,
                password TEXT,
                status TEXT DEFAULT 'active'  -- Add status column with default 'active'
            )
        """
        )

        # --- Insert the new account details ---
        cursor.execute(
            "INSERT INTO reddit_accounts (email, password) VALUES (?, ?)",
            (email, password),
        )
        conn.commit()

        # --- Create the profile table ---
        simple_username = email.split("@")[0].replace(".", "_")  # Simplified username
        create_reddit_profile_table(simple_username)  # Create the table here!

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[LOG] - {timestamp} - save_reddit_account: Reddit account saved to database."
        )

    except sqlite3.IntegrityError as e:
        handle_error(
            e,
            "save_reddit_account() - IntegrityError (likely duplicate email)",
            {"email": email, "password": password},
        )
    except Exception as e:
        handle_error(
            e, "save_reddit_account()", {"email": email, "password": password}
        )
    finally:
        conn.close()


def update_reddit_account_status(email, new_status):
    """
    Updates the status of a Reddit account in the database using the account's email address.

    Args:
        email (str): The email address of the Reddit account to update.
        new_status (str): The new status of the account (e.g., 'active', 'banned').

    Returns:
        str: A message indicating the outcome of the update operation.
    """

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(
        f"[DEBUG] - {timestamp} - [FUNCTION START] - update_reddit_account_status()"
    )
    print(
        f"[LOG] - {timestamp} - update_reddit_account_status: Updating account with email '{email}' to status '{new_status}'..."
    )

    try:
        # --- Step 1: Connect to the database ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP START] - Connecting to the database.")
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP END] - Connected to the database.")

        # --- Step 2: Update the account status in the database ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[DEBUG] - {timestamp} - [STEP START] - Updating account status in the database."
        )
        cursor.execute(
            "UPDATE reddit_accounts SET status = ? WHERE email = ?",
            (new_status, email),
        )
        conn.commit()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[DEBUG] - {timestamp} - [STEP END] - Updated account status in the database."
        )

        # --- Step 3: Check if any rows were affected (account found and updated) ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[DEBUG] - {timestamp} - [STEP START] - Checking if the account was found and updated."
        )
        if cursor.rowcount > 0:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(
                f"[LOG] - {timestamp} - update_reddit_account_status: Reddit account with email '{email}' status updated to '{new_status}'."
            )
            return (
                f"Reddit account with email '{email}' status updated to '{new_status}'."
            )
        else:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(
                f"[WARNING] - {timestamp} - update_reddit_account_status: Reddit account with email '{email}' not found."
            )
            return f"Reddit account with email '{email}' not found."
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[DEBUG] - {timestamp} - [STEP END] - Checked if the account was found and updated."
        )

    except sqlite3.Error as e:
        # --- Handle specific SQLite errors ---
        handle_error(
            e,
            "update_reddit_account_status() - SQLite Error",
            {"email": email, "new_status": new_status},
        )
        return (
            f"Error: Could not update Reddit account status due to a database error."
        )
    except Exception as e:
        handle_error(
            e,
            "update_reddit_account_status()",
            {"email": email, "new_status": new_status},
        )
        return f"Error: Could not update Reddit account status."

    finally:
        conn.close()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[DEBUG] - {timestamp} - [FUNCTION END] - update_reddit_account_status()"
        )


def delete_all_reddit_accounts():
    """Deletes all Reddit account details from the database, including profile tables."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[LOG] - {timestamp} - delete_all_reddit_accounts: Starting...")

    confirmation = input(
        "Are you sure you want to delete ALL saved Reddit user details? (yes/no): "
    ).lower()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(
        f"[DEBUG] - {timestamp} - delete_all_reddit_accounts: User confirmation: {confirmation}"
    )

    if confirmation != "yes":
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[LOG] - {timestamp} - delete_all_reddit_accounts: Task aborted.")
        return "Deletion of Reddit accounts aborted."

    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        # --- Get a list of all profile tables --- 
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'profile_%';")
        profile_tables = [table[0] for table in cursor.fetchall()]

        # --- Delete all accounts from the main table ---
        cursor.execute("DELETE FROM reddit_accounts")

        # --- Delete each profile table ---
        for table_name in profile_tables:
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

        conn.commit()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[LOG] - {timestamp} - delete_all_reddit_accounts: All Reddit accounts and profile tables deleted from database."
        )
        return "All Reddit account details have been deleted."

    except Exception as e:
        handle_error(e, "delete_all_reddit_accounts()")
        return "Error: Could not delete Reddit account details."

    finally:
        conn.close()


def list_all_reddit_accounts(unused_argument=None):
    """
    Lists all saved Reddit account details including ID and status.
    Adds 'id' and 'status' columns if they are missing.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[LOG] - {timestamp} - list_all_reddit_accounts: Starting...")

    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        # --- Check for 'id' column ---
        cursor.execute("PRAGMA table_info(reddit_accounts)")
        columns = [column[1] for column in cursor.fetchall()]
        if "id" not in columns:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(
                f"[LOG] - {timestamp} - list_all_reddit_accounts: Adding 'id' column..."
            )
            cursor.execute(
                "ALTER TABLE reddit_accounts ADD COLUMN id INTEGER PRIMARY KEY AUTOINCREMENT"
            )

        # --- Check for 'status' column ---
        if "status" not in columns:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(
                f"[LOG] - {timestamp} - list_all_reddit_accounts: Adding 'status' column..."
            )
            cursor.execute(
                "ALTER TABLE reddit_accounts ADD COLUMN status TEXT DEFAULT 'active'"
            )

        # --- Now fetch account details ---
        cursor.execute("SELECT id, email, password, status FROM reddit_accounts")
        accounts = cursor.fetchall()

        if accounts:
            account_list = []
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(
                f"[LOG] - {timestamp} - list_all_reddit_accounts: Saved Reddit accounts:"
            )
            for id, email, password, status in accounts:
                print(
                    f"ID: {id}, Email: {email}, Password: [PASSWORD REDACTED], Status: {status}"
                )  # Redact password
                account_list.append(
                    {
                        "id": id,
                        "email": email,
                        "password": password,
                        "status": status,
                    }
                )
            return account_list
        else:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(
                f"[LOG] - {timestamp} - list_all_reddit_accounts: No Reddit accounts found in the database."
            )
            return "No Reddit accounts found in the database."

    except Exception as e:
        handle_error(e, "list_all_reddit_accounts()")
        return "Error: Could not list Reddit account details."

    finally:
        conn.close()


def create_reddit_profile_table(username):
    """
    Creates a table to track Reddit profile activity for the specified username.

    Table Schema:
    - id: INTEGER PRIMARY KEY AUTOINCREMENT (Unique identifier for each action)
    - action_type: TEXT (Type of action, e.g., "comment", "post", "upvote")
    - target_id: TEXT (ID of the target post, comment, or community)
    - timestamp: DATETIME (When the action occurred)
    - content: TEXT (Content of the action, e.g., comment text)
    - reason: TEXT (Reason for the action, linked to persona goals)
    - creation_date: DATETIME (Date and time when the profile was created)
    - last_login_date: DATETIME (Date and time of the last successful login)

    Args:
        username (str): The simplified Reddit username (with underscores) for which the table will be created.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(
        f"[DEBUG] - {timestamp} - [FUNCTION START] - create_reddit_profile_table()"
    )
    print(
        f"[LOG] - {timestamp} - create_reddit_profile_table: Creating table for '{username}'..."
    )

    try:
        # --- Step 1: Connect to the database ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP START] - Connecting to the database.")
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP END] - Connected to the database.")

        # --- Step 2: Construct the table name ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP START] - Constructing the table name.")
        table_name = f"profile_{username}"  # Simplified username
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP END] - Constructed the table name.")

        # --- Step 3: Check if the table already exists ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[DEBUG] - {timestamp} - [STEP START] - Checking if table already exists."
        )
        cursor.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,),
        )
        table_exists = cursor.fetchone()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[DEBUG] - {timestamp} - [STEP END] - Checked if table already exists."
        )

        if table_exists:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(
                f"[WARNING] - {timestamp} - create_reddit_profile_table: Table '{table_name}' already exists. Skipping table creation."
            )
            return
        else:
            # --- Step 4: Create the table ---
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[DEBUG] - {timestamp} - [STEP START] - Creating the table.")
            cursor.execute(
                f"""
                CREATE TABLE {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action_type TEXT,
                    target_id TEXT,
                    timestamp DATETIME,
                    content TEXT,
                    reason TEXT,
                    creation_date DATETIME,
                    last_login_date DATETIME
                )
            """
            )
            conn.commit()
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(
                f"[LOG] - {timestamp} - create_reddit_profile_table: Table '{table_name}' created."
            )
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[DEBUG] - {timestamp} - [STEP END] - Created the table.")

    except sqlite3.OperationalError as e:
        # --- Handle potential database errors ---
        handle_error(
            e,
            "create_reddit_profile_table() - OperationalError",
            {"username": username, "table_name": table_name},
        )
    except Exception as e:
        handle_error(e, "create_reddit_profile_table()", {"username": username})

    finally:
        conn.close()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[DEBUG] - {timestamp} - [FUNCTION END] - create_reddit_profile_table()"
        )


def record_reddit_action(
    username, action_type, target_id, content=None, reason=None
):
    """Records a Reddit user action in the database using parameterized queries."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(
        f"[LOG] - {timestamp} - record_reddit_action: Recording action for '{username}'..."
    )
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        # Extract simplified username
        simple_username = username.split("@")[0].replace(".", "_")
        table_name = f"profile_{simple_username}"

        # Parameterized query
        cursor.execute(
            f"""
            INSERT INTO {table_name} (action_type, target_id, timestamp, content, reason)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                action_type,
                target_id,
                datetime.datetime.now(),
                content,
                reason,
            ),
        )

        conn.commit()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[LOG] - {timestamp} - record_reddit_action: Action recorded.")

    except Exception as e:
        handle_error(
            e,
            "record_reddit_action()",
            {
                "username": username,
                "action_type": action_type,
                "target_id": target_id,
            },
        )

    finally:
        conn.close()

### END OF FILE database/reddit_account_management.py ###