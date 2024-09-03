### START OF FILE database/writing_assistant_management.py ###

import sqlite3
from database.sqlfunctions import DATABASE_NAME
import datetime
from error_handler import handle_error

def create_prompt_template(template_name=None, template_content=None):
    """
    Creates a new prompt template in the database,
    interactively prompting the user for input if needed.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - create_prompt_template() called.")

    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        if template_name is None:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[DEBUG] - {timestamp} - Prompting user for template name.")
            while True:
                template_name = input("Enter a name for the new template: ")
                confirm_name = input(f"Confirm template name: '{template_name}' (yes/edit): ").lower()
                if confirm_name == 'yes':
                    break
                elif confirm_name == 'edit':
                    continue
                else:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[WARNING] - {timestamp} - Invalid input. Please enter 'yes' or 'edit'.")

        if template_content is None:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[DEBUG] - {timestamp} - Prompting user for template content.")
            while True:
                template_content = input("Enter the prompt template (replace the task with {user_request}): ")
                confirm_content = input(f"Confirm template content:\n'{template_content}'\n(yes/edit): ").lower()
                if confirm_content == 'yes':
                    break
                elif confirm_content == 'edit':
                    continue
                else:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[WARNING] - {timestamp} - Invalid input. Please enter 'yes' or 'edit'.")

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - Template name: {template_name}")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - Template content: {template_content}")

        # Check for existing template with the same name
        cursor.execute("SELECT version FROM prompt_templates WHERE template_name = ?", (template_name,))
        existing_template = cursor.fetchone()

        if existing_template:
            version = existing_template[0] + 1
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[LOG] - {timestamp} - Template '{template_name}' already exists. Creating new version: {version}")
        else:
            version = 1

        cursor.execute("""
            INSERT INTO prompt_templates (template_name, template_content, version)
            VALUES (?, ?, ?)
        """, (template_name, template_content, version))
        conn.commit()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[LOG] - {timestamp} - Prompt template '{template_name}' (version {version}) created.")
        return f"I have created a new template called '{template_name}'."

    except Exception as e:
        handle_error(e, "create_prompt_template()", {"template_name": template_name, "template_content": template_content})
        return "Error: Could not create the template."

    finally:
        conn.close()

def get_prompt_template(template_name, version=None):
    """Retrieves a prompt template from the database."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - get_prompt_template() called.")
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    try:
        if version is not None:
            cursor.execute("""
                SELECT template_content
                FROM prompt_templates
                WHERE template_name = ? AND version = ?
            """, (template_name, version))
        else:
            cursor.execute("""
                SELECT template_content
                FROM prompt_templates
                WHERE LOWER(template_name) = ?  -- Force lowercase comparison
                ORDER BY version DESC
                LIMIT 1
            """, (template_name.lower(),))  # Also convert input to lowercase

        template = cursor.fetchone()
        if template:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[LOG] - {timestamp} - Retrieved template '{template_name}': {template[0]}")
            return template[0]
        else:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[WARNING] - {timestamp} - Prompt template '{template_name}' not found.")
            return None

    except Exception as e:
        handle_error(e, "get_prompt_template()", {"template_name": template_name, "version": version})
        return None

    finally:
        conn.close()

def edit_prompt_template(template_name, new_template_content=None):
    """Updates an existing prompt template."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - edit_prompt_template() called.")
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    try:
        if new_template_content is None:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[DEBUG] - {timestamp} - Prompting user for new template content.")
            while True:
                new_template_content = input("Enter the new prompt template (replace the task with {user_request}): ")
                confirm_content = input(f"Confirm new template content:\n'{new_template_content}'\n(yes/edit): ").lower()
                if confirm_content == 'yes':
                    break
                elif confirm_content == 'edit':
                    continue
                else:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[WARNING] - {timestamp} - Invalid input. Please enter 'yes' or 'edit'.")

        cursor.execute("""
            UPDATE prompt_templates
            SET template_content = ?
            WHERE template_name = ?
        """, (new_template_content, template_name))

        if cursor.rowcount > 0:
            conn.commit()
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[LOG] - {timestamp} - Prompt template '{template_name}' updated.")
        else:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[WARNING] - {timestamp} - Prompt template '{template_name}' not found.")

    except Exception as e:
        handle_error(e, "edit_prompt_template()", {"template_name": template_name, "new_template_content": new_template_content})

    finally:
        conn.close()

def delete_prompt_template(template_name):
    """Deletes a prompt template."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - delete_prompt_template() called.")
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM prompt_templates WHERE template_name = ?", (template_name,))
        conn.commit()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[LOG] - {timestamp} - Prompt template '{template_name}' deleted.")
    except Exception as e:
        handle_error(e, "delete_prompt_template()", {"template_name": template_name})
    finally:
        conn.close()

def list_template_versions(template_name):
    """Lists all versions of a given template."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - list_template_versions() called.")
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT version
            FROM prompt_templates
            WHERE template_name = ?
            ORDER BY version ASC
        """, (template_name,))

        versions = cursor.fetchall()
        if versions:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[LOG] - {timestamp} - Available versions for template '{template_name}':")
            for version in versions:
                print(f"- Version {version[0]}")
        else:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[WARNING] - {timestamp} - No versions found for template '{template_name}'")

    except Exception as e:
        handle_error(e, "list_template_versions()", {"template_name": template_name})

    finally:
        conn.close()


def list_all_templates():
    """Lists all available prompt templates."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - list_all_templates() called.")
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT template_name FROM prompt_templates")
        templates = cursor.fetchall()
        if templates:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[LOG] - {timestamp} - Available prompt templates:")
            for template in templates:
                print(f"- {template[0]}")
        else:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[WARNING] - {timestamp} - No prompt templates found.")

    except Exception as e:
        handle_error(e, "list_all_templates()")

    finally:
        conn.close()

### END OF FILE database/writing_assistant_management.py ###