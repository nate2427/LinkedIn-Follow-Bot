import streamlit as st
from utils import open_csv_file
from follow_users import run_bot
from threading import Thread

st.title("LinkedIn Follow Bot")
# create a label for instructions
st.markdown("## Instructions")
# create a label for the instructions
st.markdown("1. Enter your LinkedIn profile credentials.\n")
st.markdown("2. Upload a CSV of direct LinkedIn Profile URLS\n")
st.markdown("3. Click the Start Bot button.\n")

# create a text input for the username
username = st.text_input("Enter your LinkedIn username")
# create a text input for the password
password = st.text_input("Enter your LinkedIn password", type="password")
# create a file uploader for the CSV
csv_file = st.file_uploader("Upload a CSV of LinkedIn Profile URLs", type="csv" )
col1, col2 = st.columns(2)
# create a button to start the bot
start_bot = col1.button("Start Bot")

# if the start bot button is clicked
if start_bot and csv_file and username and password:
    # open the csv file and get all of the profile urls
    profile_urls = open_csv_file(csv_file)

    # start a new thread to run the bot
    thread = Thread(target=run_bot, args=(username, password, profile_urls))
    thread.start()

    # create a label for the number of profiles
    col2.markdown(f"#### Number of Profiles: {len(profile_urls)}")
    st.markdown("##### Bot is running...")
    st.markdown("##### The bot will follow 20 profiles per hour.")
    st.markdown("##### We will email you when the bot is finished.")
    


