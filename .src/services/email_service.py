import streamlit as st
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

logger = logging.getLogger(__name__)

def send_feedback_email(
    transcript: str,
    klantuitvraag: str,
    feedback: str,
    additional_feedback: str,
    user_first_name: str
) -> bool:
    """
    Sends a feedback email with the provided content.
    
    Args:
        transcript (str): The conversation transcript
        klantuitvraag (str): The generated client inquiry
        feedback (str): Type of feedback (Positive/Negative)
        additional_feedback (str): Additional feedback comments
        user_first_name (str): User's first name
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Validate required parameters
        if not user_first_name:
            logger.error("User first name is required")
            return False

        # Get email configuration from secrets
        email_config = st.secrets.get("email", {})
        receiving_email = email_config.get("receiving_email")
        smtp_server = email_config.get("smtp_server")
        smtp_port = email_config.get("smtp_port")
        username = email_config.get("username")
        password = email_config.get("password")

        # Validate email configuration
        if not all([receiving_email, smtp_server, smtp_port, username, password]):
            logger.error("Incomplete email configuration")
            return False

        # Create email message
        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = receiving_email
        msg['Subject'] = f"Klantuitvraagtool Feedback - {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        # Format email body
        body = f"""
        Nieuwe feedback ontvangen

        Gebruiker: {user_first_name}
        Feedback Type: {feedback}
        Tijdstip: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

        Aanvullende Feedback:
        {additional_feedback if additional_feedback else 'Geen aanvullende feedback gegeven'}

        Transcript:
        {transcript if transcript else 'Geen transcript beschikbaar'}

        Gegenereerde Klantuitvraag:
        {klantuitvraag if klantuitvraag else 'Geen klantuitvraag beschikbaar'}
        """

        msg.attach(MIMEText(body, 'plain'))

        # Send email
        with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg)

        logger.info(f"Feedback email sent successfully for user {user_first_name}")
        return True

    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP authentication failed")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error occurred: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in send_feedback_email: {str(e)}")
        return False