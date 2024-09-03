### START OF FILE llm_setup.py ###

from langchain_openai import OpenAI
import datetime
from error_handler import handle_error  # Import error handler

llm = None  # Global llm object 

def get_llm():
    global llm
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[LOG] - {timestamp} - Setting up connection to LM Studio...")
    try:
        llm = OpenAI(
            base_url="http://localhost:1234/v1",
            api_key="lm-studio",  # Replace with your actual LM Studio API key
            temperature=1,
            max_tokens=500,
            model_kwargs={
                "stop": ["<-stop->","\n    Observation","\nObservation" ],
                "seed": 50
            }
        )
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[LOG] - {timestamp} - LM Studio connection established.")
        return llm
    except Exception as e:
        handle_error(e, "get_llm()")  # Use handle_error() here
        return None

### END OF FILE llm_setup.py ###