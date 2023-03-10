from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from db import get_follow_bot_collection
from utils import send_email
import os


def set_up_web_driver():
    driver = None
    # check if local or production
    if os.getenv("PRODUCTION") == "True":
        # set up web driver
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument(f'user-agent={user_agent}')
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")
        driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
        print("Headless Chrome Initialized")
    else:
        chrome_options = webdriver.ChromeOptions()
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
        chrome_options.add_argument(f'user-agent={user_agent}')
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        driver = webdriver.Chrome(chrome_options=chrome_options)
        print("Chrome Initialized")
    return driver

def navigate_to_linkedin(driver):
    # navigate to LinkedIn
    driver.get("https://www.linkedin.com/")

def login(driver, user, pwd):
    # wait for page to load
    wait = WebDriverWait(driver, 10)
    element = wait.until(EC.element_to_be_clickable((By.NAME, "session_key")))

    # log in to LinkedIn
    username = driver.find_element(By.NAME, "session_key")
    username.send_keys(user)
    password = driver.find_element(By.NAME,"session_password")
    password.send_keys(pwd)
    password.send_keys(Keys.RETURN)

def wait_for_page_load(driver):
    # wait for page to load without using time.sleep()
    wait = WebDriverWait(driver, 20)
    try:
        element =  wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@aria-label='Search']")))
    except:
        driver.get_screenshot_as_file("screenshot.png")
        # send email to notify that the bot has crashed
        return False
    return True

def go_to_profile(driver, profile_url):
    driver.get(profile_url)
    wait = WebDriverWait(driver, 60)
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "button")))

def find_buttons(driver):
    buttons = driver.find_elements(By.CSS_SELECTOR, 'button')
    connect_button = None
    more_button = None
    for button in buttons:
        if button.text == "Connect":
            connect_button = button
            break
    for button in buttons:
        if button.text == "More":
            more_button = button
            break
    return connect_button, more_button

def click_connect_button(driver, connect_button):
    try:
        connect_button.click()
        # wait for the Send now button to be clickable
        time.sleep(3)
        buttons = driver.find_elements(By.CSS_SELECTOR, 'button')
        send_now_button = None
        for button in buttons:
            if button.text == "Send":
                send_now_button = button
                break
        if send_now_button:
            send_now_button.click()
            time.sleep(5)
    except:
        # click the more button
        return False
    return True

def click_more_button(driver, more_button):
    try:
        more_button.click()
        time.sleep(5)

        button_container = driver.find_elements(By.CLASS_NAME, 'artdeco-dropdown__content-inner')
        connect_button = None
        # get the children of the button container
        for container in button_container:
            container = container.find_elements(By.TAG_NAME, 'span')
            # loop through the elements and find the one with the text connect
            for element in container:
                if element.text == "Connect":
                    connect_button = element
                    break
    except:
        return None
    return connect_button
    

def run_bot(user, password, profiles):
    driver = set_up_web_driver()
    navigate_to_linkedin(driver)
    print(f'Logging in as {user}')
    login(driver, user, password)
    if wait_for_page_load(driver):
        print("User logged in")
    else:
        print("User failed to log in")
        send_email(user, "LinkedIn Bot Error", f"LinkedIn bot was unable to log in as {user}", "screenshot.png")
        return None
    connected_profiles = []
    failed_connections = []
    for index, profile in enumerate(profiles):
        print(f"Searching for {profile}")
        did_connect = False
        go_to_profile(driver, profile)
        connect_button, more_button = find_buttons(driver)
        if connect_button and more_button:
            print("Found both buttons")
        elif connect_button:
            print("Found connect button")
        elif more_button:
            print("Found more button")
        else:
            print("Found no buttons")

        if connect_button:
            did_connect = click_connect_button(driver, connect_button)
            if not did_connect:
                connect_button = click_more_button(driver, more_button)
                did_connect = click_connect_button(driver, connect_button)
        else:
            connect_button = click_more_button(driver, more_button)
            did_connect = click_connect_button(driver, connect_button)
        if did_connect:
            connected_profiles.append(profile)
            print(f"Connected to {profile}")
        else:
            failed_connections.append(profile)
            print(f"Failed to connect to {profile}")
        if index % 20 == 0 and index != 0:
            print("Sleeping for 1 hour...")
            time.sleep(600)
        else:
            time.sleep(5)
    driver.quit()
    print("Bot finished connecting to profiles")
    follow_bot_collecyion = get_follow_bot_collection()
    follow_bot_collecyion.insert_one({'email': user, 'connected_profiles': connected_profiles, 'failed_connections': failed_connections, 'time': time.time()})
    print("Results saved to database")
    # send email to user
    email_address = user
    subject = "LinkedIn Following Bot Results"
    failed_connections_str = ""
    for profile in failed_connections:
        failed_connections_str += profile + "\n"
    # in the body of the email, include the number of profiles connected to and the number of failed connections and the profiles that failed
    body = f"Number of profiles connected to: {len(connected_profiles)}\nNumber of failed connections: {len(failed_connections)}\nProfiles that failed: {failed_connections_str}"
    send_email(email_address, subject, body)
    print(f"Email sent to {user}")
    return connected_profiles, failed_connections

# if __name__ == "__main__":
#     main()