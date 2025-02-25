from __future__ import print_function
import os
from dotenv import load_dotenv
import requests

load_dotenv()


def send_email(recipient_name, title, to_email, subject, contents):
    """Send an email using Gmail API (OAuth 2.0)."""
    try:
        # Read and customize email template
        with open("assets/email_template.html", "r") as file:
            html_content = file.read()
            html_content = html_content.replace("${title}", title)
            html_content = html_content.replace(
                "${recipient}", recipient_name)
            html_content = html_content.replace("${contents}", contents)

        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "accept": "application/json",
            "api-key": os.getenv("BREVO_API_KEY"),
            "content-type": "application/json"
        }
        payload = {
            "sender": {
                "name": "Originsoft Consultancy",
                "email": "contact@originsoftconsultancy.com"
            },
            "to": [
                {
                    "email": to_email,
                    "name": recipient_name
                }
            ],
            "subject": subject,
            "htmlContent": html_content
        }

        response = requests.post(url, headers=headers, json=payload)

        # print(response.status_code)
        # print(response.json())

        return response

    except Exception as e:

        print("Error sending email:", str(e))
