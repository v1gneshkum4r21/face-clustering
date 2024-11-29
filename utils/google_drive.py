from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from pathlib import Path
import os
from dotenv import load_dotenv
import pickle
import socket

load_dotenv()

# Allow insecure localhost for testing
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

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

def get_drive_service():
    """Get an authorized Drive service instance"""
    try:
        creds = setup_google_drive()
        service = build('drive', 'v3', credentials=creds)
        return service
    except Exception as e:
        raise Exception(f"Drive service initialization failed: {str(e)}")

def upload_images_to_drive(cluster_id, image_paths):
    """Upload cluster images to Google Drive and return sharing link"""
    try:
        service = get_drive_service()
        
        # Debug print folder ID
        folder_parent_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
        print(f"Using Drive folder ID: {folder_parent_id}")
        
        if not folder_parent_id:
            raise ValueError("GOOGLE_DRIVE_FOLDER_ID not set in environment")
            
        # Debug print image paths
        print(f"\nAttempting to upload {len(image_paths)} images:")
        for path in image_paths:
            print(f"- {path} (exists: {Path(path).exists()})")
        
        # Get folder ID from env
        folder_parent_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
        if not folder_parent_id:
            raise ValueError("GOOGLE_DRIVE_FOLDER_ID not set in environment")
            
        # Create cluster folder
        folder_metadata = {
            'name': f'Face_Cluster_{cluster_id}',
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [folder_parent_id]
        }
        
        folder = service.files().create(
            body=folder_metadata,
            fields='id, webViewLink'
        ).execute()
        
        folder_id = folder.get('id')
        folder_link = folder.get('webViewLink')
        
        if not folder_id:
            raise Exception("Failed to get folder ID")
            
        # Upload images
        uploaded_count = 0
        for image_path in image_paths:
            try:
                if not isinstance(image_path, Path):
                    image_path = Path(image_path)
                    
                if not image_path.exists():
                    print(f"Skipping non-existent image: {image_path}")
                    continue
                    
                mime_type = 'image/jpeg'
                if image_path.suffix.lower() in ['.png']:
                    mime_type = 'image/png'
                
                file_metadata = {
                    'name': image_path.name,
                    'parents': [folder_id]
                }
                
                media = MediaFileUpload(
                    str(image_path),
                    mimetype=mime_type,
                    resumable=True
                )
                
                file = service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
                
                uploaded_count += 1
                print(f"Uploaded {image_path.name} to Drive ({uploaded_count}/{len(image_paths)})")
                
            except Exception as e:
                print(f"Error uploading {image_path}: {str(e)}")
                continue
        
        if uploaded_count == 0:
            raise Exception("No images were uploaded successfully")
            
        # Set folder permissions for sharing
        permission = {
            'type': 'anyone',
            'role': 'reader',
            'allowFileDiscovery': False
        }
        
        service.permissions().create(
            fileId=folder_id,
            body=permission
        ).execute()
        
        return True, folder_link
        
    except Exception as e:
        print(f"Drive upload error: {str(e)}")
        return False, str(e)
