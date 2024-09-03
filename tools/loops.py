from tools.reddit_login import *
from tools.reddit_actions import *
from browser_setup import initialize_browser
from proxy import renew_tor_identity
import time
import datetime
from error_handler import handle_error

def run_reddit_tasks_indefinitely(search_query, llm):
    """
    Runs the specified Reddit tasks indefinitely in a loop:
    1. Logs into Reddit.
    2. Performs a Reddit search.
    3. Browses search results.
    4. Generates and posts a comment.
    5. Logs out of Reddit.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[LOG] - {timestamp} - run_reddit_tasks_indefinitely: Starting indefinite task loop...")

    while True:
        try:
            # --- Renew Tor Identity ---
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[LOG] - {timestamp} - run_reddit_tasks_indefinitely: Renewing Tor identity...")
            renew_tor_identity()
            time.sleep(5)

            # --- Initialize Browser ---
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[LOG] - {timestamp} - run_reddit_tasks_indefinitely: Initializing browser...")
            driver = initialize_browser()
            if driver is None:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(
                    f"[ERROR] - {timestamp} - run_reddit_tasks_indefinitely: Failed to initialize browser. Skipping iteration.")
                time.sleep(10)
                continue

            # --- 1. Perform Reddit Login ---
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[LOG] - {timestamp} - run_reddit_tasks_indefinitely: Attempting Reddit login...")
            login_result, username = perform_reddit_login(driver)
            print(f"[DEBUG] - {timestamp} - run_reddit_tasks_indefinitely: Login Result: {login_result}")

            if "Error" in login_result:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[ERROR] - {timestamp} - run_reddit_tasks_indefinitely:  {login_result}")
                continue

            # --- 2. Execute Reddit Search ---
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[LOG] - {timestamp} - run_reddit_tasks_indefinitely: Executing Reddit search...")
            search_result = execute_reddit_search(driver, search_query)
            print(f"[DEBUG] - {timestamp} - run_reddit_tasks_indefinitely: Search Result: {search_result}")

            if "Error" in search_result:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[ERROR] - {timestamp} - run_reddit_tasks_indefinitely:  {search_result}")
                continue

            # --- 3. Browse Search Results ---
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[LOG] - {timestamp} - run_reddit_tasks_indefinitely: Browsing search results...")
            browse_result = browse_reddit_search_results(driver, llm, search_query)  # Pass search_query
            print(f"[DEBUG] - {timestamp} - run_reddit_tasks_indefinitely: Browse Result: {browse_result}")

            if "Error" in browse_result or "No Reddit posts" in browse_result:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[ERROR] - {timestamp} - run_reddit_tasks_indefinitely: {browse_result}")
                continue

            # --- 4. Generate and Post Comment ---
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[LOG] - {timestamp} - run_reddit_tasks_indefinitely: Generating and posting comment...")
            comment_result = generate_and_post_reddit_reply(driver, llm)
            print(f"[DEBUG] - {timestamp} - run_reddit_tasks_indefinitely: Comment Result: {comment_result}")

            if "Error" in comment_result:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[ERROR] - {timestamp} - run_reddit_tasks_indefinitely:  {comment_result}")
                continue

            # --- 5. Logout of Reddit ---
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[LOG] - {timestamp} - run_reddit_tasks_indefinitely: Logging out of Reddit...")
            logout_result = logout_reddit(driver)
            print(f"[DEBUG] - {timestamp} - run_reddit_tasks_indefinitely: Logout Result: {logout_result}")

            if "Error" in logout_result:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[ERROR] - {timestamp} - run_reddit_tasks_indefinitely:  {logout_result}")
                continue

        except Exception as e:
            handle_error(e, "run_reddit_tasks_indefinitely")
        finally:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[LOG] - {timestamp} - run_reddit_tasks_indefinitely: Quitting browser...")
            if driver:
                driver.quit()