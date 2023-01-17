from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from db import get_follow_bot_collection
from utils import send_email


def set_up_web_driver():
    # set up web driver
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(chrome_options=chrome_options)
    return driver

def navigate_to_linkedin(driver):
    # navigate to LinkedIn
    driver.get("https://www.linkedin.com/")

def login(driver, username, password):
    # wait for page to load
    wait = WebDriverWait(driver, 10)
    element = wait.until(EC.element_to_be_clickable((By.NAME, "session_key")))

    # log in to LinkedIn
    username = driver.find_element(By.NAME, "session_key")
    username.send_keys(username)
    password = driver.find_element(By.NAME,"session_password")
    password.send_keys(password)
    password.send_keys(Keys.RETURN)

def wait_for_page_load(driver):
    # wait for page to load without using time.sleep()
    wait = WebDriverWait(driver, 20)
    element =  wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@aria-label='Search']")))

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
    more_button.click()
    time.sleep(2)

    button_container = driver.find_elements(By.CLASS_NAME, 'artdeco-dropdown__content-inner')
    # get the children of the button container
    for container in button_container:
        container = container.find_elements(By.TAG_NAME, 'span')
        # loop through the elements and find the one with the text connect
        for element in container:
            if element.text == "Connect":
                connect_button = element
                break
    return connect_button

def run_bot(user, password, profiles):
    driver = set_up_web_driver()
    navigate_to_linkedin(driver)
    login(driver, user, password)
    connected_profiles = []
    failed_connections = []
    for index, profile in enumerate(profiles):
        did_connect = False
        go_to_profile(driver, profile)
        wait_for_page_load(driver)
        connect_button, more_button = find_buttons(driver)
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
        else:
            failed_connections.append(profile)
        if index % 20 == 0 and index != 0:
            print("Sleeping for 1 hour...")
            time.sleep(3600)
        else:
            time.sleep(5)
    driver.quit()
    follow_bot_collecyion = get_follow_bot_collection()
    follow_bot_collecyion.insert_one({'email': user, 'connected_profiles': connected_profiles, 'failed_connections': failed_connections, 'time': time.time()})
    # send email to user
    email_address = user
    subject = "LinkedIn Following Bot Results"
    # in the body of the email, include the number of profiles connected to and the number of failed connections and the profiles that failed
    body = f"Number of profiles connected to: {len(connected_profiles)}\nNumber of failed connections: {len(failed_connections)}\nProfiles that failed: {failed_connections}"
    send_email(email_address, subject, body)
    return connected_profiles, failed_connections

# if __name__ == "__main__":
#     main()