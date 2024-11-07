import streamlit as st
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

def send_feedback_email(
    transcript: str,
    klantuitvraag: str,
    feedback: str,
    additional_feedback: str,
    user_first_name: str
) -> bool:
    """
    Sends feedback email with improved error handling and logging.
    
    Args:
        transcript (str): The conversation transcript
        klantuitvraag (str): The generated client inquiry
        feedback (str): Type of feedback (Positive/Negative)
        additional_feedback (str): Additional feedback comments
        user_first_name (str): User's first name
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Get email configuration from secrets
        email_secrets = st.secrets.get("email", {})
        receiving_email = email_secrets.get("receiving_email")
        smtp_server = email_secrets.get("smtp_server")
        smtp_port = email_secrets.get("smtp_port")
        username = email_secrets.get("username")
        password = email_secrets.get("password")

        # Validate email configuration
        if not all([receiving_email, smtp_server, smtp_port, username, password]):
            logger.error("Incomplete email configuration in secrets")
            raise ValueError("Email configuration is incomplete")

        # Create message
        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = receiving_email
        msg['Subject'] = f"Klantuitvraagtool Feedback - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # Create email body
        body = f"""
        Nieuwe feedback ontvangen van {user_first_name}

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
        
        # Connect to SMTP server and send email
        with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
            
        logger.info(f"Feedback email sent successfully from {user_first_name}")
        return True

    except ValueError as ve:
        logger.error(f"Configuration error: {str(ve)}")
        return False
    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP authentication failed")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error occurred: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in send_feedback_email: {str(e)}")
        return False