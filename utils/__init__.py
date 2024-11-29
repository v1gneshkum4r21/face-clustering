from .google_drive import upload_images_to_drive, get_drive_service
from .notifications import send_cluster_notification
from .system import show_system_stats
from .core import (
    delete_image_from_cluster,
    move_image_to_cluster,
    show_cluster_preview,
    process_uploaded_files,
    get_all_clusters,
    delete_cluster,
    save_encodings,
    email_is_valid,
    rename_cluster
)
from pathlib import Path
from shared_constants import RESULTS_FOLDER
from stages.process_image import process_file
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import psutil
from .gmail_service import send_email_notification
from PIL import Image

__all__ = [
    'upload_to_drive_and_send_email',
    'show_cluster_preview',
    'process_uploaded_files',
    'delete_cluster',
    'rename_cluster',
    'move_image_to_cluster',
    'delete_image_from_cluster',
    'get_all_clusters',
    'process_file',
    'save_encodings',
    'email_is_valid',
    'send_cluster_notification',
    'show_system_stats'
]

def upload_to_drive_and_send_email(to_email, cluster_id):
    try:
        cluster_path = Path(RESULTS_FOLDER) / str(cluster_id)
        print(f"Looking for images in: {cluster_path}")
        
        if not cluster_path.exists():
            raise Exception(f"Cluster folder not found: {cluster_path}")
        
        # Get image files with case-insensitive pattern
        image_files = []
        for ext in ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']:
            image_files.extend(list(cluster_path.glob(f'*{ext}')))
        
        print(f"Found {len(image_files)} images: {[f.name for f in image_files]}")
        
        if not image_files:
            raise Exception("No images found in cluster directory")
            
        success, drive_link = upload_images_to_drive(
            cluster_id, 
            image_files
        )
        
        if not success:
            raise Exception(f"Failed to upload to Drive: {drive_link}")
            
        notif_success, notif_msg = send_email_notification(to_email, cluster_id, drive_link)
        
        if not notif_success:
            raise Exception(f"Failed to send notification: {notif_msg}")
            
        return True, "Successfully uploaded to Drive and sent email"
        
    except Exception as e:
        print(f"Error in upload_to_drive_and_send_email: {str(e)}")
        return False, str(e)

def show_system_stats():
    """Get system statistics for admin dashboard"""
    stats = {
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent,
        'clusters_count': len(list(Path(RESULTS_FOLDER).glob('cluster_*'))),
        'total_images': sum(
            len(list(Path(RESULTS_FOLDER).glob(f'cluster_*/*.{ext}')))
            for ext in ['jpg', 'jpeg', 'png']
        )
    }
    return stats

def show_cluster_preview(cluster_id):
    cluster_path = Path(RESULTS_FOLDER) / str(cluster_id)
    print(f"Looking for images in: {cluster_path}")
    print(f"Path exists: {cluster_path.exists()}")
    
    if not cluster_path.exists():
        return []
    
    images = []
    # Check for files with individual patterns
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']:
        for img_path in cluster_path.glob(ext):
            try:
                print(f"Found image: {img_path}")
                img = Image.open(img_path)
                images.append((img_path.name, img))
            except Exception as e:
                print(f"Error loading image {img_path}: {e}")
    
    print(f"Total images found: {len(images)}")
    # Also list all files in directory for debugging
    print("All files in directory:", list(cluster_path.iterdir()))
    return images