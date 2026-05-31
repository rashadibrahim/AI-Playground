from langchain.tools import tool
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os

load_dotenv()

MAIL_ACCOUNT = os.getenv("MAIL_ACCOUNT")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

@tool("send_email",
    description=(
        "Use this tool to send an email. "
        "You need to provide the recipient's email address, subject, and body content."
    )
)
def send_email(to: str, subject: str, body: str) -> str:
    """
    Args:
        to: Recipient email address.
        subject: Subject of the email.
        body: Body content of the email.
    Returns:
        Text indicating success or failure.
    """

    try:
        msg = EmailMessage()
        msg["From"] = MAIL_ACCOUNT
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(MAIL_ACCOUNT, MAIL_PASSWORD)
            server.send_message(msg)

        return "Email sent successfully."
    except Exception as e:
        
        return f"Failed to send email: {e}"
