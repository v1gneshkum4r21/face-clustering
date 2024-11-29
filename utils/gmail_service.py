from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64
import os
import pickle

def get_gmail_service():
    """Get Gmail API service using the same credentials as Drive"""
    try:
        creds = None
        # Reuse the same credentials we're using for Drive
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
            
        service = build('gmail', 'v1', credentials=creds)
        return service
    except Exception as e:
        raise Exception(f"Gmail service initialization failed: {str(e)}")

def send_email_notification(to_email, cluster_id, drive_link):
    """Send email using Gmail API"""
    try:
        service = get_gmail_service()
        
        message = MIMEText(f"""
        Your face cluster images are ready!
        
        Cluster ID: {cluster_id}
        View images here: {drive_link}
        """)
        
        message['to'] = to_email
        message['from'] = os.getenv('SMTP_USERNAME')
        message['subject'] = f'Face Cluster {cluster_id} Images'
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        return True, "Email sent successfully"
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"
