from __future__ import print_function
import os
from dotenv import load_dotenv
import requests

load_dotenv()


def send_email(to_email, subject, contents):
    """Send an email using Gmail API (OAuth 2.0)."""
    try:
        # Read and customize email template
        with open("assets/email_template.html", "r") as file:
            html_content = file.read()
            html_content = html_content.replace("${title}", subject)
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
                    "name": "Originsoft Consultancy"
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


def broadcast_email(leads, subject, email_contents):
    """Send an email to multiple recipients."""

    send_email(os.getenv("ADDITIONAL_RECEPIENTS"), subject, email_contents)

    for lead in leads:
        print(f"Email sent to " + lead["email"])
        send_email(lead["email"], subject, email_contents)
