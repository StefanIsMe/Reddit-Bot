# reddit_actions.py
### START OF FILE tools/reddit_actions.py ###
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
    update_reddit_account_status)  # Add imports for new functions
from error_handler import handle_error
import datetime
import string
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys  # Import Keys for new tab
from tools.writing import writing_assistant
# Import confirm_element_with_llm
from tools.llm_tasks import confirm_element_with_llm
import re
import sqlite3
from database.sqlfunctions import DATABASE_NAME
from database.reddit_account_management import enforce_action_cooldown
from selenium.webdriver import ActionChains  # Add the import here!
# Import memory functions
from tools.memory import create_user_memory_table, add_memory_item, delete_all_memory_items, get_memory_item
import urllib.parse
import itertools
import os
import os
import requests
from bs4 import BeautifulSoup
import pyperclip  # Make sure to install pyperclip: pip install pyperclip
from platform import system
from proxy import renew_tor_identity
import emoji


def logout_reddit(driver):
    """
    Logs the user out of Reddit using Selenium.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[LOG] - {timestamp} - logout_reddit: Starting logout process...")
    try:
        # --- Step 1: Click the dropdown button ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[DEBUG] - {timestamp} - [STEP START] - Clicking the dropdown button.")
        dropdown_button = WebDriverWait(
            driver,
            10).until(
            EC.element_to_be_clickable(
                (By.XPATH,
                 '/html/body/shreddit-app/reddit-header-large/reddit-header-action-items/header/nav/div[3]/div[2]/shreddit-async-loader/faceplate-dropdown-menu/faceplate-tooltip/button')))
        dropdown_button.click()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP END] - Dropdown button clicked.")

        # --- Step 2: Wait for 1 second ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP START] - Waiting for 2 second.")
        time.sleep(2)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP END] - Waited for 2 second.")

        # --- Step 3: Click the logout button ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[DEBUG] - {timestamp} - [STEP START] - Clicking the logout button.")
        logout_button = WebDriverWait(
            driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="logout-list-item"]/div/span[1]')))
        logout_button.click()
        time.sleep(1.5)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP END] - Logout button clicked.")

        # --- Step 4: Wait for the page to reload ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[DEBUG] - {timestamp} - [STEP START] - Waiting for page to reload.")
        wait_for_page_load(driver)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP END] - Page reload complete.")

        # --- Step 5: Delete all memory items for the user ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[DEBUG] - {timestamp} - [STEP START] - Deleting all memory items...")
        delete_all_memory_items()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[DEBUG] - {timestamp} - [STEP END] - All memory items deleted.")

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[LOG] - {timestamp} - logout_reddit: Successfully logged out of Reddit.")
        return "Successfully logged out of Reddit."

    except Exception as e:
        handle_error(e, "logout_reddit()")
        return "Error: Could not log out of Reddit."

def execute_reddit_search(driver, search_query):
    """
    Searches Reddit for the given query. 
    Uses regular expressions to clean the search query more reliably.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [FUNCTION START] - execute_reddit_search()")
    print(f"[LOG] - {timestamp} - execute_reddit_search: Starting...")

    # --- Robust Cleaning with Regex ---
    search_query = re.sub(r"(Observation:|Thought:|Action:|Action Input:).*", "", search_query, flags=re.IGNORECASE).strip()

    # Remove special characters from search query
    for char in "()\"'":
        search_query = search_query.replace(char, "")

    # Validate search query for unintended quotes 
    if '"' in search_query or "'" in search_query:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[WARNING] - {timestamp} - execute_reddit_search: Unintended quotes found in search query. Removing quotes.")
        search_query = search_query.replace('"', "").replace("'", "")
    
    # Construct the search URL and navigate
    try:
        search_url = f"https://www.reddit.com/search/?q={search_query}&sort=top&t=week"
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[LOG] - {timestamp} - execute_reddit_search: Searching Reddit: {search_query}")
        navigate_and_wait(driver, search_url)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[LOG] - {timestamp} - execute_reddit_search: Reddit search results loaded.")
        return "Successfully navigated to Reddit search results." 

    except Exception as e:
        handle_error(e, "execute_reddit_search()", {"search_query": search_query})
        return "Error: Could not search Reddit."


def confirm_reddit_over_18(driver):
    """
    Confirms the "over 18" warning on Reddit if it's present
    on the current page.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[LOG] - {timestamp} - confirm_reddit_over_18: Starting...")

    try:
        if "reddit.com" in driver.current_url:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(
                f"[LOG] - {timestamp} - confirm_reddit_over_18: Checking for over 18 warning...")

            over_18_warning = driver.find_element(
                By.TAG_NAME, "confirm-over-18")
            if over_18_warning:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(
                    f"[LOG] - {timestamp} - confirm_reddit_over_18: Over 18 warning found. Clicking confirmation button...")

                confirmation_button = WebDriverWait(
                    driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, "span.flex.items-center.gap-xs")))
                confirmation_button.click()
                time.sleep(0.5)
                wait_for_page_load(driver)  # Wait for the content to load
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(
                    f"[LOG] - {timestamp} - confirm_reddit_over_18: Confirmed over 18. Content should be loaded.")
                return "Confirmed over 18 on Reddit."
            else:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(
                    f"[LOG] - {timestamp} - confirm_reddit_over_18: No over 18 warning found.")
                return "No over 18 warning found on Reddit."
        else:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(
                f"[LOG] - {timestamp} - confirm_reddit_over_18: Not on a Reddit page.")
            return "Not currently on a Reddit page."

    except Exception as e:
        handle_error(e, "confirm_reddit_over_18()")
        return "Error: Could not confirm over 18 warning."


def generate_and_post_reddit_reply(driver, llm):
    """
    Posts a comment on the currently open Reddit post using the writing assistant.
    Handles cases where commenting is not possible and records the outcome.

    Args:
        driver: The Selenium WebDriver instance used to interact with the browser.
        llm: The Large Language Model instance used for generating the comment.

    Returns:
        str: A message indicating the outcome of the comment posting attempt.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(
        f"[DEBUG] - {timestamp} - [FUNCTION START] - generate_and_post_reddit_reply()")
    print(f"[LOG] - {timestamp} - generate_and_post_reddit_reply: Starting...")

    try:
        # --- Step 1: Check if on a Reddit post page ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[DEBUG] - {timestamp} - [STEP START] - Checking if on a Reddit post page.")
        if "?q=" in driver.current_url:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(
                f"[LOG] - {timestamp} - generate_and_post_reddit_reply: Not on a Reddit post page. Returning to the LLM.")
            return "For some reason, we're currently on the Reddit search results page. I'll need to perform a new Reddit search with a relevant search query based on the user instructions to find a suitable post."

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[DEBUG] - {timestamp} - [STEP END] - Checked if on a Reddit post page.")

        # --- Step 2: Click the comment box ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[DEBUG] - {timestamp} - [STEP START] - Clicking the comment box.")
        print(
            f"[LOG] - {timestamp} - generate_and_post_reddit_reply: Finding comment box element...")
        comment_box_xpath = '//*[@id="main-content"]/shreddit-async-loader/comment-body-header/shreddit-async-loader[1]/comment-composer-host/faceplate-tracker[1]/button'
        try:
            comment_box = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, comment_box_xpath))
            )
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(
                f"[LOG] - {timestamp} - generate_and_post_reddit_reply: Clicking comment box...")
            comment_box.click()
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(
                f"[LOG] - {timestamp} - generate_and_post_reddit_reply: Comment box clicked.")
        except TimeoutException:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(
                f"[ERROR] - {timestamp} - generate_and_post_reddit_reply: Could not find comment box. Commenting not possible.")
            post_url = driver.current_url  # Extract post URL
            username = get_memory_item("logged_in_user")
            record_reddit_action(
                username,
                "cannot_comment",
                post_url,
                reason="Comment box not found")  # Record failed attempt
            return "Cannot comment on this post. Comment box not found. You should go back to the search results and find a different post."
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP END] - Clicked the comment box.")

        # --- Step 3: Gather context from post title, body, media, and community ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[DEBUG] - {timestamp} - [STEP START] - Gathering context from post title, body, media, and community.")
        print(
            f"[LOG] - {timestamp} - generate_and_post_reddit_reply: Gathering post and community context...")

        # --- 3.1: Post Title ---
        post_title_xpath = '//h1'
        post_title_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, post_title_xpath))
        )
        post_title = post_title_element.text.strip()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[LOG] - {timestamp} - generate_and_post_reddit_reply: Post title: {post_title}")

        # --- 3.2: Post Body ---
        post_body_content = None
        post_body_xpath = "//div[@slot='text-body']"
        try:
            post_body_element = driver.find_element(By.XPATH, post_body_xpath)
            post_body_content = post_body_element.text.strip()
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(
                f"[LOG] - {timestamp} - generate_and_post_reddit_reply: Found post body content: {post_body_content}")
        except NoSuchElementException:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(
                f"[LOG] - {timestamp} - generate_and_post_reddit_reply: No post body content found.")

        # --- 3.3: Media Container (Link) ---
        media_container_found = False
        media_container_xpath = "//div[@slot='post-media-container']"
        media_link = None
        try:
            media_container = driver.find_element(
                By.XPATH, media_container_xpath)
            media_container_found = True
            try:
                media_link_element = media_container.find_element(
                    By.TAG_NAME, "a")
                media_link = media_link_element.get_attribute("href")
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(
                    f"[LOG] - {timestamp} - generate_and_post_reddit_reply: Found media link: {media_link}")
            except NoSuchElementException:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(
                    f"[LOG] - {timestamp} - generate_and_post_reddit_reply: No media link found. It's likely an image.")
        except NoSuchElementException:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(
                f"[LOG] - {timestamp} - generate_and_post_reddit_reply: No media container found.")

        # --- 3.4: Community Name ---
        community_name = None
        try:
            community_name_element = driver.find_element(
                By.CSS_SELECTOR, "shreddit-subreddit-header[display-name]")
            community_name = community_name_element.get_attribute(
                "display-name")
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(
                f"[LOG] - {timestamp} - generate_and_post_reddit_reply: Community name: {community_name}")
        except NoSuchElementException:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(
                f"[LOG] - {timestamp} - generate_and_post_reddit_reply: Community name not found.")

        # --- 3.5: Community Description ---
        community_description = None
        community_description_xpath = "/html/body/shreddit-app/div/div[1]/div/div/faceplate-partial/aside/div/shreddit-subreddit-header"
        try:
            community_description_element = driver.find_element(
                By.XPATH, community_description_xpath)
            community_description = community_description_element.get_attribute(
                "description")
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(
                f"[LOG] - {timestamp} - generate_and_post_reddit_reply: Community description: {community_description}")
        except NoSuchElementException:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(
                f"[LOG] - {timestamp} - generate_and_post_reddit_reply: Community description not found.")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[DEBUG] - {timestamp} - [STEP END] - Gathered context from post title, body, media, and community.")

        # --- Step 4: Call the writing assistant ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[DEBUG] - {timestamp} - [STEP START] - Calling the writing assistant.")
        print(
            f"[LOG] - {timestamp} - generate_and_post_reddit_reply: Calling writing assistant...")

        # --- Construct context for the LLM ---
        context = f"""Help me write a response to this Reddit post.

                    Post Title: '{post_title}'

                    """
        if post_body_content:
            context += f"Post Body Content: '{post_body_content}'\n\n"
            context += "This is the main text of the post, providing more details about the topic.\n\n"

        if media_container_found:
            if media_link:
                context += f"This post also contains a link to an external website: '{media_link}'\n\n"
                context += "Pay attention to the external link, as it could provide more context for your response.\n\n"
            else:
                context += "This post also includes an image, which might be relevant to the post's topic.\n\n"

        if community_name:
            context += f"Community Name: '{community_name}'\n\n"
            context += f"This post was made in the '{community_name}' subreddit. This tells you about the general topics and discussions you might find in this community.\n\n"

        if community_description:
            context += f"Community Description: '{community_description}'\n\n"
            context += f"This is a short summary of what the '{community_name}' subreddit is about. It can help you understand the context of the post and the audience you are responding to.\n\n"

        context += f"""
                    **The following is your persona and information on how you can respond**
                     In the comment you write, you can acknowledge the
                    point(s) made by the Reddit post but respond in your own way. Take on the persona
                    of 

                    **Name:**  David (or a similar common name)
                    **Age:** 38 
                    **Gender:** Male
                    **Education:** Degree in Business Management
                    **Occupation:** Owner of a small digital marketing agency 
                    **Location:**  Austin, Texas (or a city known for its entrepreneurial spirit)

                    **Personality:**
                    - **Friendly and approachable:** David is always willing to help others and share his knowledge. 
                    - **Passionate about small business:** He genuinely enjoys the challenges and rewards of running his own company.
                    - **Experienced but humble:**  He's been in the digital marketing game for a while and has learned a lot, but he doesn't boast. He acknowledges that he's still learning and growing.
                    - **Community-minded:** He believes in supporting other small business owners and contributing to the community.

                    **Writing Style:**
                    - **Casual and conversational:** Uses plain language, contractions to connect with people.
                    - **Enthusiastic and positive:**  Expresses genuine excitement about helping others and sharing his experiences.
                    - **Uses personal anecdotes:**  Illustrates his points with real-life stories from his business. 
                    - **Avoids jargon:** Explains complex marketing concepts in simple terms.
                    - **No Emojis:** Do not use emojis.
                    - **Writing Style:** Remember we are writing content for Reddit.com so please try to match the writing style for the website.
                    - **Length:** Do not write more than 3 sentences.
                    - **Always:** Acknowledge part of the Reddit post by either repeating some of the title or body content, and then tie it into the comment you write.
                    - **Reddit Writing Style:** Reddit is known for it's sarcasm, humor, mocking. So please try to incoporate this into your writing style.

                    **Objectives:**
                    - **Provide valuable advice:**  David's primary goal is to help people with their digital marketing and business questions.
                    - **Share personal experiences:**  He's open about the ups and downs of running his own business, offering relatable insights. 
                    - **Build credibility:**  He aims to establish himself as a trusted source of information in the digital marketing and entrepreneurial space.
                    - **Subtly introduce Stefan:** When relevant, he mentions Stefan as a valuable resource, highlighting his expertise.
                    - **Stefan's Social Media:** If you mention Stefan, you should always link to Stefan's social media account 'https://www.threads.net/@stefancarter66'.
                    - **When mentioning Stefan's Social Media account:** You should always talk about Stefan's account as 'stefancarter66' at Threads.net and or 'https://www.threads.net/@stefancarter66'
                    by writing the full url of Stefan's account. If you write '@stefancarter66' because it contains the @ symbol, Reddit will think your talking about an account on Reddit.com.
                    So you should either refer to Stefan's account as 'stefancarter66' at Threads.net or write the full url of Stefan's profile on threads.net.

                    **Key Strategies for Introducing Stefan:**
                    - **Contextual Relevance:** Only mention Stefan when it makes sense within the conversation, related to marketing, business growth, or specific topics he's known for. 
                    - **Natural Language:** Don't make it sound like an advertisement. Use casual language, as if you're genuinely recommending a friend.
                    - **Focus on Value:**  Highlight the benefits of following Stefan (e.g., valuable insights, helpful tips).
                    - **Variety:**  Experiment with different ways of mentioning Stefan (e.g., "I learned this from Stefan...", "A friend of mine, Stefan...", "If you're interested in [topic], check out Stefan...").

                    **Important Notes:**
                    - **Don't Overdo It:**  Avoid mentioning Stefan in every comment. It's important to strike a balance between helpfulness and promotion.
                    - **Stay Authentic:** The key is to be genuine and authentic in your interactions. People are more likely to trust and engage with someone who seems real. 
                    - **Never** refer to yourself in the third person.
                    - **Never** respond with an empty response. If not enough context has been provided to you and your not sure what to discuss, 
                    """
        print(
            f"[DEBUG] - {timestamp} - generate_and_post_reddit_reply: context: {context}")
        comment_text = writing_assistant(
            llm, "Write Reddit Comment", context=context)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[LOG] - {timestamp} - generate_and_post_reddit_reply: Writing assistant returned.")
        print(
            f"[DEBUG] - {timestamp} - generate_and_post_reddit_reply: comment_text: {comment_text}")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[DEBUG] - {timestamp} - [STEP END] - Called the writing assistant.")


        # --- Step 5: Check if comment_text is not empty ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[DEBUG] - {timestamp} - [STEP START] - Checking if comment_text is not empty.")
        if comment_text:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(
                f"[LOG] - {timestamp} - generate_and_post_reddit_reply: Generated comment: {comment_text}")
        else:
            return "The writing assistant could not generate a comment. Returning to the LLM to try a different post."
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[DEBUG] - {timestamp} - [STEP END] - Checked if comment_text is not empty.")

        # --- Step 6: Clean up comment text (remove extra newlines) ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[DEBUG] - {timestamp} - [STEP START] - Cleaning up comment text.")
        comment_text = re.sub(r"\n+", "\n", comment_text)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[LOG] - {timestamp} - generate_and_post_reddit_reply: Cleaned comment: {comment_text}")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] - {timestamp} - [STEP END] - Cleaned up comment text.")

        # --- Step 7: Enter the comment text ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[DEBUG] - {timestamp} - [STEP START] - Entering the comment text.")
        print(
            f"[LOG] - {timestamp} - generate_and_post_reddit_reply: Finding comment input element...")
        comment_input_xpath = '//*[@id="main-content"]/shreddit-async-loader/comment-body-header/shreddit-async-loader[1]/comment-composer-host/faceplate-form/shreddit-composer/div/p'
        comment_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, comment_input_xpath))
        )
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[LOG] - {timestamp} - generate_and_post_reddit_reply: Entering comment text...")
        comment_input.send_keys(comment_text)
        time.sleep(0.5)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[LOG] - {timestamp} - generate_and_post_reddit_reply: Comment text entered.")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[DEBUG] - {timestamp} - [STEP END] - Entered the comment text.")

        # --- Step 8: Click the "Comment" button ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[DEBUG] - {timestamp} - [STEP START] - Clicking the comment button.")
        print(
            f"[LOG] - {timestamp} - generate_and_post_reddit_reply: Finding 'Comment' button...")
        comment_button_xpath = '//*[@id="main-content"]/shreddit-async-loader/comment-body-header/shreddit-async-loader[1]/comment-composer-host/faceplate-form/shreddit-composer/button[2]/span/span/span/span[1]'
        try:
            comment_button = driver.find_element(
                By.XPATH, comment_button_xpath)
            comment_button.click()
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(
                f"[LOG] - {timestamp} - generate_and_post_reddit_reply: 'Comment' button clicked.")
        except (NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException) as e:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(
                f"[ERROR] - {timestamp} - generate_and_post_reddit_reply: Could not click 'Comment' button.")
            post_url = driver.current_url  # Extract post URL
            username = get_memory_item("logged_in_user")
            record_reddit_action(
                username,
                "comment",
                post_url,
                comment_text,
                "Respond to Reddit post")
            return """Error: Could not post comment. The 'Comment' button is not available.
                    I will try again by performing another reddit search with a suitable search query."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[DEBUG] - {timestamp} - [STEP END] - Clicked the comment button.")

        # --- Step 9: Check for successful comment posting using JavaScript --- 
        comment_box_selector = 'document.querySelector("#main-content > shreddit-async-loader > comment-body-header > shreddit-async-loader:nth-child(1) > comment-composer-host > faceplate-form > shreddit-composer > div > p")'
        comment_posted = False
        start_time = time.time()
        timeout = 20  

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[LOG] - {timestamp} - generate_and_post_reddit_reply: Checking for successful comment posting using JavaScript...")

        while time.time() - start_time < timeout:
            comment_box_text = driver.execute_script(f"return {comment_box_selector}.innerText;").strip()
            if comment_box_text == "":
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[LOG] - {timestamp} - generate_and_post_reddit_reply: Comment posted successfully!")
                comment_posted = True
                break
            else:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[DEBUG] - {timestamp} - generate_and_post_reddit_reply: Comment still present in comment box. Waiting...")
            time.sleep(0.5)  # Check every 500 milliseconds

        if not comment_posted:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[ERROR] - {timestamp} - generate_and_post_reddit_reply: Comment posting failed (timeout).") 

        # --- Step 10: Record the Reddit Action ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[DEBUG] - {timestamp} - [STEP START] - Recording the Reddit Action.")
        post_url = driver.current_url
        username = get_memory_item("logged_in_user")
        print(
            f"[DEBUG] - {timestamp} - generate_and_post_reddit_reply: username: {username}")
        print(
            f"[DEBUG] - {timestamp} - generate_and_post_reddit_reply: post_url: {post_url}")
        print(
            f"[DEBUG] - {timestamp} - generate_and_post_reddit_reply: comment_text: {comment_text}")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[LOG] - {timestamp} - generate_and_post_reddit_reply: Recording comment action...")
        record_reddit_action(
            username,
            'comment',
            post_url,
            comment_text,
            "Respond to Reddit post")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[LOG] - {timestamp} - generate_and_post_reddit_reply: Comment action recorded.")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[DEBUG] - {timestamp} - [STEP END] - Recorded the Reddit Action.")

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[DEBUG] - {timestamp} - [FUNCTION END] - generate_and_post_reddit_reply()")
        return "Successfully posted comment on Reddit."

    except Exception as e:
        handle_error(e, "generate_and_post_reddit_reply()")
        return "Error: Could not post comment on Reddit."

def browse_reddit_search_results(driver, llm, search_query):  # Add search_query as argument
    """
    Browses Reddit search results and navigates to the first suitable post for commenting.
    Checks if the user is logged in and if the post has a title with at least 5 characters.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [FUNCTION START] - browse_reddit_search_results()")
    print(f"[LOG] - {timestamp} - browse_reddit_search_results: Starting...")

    action_type = "comment"

    # --- Step 0: Check if logged in ---
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [STEP START] - Checking if logged in...")
    username = get_memory_item("logged_in_user")
    print(f"[DEBUG] - {timestamp} - browse_reddit_search_results: username from memory: {username}")

    if not username:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[WARNING] - {timestamp} - browse_reddit_search_results: Not logged in. Cannot browse search results.")
        return "I'm on the Reddit search results page, but it seems like I'm not logged in. I need to log in to Reddit before I can browse and select posts."

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [STEP END] - Checked if logged in.")

    # --- Step 1: Check if there are any Reddit posts in the search results ---
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [STEP START] - Checking for Reddit posts...")
    try:
        # Wait for at least one post element to be present (adjust timeout if needed)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a[data-testid="post-title"]')))
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[LOG] - {timestamp} - browse_reddit_search_results: Found at least one Reddit post in the search results.")

    except TimeoutException:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[WARNING] - {timestamp} - browse_reddit_search_results: No Reddit posts found in the search results.")
        return "No Reddit posts were found for the provided search query. Please try a different search query."

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [STEP END] - Checked for Reddit posts.")

    # --- Step 2: Check for 'No Results' ---
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [STEP START] - Checking for 'No Results'...")
    print(f"[LOG] - {timestamp} - browse_reddit_search_results: Checking for 'No Results' message...")

    while 'data-testid="search-no-results"' in driver.page_source:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[LOG] - {timestamp} - browse_reddit_search_results: 'No Results' message found. Refreshing the page...")
        driver.refresh()
        wait_for_page_load(driver)
        time.sleep(3)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[LOG] - {timestamp} - browse_reddit_search_results: Page refreshed.")

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [STEP END] - Checked for 'No Results'.")

    # --- Step 3: Enforce action cooldown ---
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [STEP START] - Enforcing action cooldown.")

    if username:  # We already have the username from Step 0
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[LOG] - {timestamp} - browse_reddit_search_results: Enforcing cooldown for user: {username}...")
        enforce_action_cooldown(username, action_type)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[LOG] - {timestamp} - browse_reddit_search_results: Cooldown enforced.")
    else:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[WARNING] - {timestamp} - browse_reddit_search_results: Username not found in memory. Skipping cooldown enforcement.")

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [STEP END] - Enforced action cooldown.")

    # --- Step 4: Find the first suitable post based on sentiment ---
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [STEP START] - Finding the first suitable post...")
    print(f"[LOG] - {timestamp} - browse_reddit_search_results: Retrieving user's sentiment preference from memory...")

    desired_sentiment = get_memory_item("desired_sentiment")

    print(f"[DEBUG] - {timestamp} - browse_reddit_search_results: desired_sentiment from memory: {desired_sentiment}")


    print(f"[LOG] - {timestamp} - browse_reddit_search_results: Starting to search for suitable posts...")
    max_search_attempts = 10
    for attempt in range(max_search_attempts):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[LOG] - {timestamp} - browse_reddit_search_results: Search attempt {attempt+1} of {max_search_attempts}...")

        post_elements = driver.find_elements(By.CSS_SELECTOR, 'a[data-testid="post-title"]')
        print(f"[DEBUG] - {timestamp} - browse_reddit_search_results: Found {len(post_elements)} post elements.")

        for post_element in post_elements:
            try:
                title = post_element.text.strip()
                url = post_element.get_attribute("href")
                print(f"[DEBUG] - {timestamp} - browse_reddit_search_results: Processing post: Title: {title}, URL: {url}")

                if not url or not title:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[WARNING] - {timestamp} - browse_reddit_search_results: Skipping post with missing title or URL.")
                    continue

                # --- Check title length ---
                if len(title) < 5:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[LOG] - {timestamp} - browse_reddit_search_results: Skipping post with title shorter than 5 characters: {title}")
                    continue

                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[LOG] - {timestamp} - browse_reddit_search_results: Checking if post has already been commented on: {url}...")

                if not has_performed_action_on_post(username, action_type, url):
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[LOG] - {timestamp} - browse_reddit_search_results: Post has not been commented on.")

                    # --- Sentiment Analysis using LLM ---
                    if desired_sentiment and desired_sentiment.lower() != "none":
                        sentiment_prompt = f"""
                        Instructions: Analyze the sentiment of the following Reddit post title. 

                        Post Title: {title}

                        Possible Sentiments:
                        - Negative
                        - Positive
                        - Neutral

                        Respond in the following format:

                        ANSWER_START
                        [Sentiment]
                        ANSWER_END
                        <-stop->
                        """
                        print(f"[DEBUG] - {timestamp} - browse_reddit_search_results: Sending sentiment prompt to LLM: {sentiment_prompt}")
                        sentiment_response = llm.invoke(sentiment_prompt, stop=["<-stop->"], timeout=30, max_tokens=15).strip()
                        print(f"[DEBUG] - {timestamp} - browse_reddit_search_results: Received sentiment response from LLM: {sentiment_response}")

                        sentiment_match = re.search(r"ANSWER_START\n(.*)\nANSWER_END", sentiment_response, re.IGNORECASE)
                        if sentiment_match:
                            sentiment = sentiment_match.group(1).strip()
                            print(f"[DEBUG] - {timestamp} - browse_reddit_search_results: Extracted sentiment: {sentiment}")

                            if sentiment.lower() == desired_sentiment and any(keyword.lower() in title.lower() for keyword in search_query.split()): # Replace `extracted_search_query` with `search_query` 
                                print(f"[DEBUG] - {timestamp} - browse_reddit_search_results: Navigating to post: {url}")
                                navigate_and_wait(driver, url)
                                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                print(f"[LOG] - {timestamp} - browse_reddit_search_results: Found suitable post: {url}")
                                return f"Navigated to post: {url}"
                        else:
                            print(f"[ERROR] - {timestamp} - browse_reddit_search_results: Could not extract sentiment from LLM response:\n{sentiment_response}")
                    else:
                        # --- No sentiment preference, navigate to the first suitable post ---
                        print(f"[DEBUG] - {timestamp} - browse_reddit_search_results: Navigating to post (no sentiment preference): {url}")
                        navigate_and_wait(driver, url)
                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print(f"[LOG] - {timestamp} - browse_reddit_search_results: Found suitable post (no sentiment preference): {url}")
                        return f"Navigated to post: {url}"

            except Exception as e:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[ERROR] - {timestamp} - browse_reddit_search_results: Error processing post element: {e}")
                continue

        # --- If no suitable post is found, scroll down to load more posts ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[LOG] - {timestamp} - browse_reddit_search_results: No suitable post found in this set of results. Scrolling down to load more...")
        ActionChains(driver).send_keys(Keys.END).perform()
        time.sleep(2)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[LOG] - {timestamp} - browse_reddit_search_results: No suitable posts found after {max_search_attempts} attempts.")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] - {timestamp} - [STEP END] - Finding the first suitable post...")
    return f"No suitable posts found after {max_search_attempts} attempts. Try a different search or come back later."


def generate_password(length=12):
    """Generates a random password using only letters and numbers."""
    characters = string.ascii_letters + string.digits  # Only letters and numbers
    password = ''.join(random.choice(characters) for i in range(length))
    return password

### END OF FILE tools/reddit_actions.py ###
