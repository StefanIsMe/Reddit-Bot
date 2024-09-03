### START OF FILE tools/llm_tasks.py ###

#tools\llm_tasks.py
import datetime
from error_handler import handle_error
from llm_setup import get_llm  # Import get_llm for LLM access

def quit_current_task(unused_arg=None):
    """
    Function to signal the agent to quit the current task.
    It can take an unused argument to be compatible with LangChain tools.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[LOG] - {timestamp} - quit_current_task: Quitting current task...")
    return "Quitting the current task." # Return a signal message

def display_text(message):
    """Displays a text message to the user."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[LOG] - {timestamp} - display_text: Displaying message: {message}")
    try:
        print(message)
        return "I have displayed the message."
    except Exception as e:
        handle_error(e, "display_text()", {"message": message})
        return "Error: Could not display the message."

def get_user_input(prompt):
    """
    Displays a prompt to the user and returns their input, adding a
    dummy "Action" line for the agent if needed.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[LOG] - {timestamp} - get_user_input: Prompt: {prompt}")
    try:
        user_input = input(prompt)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[LOG] - {timestamp} - get_user_input: User Input: {user_input}")
        return f"Action: Get User Input\n{user_input}"  # Add "Action: Get User Input" line
    except Exception as e:
        handle_error(e, "get_user_input()", {"prompt": prompt})
        return "Error: Could not get user input."

def confirm_element_with_llm(llm, driver, element_information, element_text, element_description, user_instructions=None):
    """
    Asks the LLM to confirm if the given element is likely the
    specified element type, providing context from user instructions.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[LOG] - {timestamp} - confirm_element_with_llm: Confirming element with LLM...")

    try:
        if user_instructions:
            prompt = f"""
            Original Instructions: {user_instructions}

            You will be presented with a series of elements.
            Your task is to identify the element that best matches the original instructions. 

            Is the following element suitable? 
            {element_information} 

            Answer "YES" or "NO".
            """
        else:
            prompt = f"""
            You will be presented with a series of elements.
            Your task is to identify the element that best matches the description. 

            Is the following element a '{element_description}'?
            {element_information} 

            Answer "YES" or "NO".
            """

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[LOG] - {timestamp} - confirm_element_with_llm: Sending prompt to LLM: \n{prompt}")

        completion = llm.generate(prompts=[prompt], max_tokens=10)
        response = completion.generations[0][0].text.strip().upper()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[LOG] - {timestamp} - confirm_element_with_llm: LLM Response: {response}")

        if response == "YES":
            while True:  # Loop until valid input
                user_confirm = input(
                    "LLM thinks this is the right element. Do you agree? (yes/no): ")
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[DEBUG] - {timestamp} - User confirmation for element: {user_confirm}")
                if user_confirm.lower() == 'yes':
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[LOG] - {timestamp} - confirm_element_with_llm: User and LLM agreed.")
                    return True
                elif user_confirm.lower() == 'no':
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(
                        f"[LOG] - {timestamp} - confirm_element_with_llm: User disagreed with LLM. Continuing to search...")
                    return False
                else:  # Invalid input
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[WARNING] - {timestamp} - Invalid input. Please enter 'yes' or 'no'.")
        else:  # LLM said "NO"
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[LOG] - {timestamp} - confirm_element_with_llm: LLM disagreed.")
            return False

    except Exception as e:
        handle_error(e, "confirm_element_with_llm()", {"element_information": element_information, 
                                                     "element_text": element_text, 
                                                     "element_description": element_description})
        return False


def extract_label(element):
    """
    Attempts to extract a descriptive label for a text field from HTML.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[LOG] - {timestamp} - extract_label: Attempting to extract label...")

    try:
        label = None

        # 1. Check for associated <label> element
        if element.label:
            label = element.label.text.strip()

        # 2. Check for placeholder text
        if not label and element.get('placeholder'):
            label = element.get('placeholder').strip()

        # 3. Check for parent element text
        if not label:
            parent_text = element.parent.text.strip()
            if parent_text:
                label = parent_text

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[LOG] - {timestamp} - extract_label: Extracted label: {label}")
        return label

    except Exception as e:
        handle_error(e, "extract_label()", {"element": element})
        return None

### END OF FILE tools/llm_tasks.py ###