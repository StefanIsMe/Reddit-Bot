# Langchain imports
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain_openai import OpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.agents import Tool
from tools.reddit_actions import *
from tools.reddit_login import *
from tools.loops import *
from tools.llm_tasks import quit_current_task
from llm_setup import get_llm, llm # Import the global llm object
import datetime
import re

def create_agent(llm, driver):  # Reintroduced 'driver' as it's used by your tools
    # Initialize memory once
    memory = ConversationBufferWindowMemory(k=5, memory_key="chat_history")

    # Your original tools from agent_setup.py
    tools = [
        Tool(
            name="Automate Reddit Commenting", 
            func=lambda search_query: run_reddit_tasks_indefinitely(search_query,llm), 
            description="""This tool will repeatedly perform a series of actions on Reddit: 
                           1. Logs into Reddit using an available account. 
                           2. Searches Reddit using the provided search query.
                           3. Finds a suitable post in the search results. 
                           4. Generates and posts a comment on the selected post.
                           5. Logs out of Reddit. 
                           
                           This process will repeat indefinitely, handling errors and renewing the Tor identity for each iteration.

                           When to use this tool:
                           - The user wants to automate Reddit actions (login, search, comment, logout) for an extended period. 
                           - Example: "Continuously search for Reddit posts about [topic] and leave comments."

                           Input: Provide the Reddit search query to use for each iteration.
                           """
        ),
        Tool(
                name="Make A User",
                func=lambda _: create_reddit_account(driver),
                description="Creates/Registers a new Reddit account using a temporary email, does email verification of the reddit account, and saves the credentials to the database.",
            ),
            Tool(
                name="Delete All Reddit Accounts",
                func=lambda _: delete_all_reddit_accounts(),
                description="Deletes all saved Reddit accounts from the database. This tool does not require any input.",
            ),
            Tool(
                name="List All Reddit Accounts",
                func=lambda unused_argument: list_all_reddit_accounts(
                    unused_argument
                ),
                description="Lists all Reddit accounts saved in the database. This tool does not require any meaningful input.",
            ),
            Tool(
                name="Update Reddit Account Status",
                func=lambda input_str: update_reddit_account_status(
                    input_str.split(",")[0].split("=")[1].strip(),
                    input_str.split(",")[1].split("=")[1].strip(),
                ),
                description="Updates the status of a Reddit account in the database. Provide the account email AND the new status (e.g., 'active', 'banned'), separated by a comma. For example: 'Email = example@email.com, Status = banned'.",
            ),
            
    ]

    # Get the ReAct prompt
    prompt = hub.pull("hwchase17/react")

    # Construct the ReAct agent
    agent = create_react_agent(llm, tools, prompt)

    # Create an agent executor
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True, 
        memory=memory,
        handle_parsing_errors=handle_llm_output_conflict 
    )

    return agent_executor

def handle_llm_output_conflict(error):
    """
    Handles the case where the LLM output contains both a final answer and a parsable action.
    Raises a ValueError to break the agent execution loop, but attempts to extract relevant information first. 
    """
    from llm_setup import llm
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[WARNING] - {timestamp} - handle_llm_output_conflict: Entering error handler...")
    
    # --- Extract agent's response from the error message ---
    agent_response = str(error)
    print(f"[DEBUG] - {timestamp} - handle_llm_output_conflict: Agent response: {agent_response}")

    # --- Attempt to Extract Final Answer ---
    final_answer_match = re.search(r"Final Answer:\s*(.*)", agent_response, re.DOTALL)
    if final_answer_match:
        final_answer = final_answer_match.group(1).strip()
        print(f"[DEBUG] - {timestamp} - handle_llm_output_conflict: Extracted Final Answer: {final_answer}")
    else:
        final_answer = None 
        print(f"[DEBUG] - {timestamp} - handle_llm_output_conflict: Could not extract Final Answer from response.")

    # --- Attempt to Extract Action ---
    action_match = re.search(r"Action:\s*(.*)", agent_response)
    if action_match:
        action = action_match.group(1).strip()
        print(f"[DEBUG] - {timestamp} - handle_llm_output_conflict: Extracted Action: {action}")
    else:
        action = None
        print(f"[DEBUG] - {timestamp} - handle_llm_output_conflict: Could not extract Action from response.")

    # --- Raise a ValueError with more context ---
    error_message = "LLM output conflict detected."
    if final_answer:
        error_message += f" Final Answer: '{final_answer}'"
    if action:
        error_message += f" Action: '{action}'"

    raise ValueError(error_message)


###def handle_llm_output_conflict(error):
###    """
###    Handles the case where the LLM output contains both a final answer and a parsable action.
###    Instead of reprompting, it raises an exception to break the agent execution loop.
###    """
###    from llm_setup import llm
###    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
###    print(f"[WARNING] - {timestamp} - handle_llm_output_conflict: Agent returned both final answer and action. Breaking loop.")
###
###    # --- Raise an exception to break the loop --- 
###    raise ValueError("LLM output conflict detected.") 
