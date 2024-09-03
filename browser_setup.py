### START OF FILE browser_setup.py ###

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import random
import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from error_handler import handle_error
from proxy import load_proxy, disconnect_proxy

def initialize_browser():
    """
    Initializes a Chrome web browser with specific configurations, using Tor as a proxy
    managed by the proxy.py script. 
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [FUNCTION START] - initialize_browser()")
    print(f"[LOG] - {timestamp} - initialize_browser: Starting browser initialization...")

    try:
        # --- Step 1: Get Proxy from proxy.py ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP START] - Get Proxy from proxy.py")
        proxy = load_proxy()  # Get proxy from proxy.py
        if "Error" in proxy:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[ERROR] - {timestamp} - initialize_browser: {proxy}")
            handle_error(proxy, "initialize_browser() - load_proxy()")
            return None  
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP END] - Get Proxy from proxy.py")

        # --- Step 2: Set up Chrome options with Proxy ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP START] - Set up Chrome options with Proxy")
        options = Options()
        options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        options.add_argument(f'--proxy-server={proxy}') # Apply the proxy from proxy.py

        # --- Set a random window size above 720p ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP START] - Setting a random window size...")
        width = random.randint(1280, 1920)
        height = random.randint(720, 1080)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP END] - Setting up Chrome options with Proxy")

        # --- Step 2: Initialize the WebDriver ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP START] - Initializing WebDriver...")
        driver = webdriver.Chrome(options=options)
        driver.set_window_size(width, height)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP END] - Initialized WebDriver...")

        # --- Step 3: Wait for the browser to fully load ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP START] - Waiting for browser to load...")
        try:
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'body'))) 
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.TAG_NAME, 'body')))  
        except TimeoutException as e:
            handle_error(e, "initialize_browser() - Waiting for page load")
            driver.quit() 
            return None
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP END] - Browser fully loaded.")

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[LOG] - {timestamp} - initialize_browser: Browser initialized successfully.")
        print(f"[DEBUG] - {timestamp} - [FUNCTION END] - initialize_browser()")
        return driver

    except WebDriverException as e:
        handle_error(e, "initialize_browser() - WebDriver Exception")
        return None

    except Exception as e:
        handle_error(e, "initialize_browser()")
        return None 

    finally:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[LOG] - {timestamp} - initialize_browser: Browser initialization complete.")

### END OF FILE browser_setup.py ###