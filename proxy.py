### START OF FILE proxy.py ###

import subprocess
import os
import time
import datetime
from database.proxy_management import get_unused_proxy, add_used_proxy, mark_proxy_as_dead, is_proxy_used
from error_handler import handle_error
import stem.control 


def renew_tor_identity():
    """Renews the Tor circuit (changes the IP address)."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[LOG] - {timestamp} - renew_tor_identity: Renewing Tor identity...")
    try:
        with stem.control.Controller.from_port(port=9051) as controller:
            controller.authenticate()
            controller.signal(stem.Signal.NEWNYM)
            print(f"[LOG] - {timestamp} - renew_tor_identity: Finished sending signal to renew Tor identity.")
            print(f"[LOG] - {timestamp} - renew_tor_identity: Waiting 10 seconds for new signal to complete.")
            time.sleep(10)
            print(f"[LOG] - {timestamp} - renew_tor_identity: Finished 10 seconds for new signal to complete.")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[LOG] - {timestamp} - renew_tor_identity: Tor identity renewed.")
    except Exception as e:
        handle_error(e, "renew_tor_identity()")

TOR_PATH = r"D:\projects\AIAv2\tor\tor\tor.exe"  # Path to your tor.exe
TOR_CONTROL_PORT = 9051
TOR_SOCKS_PORT = 9050
TORRC_PATH = "torrc"  # Path to your torrc configuration file 

def start_tor():
    """
    Starts the Tor process.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [FUNCTION START] - start_tor()")
    print(f"[LOG] - {timestamp} - start_tor: Starting Tor process...")

    # --- Step 1: Create torrc if it doesn't exist ---
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [STEP START] - Create torrc if it doesn't exist")
    if not os.path.exists(TORRC_PATH):
        with open(TORRC_PATH, 'w') as f:
            f.write(f"SocksPort {TOR_SOCKS_PORT}\n")
            f.write(f"ControlPort {TOR_CONTROL_PORT}\n")
            # Add other Tor configurations as needed
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [STEP END] - Create torrc if it doesn't exist")

    # --- Step 2: Start Tor process ---
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [STEP START] - Start Tor process")
    try:
        tor_process = subprocess.Popen([TOR_PATH, "-f", TORRC_PATH])
        time.sleep(15)  # Give Tor time to start
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[LOG] - {timestamp} - start_tor: Tor process started successfully.")
        print(f"[DEBUG] - {timestamp} - [STEP END] - Start Tor process")
        print(f"[DEBUG] - {timestamp} - [FUNCTION END] - start_tor()")
        return tor_process 
    except Exception as e:
        handle_error(e, "start_tor()", {"TOR_PATH": TOR_PATH, "TORRC_PATH": TORRC_PATH})
        print(f"[DEBUG] - {timestamp} - [FUNCTION END] - start_tor()")
        return None

def stop_tor(tor_process):
    """
    Stops the Tor process.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [FUNCTION START] - stop_tor()")
    print(f"[LOG] - {timestamp} - stop_tor: Stopping Tor process...")
    try:
        tor_process.terminate()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[LOG] - {timestamp} - stop_tor: Tor process stopped.")
        print(f"[DEBUG] - {timestamp} - [FUNCTION END] - stop_tor()")
    except Exception as e:
        handle_error(e, "stop_tor()")
        print(f"[DEBUG] - {timestamp} - [FUNCTION END] - stop_tor()")

def load_proxy(driver=None):
    """
    Loads a proxy, always using Tor. 
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [FUNCTION START] - load_proxy()")
    print(f"[LOG] - {timestamp} - load_proxy: Loading proxy (Tor)...")
    
    global tor_process # Declare tor_process as global

    # --- Step 1: Start Tor if not running ---
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [STEP START] - Start Tor if not running")
    if not tor_process:
        tor_process = start_tor() 
        if not tor_process:
            return "Error: Could not start Tor process."
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [STEP END] - Start Tor if not running")
    
    proxy = f"socks5://127.0.0.1:{TOR_SOCKS_PORT}"  # Tor SOCKS5 proxy

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[LOG] - {timestamp} - load_proxy: Returning proxy: {proxy}")
    print(f"[DEBUG] - {timestamp} - [FUNCTION END] - load_proxy()")
    return proxy

def disconnect_proxy(driver):
    """
    Disconnects the current proxy by resetting the proxy settings 
    in the WebDriver and stops the Tor process.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [FUNCTION START] - disconnect_proxy()")
    print(f"[LOG] - {timestamp} - disconnect_proxy: Disconnecting proxy...")

    # --- Step 1: Reset WebDriver Proxy Settings ---
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [STEP START] - Reset WebDriver Proxy Settings")
    try:
        webdriver.DesiredCapabilities.CHROME['proxy'] = {}
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[LOG] - {timestamp} - disconnect_proxy: Proxy disconnected successfully.")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP END] - Reset WebDriver Proxy Settings")
    except Exception as e:
        handle_error(e, "disconnect_proxy()")

    # --- Step 2: Stop Tor Process ---
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [STEP START] - Stop Tor Process")
    global tor_process 
    if tor_process:
        stop_tor(tor_process)
        tor_process = None # Reset the tor_process variable
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [STEP END] - Stop Tor Process")

    print(f"[DEBUG] - {timestamp} - [FUNCTION END] - disconnect_proxy()")

tor_process = None # Initialize tor_process globally 

### END OF FILE proxy.py ###