from llm_setup import * # Import all functions from llm_setup
from agent_setup import * # Import all functions from agent_setup
from browser_setup import * # Import all functions from browser_setup
from langchain_community.chat_models import ChatOpenAI
import os
import shutil
import datetime
from database.sqlfunctions import *
from error_handler import *
from tools.reddit_login import *
from tools.reddit_actions import * 
from database.reddit_account_management import * 
from database.writing_assistant_management import *
import datetime
import time
from proxy import * 
import re

# Configure logging
#logging.basicConfig(level=logging.DEBUG)

def create_daily_backup():
    """Creates a daily backup of the database."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [FUNCTION START] - create_daily_backup()")
    print(f"[DEBUG] - {timestamp} - create_daily_backup() called.")

    try:
        if not os.path.exists(DATABASE_NAME):
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[LOG] - {timestamp} - Database file not found. Creating a new database...")
            create_database()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        backup_dir = "database/db_backup/" + datetime.date.today().strftime("%Y-%m-%d")
        if not os.path.exists(backup_dir):
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[LOG] - {timestamp} - Backup directory not found. Creating directory: {backup_dir}")
            os.makedirs(backup_dir)
        backup_file = os.path.join(backup_dir, os.path.basename(DATABASE_NAME) + ".bak")
        if not os.path.exists(backup_file):
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[LOG] - {timestamp} - Creating daily database backup...")
            shutil.copy2(DATABASE_NAME, backup_file)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[LOG] - {timestamp} - Backup created: {backup_file}")
        else:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[LOG] - {timestamp} - Daily backup already exists for today.")

    except Exception as e:
        handle_error(e, "create_daily_backup()")

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [FUNCTION END] - create_daily_backup()")

def get_user_instructions():
    """Gets and validates user instructions."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [STEP START] - Getting user instructions.")
    user_instructions = input("Enter your web automation instructions (or 'quit' or 'restore'): ")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [USER INPUT] - {user_instructions}")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [STEP END] - Got user instructions.")
    return user_instructions

def handle_quit_command(user_instructions):
    """Handles the 'quit' command."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [STEP START] - Handling quit command.")
    if user_instructions.lower() == "quit":
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [QUIT] - Exiting main loop.")
        return True
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [STEP END] - Handled quit command.")
    return False

def handle_restore_command(user_instructions):
    """Handles the 'restore' command."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [STEP START] - Handling restore command.")
    if user_instructions.lower() == "restore":
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [RESTORE] - Entering database restore process.")
        try:
            backup_filename = input("Enter the filename of the backup to restore (including path relative to database/db_backup/): ")
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[DEBUG] - {timestamp} - [RESTORE] - User wants to restore database from: {backup_filename}")
            restore_database(backup_filename)
        except Exception as e:
            handle_error(e, "main() - Database Restore")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [RESTORE] - Database restore process complete.")
        return True
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [STEP END] - Handled restore command.")
    return False

def handle_empty_instructions(user_instructions):
    """Handles empty user instructions."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [STEP START] - Handling empty instructions.")
    if not user_instructions.strip():
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[WARNING] - {timestamp} - Instructions cannot be empty. Please try again.")
        return True
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [STEP END] - Handled empty instructions.")
    return False

def detect_and_store_sentiment(llm, user_instructions):
    """Detects sentiment from user instructions and stores it in memory."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [STEP START] - Sentiment Detection.")
    sentiment_prompt = f"""
    Instructions: Identify the desired sentiment for Reddit post selection from the following user instructions.

    User Instructions: {user_instructions}

    Possible Sentiments:
    - Negative: The user is looking for posts that express negative opinions or feelings.
    - Positive: The user is looking for posts that express positive opinions or feelings.
    - Neutral: The user is looking for posts that are objective or do not express strong opinions.
    - None: The user has not specified any sentiment preference, and any post is acceptable. 

    Important Considerations:
    - Choose "Neutral" only if the instructions explicitly mention wanting objective or balanced posts.
    - Choose "None" if there is no mention of sentiment or if the instructions imply any sentiment is acceptable.

    You **must** respond in the following format:

    RESPONSE_START
    [Replace this with answer from the Possible Sentiments]
    RESPONSE_END
    <-stop->

    Example Response:
    RESPONSE_START
    Positive
    RESPONSE_END
    <-stop->
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[LOG] - {timestamp} - Sending sentiment detection prompt to LLM: {sentiment_prompt}")
    sentiment_response = llm.invoke(sentiment_prompt, stop=["<-stop->"], timeout=30, max_tokens=20).strip()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[LOG] - {timestamp} - Received LLM response: {sentiment_response}")

    sentiment_match = re.search(r"RESPONSE_START\n(.*)\nRESPONSE_END", sentiment_response, re.IGNORECASE)
    if sentiment_match:
        detected_sentiment = sentiment_match.group(1).strip()
        print(f"[LOG] - {timestamp} - Detected sentiment: {detected_sentiment}")

        # --- Save sentiment to memory, even if it's "None" ---
        add_memory_item("desired_sentiment", detected_sentiment.lower())  
    else:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[WARNING] - {timestamp} - Could not extract sentiment from LLM response.")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [STEP END] - Sentiment Detection.")

def execute_indefinite_loop(llm, core_instruction):
    """Executes instructions in an indefinite loop."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [STEP START] - Entering indefinite loop.")
    while True:
        try:
            # --- Renew Tor Identity for Each Iteration ---
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[LOG] - {timestamp} - Renewing Tor identity...")
            renew_tor_identity()
            time.sleep(5)

            # --- Initialize Browser for Each Iteration ---
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[DEBUG] - {timestamp} - [STEP START] - Initializing web browser.")
            driver = initialize_browser()
            if driver is None:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[ERROR] - {timestamp} - Failed to initialize browser. Skipping this iteration.")
                time.sleep(10)
                continue
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[DEBUG] - {timestamp} - [STEP END] - Web browser initialized.")

            # --- Perform Reddit Login and Check Success ---
            login_success = perform_reddit_login(driver)
            if login_success:
                # --- Agent Execution Loop with Reprompting ---
                max_attempts = 3
                attempt = 1
                while attempt <= max_attempts:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[DEBUG] - {timestamp} - Attempt {attempt} of {max_attempts}")

                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[DEBUG] - {timestamp} - [STEP START] - Creating LangChain agent.")
                    agent_chain = create_agent(llm, driver)
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[DEBUG] - {timestamp} - [STEP END] - LangChain agent created.")

                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[DEBUG] - {timestamp} - [STEP START] - Executing agent.")
                    agent_response = execute_agent(agent_chain, core_instruction)
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[DEBUG] - {timestamp} - [STEP END] - Agent execution complete.")

                    # --- Extract user_instructions from agent response (if it's a dictionary) ---
                    if isinstance(agent_response, dict) and "input" in agent_response:
                        user_instructions = agent_response["input"]
                    else:
                        user_instructions = core_instruction

                    # --- Check for both final answer and action using regex ---
                    if re.search(r"Final Answer.*Action:", agent_response, re.DOTALL):
                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print(f"[WARNING] - {timestamp} - Agent returned both final answer and action. Reprompting...")
                        attempt += 1
                        continue

                    # --- Validate Action Input format ---
                    if "Action Input:" in agent_response:
                        action_input_start = agent_response.index("Action Input:") + len("Action Input:")
                        action_input_end = agent_response.find("Observation:")
                        action_input = agent_response[action_input_start:action_input_end].strip()
                        if not (action_input.startswith("[") and action_input.endswith("]")):
                            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            print(f"[WARNING] - {timestamp} - Invalid Action Input format: {action_input}. Reprompting...")
                            attempt += 1
                            continue
                    else:
                        break

                if attempt > max_attempts:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[ERROR] - {timestamp} - Exceeded maximum attempts to get valid Action Input format.")
                    agent_response = "Error: Could not get a valid response from the agent."

                if isinstance(agent_response, dict) and "output" in agent_response:
                    agent_response = agent_response["output"]
                else:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[WARNING] - {timestamp} - Agent response does not contain 'output' key.")

                # --- Check for task termination signals ---
                if any(phrase in agent_response for phrase in [
                    "Quitting the current task.",
                    "Successfully logged out of Reddit.",
                    "I will log out of Reddit and try a different task."
                ]):
                    print("Quitting current task and restarting the loop.")
                    break  # Exit the inner loop

                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[LOG] - {timestamp} - Main Loop: Agent Response:\n{agent_response}")
            else:
                print("Reddit login failed. Skipping this iteration.")
                continue  # Skip to the next iteration of the indefinite loop

        except Exception as e:
            handle_error(e, "main() - Indefinite Loop Execution")
            continue
        finally:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[DEBUG] - {timestamp} - [STEP START] - Quitting web browser.")
            if driver:
                driver.quit()
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[DEBUG] - {timestamp} - [STEP END] - Web browser quit.")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [STEP END] - Exited indefinite loop.")

def execute_single_instruction(llm, user_instructions):
    """Executes a single user instruction."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [STEP START] - Execute the instruction once.")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[LOG] - {timestamp} - Main Loop: User Instructions: {user_instructions}")

    # --- Renew Tor Identity for Each Iteration ---
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[LOG] - {timestamp} - Renewing Tor identity...")
    renew_tor_identity()
    time.sleep(5)

    # --- Initialize Browser for Each Iteration ---
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [STEP START] - Initializing web browser.")
    driver = initialize_browser()
    if driver is None:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[ERROR] - {timestamp} - Failed to initialize browser. Skipping this iteration.")
        time.sleep(10)
        return
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [STEP END] - Web browser initialized.")

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [STEP START] - Creating LangChain agent.")
    agent_chain = create_agent(llm, driver)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [STEP END] - LangChain agent created.")

    try:
        # --- Agent Execution ---
        response = execute_agent(agent_chain, user_instructions)

        # --- Extract Final Answer from the agent's response ---
        if isinstance(response, str):
            final_answer_match = re.search(r"Final Answer:\s*(.*)", response, re.DOTALL)
            if final_answer_match:
                response = final_answer_match.group(1).strip()
            else:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[WARNING] - {timestamp} - Could not extract 'Final Answer' from agent response.")

        # --- Check for the quit signal ---
        if any(phrase in response for phrase in ["Quitting the current task.", "Successfully logged out of Reddit."]):
            print("Task quit successfully.")
            return  # Exit the function

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[LOG] - {timestamp} - Main Loop: Agent Response:\n{response}")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP END] - Execute the instruction once.")

    except ValueError as e:
        if "LLM output conflict detected." in str(e):
            print("LLM output conflict detected. Ending task.")
            # You can add additional error handling here, such as logging or returning a specific message


def execute_agent(agent_chain, instructions):
    """Executes the agent with reprompting for invalid responses."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - execute_agent() called with instructions: {instructions}")

    if agent_chain is None:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[ERROR] - {timestamp} - Agent chain is not initialized. Cannot execute instructions.")
        return "Error: Agent chain not initialized."

    max_attempts = 3
    attempt = 1

    while attempt <= max_attempts:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - Attempt {attempt} of {max_attempts} to get valid agent output.")

        try:
            # Run the agent chain
            print(f"[DEBUG] - {timestamp} - About to run agent_chain.invoke()")
            response = agent_chain.invoke({"input": instructions})
            print(f"[DEBUG] - {timestamp} - Agent response type: {type(response)}")
            print(f"[DEBUG] - {timestamp} - Agent response: {response}")

            # Check response type and extract output
            if isinstance(response, dict):
                print(f"[DEBUG] - {timestamp} - Response is a dict. Keys: {response.keys()}")
                if 'output' in response:
                    output = response['output']
                elif 'text' in response:
                    output = response['text']
                else:
                    output = str(response)
            elif isinstance(response, str):
                output = response
            else:
                output = str(response)

            print(f"[DEBUG] - {timestamp} - Extracted output: {output}")

            # Check for reprompting conditions
            if any(phrase in output.lower() for phrase in ["invalid or incomplete response", "could not parse llm output"]):
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[WARNING] - {timestamp} - Agent returned an invalid response. Reprompting...")
                attempt += 1
                continue
            else:
                return output  # Return the valid output

        except Exception as e:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[ERROR] - {timestamp} - Failed to execute agent chain: {e}")
            print(f"[ERROR] - {timestamp} - Error type: {type(e)}")
            print(f"[ERROR] - {timestamp} - Error args: {e.args}")
            handle_error(e, "execute_agent()", {"instructions": instructions})
            attempt += 1
            continue

    # Max attempts exceeded
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[ERROR] - {timestamp} - Exceeded maximum attempts to get valid agent output.")
    return "Error: Could not get a valid response from the agent."


def main():
    """
    The main function that initializes the application, sets up the LLM,
    and runs the main loop for user interaction.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [FUNCTION START] - main()")
    print(f"[DEBUG] - {timestamp} - [START] - main() function started.")

    try:
        # --- Step 1: Set up the LLM connection ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP START] - Setting up LLM connection.")
        llm = get_llm()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP END] - LLM connection setup complete.")

        # --- Step 2: Create the daily database backup ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP START] - Creating daily database backup.")
        create_daily_backup()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP END] - Daily database backup complete.")

        # --- Step 3: Enter the main loop ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[LOG] - {timestamp} - Entering the main loop.")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP START] - Entering main loop.")

        while True:
            user_instructions = get_user_instructions()

            if handle_quit_command(user_instructions):
                break

            if handle_restore_command(user_instructions):
                continue

            if handle_empty_instructions(user_instructions):
                continue

            detect_and_store_sentiment(llm, user_instructions)

            # --- Step 4: Check for "indefinitely" keyword ---
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[DEBUG] - {timestamp} - [STEP START] - Checking for 'indefinitely' keyword.")
            if "indefinitely" in user_instructions.lower():
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[LOG] - {timestamp} - Detected 'indefinitely' keyword. Entering indefinite loop.")

                core_instruction = user_instructions.lower().replace("indefinitely", "").strip()
                execute_indefinite_loop(llm, core_instruction)

            else:
                response = execute_single_instruction(llm, user_instructions)  # Capture the response

                # --- Process Agent Response ---
                if isinstance(response, str):
                    if "I will log out of Reddit and try a different task." in response:
                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print(f"[LOG] - {timestamp} - Comment posting failed. Exiting current task.")
                        continue

                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[LOG] - {timestamp} - Main Loop: Agent Response:\n{response}")
                else:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[WARNING] - {timestamp} - Unexpected response type from agent.")

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[DEBUG] - {timestamp} - [STEP END] - Checking for 'indefinitely' keyword.")

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP END] - Exited main loop.")

    except Exception as e:
        handle_error(e, "main()")

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [END] - main() function complete.")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [FUNCTION END] - main()")


if __name__ == "__main__":
    main()