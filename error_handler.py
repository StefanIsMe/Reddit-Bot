### START OF FILE error_handler.py ###
import datetime

def handle_error(error, location, additional_context=None):
    """
    Logs errors to the console with timestamps, location, and optional context. 

    Args:
        error (Exception): The exception object.
        location (str): The function name or code block where the error occurred.
        additional_context (dict, optional): A dictionary of additional information 
                                             (e.g., variable values) to include in the log.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[ERROR] - {timestamp} - {location} - {error}"

    if additional_context:
        log_message += f"\nAdditional Context: {additional_context}"

    print(log_message)
### END OF FILE FILE error_handler.py ###