### START OF FILE tools/writing.py ###
import re
from database.writing_assistant_management import get_prompt_template, list_all_templates, create_prompt_template
from error_handler import handle_error
import datetime

def writing_assistant(llm, user_input, context=None):
    """
    Assists users with writing tasks, using templates and context.
    Auto-approves content when context is provided.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[LOG] - {timestamp} - writing_assistant: Starting writing assistant...")
    print(f"[LOG] - {timestamp} - writing_assistant: Received user_input: {user_input}")
    print(f"[LOG] - {timestamp} - writing_assistant: Received context: {context}")

    task_history = []
    versions = [""]
    current_version = 0

    # Extract template_name from user_input
    template_name_match = re.search(r"(?<=Writing Assistant\s).*", user_input)
    template_name = template_name_match.group(0).strip() if template_name_match else None
    print(f"[LOG] - {timestamp} - writing_assistant: Extracted template_name: {template_name}")

    try:
        # Handle template_name argument
        if template_name:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[LOG] - {timestamp} - Received template_name: {template_name}")

            if not isinstance(template_name, str):
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[ERROR] - {timestamp} - Invalid template_name: {template_name}. Must be a string.")
                raise ValueError("Invalid template_name. Must be a string.")

            # Use the provided template_name
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[LOG] - {timestamp} - Using template: {template_name}")
            template_content = get_prompt_template(template_name)

            if template_content:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[LOG] - {timestamp} - Template content: {template_content}")

                # Construct the prompt using the template
                prompt = f"""
                {template_content}

                Please provide the resulting content based on the above task.
                **Only** use the following format for your response:

                RESPONSE_START
                [The generated or edited content goes here]
                RESPONSE_END
                """

                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[LOG] - {timestamp} - Prompt being sent to LLM: {prompt}")
                response = llm(prompt)
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[LOG] - {timestamp} - writing_assistant: Received response from LLM.")

                try:
                    content_start = response.index("RESPONSE_START") + len("RESPONSE_START")
                    content_end = response.index("RESPONSE_END")
                    response = response[content_start:content_end].strip()
                except ValueError as e:
                    handle_error(e, "writing_assistant() - Extracting content from LLM response.")
                    return None

                response = re.sub(r"```", "", response)
                response = re.sub(r"\n\s*\n", "\n", response)
                response = response.strip()

                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[LOG] - {timestamp} - Generated content:\n{response}")

                # Auto-Approve the content
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[LOG] - {timestamp} - Auto-approving content due to template usage.")
                return response  # Return the generated text

            else:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[WARNING] - {timestamp} - Template '{template_name}' not found.")
                return None

        # --- No template_name provided, handle template selection ---
        else:
            # --- Check if context is provided ---
            if context:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[LOG] - {timestamp} - Context provided, using it directly as prompt...")
                prompt = f"""
                {context}

                **Important** 
                - Only respond in natural language.
                - Do not respond with programming language or code.
                - Only write the comment in English.
                - Do not repeat more than once RESPONSE_START and or RESPONSE_END.

                The following is the format of how you must Respond. You should respond with ONLY the comment text in the following format. In your response, 
                begin "RESPONSE_START" and finish with "RESPONSE_END":

                RESPONSE_START
                [Your comment goes here]
                RESPONSE_END 
                <-stop->
                """  # More explicit prompt with output markers

                # Send the prompt to the LLM
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[LOG] - {timestamp} - Prompt being sent to LLM: {prompt}")
                response = llm(prompt,max_tokens=400,stop='<-stop->')
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[LOG] - {timestamp} - writing_assistant: Received response from LLM.")

                try:
                    content_start = response.index("RESPONSE_START") + len("RESPONSE_START")
                    content_end = response.index("RESPONSE_END")
                    response = response[content_start:content_end].strip()
                except ValueError as e:
                    handle_error(e, "writing_assistant() - Extracting content from LLM response.")
                    return None

                # --- Auto-approve the response ---
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[LOG] - {timestamp} - Auto-approving content because context was provided: \n{response}")
                return response

            # --- If no context is provided, proceed with template selection ---
            else:
                while True:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[LOG] - {timestamp} - Available prompt templates:")
                    list_all_templates()

                    template_choice = input(
                        "Enter template name to use (latest version will be used), 'new' to create a template, or 'none' to proceed without a template: "
                    ).lower()
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[DEBUG] - {timestamp} - User input for template choice: {template_choice}")

                    if template_choice == 'none':
                        template_name = None
                        break
                    elif template_choice == 'new':
                        new_template_name = input("Enter a name for the new template: ")
                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print(f"[DEBUG] - {timestamp} - User input for new template name: {new_template_name}")
                        new_template_content = input(
                            "Enter the prompt template (replace the task with {user_request}): ")
                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print(f"[DEBUG] - {timestamp} - User input for new template content: {new_template_content}")
                        create_prompt_template(new_template_name, new_template_content)
                        template_name = new_template_name  # Use the newly created template
                    else:
                        template_name = template_choice  # Try to use the entered template name

                    if template_name:
                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print(f"[LOG] - {timestamp} - Using template: {template_name}")
                        template_content = get_prompt_template(template_name)
                        if template_content:
                            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            print(f"[LOG] - {timestamp} - Template content: {template_content}")
                            break  # Exit the loop if a valid template is found
                        else:
                            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            print(f"[WARNING] - {timestamp} - Template '{template_name}' not found.")

                # --- Writing Assistant Loop ---
                while True:
                    if template_name:
                        prompt = f"""
                        {template_content}  # Use the template content

                        Please provide the resulting content based on the above task.
                        Use the following format for your response:

                        CONTENT_START
                        [The generated or edited content goes here]
                        CONTENT_END  <|eot_id|>
                        """
                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print(f"[LOG] - {timestamp} - Prompt being sent to LLM: {prompt}")
                        response = llm(prompt)
                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print(f"[LOG] - {timestamp} - writing_assistant: Received response from LLM.")

                        try:
                            content_start = response.index("CONTENT_START") + len("CONTENT_START")
                            content_end = response.index("CONTENT_END")
                            response = response[content_start:content_end].strip()
                        except ValueError as e:
                            handle_error(e, "writing_assistant() - Extracting content from LLM response.")
                            return None

                        response = re.sub(r"```", "", response)
                        response = re.sub(r"\n\s*\n", "\n", response)
                        response = response.strip()

                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print(f"[LOG] - {timestamp} - Generated content:\n{response}")

                        # Auto-Approve the content
                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print(f"[LOG] - {timestamp} - Auto-approving content due to template usage.")
                        return response  # Return the generated text
                    else:
                        user_request = input("What do you need help writing?: ")
                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print(f"[DEBUG] - {timestamp} - User input for writing request: {user_request}")
                        prompt = f"""
                        Task: {user_request}

                        Please provide the resulting content based on the above task.
                        Use the following format for your response:

                        CONTENT_START
                        [The generated or edited content goes here]
                        CONTENT_END <|eot_id|>
                        """

                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[LOG] - {timestamp} - Prompt being sent to LLM: {prompt}")
                    response = llm(prompt)
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[LOG] - {timestamp} - writing_assistant: Received response from LLM.")

                    try:
                        content_start = response.index("CONTENT_START") + len("CONTENT_START")
                        content_end = response.index("CONTENT_END")
                        response = response[content_start:content_end].strip()
                    except ValueError as e:
                        handle_error(e, "writing_assistant() - Extracting content from LLM response.")
                        continue

                    response = re.sub(r"```", "", response)
                    response = re.sub(r"\n\s*\n", "\n", response)
                    response = response.strip()

                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[LOG] - {timestamp} - Generated content:\n{response}")

                    while True:
                        approval = input("Do you approve of this content? (yes/no/edit): ").lower()
                        if approval == 'yes':
                            current_version += 1
                            versions.append(response)
                            print(f"Content approved. Current version: {current_version + 1}")
                            return versions[current_version]
                        elif approval == 'no':
                            print("Content rejected. Please try a different prompt or template.")
                            break  # Go back to the prompt/template selection
                        elif approval == 'edit':
                            edited_content = input(f"Current version:\n{response}\n\nEdit the content: ")
                            current_version += 1
                            versions.append(edited_content)
                            print(f"Content edited. Current version: {current_version + 1}")
                            return versions[current_version]
                        else:
                            print("Invalid input. Please enter 'yes', 'no', or 'edit'.")

    except Exception as e:
        handle_error(e, "writing_assistant()")
        return None

### END OF FILE tools/writing.py ###