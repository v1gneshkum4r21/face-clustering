import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from pathlib import Path

def verify_smtp_credentials():
    try:
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_username = os.getenv('SMTP_USERNAME')
        smtp_password = os.getenv('SMTP_PASSWORD')
        
        if not all([smtp_username, smtp_password]):
            return False, "SMTP credentials not configured"
            
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_username, smtp_password)
            return True, "SMTP credentials verified"
    except smtplib.SMTPAuthenticationError:
        return False, "Invalid SMTP credentials. Please check your App Password"
    except Exception as e:
        return False, f"SMTP connection error: {str(e)}"

def send_cluster_notification(to_email, cluster_id, drive_link):
    """Send email notification about cluster upload"""
    # First verify credentials
    success, message = verify_smtp_credentials()
    if not success:
        return False, f"SMTP verification failed: {message}"
        
    try:
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_username = os.getenv('SMTP_USERNAME')
        smtp_password = os.getenv('SMTP_PASSWORD')

        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = to_email
        msg['Subject'] = f'Face Cluster {cluster_id} Images'

        body = f"""
        Your face cluster images are ready!
        
        Cluster ID: {cluster_id}
        View images here: {drive_link}
        """
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)

        return True, "Notification sent successfully"
    except smtplib.SMTPAuthenticationError:
        return False, "Gmail login failed. Please check your App Password"
    except Exception as e:
        return False, f"Failed to send notification: {str(e)}"