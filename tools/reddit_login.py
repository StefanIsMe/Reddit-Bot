### START OF FILE tools/reddit_login.py ###
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tools.browser_actions import wait_for_page_load, navigate_and_wait
import random
import time
from database.reddit_account_management import (
    save_reddit_account,
    list_all_reddit_accounts,
    create_reddit_profile_table,
    record_reddit_action,
    has_performed_action_on_post,
    update_reddit_account_status,
)
from error_handler import handle_error
import datetime
import sqlite3
from database.sqlfunctions import DATABASE_NAME
from selenium.webdriver import ActionChains
from tools.memory import (
    create_user_memory_table,
    add_memory_item,
    delete_all_memory_items,
    get_memory_item,
)
from proxy import renew_tor_identity
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def select_reddit_account_for_login(exclude_email=None):
    """
    Selects the most suitable Reddit account for login, excluding the specified email.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [FUNCTION START] - select_reddit_account_for_login()")
    print(f"[LOG] - {timestamp} - select_reddit_account_for_login: Starting... Excluding email: {exclude_email}")

    selected_account = None
    selection_reason = ""

    try:
        # --- Step 1: Connect to the database ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP START] - Connecting to the database.")
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP END] - Connected to the database.")

        # --- Step 2: Get all Reddit accounts from the database ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP START] - Get all Reddit accounts from the database.")
        accounts = list_all_reddit_accounts()
        if isinstance(accounts, str) or not accounts:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[ERROR] - {timestamp} - select_reddit_account_for_login: No Reddit accounts found or error occurred.")
            return "Error: No Reddit accounts found or error occurred. Please check the database.", None
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP END] - Got all Reddit accounts from the database.")

        # --- Step 3: Create user memory table ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP START] - Creating user memory table.")
        create_user_memory_table()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP END] - Created user memory table.")

        # --- Step 4: Filter for active accounts and get last comment times ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP START] - Filtering for active accounts and get last comment times.")
        active_accounts = []
        never_commented_accounts = []
        account_comment_times = {}
        current_time = datetime.datetime.now()
        for account in accounts:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[DEBUG] - {timestamp} - select_reddit_account_for_login: Processing account: {account['email']}")
            if account["status"] == "active":
                active_accounts.append(account)
                table_name = f"profile_{account['email'].split('@')[0].replace('.', '_')}"
                cursor.execute(f"""SELECT timestamp FROM {table_name} WHERE action_type = 'comment' ORDER BY timestamp DESC LIMIT 1""")
                last_comment_timestamp = cursor.fetchone()
                if last_comment_timestamp is None:
                    never_commented_accounts.append(account)
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[DEBUG] - {timestamp} - select_reddit_account_for_login: Account {account['email']} has never commented.")
                else:
                    last_comment_time = datetime.datetime.strptime(last_comment_timestamp[0], "%Y-%m-%d %H:%M:%S.%f")
                    account_comment_times[account["email"]] = last_comment_time
                    time_since_last_comment = current_time - last_comment_time
                    minutes, seconds = divmod(time_since_last_comment.total_seconds(), 60)
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[DEBUG] - {timestamp} - select_reddit_account_for_login: Account {account['email']} last commented {int(minutes)} minutes and {int(seconds)} seconds ago.")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP END] - Filtered for active accounts and got last comment times.")

        # --- Step 5: Account selection logic ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP START] - Account selection logic.")

        # --- 5.1: Choose a random account from never_commented_accounts if any exist ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP START] - Choosing a random account from never_commented_accounts (if any).")
        if never_commented_accounts:
            while True:
                selected_account = random.choice(never_commented_accounts)
                # --- Check if the selected account is the excluded one ---
                if exclude_email and selected_account["email"] == exclude_email:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[WARNING] - {timestamp} - select_reddit_account_for_login: Tried to select excluded account {exclude_email}. Choosing another...")
                    continue 
                else:
                    selection_reason = f"Account {selected_account['email']} has never commented before."
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[DEBUG] - {timestamp} - select_reddit_account_for_login: Selected account: {selected_account['email']}. Reason: {selection_reason}")
                    break
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP END] - Chose a random account from never_commented_accounts.")

        # --- 5.2: Choose account with comment older than 10 minutes and 1 second ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP START] - Choosing account with comment older than 10 minutes and 1 second (if any).")
        if selected_account is None:  # Only proceed if no account has been selected yet
            for email, last_comment_time in account_comment_times.items():
                time_since_last_comment = current_time - last_comment_time
                minutes, seconds = divmod(time_since_last_comment.total_seconds(), 60)
                if minutes >= 10 and seconds >= 1:
                    for account in active_accounts:
                        # --- Check if the selected account is the excluded one ---
                        if exclude_email and account["email"] == exclude_email:
                            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            print(f"[WARNING] - {timestamp} - select_reddit_account_for_login: Tried to select excluded account {exclude_email}. Choosing another...")
                            continue
                        if account["email"] == email:
                            selected_account = account
                            selection_reason = f"Account {selected_account['email']} last commented more than 10 minutes ago."
                            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            print(f"[DEBUG] - {timestamp} - select_reddit_account_for_login: Selected account: {selected_account['email']}. Reason: {selection_reason}")
                            break
                if selected_account:
                    break  # Exit the outer loop if an account is already selected
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP END] - Chose account with comment older than 10 minutes and 1 second.")

        # --- 5.3: Choose the account that commented the longest time ago ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP START] - Choosing the account that commented the longest time ago (if any).")
        if selected_account is None:
            sorted_accounts = sorted(account_comment_times.items(), key=lambda item: item[1])
            if sorted_accounts:
                oldest_commented_email = sorted_accounts[0][0]
                for account in active_accounts:
                    # --- Check if the selected account is the excluded one ---
                    if exclude_email and account["email"] == exclude_email:
                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print(f"[WARNING] - {timestamp} - select_reddit_account_for_login: Tried to select excluded account {exclude_email}. Choosing another...")
                        continue
                    if account["email"] == oldest_commented_email:
                        selected_account = account
                        selection_reason = (
                            f"Account {selected_account['email']} has the oldest comment time among all active accounts."
                        )
                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print(f"[DEBUG] - {timestamp} - select_reddit_account_for_login: Selected account: {selected_account['email']}. Reason: {selection_reason}")
                        break
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP END] - Chose the account that commented the longest time ago.")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP END] - Account selection logic.")

        # --- Step 6: Handle cases where no suitable account is found ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP START] - Handling cases where no suitable account is found.")
        if selected_account is None:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[WARNING] - {timestamp} - select_reddit_account_for_login: No suitable Reddit account found.")
            return "Error: No suitable Reddit account found. Please create or activate an account.", None
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP END] - Handled cases where no suitable account is found.")

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [FUNCTION END] - select_reddit_account_for_login()")
        return selected_account, selection_reason

    except Exception as e:
        handle_error(e, "select_reddit_account_for_login()")
        return "Error: An unexpected error occurred while selecting a Reddit account.", None

def perform_reddit_login(driver):
    """
    Logs into Reddit, handling security challenges, and account protection.
    Uses navigate_and_wait for URL loading.
    Limits login attempts per account and prevents selecting the same account repeatedly.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [FUNCTION START] - perform_reddit_login()")
    print(f"[LOG] - {timestamp} - perform_reddit_login: Starting...")

    try:
        # --- Select Reddit account for login ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP START] - Selecting a reddit account for login...")
        selected_account, selection_reason = select_reddit_account_for_login()
        if "Error" in selected_account:
            return selected_account, None
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP END] - Selected a reddit account for login...")

        # --- Step 7: Login using the selected account (with looping, debugging, timeout, and attempt limit) ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP START] - Attempting to login with the selected account...")
        max_login_attempts_per_account = 5
        login_attempts = 0
        previous_account_email = None 

        while True:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[DEBUG] - {timestamp} - [STEP START] - Login using the selected account.")
            email = selected_account["email"]
            password = selected_account["password"]

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[DEBUG] - {timestamp} - Navigating to login page...")
            navigate_and_wait(driver, "https://www.reddit.com/login/") 

            # --- Find elements and click login only AFTER page load ---
            try:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[DEBUG] - {timestamp} - Finding email input element...")
                email_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='login-username']")))
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[DEBUG] - {timestamp} - Entering email...")
                email_input.send_keys(email)

                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[DEBUG] - {timestamp} - Finding password input element...")
                password_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='login-password']")))
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[DEBUG] - {timestamp} - Entering password...")
                password_input.send_keys(password)
                time.sleep(0.5)

                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[DEBUG] - {timestamp} - Finding login button...")
                login_button_selector = 'return document.querySelector("body > shreddit-app > shreddit-overlay-display").shadowRoot.querySelector("shreddit-signup-drawer").shadowRoot.querySelector("shreddit-drawer > div > shreddit-async-loader > div > shreddit-slotter").shadowRoot.querySelector("#login > auth-flow-modal > div.w-100 > faceplate-tracker")'
                login_button = driver.execute_script(login_button_selector)
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[DEBUG] - {timestamp} - Clicking login button...")
                login_button.click()

                # --- Step 7.1: Check for Login Success within 10 seconds ---
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[DEBUG] - {timestamp} - Checking for login success (URL)...")
                start_time = time.time()
                while time.time() - start_time < 10:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[DEBUG] - {timestamp} - Current URL: {driver.current_url}")
                    if "login" not in driver.current_url:
                        wait_for_page_load(driver)
                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print(f"[DEBUG] - {timestamp} - [STEP END] - Logged in using the selected account.")
                        break
                    time.sleep(0.5)

                # --- Step 7.2: Handle Login Error (after 10 seconds) ---
                if "login" in driver.current_url:
                    login_attempts += 1
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[WARNING] - {timestamp} - perform_reddit_login: Potential login error detected. Attempt {login_attempts} of {max_login_attempts_per_account}.")

                    if login_attempts >= max_login_attempts_per_account:
                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print(f"[WARNING] - {timestamp} - perform_reddit_login: Max login attempts reached for account {email}. Selecting a different account.")

                        while True:
                            selected_account, selection_reason = select_reddit_account_for_login(exclude_email=email)
                            if selected_account["email"] != previous_account_email:
                                break
                            else:
                                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                print(f"[WARNING] - {timestamp} - perform_reddit_login: Selected the same account again. Trying a different one...")

                        previous_account_email = selected_account["email"]
                        login_attempts = 0 

                        if "Error" in selected_account:
                            return selected_account, None
                    
                    renew_tor_identity()
                    driver.delete_all_cookies()
                    continue 
                else:
                    break 

            except TimeoutException:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[WARNING] - {timestamp} - perform_reddit_login: Could not find email input element. Deleting cookies, renewing Tor, and retrying...")
                driver.delete_all_cookies()
                renew_tor_identity()
                time.sleep(5) 
                continue 
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[DEBUG] - {timestamp} - [STEP END] - Login using the selected account.")

        # --- Step 8: Check for Account Ban ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP START] - Checking for account ban.")
        time.sleep(3) 

        if "<faceplate-banner" in driver.page_source:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[LOG] - {timestamp} - perform_reddit_login: Found <faceplate-banner> element. Checking 'msg' property...")
            banner_element = driver.find_element(By.TAG_NAME, "faceplate-banner")
            msg_attribute = banner_element.get_attribute("msg")

            if msg_attribute == "This account has been permanently banned. Check your inbox for a message with more information.":
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[WARNING] - {timestamp} - perform_reddit_login: Account '{email}' is banned!")
                update_reddit_account_status(email, "banned")
                return "Error: The Reddit account I attempted to log in to has been banned. Now I will log out of Reddit.", None
            else:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[LOG] - {timestamp} - perform_reddit_login: Account does not appear to be banned.")
        else:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[LOG] - {timestamp} - perform_reddit_login: No <faceplate-banner> element found. Account is likely not banned.")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP END] - Checked for account ban.")

        # --- Step 9: Store username in memory ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP START] - Storing username in memory.")
        add_memory_item("logged_in_user", email)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP END] - Stored username in memory.")

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[LOG] - {timestamp} - perform_reddit_login: Successfully logged in to Reddit. Using account: {email}. {selection_reason}")
        print(f"[DEBUG] - {timestamp} - [FUNCTION END] - perform_reddit_login()")
        return f"Successfully logged in to Reddit. Username: {email}. {selection_reason}", email

    except Exception as e:
        handle_error(e, "perform_reddit_login()")
        return "An unexpected error occurred during login.", None

### END OF FILE tools/reddit_login.py ### 