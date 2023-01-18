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

with st.form("my_form"):
   # create a text input for the username
   username = st.text_input("Enter your LinkedIn username")
   # create a text input for the password
   password = st.text_input("Enter your LinkedIn password", type="password")
    # create a file uploader for the CSV
   csv_file = st.file_uploader("Upload a CSV of LinkedIn Profile URLs", type="csv" )
   col1, col2 = st.columns(2)

   # Every form must have a submit button.
   submitted = st.form_submit_button("Start Bot")
   if submitted and csv_file and username and password:
    # get the profile urls from the csv file
    profile_urls = open_csv_file(csv_file)

    # start a new thread to run the bot
    thread = Thread(target=run_bot, args=(username, password, profile_urls))
    thread.start()

    # create a label for the number of profiles
    col2.markdown(f"#### Number of Profiles: {len(profile_urls)}")
    st.markdown("##### Bot is running...")
    st.markdown(f"##### The bot will follow 20 profiles per hour, so should take about {len(profile_urls) / 20} hours to complete.")
    st.markdown("##### We will email you when the bot is finished.")
    


