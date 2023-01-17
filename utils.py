from email.message import EmailMessage
import smtplib, os
from dotenv import load_dotenv
load_dotenv()

def open_csv_file(csv_file):
    # open the csv file and get all of the profile urls
    csv_file.seek(0)
    profile_urls = csv_file.read().decode("utf-8").splitlines()
    return profile_urls

def send_email(email_address, subject, body):
    # create a new email message
    msg = EmailMessage()
    # set the email address of the sender
    msg['From'] = 'streetcodernate@gmail.com'
    # set the email address of the receiver
    msg['To'] = email_address
    # set the subject of the email
    msg['Subject'] = subject
    # set the body of the email
    msg.set_content(body)
    # set the email server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    # start the server
    server.starttls()
    # login to the server
    server.login('streetcodernate@gmail.com', os.getenv('GMAIL_PWD'))
    # send the email
    server.send_message(msg)
    # close the server
    server.quit()

send_email('natebaker2427@gmail.com', 'Test', 'This is a test')

