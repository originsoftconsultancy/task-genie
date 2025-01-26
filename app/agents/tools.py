import uuid
import sendgrid
from sendgrid.helpers.mail import Mail, To, Attachment, FileContent, FileName, FileType, Disposition
from sendgrid import SendGridAPIClient
from pydantic_ai.models.ollama import OllamaModel
from typing import Optional, Union, List
import openai
from pydantic import BaseModel, Field, ValidationError
from pydantic_ai import Agent, RunContext, Tool
from playwright.sync_api import sync_playwright
import ast
import os
import asyncio
from pydantic_ai.models import ModelResponse
import logfire
from dotenv import load_dotenv
from pydantic.dataclasses import dataclass
import subprocess
import sys
import traceback
from tavily import TavilyClient
import base64

logfire.configure()


def search_tool(query: str) -> dict:
    """
    This tool searches for a query on the internet and returns results in json.

    Args:
        query: str, The query to search.

    Returns:
        dict: the results of the search.
    """

    tavily_client = TavilyClient(
        api_key=os.getenv("TAVILY_API_KEY"))

    response = tavily_client.search(query)

    return response["results"]


def load_page_tool(url: str) -> str:
    """
    Fetches the web page given by the `url`, stores in a file and returns its contents.

    Args:
        url: str, url of the web page to fetch.

    Returns:
        str: file path where contents are stored.

    """

    logfire.info(f"Loading page: {url}")
    content = ""
    with sync_playwright() as p:
        # Launch the browser in headless mode
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Navigate to the URL
        page.goto(url)

        # Wait for the page to fully load
        page.wait_for_load_state("networkidle")

        # Get the rendered HTML
        content = page.content()
        browser.close()

    return content


def send_email_with_attachment_tool(to_email, subject, content, file_path):
    """
    Sends an email with an attachment using SendGrid API.

    Parameters:
        to_email (str): Recipient's email address.
        subject (str): Email subject.
        content (str): Email content.
        file_path (str): Path to the attachment file.

    Returns:
        str: Status message indicating success or failure.
    """
    try:
        # Create the email
        message = Mail(
            from_email=os.getenv("SENDGRID_FROM_EMAIL"),
            to_emails=to_email,
            subject=subject,
            plain_text_content=content
        )

        # Add the attachment
        if file_path:
            with open(file_path, 'rb') as f:
                file_data = f.read()
                encoded_file = base64.b64encode(file_data).decode()

            attachment = Attachment(
                FileContent(encoded_file),
                FileName(os.path.basename(file_path)),
                FileType("application/octet-stream"),
                Disposition("attachment")
            )
            message.attachment = attachment

        # Send the email
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        response = sg.send(message)
        return f"Email sent successfully! Status code: {response.status_code}"

    except Exception as e:
        return f"An error occurred: {str(e)}"
