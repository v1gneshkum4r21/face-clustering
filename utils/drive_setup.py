from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
from pathlib import Path
import pickle

SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose'
]

def setup_google_drive():
    creds = None
    credentials_path = Path(os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'credentials.json'))
    token_path = Path('token.pickle')
    
    if not credentials_path.exists():
        raise FileNotFoundError(
            "credentials.json not found. Please download it from Google Cloud Console "
            "and place it in the project root directory or set GOOGLE_APPLICATION_CREDENTIALS"
        )
    
    if token_path.exists():
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path),
                SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    
    return creds 