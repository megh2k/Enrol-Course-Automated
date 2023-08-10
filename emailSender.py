from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
from dotenv import load_dotenv

load_dotenv()


def send_email(content):

    sg = SendGridAPIClient(os.getenv('API_KEY'))
    message = Mail(
        from_email=os.getenv('FROM_EMAIL'),
        to_emails=os.getenv('TO_EMAIL'),
        subject=content,
        html_content='Thanks <strong>pathhxh</strong> for creating this bot.')

    sg.send(message)

