from langchain.tools import tool

@tool
def send_email_summary(recipient: str, subject: str, body: str) -> str:
    """
    Sends an official email summary or notification to a recipient.
    Provide recipient email address, subject line, and body text.
    """
    # Simulated email delivery
    return f"Successfully sent email notification to '{recipient}' (Subject: {subject})."
