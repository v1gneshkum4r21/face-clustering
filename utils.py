import face_recognition
import os
import json
import numpy as np
from pathlib import Path
import streamlit as st
from shutil import copyfile
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv
import re
from PIL import Image
from shared_constants import RESULTS_FOLDER, DATASET_FOLDER
from datetime import datetime

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def show_cluster_preview(cluster_id):
    """Display preview of images in a cluster"""
    cluster_path = Path(RESULTS_FOLDER) / str(cluster_id)
    if not cluster_path.exists():
        return []
    
    images = []
    for img_path in cluster_path.glob('*.{jpg,jpeg,png}'):
        try:
            img = Image.open(img_path)
            images.append((img_path.name, img))
        except Exception as e:
            print(f"Error loading image {img_path}: {e}")
    return images

def process_uploaded_files(files):
    """Process multiple uploaded files"""
    processed_files = []
    for file in files:
        temp_path = Path("temp") / file.name
        temp_path.parent.mkdir(exist_ok=True)
        
        try:
            with open(temp_path, "wb") as f:
                f.write(file.getbuffer())
            
            face_locations = face_recognition.load_image_file(str(temp_path))
            if len(face_recognition.face_locations(face_locations)) > 0:
                processed_files.append(temp_path)
            else:
                print(f"No face detected in {file.name}")
        except Exception as e:
            print(f"Error processing {file.name}: {e}")
    
    return processed_files

def show_dashboard():
    """Show admin dashboard statistics"""
    try:
        total_clusters = len([d for d in os.listdir(RESULTS_FOLDER) if os.path.isdir(os.path.join(RESULTS_FOLDER, d))])
        total_images = sum(len(files) for _, _, files in os.walk(RESULTS_FOLDER))
        
        stats = {
            "Total Clusters": total_clusters,
            "Total Images": total_images,
        }
        return stats
    except Exception as e:
        print(f"Error generating dashboard: {e}")
        return {}

def process_folder(folder_path):
    """Process all images in a folder"""
    processed_files = []
    folder = Path(folder_path)
    
    for file_path in folder.glob('*.{jpg,jpeg,png}'):
        try:
            image = face_recognition.load_image_file(str(file_path))
            face_locations = face_recognition.face_locations(image)
            
            if face_locations:
                processed_files.append(file_path)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    return processed_files

def get_all_clusters():
    """Get information about all clusters"""
    clusters = []
    try:
        for cluster_dir in Path(RESULTS_FOLDER).iterdir():
            if cluster_dir.is_dir():
                image_count = len(list(cluster_dir.glob('*.{jpg,jpeg,png}')))
                clusters.append({
                    'id': cluster_dir.name,
                    'image_count': image_count,
                    'path': str(cluster_dir)
                })
        return clusters
    except Exception as e:
        print(f"Error getting clusters: {e}")
        return []

def delete_cluster(cluster_id):
    """Delete an entire cluster"""
    try:
        cluster_path = Path(RESULTS_FOLDER) / str(cluster_id)
        if cluster_path.exists():
            for file in cluster_path.glob('*'):
                file.unlink()
            cluster_path.rmdir()
            return True
        return False
    except Exception as e:
        print(f"Error deleting cluster {cluster_id}: {e}")
        return False

def delete_image_from_cluster(cluster_id, image_name):
    """Delete a specific image from a cluster"""
    try:
        image_path = Path(RESULTS_FOLDER) / str(cluster_id) / image_name
        if image_path.exists():
            image_path.unlink()
            return True
        return False
    except Exception as e:
        print(f"Error deleting image {image_name}: {e}")
        return False

def move_image_to_cluster(source_cluster, target_cluster, image_name):
    """Move an image from one cluster to another"""
    try:
        source_path = Path(RESULTS_FOLDER) / str(source_cluster) / image_name
        target_path = Path(RESULTS_FOLDER) / str(target_cluster) / image_name
        
        if not source_path.exists():
            return False
            
        target_path.parent.mkdir(exist_ok=True)
        copyfile(str(source_path), str(target_path))
        source_path.unlink()
        return True
    except Exception as e:
        print(f"Error moving image: {e}")
        return False

def process_file(file_path, encodings_manager):
    """Process a single file and return cluster ID"""
    try:
        image = face_recognition.load_image_file(file_path)
        face_locations = face_recognition.face_locations(image)
        
        if not face_locations:
            return None
            
        face_encoding = face_recognition.face_encodings(image, face_locations)[0]
        
        # Find matching cluster or create new one
        for cluster_id, encodings in encodings_manager.encodings.items():
            matches = face_recognition.compare_faces(encodings, face_encoding)
            if any(matches):
                return cluster_id
                
        # Create new cluster if no match found
        new_cluster_id = str(len(encodings_manager.encodings) + 1)
        encodings_manager.add_encoding(new_cluster_id, face_encoding)
        return new_cluster_id
        
    except Exception as e:
        print(f"Error processing file: {e}")
        return None

def email_is_valid(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def send_cluster_notification(email, cluster_id):
    """Send notification email about cluster results"""
    try:
        success, message = upload_to_drive_and_send_email(email, cluster_id)
        return success, message
    except Exception as e:
        print(f"Error sending notification: {e}")
        return False, str(e)

def save_encodings(encodings_dict, file_path):
    """Save face encodings to file"""
    try:
        serializable_encodings = {
            k: [enc.tolist() for enc in v] 
            for k, v in encodings_dict.items()
        }
        with open(file_path, 'w') as f:
            json.dump(serializable_encodings, f)
        return True
    except Exception as e:
        print(f"Error saving encodings: {str(e)}")
        return False

def load_encodings(file_path):
    """Load face encodings from file"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
                return {
                    k: [np.array(enc) for enc in v] 
                    for k, v in data.items()
                }
        return {}
    except Exception as e:
        print(f"Error loading encodings: {str(e)}")
        return {}

def upload_to_drive_and_send_email(to_email, cluster_id):
    """Upload cluster images to Drive and send email"""
    try:
        cluster_path = Path(RESULTS_FOLDER) / str(cluster_id)
        if not cluster_path.exists():
            raise Exception(f"Cluster folder not found: {cluster_path}")
            
        service = get_drive_service()
        
        folder_metadata = {
            'name': f'Face_Cluster_{cluster_id}',
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = service.files().create(body=folder_metadata, fields='id').execute()
        folder_id = folder.get('id')
        
        for img_path in cluster_path.glob('*.{jpg,jpeg,png}'):
            if img_path.is_file():
                file_metadata = {'name': img_path.name, 'parents': [folder_id]}
                media = MediaFileUpload(str(img_path), mimetype='image/jpeg')
                service.files().create(body=file_metadata, media_body=media).execute()
        
        permission = {'type': 'anyone', 'role': 'reader'}
        service.permissions().create(fileId=folder_id, body=permission).execute()
        
        drive_link = f"https://drive.google.com/drive/folders/{folder_id}"
        
        msg = MIMEMultipart()
        msg['Subject'] = f'Your Face Recognition Results - Cluster {cluster_id}'
        msg['From'] = os.getenv('FROM_EMAIL')
        msg['To'] = to_email
        
        email_body = f"""
        Hello,
        
        We found matches for your uploaded photos in Cluster {cluster_id}.
        You can view all the matched photos here: {drive_link}
        
        Best regards,
        Face Recognition Team
        """
        
        msg.attach(MIMEText(email_body, 'plain'))
        
        with smtplib.SMTP(os.getenv('SMTP_SERVER'), int(os.getenv('SMTP_PORT'))) as server:
            server.starttls()
            server.login(os.getenv('SMTP_USERNAME'), os.getenv('SMTP_PASSWORD'))
            server.send_message(msg)
        
        return True, "Successfully uploaded to Drive and sent email"
        
    except Exception as e:
        print(f"Error in upload_to_drive_and_send_email: {str(e)}")
        return False, str(e)

def get_drive_service():
    """Get authenticated Google Drive service"""
    creds = None
    token_file = 'token.json'
    
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
            SCOPES
        )
        creds = flow.run_local_server(port=0)
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
    
    return build('drive', 'v3', credentials=creds)

def show_system_stats():
    """Show system statistics for admin dashboard"""
    try:
        stats = {
            'total_clusters': len([d for d in os.listdir(RESULTS_FOLDER) if os.path.isdir(os.path.join(RESULTS_FOLDER, d))]),
            'total_images': sum(len(files) for _, _, files in os.walk(RESULTS_FOLDER)),
            'storage_used': sum(os.path.getsize(os.path.join(dirpath, filename)) 
                              for dirpath, _, filenames in os.walk(RESULTS_FOLDER) 
                              for filename in filenames) / (1024 * 1024),  # in MB
            'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return stats
    except Exception as e:
        print(f"Error getting system stats: {e}")
        return {}