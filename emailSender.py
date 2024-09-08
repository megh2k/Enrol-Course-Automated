
from dotenv import load_dotenv
import smtplib
import os
from email.message import EmailMessage

load_dotenv()



def send_email(subject):
    msg = EmailMessage()
    msg.set_content('Thanks pathhxh for creating this bot.')

    msg['Subject'] = subject
    msg['From'] = "hirparamegh@gmail.com"
    msg['To'] = os.getenv("TO_EMAIL")

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login("hirparamegh@gmail.com", "mbib xhyp gcng szze")
    s.send_message(msg)
    s.quit()
